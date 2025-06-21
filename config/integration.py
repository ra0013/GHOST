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
            "msgstore.db": "whatsapp_messages"
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
            tables = [row[0] for
