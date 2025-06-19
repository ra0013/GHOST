#!/usr/bin/env python3
"""
GHOST - Golden Hour Operations and Strategic Threat Assessment
Startup Script for Forensic Intelligence Suite
"""

import sys
import os
from pathlib import Path
import subprocess

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 6):
        print("❌ Python 3.6 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_directory_structure():
    """Check if required directories exist"""
    required_dirs = ["modules", "forensic_configs"]
    missing_dirs = []
    
    for directory in required_dirs:
        if not Path(directory).exists():
            missing_dirs.append(directory)
        else:
            print(f"✅ Directory exists: {directory}")
    
    if missing_dirs:
        print(f"❌ Missing directories: {', '.join(missing_dirs)}")
        print("   Run setup.py first to create directory structure")
        return False
    
    return True

def check_modules():
    """Check if required modules exist"""
    required_modules = [
        "config_manager.py",
        "database_inspector.py", 
        "encryption_detector.py",
        "forensic_logger.py",
        "data_extractor.py",
        "intelligence_modules.py",
        "pattern_analyzer.py"
    ]
    
    modules_dir = Path("modules")
    missing_modules = []
    
    for module in required_modules:
        module_path = modules_dir / module
        if not module_path.exists():
            missing_modules.append(module)
        else:
            print(f"✅ Module exists: {module}")
    
    if missing_modules:
        print(f"❌ Missing modules: {', '.join(missing_modules)}")
        print("   Copy the fixed modules to the modules/ directory")
        return False
    
    return True

def check_configurations():
    """Check if configuration files exist"""
    required_configs = [
        "data_paths.json",
        "keywords.json",
        "database_schemas.json", 
        "intelligence_modules.json"
    ]
    
    config_dir = Path("forensic_configs")
    missing_configs = []
    
    for config in required_configs:
        config_path = config_dir / config
        if not config_path.exists():
            missing_configs.append(config)
        else:
            print(f"✅ Config exists: {config}")
    
    if missing_configs:
        print(f"❌ Missing configs: {', '.join(missing_configs)}")
        print("   Run setup.py to create default configurations")
        return False
    
    return True

def test_imports():
    """Test if all modules can be imported"""
    print("\n🧪 Testing module imports...")
    
    # Add modules to path
    sys.path.insert(0, str(Path("modules")))
    
    modules_to_test = [
        "config_manager",
        "database_inspector",
        "encryption_detector", 
        "forensic_logger",
        "data_extractor",
        "intelligence_modules",
        "pattern_analyzer"
    ]
    
    failed_imports = []
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ Import successful: {module_name}")
        except Exception as e:
            print(f"❌ Import failed: {module_name} - {e}")
            failed_imports.append(module_name)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        return False
    
    print("✅ All modules imported successfully")
    return True

def run_test():
    """Run the built-in test"""
    print("\n🧪 Running built-in test...")
    
    try:
        if Path("main_forensic_suite.py").exists():
            result = subprocess.run([sys.executable, "main_forensic_suite.py", "--test"], 
                                  capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("✅ Test completed successfully")
                print("Test output:")
                print(result.stdout)
                return True
            else:
                print("❌ Test failed")
                print("Error output:")
                print(result.stderr)
                return False
        else:
            print("❌ main_forensic_suite.py not found")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Test timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def show_usage():
    """Show usage instructions"""
    print("""
🎯 GHOST is ready! Here's how to use it:

COMMAND LINE INTERFACE:
----------------------
# Analyze an extraction
python main_forensic_suite.py /path/to/extraction "Case-2024-001" "Detective Smith"

# Run built-in test
python main_forensic_suite.py --test

GRAPHICAL INTERFACE:
-------------------
# Launch GUI application
python forensic_gui_app.py

EXAMPLE USAGE:
-------------
# Analyze iOS extraction
python main_forensic_suite.py /Extractions/iPhone_John_Doe "Case-2024-001" "Det. Johnson"

# Analyze Android extraction  
python main_forensic_suite.py /Extractions/Samsung_Galaxy "Case-2024-002" "Det. Smith"

CONFIGURATION:
-------------
# Edit keyword databases
nano forensic_configs/keywords.json

# Update database schemas
nano forensic_configs/database_schemas.json

# View analysis logs
ls logs/

# View generated reports
ls reports/

For more information, see README.md
""")

def main():
    """Main startup function"""
    print("🚀 GHOST - Golden Hour Operations and Strategic Threat Assessment")
    print("=" * 65)
    print("Forensic Intelligence Suite Startup Check")
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Directory Structure", check_directory_structure), 
        ("Required Modules", check_modules),
        ("Configuration Files", check_configurations),
        ("Module Imports", test_imports)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        print(f"\n🔍 Checking {check_name}...")
        if not check_func():
            all_passed = False
            print(f"❌ {check_name} check failed")
        else:
            print(f"✅ {check_name} check passed")
    
    if not all_passed:
        print(f"\n❌ Startup checks failed!")
        print("   Fix the issues above before running GHOST")
        print("\n🔧 Quick fixes:")
        print("   1. Run: python setup.py")
        print("   2. Copy fixed modules to modules/ directory")
        print("   3. Run this script again")
        return False
    
    print(f"\n✅ All startup checks passed!")
    
    # Ask if user wants to run test
    try:
        run_test_choice = input("\n🧪 Run built-in test? (y/N): ").lower().strip()
        if run_test_choice in ['y', 'yes']:
            if run_test():
                print("\n🎉 GHOST is fully operational!")
            else:
                print("\n⚠️  Test failed but basic checks passed")
                print("   GHOST should still work for basic analysis")
        else:
            print("\n✅ Skipping test - GHOST appears ready")
    except KeyboardInterrupt:
        print("\n\n✅ Setup check complete")
    
    show_usage()
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Startup check cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Startup error: {e}")
        sys.exit(1)
