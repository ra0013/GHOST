#!/usr/bin/env python3
"""
GHOST - Golden Hour Operations and Strategic Threat Assessment
Main Entry Point for Modular Structure
"""

import sys
import os
import argparse
from pathlib import Path

# Add the GHOST root to Python path
GHOST_ROOT = Path(__file__).parent
sys.path.insert(0, str(GHOST_ROOT))

def show_banner():
    """Display GHOST banner"""
    print("""
🔍 GHOST - Golden Hour Operations and Strategic Threat Assessment
═══════════════════════════════════════════════════════════════
    Rapid Digital Forensic Intelligence for Law Enforcement
""")

def check_dependencies():
    """Check if core modules can be imported"""
    try:
        # Test core imports
        from config.config_manager import ConfigurationManager
        from logging.forensic_logger import ForensicLogger
        print("✅ Core dependencies: OK")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def run_test_mode():
    """Run system tests"""
    print("🧪 Running GHOST system tests...")
    
    if not check_dependencies():
        return False
    
    # Test core analysis
    try:
        from core.forensic_suite import FocusedForensicSuite
        print("✅ Core analysis engine: OK")
    except ImportError as e:
        print(f"❌ Core analysis engine: {e}")
        return False
    
    # Test GUI components
    try:
        from gui.main_window import EvidenceAnalysisMainWindow
        print("✅ GUI interface: OK")
    except ImportError as e:
        print(f"⚠️  GUI interface: {e} (optional)")
    
    print("✅ System tests completed!")
    return True

def run_gui_mode():
    """Launch GUI interface"""
    try:
        from gui.main_window import EvidenceAnalysisMainWindow
        print("🖥️  Launching GHOST GUI...")
        
        app = EvidenceAnalysisMainWindow()
        app.run()
        return True
        
    except ImportError as e:
        print(f"❌ Cannot import GUI: {e}")
        return False
    except Exception as e:
        print(f"❌ GUI error: {e}")
        return False

def run_cli_mode(extraction_path, case_name, examiner_name):
    """Run CLI analysis"""
    try:
        from core.forensic_suite import FocusedForensicSuite
        print(f"⚡ Starting CLI analysis...")
        print(f"   Case: {case_name}")
        print(f"   Examiner: {examiner_name}")
        print(f"   Source: {extraction_path}")
        
        suite = FocusedForensicSuite(case_name, examiner_name)
        results = suite.analyze_extraction(extraction_path)
        
        # Save results
        report_file = suite.save_report(results)
        print(f"✅ Analysis complete! Report: {report_file}")
        return True
        
    except ImportError as e:
        print(f"❌ Cannot import analysis engine: {e}")
        return False
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="GHOST Forensic Intelligence Suite")
    parser.add_argument('mode', nargs='?', choices=['gui', 'cli', 'test'], 
                       default='test', help='Operation mode')
    parser.add_argument('extraction_path', nargs='?', help='Path to extraction (CLI mode)')
    parser.add_argument('case_name', nargs='?', help='Case name (CLI mode)')
    parser.add_argument('examiner_name', nargs='?', help='Examiner name (CLI mode)')
    
    args = parser.parse_args()
    
    show_banner()
    
    if args.mode == 'test':
        if not run_test_mode():
            sys.exit(1)
    elif args.mode == 'gui':
        if not run_gui_mode():
            sys.exit(1)
    elif args.mode == 'cli':
        if not all([args.extraction_path, args.case_name, args.examiner_name]):
            print("❌ CLI mode requires: extraction_path case_name examiner_name")
            sys.exit(1)
        if not run_cli_mode(args.extraction_path, args.case_name, args.examiner_name):
            sys.exit(1)

if __name__ == "__main__":
    main()
