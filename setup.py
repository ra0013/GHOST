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

def check_dependencies():
    """Check if required Python modules are available"""
    print("\n🔍 Checking dependencies...")
    
    required_modules = [
        "sqlite3",
        "json", 
        "pathlib",
        "datetime",
        "hashlib",
        "logging",
        "re",
        "collections"
    ]
    
    missing = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError:
            print(f"   ❌ {module} (missing)")
            missing.append(module)
    
    if missing:
        print(f"\n⚠️  Missing modules: {', '.join(missing)}")
        print("   These are usually part of Python standard library.")
        return False
    else:
        print("\n✅ All dependencies satisfied!")
        return True

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
        }
    }
    
    # Sample keywords
    keywords = {
        "narcotics": {
            "street_names": [
                "molly", "mdma", "ecstasy", "snow", "white", "powder",
                "ice", "crystal", "meth", "glass", "weed", "bud"
            ],
            "transaction_terms": [
                "gram", "ounce", "oz", "pound", "front", "dealer"
            ]
        },
        "financial_fraud": {
            "scam_terms": [
                "western union", "gift card", "emergency", "stranded"
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
                "is_from_me": "is_from_me"
            },
            "timestamp_conversion": "datetime(date/1000000000 + 978307200, 'unixepoch')"
        }
    }
    
    # Sample modules config
    modules = {
        "narcotics": {
            "enabled": True,
            "risk_weights": {"high_risk_drugs": 4, "quantity_indicators": 3}
        },
        "financial_fraud": {
            "enabled": True, 
            "risk_weights": {"gift_cards": 4, "urgency": 2}
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

def create_readme():
    """Create a README file with usage instructions"""
    readme_content = """# GHOST - Forensic Intelligence Suite

## Quick Start

1. **Test the installation:**
   ```bash
   python main_forensic_suite.py --test
   ```

2. **Analyze an extraction:**
   ```bash
   python main_forensic_suite.py /path/to/extraction "Case-2024-001" "Detective Smith"
   ```

3. **Run the GUI (if available):**
   ```bash
   python forensic_gui_app.py
   ```

## Directory Structure

- `modules/` - Core forensic analysis modules
- `forensic_configs/` - Configuration files (keywords, schemas, etc.)
- `logs/` - Analysis logs and chain of custody
- `reports/` - Generated reports

## Key Features

- 🔍 **Database Discovery** - Automatically finds and analyzes SQLite databases
- 🔐 **Encryption Detection** - Identifies encrypted databases
- 🧠 **Intelligence Analysis** - Crime-specific analysis modules
- 📊 **Adaptive Processing** - Resource-aware analysis
- 📋 **Chain of Custody** - Forensic logging and audit trails

## Configuration

Edit files in `forensic_configs/` to customize:
- Database schemas (`database_schemas.json`)
- Intelligence keywords (`keywords.json`) 
- Module settings (`intelligence_modules.json`)
- Data source paths (`data_paths.json`)

## Troubleshooting

If you encounter errors:
1. Check that all modules are in the `modules/` directory
2. Verify configuration files in `forensic_configs/`
3. Run with `--test` flag to validate setup
4. Check logs in the `logs/` directory

## Support

This is the GHOST (Golden Hour Operations and Strategic Threat Assessment) suite
for rapid forensic intelligence analysis during critical investigation phases.
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
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Setup incomplete due to missing dependencies")
        return False
    
    # Create configurations
    create_sample_config()
    
    # Create README
    create_readme()
    
    print("\n🎉 Setup complete!")
    print("\n📋 Next steps:")
    print("   1. Copy your fixed module files to the 'modules/' directory")
    print("   2. Run: python main_forensic_suite.py --test")
    print("   3. If test passes, analyze real extractions")
    
    print(f"\n📁 Files created:")
    print(f"   • Directory structure in current folder")
    print(f"   • Configuration files in forensic_configs/")
    print(f"   • README.md with usage instructions")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        exit(1)
