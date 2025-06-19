# modules/data_extractor.py
"""
Data Extractor Module
Handles database extraction with configurable schemas
"""

import sqlite3
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class DataExtractor:
    """Extracts data from databases using configurable schemas"""
    
    def __init__(self, config_manager, logger=None):
        self.config_manager = config_manager
        self.logger = logger
    
    def find_database_file(self, extraction_path: Path, db_config: Dict[str, Any]) -> Optional[Path]:
        """Find database file using configured paths"""
        if self.logger:
            self.logger.log_action("DB_SEARCH", f"Searching for database {db_config.get('description', 'Unknown')}")
        
        # Try primary path
        primary_path = extraction_path / db_config["primary"]
        if primary_path.exists():
            if self.logger:
                self.logger.log_action("DB_FOUND", f"Found at primary path: {primary_path}")
            return primary_path
        
        # Try backup path
        if "backup" in db_config:
            backup_path = extraction_path / db_config["backup"]
            if backup_path.exists():
                if self.logger:
                    self.logger.log_action("DB_FOUND", f"Found at backup path: {backup_path}")
                return backup_path
        
        # Try alternatives
        if "alternatives" in db_config:
            for alt_path in db_config["alternatives"]:
                alt_full_path = extraction_path / alt_path
                if alt_full_path.exists():
                    if self.logger:
                        self.logger.log_action("DB_FOUND", f"Found at alternative path: {alt_full_path}")
                    return alt_full_path
        
        # Try pattern matching for wildcards
        if "*" in db_config["primary"]:
            pattern_parts = db_config["primary"].split("*")
            try:
                for candidate in extraction_path.rglob(pattern_parts[-1]):
                    if all(part in str(candidate) for part in pattern_parts[:-1]):
                        if self.logger:
                            self.logger.log_action("DB_FOUND", f"Found via pattern matching: {candidate}")
                        return candidate
            except Exception as e:
                if self.logger:
                    self.logger.log_action("PATTERN_ERROR", f"Error in pattern matching: {str(e)}")
        
        if self.logger:
            self.logger.log_action("DB_NOT_FOUND", f"Database not found: {db_config['primary']}")
        return None
    
    def extract_from_database(self, db_path: Path, schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract data using configured schema"""
        if self.logger:
            self.logger.log_action("EXTRACTION_START", f"Starting extraction from {db_path}")
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Build and execute query
            query = self._build_query_from_schema(schema)
            
            if self.logger:
                self.logger.log_action("QUERY_EXECUTE", f"Executing query: {query[:200]}...")
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            # Get column names
            columns = [desc[0] for desc in cursor.description]
            
            # Convert to list of dictionaries
            extracted_data = []
            for row in results:
                record = {}
                for i, value in enumerate(row):
                    column_name = columns[i]
                    
                    # Apply data type conversions
                    converted_value = self._convert_data_type(value, column_name, schema)
                    record[column_name] = converted_value
                
                extracted_data.append(record)
            
            conn.close()
            
            if self.logger:
                self.logger.log_database_access(str(db_path), "EXTRACTION", len(extracted_data))
            
            return extracted_data
            
        except Exception as e:
            error_msg = f"Error extracting from {db_path}: {str(e)}"
            if self.logger:
                self.logger.log_action("EXTRACTION_ERROR", error_msg)
            raise Exception(error_msg)
    
    def _build_query_from_schema(self, schema: Dict[str, Any]) -> str:
        """Build SQL query from schema configuration"""
        table = schema["table"]
        columns = schema["columns"]
        
        # Build column selections
        select_parts = []
        for alias, column in columns.items():
            if alias == "timestamp" and "timestamp_conversion" in schema:
                select_parts.append(f"{schema['timestamp_conversion']} as {alias}")
            else:
                select_parts.append(f"{column} as {alias}")
        
        # Add join columns
        if "joins" in schema:
            for join_name, join_config in schema["joins"].items():
                for alias, column in join_config["columns"].items():
                    select_parts.append(f"{join_config['table']}.{column} as {alias}")
        
        query = f"SELECT {', '.join(select_parts)} FROM {table}"
        
        # Add joins
        if "joins" in schema:
            for join_name, join_config in schema["joins"].items():
                query += f" LEFT JOIN {join_config['table']} ON {join_config['on']}"
        
        # Add time filter for recent data (configurable timeframe)
        timeframe_days = schema.get("timeframe_days", 90)  # Default 90 days
        
        if "timestamp" in columns and "timestamp_conversion" in schema:
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=timeframe_days)
            cutoff_timestamp = cutoff_date.timestamp()
            
            # Handle different timestamp formats
            timestamp_conversion = schema["timestamp_conversion"]
            if "978307200" in timestamp_conversion:  # Cocoa timestamp
                query += f" WHERE {columns['timestamp']} > {cutoff_timestamp - 978307200}"
            elif "1000" in timestamp_conversion:  # Milliseconds
                query += f" WHERE {columns['timestamp']} > {cutoff_timestamp * 1000}"
            else:  # Regular Unix timestamp
                query += f" WHERE {columns['timestamp']} > {cutoff_timestamp}"
        
        # Add ordering
        order_column = columns.get("timestamp", columns.get("id", "1"))
        query += f" ORDER BY {order_column} DESC"
        
        # Add limit (configurable)
        record_limit = schema.get("record_limit", 10000)
        query += f" LIMIT {record_limit}"
        
        return query
    
    def _convert_data_type(self, value: Any, column_name: str, schema: Dict[str, Any]) -> Any:
        """Convert data types based on schema configuration"""
        if value is None:
            return None
        
        # Get data type conversions from schema
        conversions = schema.get("data_conversions", {})
        
        if column_name in conversions:
            conversion_type = conversions[column_name]
            
            try:
                if conversion_type == "boolean":
                    return bool(value)
                elif conversion_type == "integer":
                    return int(value)
                elif conversion_type == "float":
                    return float(value)
                elif conversion_type == "string":
                    return str(value)
                elif conversion_type == "datetime":
                    # Handle datetime conversion
                    if isinstance(value, str):
                        return value  # Already converted by SQL
                    else:
                        return datetime.datetime.fromtimestamp(float(value)).isoformat()
            except (ValueError, TypeError):
                pass  # Keep original value if conversion fails
        
        # Default conversions based on column naming
        column_lower = column_name.lower()
        
        # Boolean indicators
        if any(indicator in column_lower for indicator in ['is_', 'has_', 'can_', 'should_']):
            try:
                return bool(int(value))
            except (ValueError, TypeError):
                pass
        
        # Timestamp indicators
        if any(indicator in column_lower for indicator in ['timestamp', 'date', 'time']):
            if isinstance(value, (int, float)) and value > 1000000000:  # Looks like timestamp
                try:
                    return datetime.datetime.fromtimestamp(value).isoformat()
                except (ValueError, OSError):
                    pass
        
        return value
    
    def extract_sample_data(self, db_path: Path, table_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Extract sample data from any table for analysis"""
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Get column information
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Get sample data
            cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
            results = cursor.fetchall()
            
            # Convert to dictionaries
            sample_data = []
            for row in results:
                record = dict(zip(columns, row))
                sample_data.append(record)
            
            conn.close()
            
            if self.logger:
                self.logger.log_action("SAMPLE_EXTRACT", f"Extracted {len(sample_data)} sample records from {table_name}")
            
            return sample_data
            
        except Exception as e:
            if self.logger:
                self.logger.log_action("SAMPLE_ERROR", f"Error extracting sample from {table_name}: {str(e)}")
            return []
    
    def test_schema_compatibility(self, db_path: Path, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Test if schema is compatible with database"""
        compatibility_result = {
            'compatible': False,
            'table_exists': False,
            'columns_found': [],
            'columns_missing': [],
            'join_tables_found': [],
            'join_tables_missing': [],
            'test_query_success': False,
            'sample_record_count': 0
        }
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            table = schema["table"]
            columns = schema["columns"]
            
            # Check if main table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            if cursor.fetchone():
                compatibility_result['table_exists'] = True
                
                # Check columns
                cursor.execute(f"PRAGMA table_info({table})")
                existing_columns = [col[1] for col in cursor.fetchall()]
                
                for logical_name, column_name in columns.items():
                    if column_name in existing_columns:
                        compatibility_result['columns_found'].append(column_name)
                    else:
                        compatibility_result['columns_missing'].append(column_name)
                
                # Check join tables
                if "joins" in schema:
                    for join_name, join_config in schema["joins"].items():
                        join_table = join_config["table"]
                        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (join_table,))
                        if cursor.fetchone():
                            compatibility_result['join_tables_found'].append(join_table)
                        else:
                            compatibility_result['join_tables_missing'].append(join_table)
                
                # Test query execution
                try:
                    test_query = self._build_query_from_schema(schema).replace("LIMIT 10000", "LIMIT 1")
                    cursor.execute(test_query)
                    test_result = cursor.fetchone()
                    
                    if test_result:
                        compatibility_result['test_query_success'] = True
                        compatibility_result['sample_record_count'] = 1
                        
                        # Get actual record count
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        total_count = cursor.fetchone()[0]
                        compatibility_result['total_record_count'] = total_count
                
                except Exception as query_error:
                    compatibility_result['query_error'] = str(query_error)
            
            conn.close()
            
            # Determine overall compatibility
            compatibility_result['compatible'] = (
                compatibility_result['table_exists'] and
                compatibility_result['test_query_success'] and
                len(compatibility_result['columns_found']) > len(compatibility_result['columns_missing'])
            )
            
        except Exception as e:
            compatibility_result['error'] = str(e)
        
        return compatibility_result
    
    def get_database_statistics(self, db_path: Path) -> Dict[str, Any]:
        """Get comprehensive database statistics"""
        stats = {
            'file_path': str(db_path),
            'file_size_bytes': 0,
            'total_tables': 0,
            'total_records': 0,
            'tables': {},
            'largest_tables': [],
            'database_version': 'unknown'
        }
        
        try:
            # File statistics
            stats['file_size_bytes'] = db_path.stat().st_size
            stats['file_size_mb'] = round(stats['file_size_bytes'] / (1024 * 1024), 2)
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Get SQLite version
            cursor.execute("SELECT sqlite_version()")
            stats['database_version'] = cursor.fetchone()[0]
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            stats['total_tables'] = len(tables)
            
            # Get statistics for each table
            table_sizes = []
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    row_count = cursor.fetchone()[0]
                    
                    stats['tables'][table] = {
                        'row_count': row_count,
                        'estimated_size_kb': 0  # Could calculate if needed
                    }
                    
                    stats['total_records'] += row_count
                    table_sizes.append((table, row_count))
                    
                except Exception:
                    stats['tables'][table] = {'row_count': 0, 'error': 'Could not count rows'}
            
            # Sort tables by size
            table_sizes.sort(key=lambda x: x[1], reverse=True)
            stats['largest_tables'] = table_sizes[:10]  # Top 10 largest tables
            
            conn.close()
            
        except Exception as e:
            stats['error'] = str(e)
        
        return stats
