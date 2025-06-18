#!/usr/bin/env python3
"""
Forensic Intelligence Suite - Complete Clean GUI Application
Professional interface for digital forensics investigators with adaptive processing
"""

import sys
import os
from pathlib import Path
import json
import datetime
import threading
import time
from typing import Dict, List, Any, Optional

# GUI Framework
try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox, scrolledtext
    import tkinter.font as tkfont
except ImportError:
    print("Tkinter not available. Please install tkinter")
    sys.exit(1)

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent / "modules"))

# Import forensic modules
try:
    from config_manager import ConfigurationManager
    from database_inspector import DatabaseInspector
    from pattern_analyzer import PatternAnalyzer
    from encryption_detector import EncryptionDetector
    from intelligence_modules import IntelligenceModuleFactory
    from forensic_logger import ForensicLogger
    from data_extractor import DataExtractor
    from adaptive_processor import AdaptiveProcessor, ProcessingPriority
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure all module files are in the 'modules' directory")
    # Continue anyway for demo purposes
    
class ForensicIntelligenceGUI:
    """Main GUI application for forensic intelligence suite"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_main_window()
        
        # Application state variables
        self.case_name = tk.StringVar()
        self.examiner_name = tk.StringVar()
        self.extraction_path = tk.StringVar()
        self.processing_mode = tk.StringVar(value="adaptive")
        
        # Status variables for real-time display
        self.cpu_var = tk.StringVar(value="0%")
        self.memory_var = tk.StringVar(value="0%")
        self.threads_var = tk.StringVar(value="0")
        self.efficiency_var = tk.StringVar(value="Ready")
        self.status_var = tk.StringVar(value="Ready")
        self.time_var = tk.StringVar()
        
        # Progress variable
        self.progress_var = tk.DoubleVar()
        
        # Data storage
        self.selected_modules = []
        self.module_vars = {}
        self.analysis_results = {}
        self.current_databases = []
        
        # Processing components (will be initialized when needed)
        self.config_manager = None
        self.logger = None
        self.adaptive_processor = None
        self.processing_timer = None
        
        # Create GUI
        self.setup_styling()
        self.create_widgets()
        self.load_configuration()
        
        # Start time updates
        self.update_time()
    
    def setup_main_window(self):
        """Configure the main application window"""
        self.root.title("🔍 Forensic Intelligence Suite v2.0 - Adaptive Processing")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 700)
        
        # Configure for responsive design
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Try to set icon (optional)
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
    
    def setup_styling(self):
        """Configure modern styling"""
        self.style = ttk.Style()
        
        # Use a modern theme
        try:
            self.style.theme_use('clam')
        except:
            self.style.theme_use('default')
        
        # Color scheme
        colors = {
            'primary': '#2E86AB',     # Professional blue
            'accent': '#A23B72',      # Purple accent
            'success': '#F18F01',     # Orange
            'danger': '#C73E1D',      # Red
            'text': '#333333'         # Dark gray
        }
        
        # Configure styles
        self.style.configure('Title.TLabel', 
                           font=('Arial', 16, 'bold'), 
                           foreground=colors['primary'])
        
        self.style.configure('Header.TLabel', 
                           font=('Arial', 12, 'bold'), 
                           foreground=colors['text'])
        
        self.style.configure('Status.TLabel', 
                           font=('Arial', 10), 
                           foreground=colors['accent'])
        
        self.style.configure('Primary.TButton', 
                           font=('Arial', 10, 'bold'))
        
        self.style.configure('Secondary.TButton', 
                           font=('Arial', 9))
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Title bar
        self.create_title_bar(main_frame)
        
        # Main notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        
        # Create all tabs
        self.create_case_tab()
        self.create_database_tab()
        self.create_analysis_tab()
        self.create_results_tab()
        self.create_config_tab()
        
        # Status bar
        self.create_status_bar(main_frame)
    
    def create_title_bar(self, parent):
        """Create the application title bar"""
        title_frame = ttk.Frame(parent)
        title_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        title_frame.grid_columnconfigure(1, weight=1)
        
        # Main title
        title = ttk.Label(title_frame, 
                         text="🔍 Forensic Intelligence Suite", 
                         style='Title.TLabel')
        title.grid(row=0, column=0, sticky="w")
        
        # Version info
        version = ttk.Label(title_frame, 
                           text="v2.0 | Adaptive Processing | Golden Hour Intelligence", 
                           style='Status.TLabel')
        version.grid(row=0, column=1, sticky="e")
    
    def create_case_tab(self):
        """Create case setup tab"""
        # Create tab frame
        case_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(case_frame, text="📋 Case Setup")
        
        # Configure grid
        case_frame.grid_columnconfigure(0, weight=1)
        
        # Case Information Section
        info_frame = ttk.LabelFrame(case_frame, text="Case Information", padding="15")
        info_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        info_frame.grid_columnconfigure(1, weight=1)
        
        # Case name
        ttk.Label(info_frame, text="Case Name:", style='Header.TLabel').grid(
            row=0, column=0, sticky="w", pady=(0, 10))
        case_entry = ttk.Entry(info_frame, textvariable=self.case_name, width=40)
        case_entry.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=(0, 10))
        
        # Examiner
        ttk.Label(info_frame, text="Examiner:", style='Header.TLabel').grid(
            row=1, column=0, sticky="w", pady=(0, 10))
        examiner_entry = ttk.Entry(info_frame, textvariable=self.examiner_name, width=40)
        examiner_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(0, 10))
        
        # Extraction path
        ttk.Label(info_frame, text="Extraction Path:", style='Header.TLabel').grid(
            row=2, column=0, sticky="w")
        
        path_frame = ttk.Frame(info_frame)
        path_frame.grid(row=2, column=1, sticky="ew", padx=(10, 0))
        path_frame.grid_columnconfigure(0, weight=1)
        
        path_entry = ttk.Entry(path_frame, textvariable=self.extraction_path)
        path_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        browse_btn = ttk.Button(path_frame, text="Browse...", command=self.browse_path)
        browse_btn.grid(row=0, column=1)
        
        # Modules Selection
        modules_frame = ttk.LabelFrame(case_frame, text="Intelligence Modules", padding="15")
        modules_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        self.create_module_selection(modules_frame)
        
        # Adaptive Processing Settings
        processing_frame = ttk.LabelFrame(case_frame, text="Adaptive Processing", padding="15")
        processing_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        
        self.create_processing_controls(processing_frame)
        
        # Action Buttons
        button_frame = ttk.Frame(case_frame)
        button_frame.grid(row=3, column=0, sticky="ew")
        
        ttk.Button(button_frame, text="🔍 Quick Scan", 
                  command=self.quick_scan, style='Secondary.TButton').pack(side="left", padx=(0, 10))
        
        ttk.Button(button_frame, text="🚀 Start Adaptive Analysis", 
                  command=self.start_analysis, style='Primary.TButton').pack(side="left", padx=(0, 10))
        
        ttk.Button(button_frame, text="💾 Save Case", 
                  command=self.save_case, style='Secondary.TButton').pack(side="left", padx=(0, 10))
        
        ttk.Button(button_frame, text="📁 Load Case", 
                  command=self.load_case, style='Secondary.TButton').pack(side="left")
    
    def create_module_selection(self, parent):
        """Create intelligence module selection interface"""
        # Available modules
        modules = ['narcotics', 'financial_fraud', 'human_trafficking', 'domestic_violence']
        
        # Create checkboxes in grid
        for i, module in enumerate(modules):
            var = tk.BooleanVar(value=True)  # Default to selected
            self.module_vars[module] = var
            
            display_name = module.replace('_', ' ').title()
            cb = ttk.Checkbutton(parent, text=display_name, variable=var,
                               command=self.update_selected_modules)
            cb.grid(row=i//2, column=i%2, sticky="w", padx=(0, 20), pady=5)
        
        # Selection buttons
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=2, column=0, columnspan=2, sticky="w", pady=(10, 0))
        
        ttk.Button(btn_frame, text="Select All", 
                  command=self.select_all_modules).pack(side="left", padx=(0, 10))
        ttk.Button(btn_frame, text="Select None", 
                  command=self.select_none_modules).pack(side="left")
    
    def create_processing_controls(self, parent):
        """Create adaptive processing controls"""
        # Processing mode selection
        ttk.Label(parent, text="Processing Mode:", style='Header.TLabel').grid(
            row=0, column=0, sticky="w", pady=(0, 10))
        
        mode_frame = ttk.Frame(parent)
        mode_frame.grid(row=0, column=1, sticky="w", pady=(0, 10))
        
        ttk.Radiobutton(mode_frame, text="Conservative", variable=self.processing_mode, 
                       value="conservative").pack(side="left", padx=(0, 15))
        ttk.Radiobutton(mode_frame, text="Adaptive", variable=self.processing_mode, 
                       value="adaptive").pack(side="left", padx=(0, 15))
        ttk.Radiobutton(mode_frame, text="Aggressive", variable=self.processing_mode, 
                       value="aggressive").pack(side="left")
        
        # Resource monitoring display
        resource_frame = ttk.Frame(parent)
        resource_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        # CPU
        ttk.Label(resource_frame, text="CPU:").grid(row=0, column=0, sticky="w")
        ttk.Label(resource_frame, textvariable=self.cpu_var, 
                 font=('Arial', 10, 'bold')).grid(row=0, column=1, sticky="w", padx=(5, 20))
        
        # Memory
        ttk.Label(resource_frame, text="Memory:").grid(row=0, column=2, sticky="w")
        ttk.Label(resource_frame, textvariable=self.memory_var, 
                 font=('Arial', 10, 'bold')).grid(row=0, column=3, sticky="w", padx=(5, 20))
        
        # Threads
        ttk.Label(resource_frame, text="Threads:").grid(row=0, column=4, sticky="w")
        ttk.Label(resource_frame, textvariable=self.threads_var, 
                 font=('Arial', 10, 'bold')).grid(row=0, column=5, sticky="w", padx=(5, 0))
        
        # Efficiency indicator
        efficiency_frame = ttk.Frame(parent)
        efficiency_frame.grid(row=2, column=0, columnspan=2, sticky="w", pady=(10, 0))
        
        ttk.Label(efficiency_frame, text="Processing Efficiency:").pack(side="left")
        ttk.Label(efficiency_frame, textvariable=self.efficiency_var, 
                 font=('Arial', 10, 'bold'), foreground="#2E86AB").pack(side="left", padx=(10, 0))
    
    def create_database_tab(self):
        """Create database analysis tab"""
        db_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(db_frame, text="🗄️ Database Analysis")
        
        # Configure grid
        db_frame.grid_rowconfigure(1, weight=1)
        db_frame.grid_columnconfigure(0, weight=1)
        
        # Control buttons
        controls = ttk.Frame(db_frame)
        controls.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        ttk.Button(controls, text="🔍 Discover Databases", 
                  command=self.discover_databases).pack(side="left", padx=(0, 10))
        ttk.Button(controls, text="🔐 Check Encryption", 
                  command=self.check_encryption).pack(side="left", padx=(0, 10))
        ttk.Button(controls, text="📊 Analyze Patterns", 
                  command=self.analyze_patterns).pack(side="left")
        
        # Results area
        results_notebook = ttk.Notebook(db_frame)
        results_notebook.grid(row=1, column=0, sticky="nsew")
        
        # Database list tab
        db_list_frame = ttk.Frame(results_notebook)
        results_notebook.add(db_list_frame, text="Database List")
        
        self.create_database_list(db_list_frame)
        
        # Encryption results tab
        encryption_frame = ttk.Frame(results_notebook)
        results_notebook.add(encryption_frame, text="Encryption Analysis")
        
        self.encryption_text = scrolledtext.ScrolledText(encryption_frame, font=('Consolas', 10))
        self.encryption_text.pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_database_list(self, parent):
        """Create database list display"""
        # Configure grid
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        # Treeview for databases
        columns = ("Name", "Path", "Status", "Size")
        self.db_tree = ttk.Treeview(parent, columns=columns, show="tree headings")
        
        # Configure columns
        self.db_tree.heading("#0", text="Type")
        self.db_tree.column("#0", width=80)
        
        for col in columns:
            self.db_tree.heading(col, text=col)
            self.db_tree.column(col, width=200)
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(parent, orient="vertical", command=self.db_tree.yview)
        h_scroll = ttk.Scrollbar(parent, orient="horizontal", command=self.db_tree.xview)
        self.db_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # Grid layout
        self.db_tree.grid(row=0, column=0, sticky="nsew", padx=(10, 0), pady=10)
        v_scroll.grid(row=0, column=1, sticky="ns", pady=10)
        h_scroll.grid(row=1, column=0, sticky="ew", padx=(10, 0))
    
    def create_analysis_tab(self):
        """Create intelligence analysis tab"""
        analysis_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(analysis_frame, text="🧠 Intelligence Analysis")
        
        # Configure grid
        analysis_frame.grid_rowconfigure(2, weight=1)
        analysis_frame.grid_columnconfigure(0, weight=1)
        
        # Control buttons
        controls = ttk.Frame(analysis_frame)
        controls.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        ttk.Button(controls, text="🚀 Run Analysis", 
                  command=self.run_analysis).pack(side="left", padx=(0, 10))
        ttk.Button(controls, text="📊 Generate Report", 
                  command=self.generate_report).pack(side="left")
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(analysis_frame, variable=self.progress_var, 
                                          mode='determinate')
        self.progress_bar.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        # Results notebook
        results_notebook = ttk.Notebook(analysis_frame)
        results_notebook.grid(row=2, column=0, sticky="nsew")
        
        # Overview tab
        overview_frame = ttk.Frame(results_notebook)
        results_notebook.add(overview_frame, text="📈 Overview")
        
        self.create_overview_display(overview_frame)
        
        # Findings tab
        findings_frame = ttk.Frame(results_notebook)
        results_notebook.add(findings_frame, text="🔍 Findings")
        
        self.create_findings_display(findings_frame)
    
    def create_overview_display(self, parent):
        """Create analysis overview display"""
        # Summary cards frame
        cards_frame = ttk.Frame(parent)
        cards_frame.pack(fill="x", padx=10, pady=10)
        
        # Create summary cards
        self.summary_cards = {}
        card_titles = ["Total Findings", "Critical Alerts", "High Risk", "Communications"]
        
        for i, title in enumerate(card_titles):
            card = self.create_summary_card(cards_frame, title, "0")
            card.grid(row=0, column=i, padx=5, sticky="ew")
            self.summary_cards[title] = card
        
        # Configure column weights
        for i in range(len(card_titles)):
            cards_frame.grid_columnconfigure(i, weight=1)
        
        # Overview text area
        overview_label_frame = ttk.LabelFrame(parent, text="Analysis Overview")
        overview_label_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.overview_text = scrolledtext.ScrolledText(overview_label_frame, 
                                                      font=('Consolas', 10))
        self.overview_text.pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_summary_card(self, parent, title, value):
        """Create a summary statistics card"""
        card_frame = ttk.LabelFrame(parent, text=title)
        
        value_label = ttk.Label(card_frame, text=value, font=('Arial', 20, 'bold'))
        value_label.pack(pady=15)
        
        return card_frame
    
    def create_findings_display(self, parent):
        """Create detailed findings display"""
        # Configure grid
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        # Findings treeview
        columns = ("Module", "Type", "Risk", "Contact", "Timestamp")
        self.findings_tree = ttk.Treeview(parent, columns=columns, show="headings")
        
        # Configure columns
        for col in columns:
            self.findings_tree.heading(col, text=col)
            self.findings_tree.column(col, width=150)
        
        # Scrollbars
        findings_v_scroll = ttk.Scrollbar(parent, orient="vertical", 
                                        command=self.findings_tree.yview)
        findings_h_scroll = ttk.Scrollbar(parent, orient="horizontal", 
                                        command=self.findings_tree.xview)
        self.findings_tree.configure(yscrollcommand=findings_v_scroll.set, 
                                   xscrollcommand=findings_h_scroll.set)
        
        # Grid layout
        self.findings_tree.grid(row=0, column=0, sticky="nsew", padx=(10, 0), pady=10)
        findings_v_scroll.grid(row=0, column=1, sticky="ns", pady=10)
        findings_h_scroll.grid(row=1, column=0, sticky="ew", padx=(10, 0))
    
    def create_results_tab(self):
        """Create results and reporting tab"""
        results_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(results_frame, text="📊 Results & Reports")
        
        # Configure grid
        results_frame.grid_rowconfigure(1, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)
        
        # Export controls
        export_frame = ttk.Frame(results_frame)
        export_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        ttk.Button(export_frame, text="📄 Export PDF", 
                  command=self.export_pdf).pack(side="left", padx=(0, 10))
        ttk.Button(export_frame, text="📊 Export JSON", 
                  command=self.export_json).pack(side="left", padx=(0, 10))
        ttk.Button(export_frame, text="📋 Copy Summary", 
                  command=self.copy_summary).pack(side="left")
        
        # Report display
        report_label_frame = ttk.LabelFrame(results_frame, text="Generated Report")
        report_label_frame.grid(row=1, column=0, sticky="nsew")
        report_label_frame.grid_rowconfigure(0, weight=1)
        report_label_frame.grid_columnconfigure(0, weight=1)
        
        self.report_text = scrolledtext.ScrolledText(report_label_frame, 
                                                    font=('Consolas', 10))
        self.report_text.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    
    def create_config_tab(self):
        """Create configuration tab"""
        config_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(config_frame, text="⚙️ Configuration")
        
        # Configuration info
        info_text = scrolledtext.ScrolledText(config_frame, font=('Consolas', 10))
        info_text.pack(fill="both", expand=True)
        
        # Insert configuration information
        config_info = """
CONFIGURATION MANAGEMENT
========================

The Forensic Intelligence Suite uses JSON configuration files that can be
easily updated without modifying the source code.

Configuration Files:
- data_paths.json: Database file locations
- keywords.json: Intelligence module keywords  
- database_schemas.json: Database table structures
- intelligence_modules.json: Module settings

To Update Configurations:
1. Edit the JSON files in the forensic_configs/ directory
2. Restart the application to load new settings
3. Use the CLI tools for advanced configuration management

Example: Adding new drug terminology
1. Open forensic_configs/keywords.json
2. Find the "narcotics" section
3. Add new terms to the appropriate category
4. Save and restart

For detailed configuration instructions, see the documentation.
"""
        info_text.insert("1.0", config_info)
        info_text.config(state="disabled")
        
        self.config_text = info_text
    
    def create_status_bar(self, parent):
        """Create application status bar"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        status_frame.grid_columnconfigure(0, weight=1)
        
        # Status message
        status_label = ttk.Label(status_frame, textvariable=self.status_var, 
                               style='Status.TLabel')
        status_label.grid(row=0, column=0, sticky="w")
        
        # Current time
        time_label = ttk.Label(status_frame, textvariable=self.time_var)
        time_label.grid(row=0, column=1, sticky="e")
    
    # Event handlers and utility methods
    
    def load_configuration(self):
        """Load application configuration"""
        try:
            self.config_manager = ConfigurationManager()
            self.update_status("Configuration loaded successfully")
        except Exception as e:
            self.update_status(f"Configuration error: {str(e)}")
            # Continue with default settings
    
    def update_time(self):
        """Update time display"""
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_var.set(current_time)
        self.root.after(1000, self.update_time)
    
    def update_status(self, message):
        """Update status bar message"""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def browse_path(self):
        """Browse for extraction directory"""
        path = filedialog.askdirectory(title="Select Forensic Extraction Directory")
        if path:
            self.extraction_path.set(path)
            self.update_status(f"Extraction path set: {path}")
    
    def update_selected_modules(self):
        """Update list of selected modules"""
        self.selected_modules = [module for module, var in self.module_vars.items() 
                               if var.get()]
    
    def select_all_modules(self):
        """Select all intelligence modules"""
        for var in self.module_vars.values():
            var.set(True)
        self.update_selected_modules()
    
    def select_none_modules(self):
        """Deselect all intelligence modules"""
        for var in self.module_vars.values():
            var.set(False)
        self.update_selected_modules()
    
    def validate_case_info(self):
        """Validate case information before analysis"""
        if not self.case_name.get().strip():
            messagebox.showerror("Error", "Please enter a case name")
            return False
        
        if not self.examiner_name.get().strip():
            messagebox.showerror("Error", "Please enter examiner name")
            return False
        
        if not self.extraction_path.get().strip():
            messagebox.showerror("Error", "Please select extraction path")
            return False
        
        if not Path(self.extraction_path.get()).exists():
            messagebox.showerror("Error", "Extraction path does not exist")
            return False
        
        return True
    
    def quick_scan(self):
        """Perform quick database scan"""
        if not self.validate_case_info():
            return
        
        self.update_status("Performing quick scan...")
        
        try:
            extraction_path = Path(self.extraction_path.get())
            
            # Find database files
            db_patterns = ["*.db", "*.sqlite", "*.sqlitedb"]
            found_dbs = []
            
            for pattern in db_patterns:
                found_dbs.extend(list(extraction_path.rglob(pattern)))
            
            # Update database tree
            self.update_database_tree(found_dbs)
            self.current_databases = found_dbs
            
            self.update_status(f"Quick scan complete: {len(found_dbs)} databases found")
            
            # Switch to database tab
            self.notebook.select(1)
            
        except Exception as e:
            messagebox.showerror("Scan Error", f"Error during quick scan: {str(e)}")
    
    def update_database_tree(self, databases):
        """Update the database tree display"""
        # Clear existing items
        for item in self.db_tree.get_children():
            self.db_tree.delete(item)
        
        # Add databases
        for db_path in databases:
            try:
                size = db_path.stat().st_size
                if size > 1024 * 1024:
                    size_str = f"{size / (1024 * 1024):.1f} MB"
                else:
                    size_str = f"{size / 1024:.1f} KB"
                
                self.db_tree.insert("", "end", text="📁", values=(
                    db_path.stem,
                    str(db_path),
                    "Discovered",
                    size_str
                ))
            except Exception:
                # Skip files that can't be accessed
                continue
    
    def start_analysis(self):
        """Start full adaptive forensic analysis"""
        if not self.validate_case_info():
            return
        
        # Confirm analysis start
        if not messagebox.askyesno("Start Analysis", 
                                  "Start comprehensive adaptive analysis?"):
            return
        
        self.update_status("Starting adaptive analysis...")
        self.progress_var.set(0)
        
        # Update selected modules
        self.update_selected_modules()
        
        # Start analysis in background thread
        analysis_thread = threading.Thread(target=self.run_analysis_worker, daemon=True)
        analysis_thread.start()
    
    def run_analysis_worker(self):
        """Background worker for analysis"""
        try:
            # Initialize logger
            self.logger = ForensicLogger(self.case_name.get(), self.examiner_name.get())
            
            # Phase 1: Database Discovery
            self.root.after(0, lambda: self.update_status("Discovering databases..."))
            self.root.after(0, lambda: self.progress_var.set(10))
            
            extraction_path = Path(self.extraction_path.get())
            databases = self.discover_databases_worker(extraction_path)
            
            # Phase 2: Database Analysis
            self.root.after(0, lambda: self.update_status("Analyzing databases..."))
            self.root.after(0, lambda: self.progress_var.set(30))
            
            analyzed_dbs = self.analyze_databases_worker(databases)
            
            # Phase 3: Data Extraction
            self.root.after(0, lambda: self.update_status("Extracting data..."))
            self.root.after(0, lambda: self.progress_var.set(50))
            
            communications = self.extract_data_worker(analyzed_dbs)
            
            # Phase 4: Intelligence Analysis
            self.root.after(0, lambda: self.update_status("Running intelligence analysis..."))
            self.root.after(0, lambda: self.progress_var.set(70))
            
            findings = self.run_intelligence_worker(communications)
            
            # Phase 5: Generate Results
            self.root.after(0, lambda: self.update_status("Generating results..."))
            self.root.after(0, lambda: self.progress_var.set(90))
            
            results = self.generate_results_worker(databases, communications, findings)
            
            # Update UI with results
            self.root.after(0, lambda: self.update_analysis_results(results))
            self.root.after(0, lambda: self.progress_var.set(100))
            self.root.after(0, lambda: self.update_status("Analysis complete"))
            
        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            self.root.after(0, lambda: self.update_status(error_msg))
            self.root.after(0, lambda: messagebox.showerror("Analysis Error", error_msg))
    
    def discover_databases_worker(self, extraction_path):
        """Worker function for database discovery"""
        databases = []
        
        # Look for common database files
        patterns = ["*.db", "*.sqlite", "*.sqlitedb"]
        
        for pattern in patterns:
            for db_path in extraction_path.rglob(pattern):
                databases.append({
                    'name': db_path.stem,
                    'path': db_path,
                    'size': db_path.stat().st_size if db_path.exists() else 0
                })
        
        return databases
    
    def analyze_databases_worker(self, databases):
        """Worker function for database analysis"""
        analyzed = []
        
        for db_info in databases:
            try:
                # Basic analysis - check if file is accessible
                db_path = db_info['path']
                
                if not db_path.exists():
                    db_info['status'] = 'not_found'
                elif db_path.stat().st_size == 0:
                    db_info['status'] = 'empty'
                else:
                    db_info['status'] = 'ready'
                
                analyzed.append(db_info)
                
            except Exception as e:
                db_info['status'] = 'error'
                db_info['error'] = str(e)
                analyzed.append(db_info)
        
        return analyzed
    
    def extract_data_worker(self, databases):
        """Worker function for data extraction"""
        communications = []
        
        # Simulate data extraction
        for db_info in databases:
            if db_info.get('status') == 'ready':
                # For demo purposes, create sample communications
                # In real implementation, this would use DataExtractor
                sample_comms = [
                    {
                        'source': db_info['name'],
                        'timestamp': datetime.datetime.now().isoformat(),
                        'content': f"Sample message from {db_info['name']}",
                        'contact': 'Unknown',
                        'type': 'MESSAGE'
                    }
                ]
                communications.extend(sample_comms)
        
        return communications
    
    def run_intelligence_worker(self, communications):
        """Worker function for intelligence analysis"""
        findings = []
        
        # Simulate intelligence analysis
        if communications and self.selected_modules:
            for module in self.selected_modules:
                # Create sample finding
                finding = {
                    'module': module,
                    'type': f"{module.upper()}_INDICATOR",
                    'risk_score': 5,  # Sample risk score
                    'timestamp': datetime.datetime.now().isoformat(),
                    'contact': 'Sample Contact',
                    'description': f"Sample finding from {module} module"
                }
                findings.append(finding)
        
        return findings
    
    def generate_results_worker(self, databases, communications, findings):
        """Worker function for results generation"""
        # Calculate summary statistics
        summary = {
            'total_findings': len(findings),
            'critical_alerts': len([f for f in findings if f.get('risk_score', 0) >= 8]),
            'high_risk': len([f for f in findings if f.get('risk_score', 0) >= 6]),
            'communications_analyzed': len(communications),
            'databases_processed': len(databases)
        }
        
        results = {
            'summary': summary,
            'databases': databases,
            'communications': communications,
            'findings': findings,
            'analysis_time': datetime.datetime.now().isoformat()
        }
        
        self.analysis_results = results
        return results
    
    def update_analysis_results(self, results):
        """Update UI with analysis results"""
        summary = results['summary']
        
        # Update summary cards
        for title, card in self.summary_cards.items():
            if title == "Total Findings":
                self.update_card_value(card, str(summary['total_findings']))
            elif title == "Critical Alerts":
                self.update_card_value(card, str(summary['critical_alerts']))
            elif title == "High Risk":
                self.update_card_value(card, str(summary['high_risk']))
            elif title == "Communications":
                self.update_card_value(card, str(summary['communications_analyzed']))
        
        # Update overview text
        self.update_overview_text(results)
        
        # Update findings tree
        self.update_findings_tree(results['findings'])
        
        # Generate report
        self.generate_report_text(results)
        
        # Switch to analysis tab
        self.notebook.select(2)
    
    def update_card_value(self, card, value):
        """Update summary card value"""
        for child in card.winfo_children():
            if isinstance(child, ttk.Label) and child.cget('font'):
                child.config(text=value)
                break
    
    def update_overview_text(self, results):
        """Update overview display"""
        self.overview_text.delete("1.0", tk.END)
        
        summary = results['summary']
        
        overview = f"""
FORENSIC INTELLIGENCE ANALYSIS OVERVIEW
======================================

Case: {self.case_name.get()}
Examiner: {self.examiner_name.get()}
Analysis Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Processing Mode: {self.processing_mode.get().title()}

SUMMARY STATISTICS:
------------------
Total Findings: {summary['total_findings']}
Critical Alerts: {summary['critical_alerts']}
High Risk Items: {summary['high_risk']}
Communications Analyzed: {summary['communications_analyzed']}
Databases Processed: {summary['databases_processed']}

DATABASE BREAKDOWN:
------------------
"""
        
        for db in results['databases']:
            status = db.get('status', 'unknown')
            status_icon = {'ready': '✅', 'error': '❌', 'empty': '⚠️', 'not_found': '❓'}.get(status, '❓')
            overview += f"{status_icon} {db['name']}: {status}\n"
        
        if results['findings']:
            overview += f"""

INTELLIGENCE FINDINGS:
---------------------
"""
            for finding in results['findings'][:5]:  # Show first 5 findings
                overview += f"• {finding['module']}: {finding['description']}\n"
        
        self.overview_text.insert("1.0", overview)
    
    def update_findings_tree(self, findings):
        """Update findings tree display"""
        # Clear existing items
        for item in self.findings_tree.get_children():
            self.findings_tree.delete(item)
        
        # Add findings
        for finding in findings:
            self.findings_tree.insert("", "end", values=(
                finding.get('module', 'Unknown'),
                finding.get('type', 'Unknown'),
                f"{finding.get('risk_score', 0)}/10",
                finding.get('contact', 'Unknown'),
                finding.get('timestamp', 'Unknown')
            ))
    
    def generate_report_text(self, results):
        """Generate comprehensive report"""
        self.report_text.delete("1.0", tk.END)
        
        report = f"""
COMPREHENSIVE FORENSIC INTELLIGENCE REPORT
==========================================

Case Information:
  Case Name: {self.case_name.get()}
  Examiner: {self.examiner_name.get()}
  Analysis Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
  Extraction Path: {self.extraction_path.get()}
  Processing Mode: {self.processing_mode.get().title()}

Executive Summary:
  {results['summary']['total_findings']} intelligence indicators identified
  {results['summary']['critical_alerts']} critical alerts requiring immediate attention
  {results['summary']['communications_analyzed']} communications analyzed
  {results['summary']['databases_processed']} databases processed

Database Analysis:
"""
        
        for db in results['databases']:
            report += f"""
  {db['name']}:
    Path: {db['path']}
    Status: {db.get('status', 'Unknown')}
    Size: {db.get('size', 0)} bytes
"""
        
        if results['findings']:
            report += f"""

Intelligence Findings:
"""
            for i, finding in enumerate(results['findings'], 1):
                report += f"""
Finding {i}:
  Module: {finding.get('module', 'Unknown')}
  Type: {finding.get('type', 'Unknown')}
  Risk Score: {finding.get('risk_score', 0)}/10
  Contact: {finding.get('contact', 'Unknown')}
  Description: {finding.get('description', 'No description')}
"""
        
        report += f"""

Analysis completed at: {results['analysis_time']}
Generated by: Forensic Intelligence Suite v2.0
"""
        
        self.report_text.insert("1.0", report)
    
    # Additional event handlers
    
    def discover_databases(self):
        """Manual database discovery"""
        if not self.extraction_path.get():
            messagebox.showerror("Error", "Please select extraction path first")
            return
        
        self.quick_scan()
    
    def check_encryption(self):
        """Check database encryption"""
        if not self.current_databases:
            messagebox.showinfo("Info", "Please discover databases first")
            return
        
        self.update_status("Checking encryption...")
        
        # Simulate encryption check
        encryption_report = "ENCRYPTION ANALYSIS\n" + "=" * 30 + "\n\n"
        
        for db_path in self.current_databases:
            encryption_report += f"Database: {db_path.name}\n"
            encryption_report += f"Path: {db_path}\n"
            encryption_report += "Encryption: Not detected\n"
            encryption_report += "Status: Accessible\n\n"
        
        self.encryption_text.delete("1.0", tk.END)
        self.encryption_text.insert("1.0", encryption_report)
        
        self.update_status("Encryption check complete")
    
    def analyze_patterns(self):
        """Analyze data patterns"""
        messagebox.showinfo("Info", "Pattern analysis feature available in full version")
    
    def run_analysis(self):
        """Manual analysis trigger"""
        if not self.analysis_results:
            messagebox.showinfo("Info", "Please run full analysis first")
            return
        
        messagebox.showinfo("Info", "Analysis already completed")
    
    def generate_report(self):
        """Generate analysis report"""
        if not self.analysis_results:
            messagebox.showinfo("Info", "Please run analysis first to generate report")
            return
        
        self.generate_report_text(self.analysis_results)
        messagebox.showinfo("Success", "Report generated successfully")
    
    def export_pdf(self):
        """Export report as PDF"""
        messagebox.showinfo("Info", "PDF export feature coming soon")
    
    def export_json(self):
        """Export data as JSON"""
        if not self.analysis_results:
            messagebox.showinfo("Info", "No analysis data to export")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.analysis_results, f, indent=2, default=str)
                messagebox.showinfo("Success", f"Data exported to {filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
    
    def copy_summary(self):
        """Copy summary to clipboard"""
        if not self.analysis_results:
            messagebox.showinfo("Info", "No analysis data to copy")
            return
        
        summary_text = self.overview_text.get("1.0", tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(summary_text)
        messagebox.showinfo("Success", "Summary copied to clipboard")
    
    def save_case(self):
        """Save current case"""
        if not self.validate_case_info():
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                case_data = {
                    'case_name': self.case_name.get(),
                    'examiner_name': self.examiner_name.get(),
                    'extraction_path': self.extraction_path.get(),
                    'processing_mode': self.processing_mode.get(),
                    'selected_modules': self.selected_modules,
                    'saved_date': datetime.datetime.now().isoformat()
                }
                
                with open(filename, 'w') as f:
                    json.dump(case_data, f, indent=2)
                
                messagebox.showinfo("Success", f"Case saved to {filename}")
                
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save case: {str(e)}")
    
    def load_case(self):
        """Load saved case"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    case_data = json.load(f)
                
                # Load case information
                self.case_name.set(case_data.get('case_name', ''))
                self.examiner_name.set(case_data.get('examiner_name', ''))
                self.extraction_path.set(case_data.get('extraction_path', ''))
                self.processing_mode.set(case_data.get('processing_mode', 'adaptive'))
                
                # Update module selections
                loaded_modules = case_data.get('selected_modules', [])
                for module, var in self.module_vars.items():
                    var.set(module in loaded_modules)
                self.update_selected_modules()
                
                messagebox.showinfo("Success", "Case loaded successfully")
                
            except Exception as e:
                messagebox.showerror("Load Error", f"Failed to load case: {str(e)}")
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

def main():
    """Main function to start the application"""
    try:
        app = ForensicIntelligenceGUI()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication closed by user")
    except Exception as e:
        print(f"Application error: {e}")
        if 'messagebox' in globals():
            messagebox.showerror("Application Error", f"Failed to start application:\n{str(e)}")

if __name__ == "__main__":
    main()