# config/integration.py
"""
GHOST Configuration Integration
Shows how to replace hardcoded values with dynamic configuration
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from config.dynamic_config_manager import GHOSTConfigManager

class GHOSTIntegration:
    """
    Integration layer that replaces hardcoded values throughout GHOST
    """
    
    def __init__(self, environment: str = None):
        self.environment = environment or os.getenv("GHOST_ENV", "development")
        self.config = GHOSTConfigManager(environment=self.environment)
    def export_case_info(self, case_config: Dict[str, Any], output_path: Path) -> None:
        with open(output_path, 'w') as f:
            json.dump(case_config, f, indent=2)
            
    def get_forensic_suite_config(self) -> Dict[str, Any]:
        """Configuration for the main forensic suite"""
        return {
            "processing": self.config.get_analysis_config("processing"),
            "output_dir": self.config.get_paths("base")["output_dir"],
            "temp_dir": self.config.get_paths("base")["temp_dir"],
            "max_workers": self.config.get_analysis_config("processing").get("max_workers", 8),
            "timeout": self.config.get_analysis_config("processing").get("timeout_seconds", 300)
        }
    
    def get_database_paths(self, platform: str = "auto") -> Dict[str, List[str]]:
        """
        Get database paths for extraction analysis
        Replaces hardcoded paths in forensic_suite.py
        """
        if platform == "auto":
            # Return both iOS and Android paths
            paths = {}
            paths.update(self.config.get_paths("ios"))
            paths.update(self.config.get_paths("android"))
            return paths
        else:
            return self.config.get_paths(platform)
    
    def find_database_files(self, extraction_path: Path, data_type: str) -> List[Path]:
        """
        Find database files using configured paths
        Replaces hardcoded file discovery logic
        """
        found_files = []
        
        # Get paths for all platforms
        all_paths = []
        for platform in ["ios", "android", "common_apps"]:
            platform_paths = self.config.get_paths(platform, data_type)
            if platform_paths:
                all_paths.extend(platform_paths)
        
        # Search for files
        for path_pattern in all_paths:
            if "*" in path_pattern:
                # Handle wildcard patterns
                found_files.extend(extraction_path.glob(path_pattern))
            else:
                # Handle exact paths
                full_path = extraction_path / path_pattern
                if full_path.exists():
                    found_files.append(full_path)
        
        return found_files
    
    def get_database_schema(self, db_file: Path) -> Optional[Dict[str, Any]]:
        """
        Get database schema based on file characteristics
        Replaces hardcoded schema selection
        """
        file_name = db_file.name.lower()
        
        # Schema mapping based on filename patterns
        schema_mapping = {
            "sms.db": "ios_messages",
            "mmssms.db": "android_sms", 
            "callhistory.storedata": "ios_call_history",
            "calllog.db": "android_call_log",
            "msgstore.db": "whatsapp_messages",
            "wa.db": "whatsapp_messages",
            "cache.db": "telegram_messages",
            "contacts.db": "android_contacts",
            "addressbook.sqlitedb": "ios_contacts",
            "history.db": "safari_history",
            "browser.db": "android_browser"
        }
        
        for pattern, schema_name in schema_mapping.items():
            if pattern in file_name:
                return self.config.get_database_schema(schema_name)
        
        # Try to auto-detect schema
        return self._auto_detect_schema(db_file)
    
    def _auto_detect_schema(self, db_file: Path) -> Optional[Dict[str, Any]]:
        """Auto-detect database schema"""
        import sqlite3
        
        try:
            conn = sqlite3.connect(str(db_file))
            cursor = conn.cursor()
            
            # Get table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            
            # Analyze table names to determine schema type
            schema_indicators = {
                "ios_messages": ["message", "handle", "chat"],
                "android_sms": ["sms", "mms", "threads"],
                "call_history": ["call", "calls"],
                "contacts": ["contact", "person", "people"],
                "browser": ["history", "urls", "visits"],
                "location": ["location", "coordinates", "cache"]
            }
            
            for schema_type, indicators in schema_indicators.items():
                if any(indicator in [t.lower() for t in tables] for indicator in indicators):
                    base_schema = self.config.get_database_schema(schema_type)
                    if base_schema:
                        return base_schema
            
            # Return generic schema for unknown databases
            return self._create_generic_schema(tables)
            
        except Exception as e:
            print(f"Error auto-detecting schema for {db_file}: {e}")
            return None
    
    def _create_generic_schema(self, tables: List[str]) -> Dict[str, Any]:
        """Create a generic schema for unknown databases"""
        # Find the largest table (likely the main data table)
        main_table = tables[0] if tables else "unknown"
        
        return {
            "table": main_table,
            "columns": {
                "id": "rowid",
                "timestamp": "timestamp",
                "text": "text",
                "data": "data"
            },
            "timestamp_conversion": "datetime(timestamp, 'unixepoch')",
            "auto_generated": True
        }
    
    def get_intelligence_keywords(self, module_name: str = None) -> Dict[str, Any]:
        """
        Get keywords for intelligence modules
        Replaces hardcoded keyword lists
        """
        return self.config.get_keywords(module_name)
    
    def get_analysis_modules_config(self) -> Dict[str, Any]:
        """
        Get analysis modules configuration
        Replaces hardcoded module settings
        """
        modules_config = {}
        
        # Get all enabled modules
        all_modules = self.config.modules_config
        for module_name, module_config in all_modules.items():
            if module_config.get('enabled', True):
                modules_config[module_name] = {
                    'enabled': True,
                    'priority': module_config.get('priority', 'medium'),
                    'risk_weights': module_config.get('risk_weights', {}),
                    'keywords': self.config.get_keywords(module_name)
                }
        
        return modules_config
    
    def get_extraction_patterns(self, platform: str) -> Dict[str, List[str]]:
        """
        Get file patterns for evidence extraction
        """
        patterns = {}
        
        platform_paths = self.config.get_paths(platform)
        for data_type, paths in platform_paths.items():
            if isinstance(paths, list):
                patterns[data_type] = paths
            else:
                patterns[data_type] = [paths]
        
        return patterns
    
    def get_encryption_config(self) -> Dict[str, Any]:
        """Get encryption detection and bypass configuration"""
        return self.config.database_config.get("encryption", {})
    
    def get_processing_config(self) -> Dict[str, Any]:
        """Get processing configuration for performance tuning"""
        return self.config.get_analysis_config("processing")
    
    def get_export_config(self) -> Dict[str, Any]:
        """Get export configuration for reports"""
        return self.config.get_export_config()
    
    def get_timeline_config(self) -> Dict[str, Any]:
        """Get timeline analysis configuration"""
        return self.config.get_analysis_config("timeline")
    
    def adapt_schema_to_database(self, db_file: Path, base_schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt schema configuration to actual database structure
        """
        import sqlite3
        
        try:
            conn = sqlite3.connect(str(db_file))
            cursor = conn.cursor()
            
            # Get actual table structure
            table_name = base_schema.get("table")
            if not table_name:
                conn.close()
                return base_schema
            
            # Check if table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            if not cursor.fetchone():
                # Try to find similar table
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                # Find best match
                table_name = self._find_best_table_match(table_name, tables)
                if table_name:
                    base_schema = base_schema.copy()
                    base_schema["table"] = table_name
                else:
                    conn.close()
                    return base_schema
            
            # Get column information
            cursor.execute(f"PRAGMA table_info({table_name})")
            actual_columns = [col[1] for col in cursor.fetchall()]
            
            # Adapt column mappings
            adapted_schema = base_schema.copy()
            adapted_columns = {}
            
            for logical_name, column_name in base_schema.get("columns", {}).items():
                if column_name in actual_columns:
                    adapted_columns[logical_name] = column_name
                else:
                    # Try to find similar column
                    similar_column = self._find_similar_column(column_name, actual_columns)
                    if similar_column:
                        adapted_columns[logical_name] = similar_column
            
            adapted_schema["columns"] = adapted_columns
            
            # Adapt joins if necessary
            if "joins" in base_schema:
                adapted_joins = {}
                for join_name, join_config in base_schema["joins"].items():
                    join_table = join_config.get("table")
                    if join_table:
                        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (join_table,))
                        if cursor.fetchone():
                            adapted_joins[join_name] = join_config
                
                if adapted_joins:
                    adapted_schema["joins"] = adapted_joins
                else:
                    adapted_schema.pop("joins", None)
            
            conn.close()
            return adapted_schema
            
        except Exception as e:
            print(f"Error adapting schema for {db_file}: {e}")
            return base_schema
    
    def _find_best_table_match(self, target_table: str, available_tables: List[str]) -> Optional[str]:
        """Find the best matching table name"""
        target_lower = target_table.lower()
        
        # Exact match
        for table in available_tables:
            if table.lower() == target_lower:
                return table
        
        # Partial match
        for table in available_tables:
            if target_lower in table.lower() or table.lower() in target_lower:
                return table
        
        # If no match, return the first table (fallback)
        return available_tables[0] if available_tables else None
    
    def _find_similar_column(self, target_column: str, available_columns: List[str]) -> Optional[str]:
        """Find similar column name"""
        target_lower = target_column.lower()
        
        # Exact match
        for column in available_columns:
            if column.lower() == target_lower:
                return column
        
        # Common variations
        variations = {
            'id': ['rowid', '_id', 'z_pk'],
            'timestamp': ['date', 'time', 'created', 'modified'],
            'text': ['body', 'message', 'content'],
            'contact': ['address', 'phone', 'number', 'from', 'to']
        }
        
        if target_lower in variations:
            for variation in variations[target_lower]:
                for column in available_columns:
                    if variation in column.lower():
                        return column
        
        # Reverse lookup
        for key, var_list in variations.items():
            if target_lower in var_list:
                for column in available_columns:
                    if key in column.lower():
                        return column
        
        # Partial match
        for column in available_columns:
            if target_lower in column.lower() or column.lower() in target_lower:
                return column
        
        return None
    
    def get_app_specific_config(self, app_name: str) -> Dict[str, Any]:
        """Get configuration for specific apps"""
        app_paths = self.config.get_paths("common_apps", app_name.lower())
        
        # App-specific database schemas
        app_schemas = {
            "whatsapp": "whatsapp_messages",
            "telegram": "telegram_messages",
            "signal": "signal_messages",
            "instagram": "instagram_messages",
            "facebook": "facebook_messages"
        }
        
        schema_name = app_schemas.get(app_name.lower())
        schema = self.config.get_database_schema(schema_name) if schema_name else None
        
        return {
            "paths": app_paths or [],
            "schema": schema,
            "priority": "high" if app_name.lower() in ["whatsapp", "telegram", "signal"] else "medium"
        }
    
    def validate_configuration(self) -> Dict[str, List[str]]:
        """Validate configuration integrity"""
        return self.config.validate_configuration()
    
    def create_case_specific_config(self, case_name: str, extraction_path: Path) -> Dict[str, Any]:
        """Create case-specific configuration"""
        case_config = {
            "case_name": case_name,
            "extraction_path": str(extraction_path),
            "processing": self.get_processing_config(),
            "analysis": self.get_analysis_modules_config(),
            "export": self.get_export_config(),
            "timestamp": self.config.get_analysis_config().get("timestamp_format", "%Y-%m-%d %H:%M:%S")
        }
        
        # Detect platform based on extraction content
        platform = self._detect_platform(extraction_path)
        if platform:
            case_config["platform"] = platform
            case_config["paths"] = self.get_extraction_patterns(platform)
        
        return case_config
    
    def _detect_platform(self, extraction_path: Path) -> Optional[str]:
        """Detect platform (iOS/Android) from extraction"""
        if not extraction_path.exists():
            return None
        
        # iOS indicators
        ios_indicators = [
            "var/mobile/Library",
            "Applications",
            "System/Library",
            "Library/SMS/sms.db"
        ]
        
        # Android indicators
        android_indicators = [
            "data/data",
            "system/app",
            "data/system",
            "databases/telephony.db"
        ]
        
        try:
            # Check for iOS indicators
            for indicator in ios_indicators:
                if list(extraction_path.glob(f"**/{indicator}")):
                    return "ios"
            
            # Check for Android indicators
            for indicator in android_indicators:
                if list(extraction_path.glob(f"**/{indicator}")):
                    return "android"
                    
        except Exception:
            pass
        
        return None
    
    def get_forensic_logger_config(self) -> Dict[str, Any]:
        """Get forensic logging configuration"""
        return {
            "log_level": "INFO",
            "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "log_file": True,
            "chain_of_custody": True,
            "integrity_hashing": True
        }
    
    def create_module_factory_config(self) -> Dict[str, Any]:
        """Create configuration for intelligence module factory"""
        return {
            "keywords_config": self.config.keywords_config,
            "modules_config": self.config.modules_config,
            "enabled_modules": [
                name for name, config in self.config.modules_config.items()
                if config.get("enabled", True)
            ]
        }


# Convenience functions for easy integration

def get_ghost_integration(environment: str = None) -> GHOSTIntegration:
    """Get GHOST integration instance"""
    return GHOSTIntegration(environment)

def replace_hardcoded_paths(extraction_path: Path, data_type: str) -> List[Path]:
    """Replace hardcoded path discovery with configuration-based approach"""
    integration = get_ghost_integration()
    return integration.find_database_files(extraction_path, data_type)

def get_dynamic_schema(db_file: Path) -> Optional[Dict[str, Any]]:
    """Get database schema using dynamic configuration"""
    integration = get_ghost_integration()
    return integration.get_database_schema(db_file)

def get_intelligence_config(module_name: str = None) -> Dict[str, Any]:
    """Get intelligence analysis configuration"""
    integration = get_ghost_integration()
    return {
        "keywords": integration.get_intelligence_keywords(module_name),
        "modules": integration.get_analysis_modules_config()
    }

def create_adaptive_processor_config(extraction_path: Path) -> Dict[str, Any]:
    """Create configuration for adaptive processing"""
    integration = get_ghost_integration()
    
    # Analyze extraction to determine optimal processing strategy
    case_config = integration.create_case_specific_config("auto_analysis", extraction_path)
    
    # Get performance configuration
    processing_config = integration.get_processing_config()
    
    # Combine for adaptive processing
    return {
        "case_config": case_config,
        "processing": processing_config,
        "encryption": integration.get_encryption_config(),
        "export": integration.get_export_config()
    }


# Example usage and integration patterns

if __name__ == "__main__":
    # Example: Initialize GHOST integration
    integration = GHOSTIntegration(environment="production")
    
    # Example: Get configuration for forensic suite
    suite_config = integration.get_forensic_suite_config()
    print("Forensic Suite Config:", suite_config)
    
    # Example: Find database files dynamically
    extraction_path = Path("/path/to/extraction")
    if extraction_path.exists():
        message_dbs = integration.find_database_files(extraction_path, "messages")
        print(f"Found message databases: {message_dbs}")
    
    # Example: Get schema for specific database
    for db_file in ["sms.db", "mmssms.db", "msgstore.db"]:
        schema = integration.get_database_schema(Path(db_file))
        if schema:
            print(f"Schema for {db_file}: {schema['table']}")
    
    # Example: Get intelligence keywords
    narcotics_keywords = integration.get_intelligence_keywords("narcotics")
    print(f"Narcotics keywords: {len(narcotics_keywords.get('drugs', {}).get('street_names', []))} terms")
    
    # Example: Validate configuration
    validation_results = integration.validate_configuration()
    if validation_results.get("errors"):
        print("Configuration errors:", validation_results["errors"])
    else:
        print("Configuration validation passed")
