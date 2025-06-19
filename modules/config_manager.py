# modules/config_manager.py
"""
Configuration Manager Module
Handles all configuration file management and updates
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
import datetime

class ConfigurationManager:
    """Manages user-configurable settings and data paths"""
    
    def __init__(self, config_dir: str = "forensic_configs"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        # Configuration files
        self.paths_config = self.config_dir / "data_paths.json"
        self.keywords_config = self.config_dir / "keywords.json" 
        self.schemas_config = self.config_dir / "database_schemas.json"
        self.modules_config = self.config_dir / "intelligence_modules.json"
        
        # Load configurations
        self.load_configurations()
    
    def load_configurations(self):
        """Load all configuration files, creating defaults if needed"""
        self.data_paths = self.load_or_create_config(self.paths_config, self.default_data_paths())
        self.keywords = self.load_or_create_config(self.keywords_config, self.default_keywords())
        self.schemas = self.load_or_create_config(self.schemas_config, self.default_schemas())
        self.modules = self.load_or_create_config(self.modules_config, self.default_modules())
        
    def load_or_create_config(self, config_file: Path, default_config: dict) -> dict:
        """Load configuration file or create with defaults"""
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading {config_file}: {e}")
                return default_config
        else:
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            print(f"Created default configuration: {config_file}")
            return default_config
    
    def default_data_paths(self) -> dict:
        """Default data paths for iOS forensic extraction"""
        return {
            "messages": {
                "primary": "var/mobile/Library/SMS/sms.db",
                "backup": "var/mobile/Library/SMS/sms.backup.db",
                "description": "iOS Messages database"
            },
            "call_history": {
                "primary": "var/mobile/Library/CallHistoryDB/CallHistory.storedata",
                "backup": "var/mobile/Library/CallHistory/CallHistory.storedata",
                "description": "iOS Call History database"
            },
            "contacts": {
                "primary": "var/mobile/Library/AddressBook/AddressBook.sqlitedb",
                "backup": "var/mobile/Library/AddressBook/AddressBookImages.sqlitedb",
                "description": "iOS Contacts database"
            },
            "safari": {
                "primary": "var/mobile/Library/Safari/History.db",
                "backup": "var/mobile/Containers/Data/Application/*/Library/Safari/History.db",
                "description": "Safari browsing history"
            },
            "photos": {
                "primary": "var/mobile/Media/PhotoData/Photos.sqlite",
                "backup": "var/mobile/Media/DCIM",
                "description": "Photos and media files"
            }
        }
    
    def default_keywords(self) -> dict:
        """Default keyword libraries for intelligence modules"""
        return {
            "narcotics": {
                "street_names": [
                    "molly", "mdma", "ecstasy", "x", "rolls", "snow", "white", "powder",
                    "ice", "crystal", "meth", "glass", "crank", "blow", "coke", "yayo",
                    "weed", "bud", "green", "herb", "mary jane", "ganja", "chronic"
                ],
                "transaction_terms": [
                    "gram", "ounce", "oz", "pound", "lb", "kilo", "key", "brick",
                    "front", "fronted", "spot", "connect", "plug", "dealer"
                ]
            },
            "financial_fraud": {
                "romance_scam": [
                    "western union", "moneygram", "gift card", "amazon card",
                    "emergency", "stranded", "customs", "lawyer fees"
                ],
                "investment_fraud": [
                    "guaranteed return", "risk free", "double your money",
                    "crypto opportunity", "forex trading"
                ]
            }
        }
    
    def default_schemas(self) -> dict:
        """Default database schemas for data extraction"""
        return {
            "messages": {
                "table": "message",
                "columns": {
                    "id": "ROWID",
                    "timestamp": "date",
                    "text": "text", 
                    "is_from_me": "is_from_me",
                    "service": "service",
                    "handle_id": "handle_id"
                },
                "joins": {
                    "handle": {
                        "table": "handle",
                        "on": "message.handle_id = handle.ROWID",
                        "columns": {
                            "contact": "id"
                        }
                    }
                },
                "timestamp_conversion": "datetime(date/1000000000 + 978307200, 'unixepoch')"
            }
        }
    
    def default_modules(self) -> dict:
        """Default intelligence module configurations"""
        return {
            "narcotics": {
                "enabled": True,
                "risk_weights": {
                    "high_risk_drugs": 4,
                    "multiple_drugs": 2,
                    "quantity_indicators": 3
                }
            },
            "financial_fraud": {
                "enabled": True,
                "risk_weights": {
                    "gift_cards": 4,
                    "wire_transfers": 4,
                    "urgency": 2
                }
            }
        }
    
    def add_custom_keywords(self, module: str, category: str, new_keywords: List[str]):
        """Add custom keywords to a module"""
        if module not in self.keywords:
            self.keywords[module] = {}
        if category not in self.keywords[module]:
            self.keywords[module][category] = []
        
        self.keywords[module][category].extend(new_keywords)
        self.save_config(self.keywords_config, self.keywords)
    
    def update_database_schema(self, db_name: str, new_schema: dict):
        """Update database schema configuration"""
        self.schemas[db_name] = new_schema
        self.save_config(self.schemas_config, self.schemas)
    
    def save_config(self, config_file: Path, config_data: dict):
        """Save configuration to file"""
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def export_configuration(self, export_path: str):
        """Export all configurations for sharing"""
        export_data = {
            "data_paths": self.data_paths,
            "keywords": self.keywords,
            "schemas": self.schemas,
            "modules": self.modules,
            "export_date": datetime.datetime.now().isoformat(),
            "version": "1.0"
        }
        
        with open(export_path, 'w') as f:
            json.dump(export_data, f, indent=2)
    
    def import_configuration(self, import_path: str):
        """Import shared configuration"""
        with open(import_path, 'r') as f:
            import_data = json.load(f)
        
        # Merge configurations
        for key in ["data_paths", "keywords", "schemas", "modules"]:
            if key in import_data:
                current_config = getattr(self, key)
                imported_config = import_data[key]
                current_config.update(imported_config)
                
                config_file = getattr(self, f"{key.replace('_', '')}_config")
                self.save_config(config_file, current_config)
