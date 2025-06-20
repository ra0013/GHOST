#!/usr/bin/env python3
"""
GHOST Evidence Analysis Interface - Main Application
Entry point for the refactored evidence GUI application
"""

import sys
import os
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from gui.main_window import EvidenceAnalysisMainWindow
    print("[OK] GUI components loaded successfully")
except ImportError as e:
    print(f"[ERROR] Failed to import GUI components: {e}")
    print("Make sure all GUI modules are in the 'gui' directory")
    sys.exit(1)

def main():
    """Main application entry point"""
    print("[INFO] Starting GHOST Evidence Analysis Interface...")
    
    try:
        # Create and run the main application
        app = EvidenceAnalysisMainWindow()
        app.run()
        
    except KeyboardInterrupt:
        print("\nApplication closed by user")
    except Exception as e:
        print(f"Application error: {e}")
        if 'messagebox' in globals():
            try:
                root = tk.Tk()
                root.withdraw()  # Hide the root window
                messagebox.showerror("Application Error", 
                                   f"Failed to start GHOST Evidence Analysis:\n{str(e)}")
                root.destroy()
            except:
                pass

if __name__ == "__main__":
    main()
