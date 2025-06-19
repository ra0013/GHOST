#!/usr/bin/env python3
"""
Setup Script for GHOST Forensic Intelligence Suite
Creates directory structure and initializes configurations
"""

import os
import json
from pathlib import Path

def create_directory_structure():
    """Create the required directory structure"""
    print("📁 Creating directory structure...")
    
    directories = [
        "modules",
        "forensic_configs", 
        "forensic_configs/auto_generated",
        "logs",
        "reports"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"   ✅ Created: {directory}")

def create_module_init():
    """Create __init__.py for modules directory"""
    modules_init = Path("modules") / "__init__.py"
    if not modules_init.exists():
        modules_init.write_text("# Forensic Intelligence Modules\n")
        print("   ✅ Created: modules/__init__.py")

def create_sample_config():
    """Create sample configuration files"""
    print("\n📝 Creating sample configurations...")
    
    # Sample data paths
    data_paths = {
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
        }
    }
    
    # Sample keywords
    keywords = {
        "narcotics": {
            "street_names": [
                "molly", "mdma", "ecstasy", "snow", "white", "powder",
                "ice", "crystal", "meth", "glass", "weed", "bud", "green"
            ],
            "transaction_terms": [
                "gram", "ounce", "oz", "pound", "front", "dealer", "connect"
            ]
        },
        "financial_fraud": {
            "romance_scam": [
                "western union", "gift card", "emergency", "stranded", "customs"
            ],
            "investment_fraud": [
                "guaranteed return", "risk free", "double your money"
            ]
        },
        "human_trafficking": {
            "control_language": [
                "belong to me", "property", "owe me", "debt"
            ]
        },
        "domestic_violence": {
            "threats": [
                "hurt you", "kill you", "destroy you"
            ]
        }
    }
    
    # Sample schemas
    schemas = {
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
    
    # Sample modules config
    modules = {
        "narcotics": {
            "enabled": True,
            "risk_weights": {
                "high_risk_drugs": 4,
                "quantity_indicators": 3,
                "multiple_drugs": 2
            }
        },
        "financial_fraud": {
            "enabled": True, 
            "risk_weights": {
                "gift_cards": 4,
                "wire_transfers": 4,
                "urgency": 2
            }
        },
        "human_trafficking": {
            "enabled": True,
            "risk_weights": {
                "control_language": 4,
                "movement": 3
            }
        },
        "domestic_violence": {
            "enabled": True,
            "risk_weights": {
                "direct_threats": 5,
                "control": 3
            }
        }
    }
    
    # Write config files
    configs = [
        ("forensic_configs/data_paths.json", data_paths),
        ("forensic_configs/keywords.json", keywords),
        ("forensic_configs/database_schemas.json", schemas),
        ("forensic_configs/intelligence_modules.json", modules)
    ]
    
    for filename, config in configs:
        with open(filename, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"   ✅ Created: {filename}")

def fix_config_manager():
    """Fix config_manager.py to remove yaml dependency"""
    print("\n🔧 Fixing config_manager.py...")
    
    config_manager_path = Path("modules/config_manager.py")
    if config_manager_path.exists():
        # Read the current file
        with open(config_manager_path, 'r') as f:
            content = f.read()
        
        # Remove yaml import if present
        if 'import yaml' in content:
            content = content.replace('import yaml\n', '')
            content = content.replace('import yaml', '')
            
            # Write back the fixed file
            with open(config_manager_path, 'w') as f:
                f.write(content)
            
            print("   ✅ Removed yaml dependency from config_manager.py")
        else:
            print("   ✅ config_manager.py already clean")
    else:
        print("   ⚠️  config_manager.py not found in modules/")

def create_readme():
    """Create a basic README file"""
    readme_content = """# GHOST - Forensic Intelligence Suite

## Quick Start

1. **Test the installation:**
   ```bash
   python run_ghost.py
   ```

2. **Analyze an extraction:**
   ```bash
   python main_forensic_suite.py /path/to/extraction "Case-2024-001" "Detective Smith"
   ```

3. **Run the GUI:**
   ```bash
   python forensic_gui_app.py
   ```

## Directory Structure

- `modules/` - Core forensic analysis modules
- `forensic_configs/` - Configuration files
- `logs/` - Analysis logs
- `reports/` - Generated reports

## Configuration

Edit files in `forensic_configs/` to customize keywords and settings.
"""
    
    with open("README.md", 'w') as f:
        f.write(readme_content)
    print("   ✅ Created: README.md")

def main():
    """Main setup function"""
    print("🚀 GHOST Forensic Intelligence Suite Setup")
    print("=" * 50)
    
    # Create directories
    create_directory_structure()
    
    # Create module init
    create_module_init()
    
    # Create configurations
    create_sample_config()
    
    # Fix config manager
    fix_config_manager()
    
    # Create README
    create_readme()
    
    print("\n🎉 Setup complete!")
    print("\n📋 Next steps:")
    print("   1. Run: python run_ghost.py (to verify everything works)")
    print("   2. Test: python main_forensic_suite.py --test")
    print("   3. GUI: python forensic_gui_app.py")
    
    print(f"\n📁 Created:")
    print(f"   • Directory structure")
    print(f"   • Configuration files in forensic_configs/")
    print(f"   • Module initialization files")
    print(f"   • README.md")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        exit(1)
