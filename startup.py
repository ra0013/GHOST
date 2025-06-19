#!/usr/bin/env python3
"""
GHOST - Golden Hour Operations and Strategic Threat Assessment
Startup Script for Forensic Intelligence Suite
Multiple Analysis Options
"""

import sys
import os
from pathlib import Path
import subprocess

def show_ghost_menu():
    """Show GHOST analysis options"""
    print("🔍 GHOST - Golden Hour Operations and Strategic Threat Assessment")
    print("=" * 65)
    print()
    print("Available Analysis Tools:")
    print()
    print("1. 📋 EVIDENCE ANALYSIS (Recommended)")
    print("   Focused forensic analysis for investigators")
    print("   → python ghost_forensic_suite.py <extraction> <case> <examiner>")
    print()
    print("2. 🖥️  GUI INTERFACE")
    print("   Visual interface for interactive analysis")
    print("   → python forensic_gui_app.py")
    print()
    print("3. ⚡ THREADED ANALYSIS")
    print("   High-performance multi-threaded processing")
    print("   → python threaded_forensic_suite.py <extraction> <case> <examiner>")
    print()
    print("4. 🧪 SYSTEM TEST")
    print("   Verify GHOST installation and functionality")
    print("   → python ghost_forensic_suite.py --test")
    print()

def check_files():
    """Check which GHOST files are available"""
    files_status = {}
    
    ghost_files = [
        ("ghost_forensic_suite.py", "Evidence Analysis Tool"),
        ("forensic_gui_app.py", "GUI Interface"),
        ("threaded_forensic_suite.py", "Threaded Analysis"),
        ("main_forensic_suite.py", "Original Analysis Tool")
    ]
    
    print("📁 Checking GHOST Components...")
    
    for filename, description in ghost_files:
        if Path(filename).exists():
            files_status[filename] = True
            print(f"   ✅ {description}: {filename}")
        else:
            files_status[filename] = False
            print(f"   ❌ {description}: {filename} (missing)")
    
    return files_status

def run_quick_test():
    """Run a quick test of the evidence analysis tool"""
    print("\n🧪 Running Quick Test...")
    
    # Check if focused evidence tool exists
    if Path("ghost_forensic_suite.py").exists():
        try:
            result = subprocess.run([
                sys.executable, "ghost_forensic_suite.py", 
                "test_data", "QuickTest", "TestUser"
            ], capture_output=True, text=True, timeout=30)
            
            if "GHOST - Golden Hour Operations" in result.stdout:
                print("✅ Evidence analysis tool responding correctly")
                return True
            else:
                print("❌ Evidence analysis tool not responding properly")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Test timed out")
            return False
        except Exception as e:
            print(f"❌ Test error: {e}")
            return False
    else:
        print("❌ ghost_forensic_suite.py not found")
        return False

def show_usage_examples():
    """Show practical usage examples"""
    print("\n📖 USAGE EXAMPLES:")
    print()
    print("🔍 ANALYZE iPhone EXTRACTION (ZIP):")
    print('   python ghost_forensic_suite.py "C:\\Cases\\iPhone_Suspect.zip" "Case-2024-001" "Det. Smith"')
    print()
    print("🔍 ANALYZE Android EXTRACTION (Directory):")
    print('   python ghost_forensic_suite.py "C:\\Cases\\Android_Extract\\" "Case-2024-002" "Det. Jones"')
    print()
    print("🖥️  LAUNCH GUI INTERFACE:")
    print("   python forensic_gui_app.py")
    print()
    print("🧪 RUN SYSTEM TEST:")
    print("   python ghost_forensic_suite.py --test")
    print()

def show_what_you_get():
    """Show what GHOST provides"""
    print("🎯 WHAT GHOST PROVIDES:")
    print()
    print("📱 COMMUNICATION INTELLIGENCE:")
    print("   • SMS/Text message analysis with keyword detection")
    print("   • Call log patterns and frequency analysis")
    print("   • Contact relationship mapping")
    print()
    print("📷 MULTIMEDIA EVIDENCE:")
    print("   • Photo and video inventory with metadata")
    print("   • Timeline analysis of media creation")
    print()
    print("🗺️  LOCATION INTELLIGENCE:")
    print("   • GPS tracking and movement patterns")
    print("   • Frequent location identification")
    print()
    print("📱 APP DATA ANALYSIS:")
    print("   • WhatsApp, Snapchat, Telegram data extraction")
    print("   • Social media app analysis")
    print("   • Messaging platform intelligence")
    print()
    print("📊 INVESTIGATIVE OUTPUTS:")
    print("   • Executive summary with priority assessment")
    print("   • Actionable intelligence leads")
    print("   • Data export options (CSV, JSON)")
    print("   • Professional forensic reports")
    print()

def main():
    """Main function"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help":
            show_ghost_menu()
            show_usage_examples()
            show_what_you_get()
            return
        elif sys.argv[1] == "--test":
            check_files()
            run_quick_test()
            return
        elif sys.argv[1] == "--menu":
            show_ghost_menu()
            return
    
    # Default behavior - show menu and check system
    show_ghost_menu()
    
    print()
    files_status = check_files()
    
    # Recommend next steps based on what's available
    print("\n🚀 RECOMMENDED NEXT STEPS:")
    
    if files_status.get("ghost_forensic_suite.py", False):
        print("   1. Test the system:")
        print("      python run_ghost.py --test")
        print()
        print("   2. Analyze real evidence:")
        print('      python ghost_forensic_suite.py "path\\to\\extraction.zip" "CaseName" "ExaminerName"')
        
    elif files_status.get("forensic_gui_app.py", False):
        print("   1. Launch GUI interface:")
        print("      python forensic_gui_app.py")
        
    else:
        print("   1. Set up GHOST components:")
        print("      python setup.py")
        print()
        print("   2. Add the forensic analysis tools")
    
    print()
    print("💡 For detailed help: python run_ghost.py --help")

if __name__ == "__main__":
    main()
