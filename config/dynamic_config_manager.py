# config/dynamic_config_manager.py
"""
GHOST Dynamic Configuration Manager
Eliminates hardcoding by using flexible configuration files
"""

import json
import yaml
import toml
import configparser
import os
from pathlib import Path
from typing import Dict, Any, Union, List, Optional
from dataclasses import dataclass, asdict
import datetime
import re

@dataclass
class GHOSTConfigManager:
    """
    Enhanced configuration manager for GHOST that eliminates hardcoding
    Supports multiple file formats and environment-specific configs
    """
    config_dir: str = "config"
    default_config_file: str = "ghost_config.json"
    environment: str = "development"
    
    def __post_init__(self):
        self.config_path = Path(self.config_dir)
        self.config_path.mkdir(exist_ok=True)
        self._config_cache = {}
        self._load_all_configs()
    
    def _load_all_configs(self):
        """Load all configuration files"""
        # Core configuration files
        self.paths_config = self.load_config("paths.json", self._default_paths_config())
        self.database_config = self.load_config("databases.json", self._default_database_config())
        self.analysis_config = self.load_config("analysis.json", self._default_analysis_config())
        self.keywords_config = self.load_config("keywords.json", self._default_keywords_config())
        self.modules_config = self.load_config("modules.json", self._default_modules_config())
        self.export_config = self.load_config("export.json", self._default_export_config())
        
    def load_config(self, config_file: str, default_config: Dict = None) -> Dict[str, Any]:
        """
        Load configuration from file with fallback to defaults
        Supports JSON, YAML, TOML, INI, and custom .ghost files
        """
        config_path = self.config_path / config_file
        
        # Check cache first
        cache_key = str(config_path)
        if cache_key in self._config_cache:
            return self._config_cache[cache_key]
        
        # Create default if doesn't exist
        if not config_path.exists() and default_config:
            self._save_config(default_config, config_path)
        
        if not config_path.exists():
            return {}
        
        # Load based on file extension
        config_data = self._load_by_extension(config_path)
        
        # Apply environment overrides
        config_data = self._apply_environment_overrides(config_data, config_file)
        
        # Process environment variables and expressions
        config_data = self._process_dynamic_values(config_data)
        
        # Cache and return
        self._config_cache[cache_key] = config_data
        return config_data
    
    def _load_by_extension(self, config_path: Path) -> Dict[str, Any]:
        """Load config based on file extension"""
        extension = config_path.suffix.lower()
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                if extension == '.json':
                    return json.loads(content)
                elif extension in ['.yaml', '.yml']:
                    return yaml.safe_load(content) or {}
                elif extension == '.toml':
                    return toml.loads(content)
                elif extension == '.ini':
                    parser = configparser.ConfigParser()
                    parser.read_string(content)
                    return {section: dict(parser[section]) for section in parser.sections()}
                elif extension == '.ghost':
                    return self._load_ghost_format(content)
                else:
                    # Try JSON as fallback
                    return json.loads(content)
        except Exception as e:
            print(f"Error loading {config_path}: {e}")
            return {}
    
    def _load_ghost_format(self, content: str) -> Dict[str, Any]:
        """
        Load custom .ghost format
        Supports JSON with comments and environment variable substitution
        """
        # Remove comments (lines starting with # or //)
        lines = []
        for line in content.split('\n'):
            stripped = line.strip()
            if not stripped.startswith('#') and not stripped.startswith('//'):
                lines.append(line)
        
        clean_content = '\n'.join(lines)
        
        # Replace environment variables ${VAR:default}
        clean_content = self._substitute_env_vars(clean_content)
        
        return json.loads(clean_content)
    
    def _substitute_env_vars(self, content: str) -> str:
        """Substitute environment variables in config content"""
        env_pattern = r'\$\{([^}]+)\}'
        
        def replace_env_var(match):
            env_expr = match.group(1)
            
            # Handle default values: ${VAR:default}
            if ':' in env_expr:
                var_name, default_value = env_expr.split(':', 1)
            else:
                var_name, default_value = env_expr, ''
            
            return os.getenv(var_name.strip(), default_value.strip())
        
        return re.sub(env_pattern, replace_env_var, content)
    
    def _apply_environment_overrides(self, config: Dict[str, Any], config_file: str) -> Dict[str, Any]:
        """Apply environment-specific configuration overrides"""
        if self.environment == "development":
            return config
        
        # Look for environment-specific config file
        base_name = Path(config_file).stem
        extension = Path(config_file).suffix
        env_config_file = f"{base_name}.{self.environment}{extension}"
        env_config_path = self.config_path / env_config_file
        
        if env_config_path.exists():
            env_config = self._load_by_extension(env_config_path)
            config = self._deep_merge(config, env_config)
        
        return config
    
    def _process_dynamic_values(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Process dynamic values like expressions and references"""
        def process_value(value):
            if isinstance(value, str):
                # Handle references to other config values: @{paths.base_dir}
                if value.startswith('@{') and value.endswith('}'):
                    ref_path = value[2:-1]
                    return self.get_nested_value(config, ref_path, value)
                
                # Handle date expressions: #{today}, #{now}
                if value.startswith('#{') and value.endswith('}'):
                    expr = value[2:-1]
                    if expr == 'today':
                        return datetime.date.today().isoformat()
                    elif expr == 'now':
                        return datetime.datetime.now().isoformat()
                    elif expr == 'timestamp':
                        return str(int(datetime.datetime.now().timestamp()))
                
                return value
            elif isinstance(value, dict):
                return {k: process_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [process_value(item) for item in value]
            else:
                return value
        
        return process_value(config)
    
    def get_nested_value(self, data: Dict, path: str, default=None):
        """Get nested value using dot notation"""
        keys = path.split('.')
        current = data
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _save_config(self, config_data: Dict[str, Any], config_path: Path):
        """Save configuration to file"""
        extension = config_path.suffix.lower()
        
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            if extension == '.json':
                json.dump(config_data, f, indent=2, default=str)
            elif extension in ['.yaml', '.yml']:
                yaml.dump(config_data, f, default_flow_style=False)
            elif extension == '.toml':
                toml.dump(config_data, f)
            elif extension == '.ghost':
                f.write(f"# GHOST Configuration File\n")
                f.write(f"# Generated: {datetime.datetime.now().isoformat()}\n\n")
                json.dump(config_data, f, indent=2, default=str)
    
    # Default configuration generators
    
    def _default_paths_config(self) -> Dict[str, Any]:
        """Default paths configuration"""
        return {
            "base": {
                "app_root": "${APP_ROOT:.}",
                "data_dir": "${DATA_DIR:./data}",
                "logs_dir": "${LOGS_DIR:./logs}",
                "temp_dir": "${TEMP_DIR:./temp}",
                "output_dir": "${OUTPUT_DIR:./output}",
                "config_dir": "${CONFIG_DIR:./config}",
                "cache_dir": "${CACHE_DIR:./cache}"
            },
            "ios": {
                "messages": [
                    "var/mobile/Library/SMS/sms.db",
                    "var/mobile/Library/SMS/sms.backup.db",
                    "Library/SMS/sms.db"
                ],
                "call_history": [
                    "var/mobile/Library/CallHistoryDB/CallHistory.storedata",
                    "var/mobile/Library/CallHistory/CallHistory.storedata",
                    "Library/CallHistory.storedata"
                ],
                "contacts": [
                    "var/mobile/Library/AddressBook/AddressBook.sqlitedb",
                    "var/mobile/Library/AddressBook/AddressBookImages.sqlitedb",
                    "Library/AddressBook/AddressBook.sqlitedb"
                ],
                "safari": [
                    "var/mobile/Library/Safari/History.db",
                    "Library/Safari/History.db"
                ],
                "photos": [
                    "var/mobile/Media/PhotoData/Photos.sqlite",
                    "var/mobile/Media/DCIM/**/*.jpg",
                    "var/mobile/Media/DCIM/**/*.png",
                    "var/mobile/Media/DCIM/**/*.heic"
                ],
                "locations": [
                    "var/mobile/Library/Caches/locationd/cache_encryptedA.db",
                    "var/mobile/Library/Caches/com.apple.routined/Cache.sqlite"
                ],
                "keychain": [
                    "var/Keychains/keychain-2.db",
                    "var/mobile/Library/Keychains/keychain-2.db"
                ]
            },
            "android": {
                "messages": [
                    "data/data/com.android.providers.telephony/databases/mmssms.db",
                    "data/data/com.android.providers.telephony/databases/telephony.db"
                ],
                "call_history": [
                    "data/data/com.android.providers.contacts/databases/calllog.db",
                    "data/data/com.android.providers.contacts/databases/contacts2.db"
                ],
                "contacts": [
                    "data/data/com.android.providers.contacts/databases/contacts2.db"
                ],
                "browser": [
                    "data/data/com.android.browser/databases/browser.db",
                    "data/data/com.google.android.browser/databases/browser.db"
                ],
                "whatsapp": [
                    "data/data/com.whatsapp/databases/msgstore.db",
                    "data/data/com.whatsapp/databases/wa.db"
                ]
            },
            "common_apps": {
                "whatsapp": [
                    "var/mobile/Containers/Shared/AppGroup/*/ChatStorage.sqlite",
                    "data/data/com.whatsapp/databases/msgstore.db"
                ],
                "telegram": [
                    "var/mobile/Containers/Data/Application/*/Documents/cache.db",
                    "data/data/org.telegram.messenger/databases/cache4.db"
                ],
                "signal": [
                    "var/mobile/Containers/Data/Application/*/Documents/database.sqlite",
                    "data/data/org.thoughtcrime.securesms/databases/signal.db"
                ],
                "snapchat": [
                    "var/mobile/Containers/Data/Application/*/Documents/tc.db"
                ]
            }
        }
    
    def _default_database_config(self) -> Dict[str, Any]:
        """Default database configuration"""
        return {
            "schemas": {
                "ios_messages": {
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
                            "columns": {"contact": "id"}
                        }
                    },
                    "timestamp_conversion": "datetime(date/1000000000 + 978307200, 'unixepoch')",
                    "filters": {
                        "recent_days": 90,
                        "max_records": 10000
                    }
                },
                "android_sms": {
                    "table": "sms",
                    "columns": {
                        "id": "_id",
                        "timestamp": "date",
                        "text": "body",
                        "is_from_me": "type",
                        "contact": "address"
                    },
                    "timestamp_conversion": "datetime(date/1000, 'unixepoch')"
                },
                "call_history": {
                    "table": "call",
                    "columns": {
                        "id": "ROWID",
                        "timestamp": "date",
                        "duration": "duration",
                        "contact": "address",
                        "answered": "answered"
                    },
                    "timestamp_conversion": "datetime(date + 978307200, 'unixepoch')"
                }
            },
            "encryption": {
                "detection_enabled": True,
                "common_passwords": [
                    "", "password", "admin", "123456", "default", "user", "root"
                ],
                "entropy_threshold": 7.5,
                "bypass_methods": [
                    "common_passwords", "app_specific", "keychain_extraction"
                ]
            }
        }
    
    def _default_analysis_config(self) -> Dict[str, Any]:
        """Default analysis configuration"""
        return {
            "processing": {
                "max_workers": "${MAX_WORKERS:8}",
                "chunk_size": 1000,
                "memory_limit_mb": 512,
                "timeout_seconds": 300,
                "parallel_processing": True
            },
            "intelligence": {
                "enabled_modules": [
                    "narcotics", "financial_fraud", "domestic_violence", 
                    "human_trafficking", "extremism"
                ],
                "risk_thresholds": {
                    "critical": 8,
                    "high": 6,
                    "medium": 4,
                    "low": 1
                },
                "keyword_matching": {
                    "case_sensitive": False,
                    "partial_match": True,
                    "fuzzy_matching": False
                }
            },
            "timeline": {
                "default_days": 90,
                "group_by_day": True,
                "include_deleted": True,
                "correlation_window_hours": 24
            }
        }
    
    def _default_keywords_config(self) -> Dict[str, Any]:
        """Default keywords configuration"""
        return {
            "narcotics": {
                "drugs": {
                    "street_names": [
                        "molly", "mdma", "ecstasy", "x", "rolls", "snow", "white", "powder",
                        "ice", "crystal", "meth", "glass", "crank", "blow", "coke", "yayo",
                        "weed", "bud", "green", "herb", "mary jane", "ganja", "chronic",
                        "pills", "tabs", "bars", "percs", "oxys", "addies"
                    ],
                    "hard_drugs": [
                        "heroin", "fentanyl", "fent", "china white", "black tar",
                        "cocaine", "crack", "rock", "methamphetamine", "meth"
                    ]
                },
                "transactions": [
                    "gram", "ounce", "oz", "pound", "lb", "kilo", "key", "brick",
                    "front", "fronted", "spot", "connect", "plug", "dealer", "trap",
                    "move", "flip", "push", "serve", "bag", "sack"
                ],
                "locations": [
                    "corner", "block", "trap house", "spot", "stash", "drop",
                    "meet", "pickup", "delivery"
                ]
            },
            "financial_fraud": {
                "payment_methods": [
                    "gift card", "amazon card", "itunes card", "google play",
                    "western union", "moneygram", "bitcoin", "crypto", "wire transfer",
                    "paypal", "cashapp", "venmo", "zelle"
                ],
                "scam_indicators": [
                    "emergency", "urgent", "stranded", "customs", "lawyer fees",
                    "guaranteed return", "risk free", "investment opportunity",
                    "prince", "inheritance", "lottery", "winner"
                ],
                "personal_info": [
                    "ssn", "social security", "pin", "password", "account number",
                    "routing number", "credit card", "debit card"
                ]
            },
            "domestic_violence": {
                "threats": [
                    "hurt you", "kill you", "beat you", "destroy you", "end you",
                    "make you pay", "regret this", "sorry you'll be"
                ],
                "control": [
                    "belong to me", "property", "own you", "control you",
                    "can't leave", "never let you", "always watching"
                ],
                "isolation": [
                    "no one cares", "no one will help", "nowhere to go",
                    "no friends", "family doesn't want you"
                ]
            },
            "human_trafficking": {
                "control_language": [
                    "owe me", "debt", "work off", "until paid", "belong to me",
                    "property", "investment", "bought you"
                ],
                "movement": [
                    "new city", "travel", "move you", "relocate", "different state",
                    "across country", "border", "passport"
                ],
                "exploitation": [
                    "work for me", "clients", "johns", "dates", "appointments",
                    "quota", "earnings", "money you made"
                ]
            }
        }
    
    def _default_modules_config(self) -> Dict[str, Any]:
        """Default modules configuration"""
        return {
            "narcotics": {
                "enabled": True,
                "priority": "high",
                "risk_weights": {
                    "hard_drugs": 5,
                    "distribution_indicators": 4,
                    "quantity_mentions": 3,
                    "money_amounts": 2
                },
                "patterns": [
                    r'\b\d+\s*(gram|g|oz|ounce|lb|pound)\b',
                    r'\$\d+\s*(each|per|for)',
                    r'\b(front|fronted|credit)\b'
                ]
            },
            "financial_fraud": {
                "enabled": True,
                "priority": "high",
                "risk_weights": {
                    "gift_cards": 4,
                    "wire_transfers": 4,
                    "personal_info_requests": 3,
                    "urgency_indicators": 2
                }
            },
            "domestic_violence": {
                "enabled": True,
                "priority": "critical",
                "risk_weights": {
                    "direct_threats": 5,
                    "control_language": 4,
                    "isolation_tactics": 3
                }
            },
            "human_trafficking": {
                "enabled": True,
                "priority": "critical",
                "risk_weights": {
                    "control_language": 5,
                    "movement_indicators": 4,
                    "exploitation_terms": 4
                }
            }
        }
    
    def _default_export_config(self) -> Dict[str, Any]:
        """Default export configuration"""
        return {
            "formats": {
                "json": {
                    "enabled": True,
                    "pretty_print": True,
                    "include_metadata": True
                },
                "csv": {
                    "enabled": True,
                    "delimiter": ",",
                    "encoding": "utf-8",
                    "include_headers": True
                },
                "xlsx": {
                    "enabled": True,
                    "multiple_sheets": True,
                    "freeze_header": True
                },
                "html": {
                    "enabled": True,
                    "template": "default",
                    "include_charts": True
                }
            },
            "output": {
                "directory": "@{base.output_dir}",
                "filename_pattern": "ghost_export_{case_name}_{timestamp}",
                "compression": {
                    "enabled": True,
                    "format": "zip",
                    "level": 6
                }
            },
            "privacy": {
                "redact_pii": False,
                "hash_identifiers": False,
                "encrypt_exports": False
            }
        }
    
    # Convenience methods for accessing configurations
    
    def get_paths(self, platform: str = None, data_type: str = None) -> Union[Dict, List, str]:
        """Get path configurations"""
        if not platform and not data_type:
            return self.paths_config
        
        if platform and data_type:
            return self.paths_config.get(platform, {}).get(data_type, [])
        elif platform:
            return self.paths_config.get(platform, {})
        else:
            return self.paths_config
    
    def get_database_schema(self, schema_name: str) -> Dict[str, Any]:
        """Get database schema configuration"""
        return self.database_config.get("schemas", {}).get(schema_name, {})
    
    def get_keywords(self, module: str = None, category: str = None) -> Union[Dict, List]:
        """Get keyword configurations"""
        if not module and not category:
            return self.keywords_config
        
        if module and category:
            return self.keywords_config.get(module, {}).get(category, [])
        elif module:
            return self.keywords_config.get(module, {})
        else:
            return self.keywords_config
    
    def get_module_config(self, module_name: str) -> Dict[str, Any]:
        """Get module configuration"""
        return self.modules_config.get(module_name, {})
    
    def get_analysis_config(self, section: str = None) -> Union[Dict, Any]:
        """Get analysis configuration"""
        if section:
            return self.analysis_config.get(section, {})
        return self.analysis_config
    
    def get_export_config(self, format_type: str = None) -> Union[Dict, Any]:
        """Get export configuration"""
        if format_type:
            return self.export_config.get("formats", {}).get(format_type, {})
        return self.export_config
    
    # Dynamic configuration updates
    
    def add_path(self, platform: str, data_type: str, path: str):
        """Add a new path to configuration"""
        if platform not in self.paths_config:
            self.paths_config[platform] = {}
        
        if data_type not in self.paths_config[platform]:
            self.paths_config[platform][data_type] = []
        
        if isinstance(self.paths_config[platform][data_type], list):
            if path not in self.paths_config[platform][data_type]:
                self.paths_config[platform][data_type].append(path)
        else:
            self.paths_config[platform][data_type] = [self.paths_config[platform][data_type], path]
        
        self._save_config(self.paths_config, self.config_path / "paths.json")
    
    def add_keywords(self, module: str, category: str, keywords: List[str]):
        """Add keywords to configuration"""
        if module not in self.keywords_config:
            self.keywords_config[module] = {}
        
        if category not in self.keywords_config[module]:
            self.keywords_config[module][category] = []
        
        for keyword in keywords:
            if keyword not in self.keywords_config[module][category]:
                self.keywords_config[module][category].append(keyword)
        
        self._save_config(self.keywords_config, self.config_path / "keywords.json")
    
    def update_module_config(self, module_name: str, config_updates: Dict[str, Any]):
        """Update module configuration"""
        if module_name not in self.modules_config:
            self.modules_config[module_name] = {}
        
        self.modules_config[module_name] = self._deep_merge(
            self.modules_config[module_name], config_updates
        )
        
        self._save_config(self.modules_config, self.config_path / "modules.json")
    
    def clear_cache(self):
        """Clear configuration cache"""
        self._config_cache.clear()
        self._load_all_configs()
    
    def validate_configuration(self) -> Dict[str, List[str]]:
        """Validate all configurations and return issues"""
        issues = {
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        # Validate paths exist
        base_paths = self.get_paths("base")
        for path_name, path_value in base_paths.items():
            if not Path(path_value).parent.exists():
                issues["warnings"].append(f"Base path parent doesn't exist: {path_name} -> {path_value}")
        
        # Validate required modules
        required_modules = ["narcotics", "financial_fraud", "domestic_violence"]
        for module in required_modules:
            if not self.get_module_config(module).get("enabled", False):
                issues["suggestions"].append(f"Consider enabling {module} module for comprehensive analysis")
        
        return issues
    
    def export_configuration(self, output_path: str = None) -> str:
        """Export all configurations to a single file"""
        if not output_path:
            output_path = f"ghost_config_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            "export_metadata": {
                "timestamp": datetime.datetime.now().isoformat(),
                "environment": self.environment,
                "version": "1.0"
            },
            "paths": self.paths_config,
            "databases": self.database_config,
            "analysis": self.analysis_config,
            "keywords": self.keywords_config,
            "modules": self.modules_config,
            "export": self.export_config
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        return output_path


# Usage example
if __name__ == "__main__":
    # Initialize configuration manager
    config = GHOSTConfigManager(
        config_dir="config",
        environment=os.getenv("GHOST_ENV", "development")
    )
    
    # Get iOS message paths
    ios_message_paths = config.get_paths("ios", "messages")
    print("iOS Message Paths:", ios_message_paths)
    
    # Get narcotics keywords
    drug_keywords = config.get_keywords("narcotics", "drugs")
    print("Drug Keywords:", drug_keywords)
    
    # Get database schema
    ios_schema = config.get_database_schema("ios_messages")
    print("iOS Messages Schema:", ios_schema)
    
    # Add custom path
    config.add_path("ios", "custom_app", "var/mobile/Containers/Data/Application/*/Documents/app.db")
    
    # Export configuration
    export_file = config.export_configuration()
    print(f"Configuration exported to: {export_file}")
