# modules/database_inspector.py
"""
Database Inspector Module
Handles database structure analysis and schema detection
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional
import json

class DatabaseInspector:
    """Inspects database structure and generates configurations"""
    
    def __init__(self, logger=None):
        self.logger = logger
    
    def inspect_database(self, db_path: Path) -> Dict[str, Any]:
        """Inspect database structure and return analysis"""
        if self.logger:
            self.logger.log_action("DB_INSPECT_START", f"Inspecting {db_path}")
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            inspection_result = {
                'database_path': str(db_path),
                'table_count': len(tables),
                'tables': {}
            }
            
            # Analyze each table
            for table in tables:
                table_info = self._analyze_table(cursor, table)
                inspection_result['tables'][table] = table_info
            
            conn.close()
            
            if self.logger:
                self.logger.log_action("DB_INSPECT_COMPLETE", f"Found {len(tables)} tables in {db_path}")
            
            return inspection_result
            
        except Exception as e:
            error_result = {'error': str(e), 'database_path': str(db_path)}
            if self.logger:
                self.logger.log_action("DB_INSPECT_ERROR", f"Error inspecting {db_path}: {str(e)}")
            return error_result
    
    def _analyze_table(self, cursor, table_name: str) -> Dict[str, Any]:
        """Analyze individual table structure"""
        table_info = {
            'name': table_name,
            'columns': [],
            'row_count': 0,
            'sample_data': [],
            'indexes': [],
            'intelligence_indicators': {}
        }
        
        try:
            # Get column information
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            for col in columns:
                table_info['columns'].append({
                    'cid': col[0],
                    'name': col[1],
                    'type': col[2],
                    'notnull': bool(col[3]),
                    'default': col[4],
                    'pk': bool(col[5])
                })
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            table_info['row_count'] = cursor.fetchone()[0]
            
            # Get sample data (if table has rows)
            if table_info['row_count'] > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                table_info['sample_data'] = cursor.fetchall()
            
            # Get index information
            cursor.execute(f"PRAGMA index_list({table_name})")
            indexes = cursor.fetchall()
            table_info['indexes'] = [
                {'name': idx[1], 'unique': bool(idx[2])} 
                for idx in indexes
            ]
            
            # Analyze intelligence indicators
            table_info['intelligence_indicators'] = self._analyze_intelligence_indicators(
                table_name, table_info['columns'], table_info['sample_data']
            )
            
        except Exception as e:
            table_info['error'] = str(e)
        
        return table_info
    
    def _analyze_intelligence_indicators(self, table_name: str, columns: List[Dict], sample_data: List) -> Dict[str, Any]:
        """Analyze table for intelligence value indicators"""
        indicators = {
            'communication_score': 0,
            'temporal_score': 0,
            'location_score': 0,
            'financial_score': 0,
            'overall_score': 0,
            'suggested_purpose': []
        }
        
        table_lower = table_name.lower()
        col_names = [col['name'].lower() for col in columns]
        
        # Communication indicators
        comm_patterns = ['message', 'sms', 'chat', 'call', 'phone', 'text', 'contact']
        for pattern in comm_patterns:
            if pattern in table_lower:
                indicators['communication_score'] += 20
            if any(pattern in col for col in col_names):
                indicators['communication_score'] += 10
        
        # Temporal indicators
        time_patterns = ['date', 'time', 'timestamp', 'created', 'modified']
        for pattern in time_patterns:
            if any(pattern in col for col in col_names):
                indicators['temporal_score'] += 15
        
        # Location indicators
        location_patterns = ['location', 'gps', 'latitude', 'longitude', 'address', 'coordinate']
        for pattern in location_patterns:
            if pattern in table_lower:
                indicators['location_score'] += 20
            if any(pattern in col for col in col_names):
                indicators['location_score'] += 10
        
        # Financial indicators
        financial_patterns = ['payment', 'transaction', 'account', 'money', 'amount', 'price']
        for pattern in financial_patterns:
            if pattern in table_lower:
                indicators['financial_score'] += 20
            if any(pattern in col for col in col_names):
                indicators['financial_score'] += 10
        
        # Calculate overall score
        indicators['overall_score'] = (
            indicators['communication_score'] + 
            indicators['temporal_score'] + 
            indicators['location_score'] + 
            indicators['financial_score']
        )
        
        # Suggest purpose based on scores
        if indicators['communication_score'] > 20:
            indicators['suggested_purpose'].append('communication_data')
        if indicators['temporal_score'] > 15:
            indicators['suggested_purpose'].append('timeline_analysis')
        if indicators['location_score'] > 15:
            indicators['suggested_purpose'].append('location_intelligence')
        if indicators['financial_score'] > 15:
            indicators['suggested_purpose'].append('financial_analysis')
        
        return indicators
    
    def suggest_timestamp_columns(self, inspection_result: Dict[str, Any]) -> List[str]:
        """Suggest which columns might contain timestamps"""
        timestamp_indicators = ['date', 'time', 'timestamp', 'created', 'modified', 'updated']
        suggestions = []
        
        for table_name, table_info in inspection_result.get('tables', {}).items():
            for col in table_info.get('columns', []):
                col_name = col.get('name', '').lower()
                if any(indicator in col_name for indicator in timestamp_indicators):
                    suggestions.append(f"{table_name}.{col.get('name', '')}")
        
        return suggestions
    
    def suggest_text_columns(self, inspection_result: Dict[str, Any]) -> List[str]:
        """Suggest which columns might contain text content"""
        text_indicators = ['text', 'message', 'content', 'body', 'description', 'note']
        suggestions = []
        
        for table_name, table_info in inspection_result.get('tables', {}).items():
            for col in table_info.get('columns', []):
                col_name = col.get('name', '').lower()
                if any(indicator in col_name for indicator in text_indicators):
                    suggestions.append(f"{table_name}.{col.get('name', '')}")
        
        return suggestions
    
    def generate_smart_configuration(self, inspection_result: Dict[str, Any], 
                                   pattern_analysis: Dict[str, Any], 
                                   db_name: str) -> Dict[str, Any]:
        """Generate intelligent configuration based on inspection"""
        config = {
            'confidence': 'low',
            'table': None,
            'columns': {},
            'timestamp_conversion': 'timestamp',
            'intelligence_value': 'low',
            'suggested_modules': []
        }
        
        if 'error' in inspection_result:
            return config
        
        tables = inspection_result.get('tables', {})
        if not tables:
            return config
        
        # Find the most promising table
        best_table = self._find_best_table(tables)
        if not best_table:
            return config
        
        table_info = tables[best_table]
        config['table'] = best_table
        
        # Map columns intelligently
        column_mapping = self._generate_column_mapping(table_info)
        config['columns'] = column_mapping['columns']
        config['timestamp_conversion'] = column_mapping['timestamp_conversion']
        config['confidence'] = column_mapping['confidence']
        
        # Assess intelligence value
        intelligence_indicators = table_info.get('intelligence_indicators', {})
        overall_score = intelligence_indicators.get('overall_score', 0)
        
        if overall_score > 60:
            config['intelligence_value'] = 'high'
        elif overall_score > 30:
            config['intelligence_value'] = 'medium'
        else:
            config['intelligence_value'] = 'low'
        
        # Suggest analysis modules
        suggested_purposes = intelligence_indicators.get('suggested_purpose', [])
        module_mapping = {
            'communication_data': ['narcotics', 'fraud', 'domestic_violence'],
            'financial_analysis': ['financial_fraud'],
            'location_intelligence': ['location_analysis']
        }
        
        for purpose in suggested_purposes:
            if purpose in module_mapping:
                config['suggested_modules'].extend(module_mapping[purpose])
        
        config['suggested_modules'] = list(set(config['suggested_modules']))
        
        return config
    
    def _find_best_table(self, tables: Dict[str, Any]) -> Optional[str]:
        """Find the table with highest intelligence value"""
        best_table = None
        best_score = 0
        
        for table_name, table_info in tables.items():
            score = 0
            
            # Score based on row count
            row_count = table_info.get('row_count', 0)
            if row_count > 1000:
                score += 30
            elif row_count > 100:
                score += 20
            elif row_count > 10:
                score += 10
            
            # Score based on intelligence indicators
            indicators = table_info.get('intelligence_indicators', {})
            score += indicators.get('overall_score', 0)
            
            if score > best_score:
                best_score = score
                best_table = table_name
        
        return best_table
    
    def _generate_column_mapping(self, table_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate intelligent column mapping for a table"""
        mapping = {
            'columns': {},
            'timestamp_conversion': 'timestamp',
            'confidence': 'low'
        }
        
        columns = table_info.get('columns', [])
        col_dict = {col['name']: col for col in columns}
        
        # Standard mapping patterns
        mapping_patterns = {
            'id': ['rowid', 'id', '_id', 'z_pk'],
            'timestamp': ['date', 'time', 'timestamp', 'created', 'modified'],
            'text': ['text', 'body', 'message', 'content'],
            'contact': ['phone', 'address', 'contact', 'number', 'from', 'to']
        }
        
        mapped_count = 0
        total_patterns = len(mapping_patterns)
        
        for logical_name, possible_names in mapping_patterns.items():
            best_match = None
            best_score = 0
            
            for col_name in col_dict.keys():
                col_lower = col_name.lower()
                score = 0
                
                # Exact match
                if col_lower in possible_names:
                    score = 100
                else:
                    # Partial match
                    for possible in possible_names:
                        if possible in col_lower:
                            score = max(score, 80)
                        elif col_lower in possible:
                            score = max(score, 60)
                
                if score > best_score:
                    best_score = score
                    best_match = col_name
            
            if best_match and best_score > 50:
                mapping['columns'][logical_name] = best_match
                mapped_count += 1
                
                # Set timestamp conversion
                if logical_name == 'timestamp':
                    mapping['timestamp_conversion'] = self._determine_timestamp_conversion(
                        best_match, table_info
                    )
        
        # Calculate confidence
        confidence_ratio = mapped_count / total_patterns
        if confidence_ratio >= 0.8:
            mapping['confidence'] = 'high'
        elif confidence_ratio >= 0.5:
            mapping['confidence'] = 'medium'
        else:
            mapping['confidence'] = 'low'
        
        return mapping
    
    def _determine_timestamp_conversion(self, timestamp_column: str, table_info: Dict[str, Any]) -> str:
        """Determine appropriate timestamp conversion based on sample data"""
        sample_data = table_info.get('sample_data', [])
        
        if not sample_data:
            return f"datetime({timestamp_column}, 'unixepoch')"
        
        # Find the timestamp column index
        columns = table_info.get('columns', [])
        timestamp_index = None
        
        for i, col in enumerate(columns):
            if col['name'] == timestamp_column:
                timestamp_index = i
                break
        
        if timestamp_index is None:
            return f"datetime({timestamp_column}, 'unixepoch')"
        
        # Analyze sample values
        sample_values = []
        for row in sample_data:
            if len(row) > timestamp_index and row[timestamp_index] is not None:
                sample_values.append(str(row[timestamp_index]))
        
        if not sample_values:
            return f"datetime({timestamp_column}, 'unixepoch')"
        
        # Determine format based on sample values
        sample_val = sample_values[0]
        
        try:
            val = float(sample_val)
            
            # Cocoa timestamp (large numbers, iOS style)
            if val > 500000000 and val < 700000000:
                return f"datetime({timestamp_column} + 978307200, 'unixepoch')"
            
            # Unix timestamp in milliseconds
            elif val > 1000000000000:
                return f"datetime({timestamp_column}/1000, 'unixepoch')"
            
            # Regular Unix timestamp
            elif val > 1000000000:
                return f"datetime({timestamp_column}, 'unixepoch')"
            
        except ValueError:
            # Not a number, might be ISO format
            if '-' in sample_val and 'T' in sample_val:
                return timestamp_column  # Already in good format
        
        # Default fallback
        return f"datetime({timestamp_column}, 'unixepoch')"
