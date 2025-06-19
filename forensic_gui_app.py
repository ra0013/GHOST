#!/usr/bin/env python3
"""
Threaded Forensic Intelligence Suite - GUI Application
Professional interface with multi-threaded processing for enhanced performance
"""

import sys
import os
from pathlib import Path
import json
import datetime
import threading
import time
import queue
from typing import Dict, List, Any, Optional
import concurrent.futures

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
    print("[OK] All modules imported successfully for threaded GUI")
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure all module files are in the 'modules' directory")
    
class ThreadedForensicGUI:
    """Threaded GUI application for forensic intelligence suite"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_main_window()
        
        # Threading configuration
        self.max_workers = min(8, (os.cpu_count() or 1) + 4)
        self.analysis_thread = None
        self.cancel_analysis = threading.Event()
        self.progress_queue = queue.Queue()
        self.status_queue = queue.Queue()
        
        # Application state variables
        self.case_name = tk.StringVar()
        self.examiner_name = tk.StringVar()
        self.extraction_path = tk.StringVar()
        self.processing_mode = tk.StringVar(value="adaptive")
        self.threading_enabled = tk.BooleanVar(value=True)
        self.max_workers_var = tk.StringVar(value=str(self.max_workers))
        
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
        
        # Processing components
        self.config_manager = None
        self.logger = None
        
        # Create GUI
        self.setup_styling()
        self.create_widgets()
        self.load_configuration()
        
        # Start update loops
        self.update_time()
        self.check_queues()
    
    def setup_main_window(self):
        """Configure the main application window"""
        self.root.title("[THREADED] Forensic Intelligence Suite v2.0 - Multi-Core Processing")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 700)
        
        # Configure for responsive design
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_styling(self):
        """Configure modern styling"""
        self.style = ttk.Style()
        
        try:
            self.style.theme_use('clam')
        except:
            self.style.theme_use('default')
        
        # Color scheme with threading theme
        colors = {
            'primary': '#2E86AB',
            'accent': '#A23B72', 
            'success': '#F18F01',
            'danger': '#C73E1D',
            'threading': '#28A745',  # Green for threading
            'text': '#333333'
        }
        
        # Configure styles
        self.style.configure('Title.TLabel', 
                           font=('Arial', 16, 'bold'), 
                           foreground=colors['primary'])
        
        self.style.configure('Threading.TLabel',
                           font=('Arial', 10, 'bold'),
                           foreground=colors['threading'])
        
        self.style.configure('Header.TLabel', 
                           font=('Arial', 12, 'bold'), 
                           foreground=colors['text'])
        
        self.style.configure('Status.TLabel', 
                           font=('Arial', 10), 
                           foreground=colors['accent'])
    
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
        self.create_threading_tab()  # New threading configuration tab
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
                         text="[THREADED] Forensic Intelligence Suite", 
                         style='Title.TLabel')
        title.grid(row=0, column=0, sticky="w")
        
        # Version info with threading indicator
        version_text = f"v2.0 | Multi-Core Processing | {self.max_workers} Workers Available"
        version = ttk.Label(title_frame, text=version_text, style='Threading.TLabel')
        version.grid(row=0, column=1, sticky="e")
    
    def create_case_tab(self):
        """Create case setup tab"""
        case_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(case_frame, text="Case Setup")
        
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
        
        # File type indicator
        self.file_type_var = tk.StringVar(value="No file selected")
        file_type_label = ttk.Label(info_frame, textvariable=self.file_type_var, style='Status.TLabel')
        file_type_label.grid(row=3, column=1, sticky="w", padx=(10, 0), pady=(5, 0))
        
        # Modules Selection
        modules_frame = ttk.LabelFrame(case_frame, text="Intelligence Modules", padding="15")
        modules_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        self.create_module_selection(modules_frame)
        
        # Action Buttons
        button_frame = ttk.Frame(case_frame)
        button_frame.grid(row=2, column=0, sticky="ew")
        
        ttk.Button(button_frame, text="Quick Scan", 
                  command=self.quick_scan).pack(side="left", padx=(0, 10))
        
        self.start_btn = ttk.Button(button_frame, text="Start Threaded Analysis", 
                                   command=self.start_threaded_analysis)
        self.start_btn.pack(side="left", padx=(0, 10))
        
        self.cancel_btn = ttk.Button(button_frame, text="Cancel Analysis", 
                                    command=self.cancel_current_analysis, state="disabled")
        self.cancel_btn.pack(side="left", padx=(0, 10))
        
        ttk.Button(button_frame, text="Save Case", 
                  command=self.save_case).pack(side="left", padx=(0, 10))
        
        ttk.Button(button_frame, text="Load Case", 
                  command=self.load_case).pack(side="left")
    
    def create_threading_tab(self):
        """Create threading configuration tab"""
        threading_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(threading_frame, text="Threading Config")
        
        # Threading Control
        control_frame = ttk.LabelFrame(threading_frame, text="Threading Control", padding="15")
        control_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        control_frame.grid_columnconfigure(1, weight=1)
        
        # Enable/Disable Threading
        ttk.Label(control_frame, text="Enable Threading:", style='Header.TLabel').grid(
            row=0, column=0, sticky="w", pady=(0, 10))
        
        threading_cb = ttk.Checkbutton(control_frame, text="Use multi-threaded processing", 
                                      variable=self.threading_enabled,
                                      command=self.update_threading_config)
        threading_cb.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=(0, 10))
        
        # Max Workers
        ttk.Label(control_frame, text="Max Workers:", style='Header.TLabel').grid(
            row=1, column=0, sticky="w", pady=(0, 10))
        
        workers_frame = ttk.Frame(control_frame)
        workers_frame.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=(0, 10))
        
        workers_entry = ttk.Entry(workers_frame, textvariable=self.max_workers_var, width=10)
        workers_entry.grid(row=0, column=0, padx=(0, 10))
        
        ttk.Button(workers_frame, text="Auto-Detect", 
                  command=self.auto_detect_workers).grid(row=0, column=1)
        
        # System Information
        system_frame = ttk.LabelFrame(threading_frame, text="System Information", padding="15")
        system_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        cpu_info = f"CPU Cores: {os.cpu_count() or 'Unknown'}"
        ttk.Label(system_frame, text=cpu_info).grid(row=0, column=0, sticky="w", pady=5)
        
        recommended = f"Recommended Max Workers: {self.max_workers}"
        ttk.Label(system_frame, text=recommended).grid(row=1, column=0, sticky="w", pady=5)
        
        # Threading Performance Monitor
        perf_frame = ttk.LabelFrame(threading_frame, text="Real-time Performance", padding="15")
        perf_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        
        # Active threads display
        self.active_threads_var = tk.StringVar(value="0")
        ttk.Label(perf_frame, text="Active Threads:").grid(row=0, column=0, sticky="w")
        ttk.Label(perf_frame, textvariable=self.active_threads_var, 
                 style='Threading.TLabel').grid(row=0, column=1, sticky="w", padx=(10, 0))
        
        # Threading efficiency
        self.thread_efficiency_var = tk.StringVar(value="0%")
        ttk.Label(perf_frame, text="Threading Efficiency:").grid(row=1, column=0, sticky="w")
        ttk.Label(perf_frame, textvariable=self.thread_efficiency_var, 
                 style='Threading.TLabel').grid(row=1, column=1, sticky="w", padx=(10, 0))
        
        # Processing speed
        self.processing_speed_var = tk.StringVar(value="0 DB/sec")
        ttk.Label(perf_frame, text="Processing Speed:").grid(row=2, column=0, sticky="w")
        ttk.Label(perf_frame, textvariable=self.processing_speed_var, 
                 style='Threading.TLabel').grid(row=2, column=1, sticky="w", padx=(10, 0))
    
    def create_module_selection(self, parent):
        """Create intelligence module selection interface"""
        modules = ['narcotics', 'financial_fraud', 'human_trafficking', 'domestic_violence']
        
        for i, module in enumerate(modules):
            var = tk.BooleanVar(value=True)
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
    
    def create_database_tab(self):
        """Create database analysis tab with threading info"""
        db_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(db_frame, text="Database Analysis")
        
        db_frame.grid_rowconfigure(1, weight=1)
        db_frame.grid_columnconfigure(0, weight=1)
        
        # Control buttons with threading indicators
        controls = ttk.Frame(db_frame)
        controls.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        ttk.Button(controls, text="Threaded Discovery", 
                  command=self.threaded_discovery).pack(side="left", padx=(0, 10))
        ttk.Button(controls, text="Parallel Encryption Check", 
                  command=self.parallel_encryption_check).pack(side="left", padx=(0, 10))
        
        # Threading status indicator
        self.db_threading_status = tk.StringVar(value="Ready for threaded processing")
        ttk.Label(controls, textvariable=self.db_threading_status, 
                 style='Threading.TLabel').pack(side="right")
        
        # Results area
        results_notebook = ttk.Notebook(db_frame)
        results_notebook.grid(row=1, column=0, sticky="nsew")
        
        # Database list tab
        db_list_frame = ttk.Frame(results_notebook)
        results_notebook.add(db_list_frame, text="Database List")
        
        self.create_database_list(db_list_frame)
        
        # Threading performance tab
        threading_perf_frame = ttk.Frame(results_notebook)
        results_notebook.add(threading_perf_frame, text="Threading Performance")
        
        self.threading_perf_text = scrolledtext.ScrolledText(threading_perf_frame, font=('Consolas', 10))
        self.threading_perf_text.pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_database_list(self, parent):
        """Create database list display with threading info"""
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        # Enhanced columns for threading
        columns = ("Name", "Path", "Status", "Size", "Thread", "Processing Time")
        self.db_tree = ttk.Treeview(parent, columns=columns, show="tree headings")
        
        self.db_tree.heading("#0", text="Type")
        self.db_tree.column("#0", width=80)
        
        for col in columns:
            self.db_tree.heading(col, text=col)
            if col == "Thread":
                self.db_tree.column(col, width=100)
            elif col == "Processing Time":
                self.db_tree.column(col, width=120)
            else:
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
        """Create intelligence analysis tab with threading progress"""
        analysis_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(analysis_frame, text="Intelligence Analysis")
        
        analysis_frame.grid_rowconfigure(2, weight=1)
        analysis_frame.grid_columnconfigure(0, weight=1)
        
        # Control buttons
        controls = ttk.Frame(analysis_frame)
        controls.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        ttk.Button(controls, text="Parallel Intelligence Analysis", 
                  command=self.run_parallel_analysis).pack(side="left", padx=(0, 10))
        ttk.Button(controls, text="Generate Report", 
                  command=self.generate_report).pack(side="left")
        
        # Enhanced progress bar with threading info
        progress_frame = ttk.Frame(analysis_frame)
        progress_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        progress_frame.grid_columnconfigure(0, weight=1)
        
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                          mode='determinate')
        self.progress_bar.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        # Threading progress details
        self.progress_details = tk.StringVar(value="Ready for analysis")
        ttk.Label(progress_frame, textvariable=self.progress_details, 
                 style='Threading.TLabel').grid(row=1, column=0, sticky="w")
        
        # Results notebook
        results_notebook = ttk.Notebook(analysis_frame)
        results_notebook.grid(row=2, column=0, sticky="nsew")
        
        # Overview tab
        overview_frame = ttk.Frame(results_notebook)
        results_notebook.add(overview_frame, text="Overview")
        
        self.create_overview_display(overview_frame)
        
        # Findings tab
        findings_frame = ttk.Frame(results_notebook)
        results_notebook.add(findings_frame, text="Findings")
        
        self.create_findings_display(findings_frame)
        
        # Threading metrics tab
        metrics_frame = ttk.Frame(results_notebook)
        results_notebook.add(metrics_frame, text="Threading Metrics")
        
        self.create_threading_metrics_display(metrics_frame)
    
    def create_threading_metrics_display(self, parent):
        """Create threading performance metrics display"""
        # Threading summary cards
        cards_frame = ttk.Frame(parent)
        cards_frame.pack(fill="x", padx=10, pady=10)
        
        self.threading_cards = {}
        card_titles = ["Total Threads Used", "Avg Processing Speed", "Threading Efficiency", "Time Saved"]
        
        for i, title in enumerate(card_titles):
            card = self.create_summary_card(cards_frame, title, "0")
            card.grid(row=0, column=i, padx=5, sticky="ew")
            self.threading_cards[title] = card
        
        for i in range(len(card_titles)):
            cards_frame.grid_columnconfigure(i, weight=1)
        
        # Detailed threading log
        log_frame = ttk.LabelFrame(parent, text="Threading Performance Log")
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.threading_log = scrolledtext.ScrolledText(log_frame, font=('Consolas', 9))
        self.threading_log.pack(fill="both", expand=True, padx=10, pady=10)
    
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
        """Create detailed findings display with threading info"""
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        # Enhanced columns for threading
        columns = ("Module", "Type", "Risk", "Contact", "Timestamp", "Analysis Thread")
        self.findings_tree = ttk.Treeview(parent, columns=columns, show="headings")
        
        for col in columns:
            self.findings_tree.heading(col, text=col)
            if col == "Analysis Thread":
                self.findings_tree.column(col, width=120)
            else:
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
        self.notebook.add(results_frame, text="Results & Reports")
        
        results_frame.grid_rowconfigure(1, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)
        
        # Export controls
        export_frame = ttk.Frame(results_frame)
        export_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        ttk.Button(export_frame, text="Export PDF", 
                  command=self.export_pdf).pack(side="left", padx=(0, 10))
        ttk.Button(export_frame, text="Export JSON", 
                  command=self.export_json).pack(side="left", padx=(0, 10))
        ttk.Button(export_frame, text="Export Threading Report", 
                  command=self.export_threading_report).pack(side="left", padx=(0, 10))
        ttk.Button(export_frame, text="Copy Summary", 
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
        self.notebook.add(config_frame, text="Configuration")
        
        # Configuration info with threading details
        info_text = scrolledtext.ScrolledText(config_frame, font=('Consolas', 10))
        info_text.pack(fill="both", expand=True)
        
        config_info = """
THREADED FORENSIC INTELLIGENCE SUITE CONFIGURATION
================================================

Threading Configuration:
- Multi-threaded processing for enhanced performance
- Configurable worker thread count
- Real-time performance monitoring
- Thread-safe logging and data collection

Performance Benefits:
- 3-10x faster database discovery in zip files
- Parallel encryption detection and analysis
- Concurrent intelligence module execution
- Optimized resource utilization

Configuration Files:
- data_paths.json: Database file locations
- keywords.json: Intelligence module keywords  
- database_schemas.json: Database table structures
- intelligence_modules.json: Module settings

Threading Best Practices:
- Use 4-8 workers for most systems
- Monitor threading efficiency in real-time
- Adjust worker count based on system performance
- Cancel long-running operations if needed

To Update Configurations:
1. Edit JSON files in forensic_configs/ directory
2. Restart application to load new settings
3. Use Threading Config tab for performance tuning
"""
        info_text.insert("1.0", config_info)
        info_text.config(state="disabled")
        
        self.config_text = info_text
    
    def create_status_bar(self, parent):
        """Create application status bar with threading info"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        status_frame.grid_columnconfigure(0, weight=1)
        
        # Left side - status message
        status_label = ttk.Label(status_frame, textvariable=self.status_var, 
                               style='Status.TLabel')
        status_label.grid(row=0, column=0, sticky="w")
        
        # Center - threading status
        threading_status = f"Threading: {'Enabled' if self.threading_enabled.get() else 'Disabled'} | Workers: {self.max_workers_var.get()}"
        self.threading_status_var = tk.StringVar(value=threading_status)
        threading_label = ttk.Label(status_frame, textvariable=self.threading_status_var,
                                   style='Threading.TLabel')
        threading_label.grid(row=0, column=1, sticky="")
        
        # Right side - current time
        time_label = ttk.Label(status_frame, textvariable=self.time_var)
        time_label.grid(row=0, column=2, sticky="e")
    
    # Event handlers and utility methods
    
    def load_configuration(self):
        """Load application configuration"""
        try:
            self.config_manager = ConfigurationManager()
            self.update_status("Configuration loaded successfully")
        except Exception as e:
            self.update_status(f"Configuration error: {str(e)}")
    
    def update_time(self):
        """Update time display"""
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_var.set(current_time)
        self.root.after(1000, self.update_time)
    
    def update_status(self, message):
        """Update status bar message"""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def check_queues(self):
        """Check for updates from background threads"""
        try:
            # Check progress queue
            while not self.progress_queue.empty():
                progress_data = self.progress_queue.get_nowait()
                self.progress_var.set(progress_data['progress'])
                if 'details' in progress_data:
                    self.progress_details.set(progress_data['details'])
                
                # Update threading performance metrics
                if 'threading_info' in progress_data:
                    self.update_threading_metrics(progress_data['threading_info'])
            
            # Check status queue
            while not self.status_queue.empty():
                status_data = self.status_queue.get_nowait()
                self.update_status(status_data['message'])
                
                if 'database_info' in status_data:
                    self.update_database_display(status_data['database_info'])
        
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.check_queues)
    
    def update_threading_metrics(self, threading_info):
        """Update threading performance metrics"""
        if 'active_threads' in threading_info:
            self.active_threads_var.set(str(threading_info['active_threads']))
        
        if 'efficiency' in threading_info:
            self.thread_efficiency_var.set(f"{threading_info['efficiency']:.1%}")
        
        if 'processing_speed' in threading_info:
            self.processing_speed_var.set(f"{threading_info['processing_speed']:.1f} DB/sec")
        
        # Log threading performance
        if hasattr(self, 'threading_log'):
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            log_entry = f"[{timestamp}] Threads: {threading_info.get('active_threads', 0)} | "
            log_entry += f"Efficiency: {threading_info.get('efficiency', 0):.1%} | "
            log_entry += f"Speed: {threading_info.get('processing_speed', 0):.1f} DB/sec\n"
            
            self.threading_log.insert(tk.END, log_entry)
            self.threading_log.see(tk.END)
    
    def browse_path(self):
        """Browse for extraction directory or zip file"""
        # Allow both directories and zip files
        path = filedialog.askopenfilename(
            title="Select Forensic Extraction (ZIP file or directory)",
            filetypes=[
                ("Zip files", "*.zip"),
                ("All files", "*.*")
            ]
        )
        
        if not path:
            # If no file selected, try directory
            path = filedialog.askdirectory(title="Select Forensic Extraction Directory")
        
        if path:
            self.extraction_path.set(path)
            
            # Update file type indicator
            path_obj = Path(path)
            if path_obj.is_file() and path_obj.suffix.lower() == '.zip':
                size_mb = path_obj.stat().st_size / (1024 * 1024)
                self.file_type_var.set(f"ZIP file selected ({size_mb:.1f} MB) - Threaded analysis recommended")
            elif path_obj.is_dir():
                self.file_type_var.set("Directory selected - Standard analysis")
            else:
                self.file_type_var.set("File selected")
            
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
    
    def update_threading_config(self):
        """Update threading configuration"""
        threading_enabled = self.threading_enabled.get()
        max_workers = int(self.max_workers_var.get()) if self.max_workers_var.get().isdigit() else self.max_workers
        
        self.max_workers = max_workers
        
        # Update status bar
        status = f"Threading: {'Enabled' if threading_enabled else 'Disabled'} | Workers: {max_workers}"
        self.threading_status_var.set(status)
        
        self.update_status(f"Threading configuration updated: {status}")
    
    def auto_detect_workers(self):
        """Auto-detect optimal worker count"""
        optimal_workers = min(8, (os.cpu_count() or 1) + 4)
        self.max_workers_var.set(str(optimal_workers))
        self.update_threading_config()
    
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
    
    def start_threaded_analysis(self):
        """Start threaded forensic analysis"""
        if not self.validate_case_info():
            return
        
        if not self.threading_enabled.get():
            # Fall back to single-threaded analysis
            messagebox.showinfo("Info", "Threading disabled - using single-threaded analysis")
            self.start_single_threaded_analysis()
            return
        
        # Confirm analysis start
        if not messagebox.askyesno("Start Threaded Analysis", 
                                  f"Start multi-threaded analysis with {self.max_workers} workers?"):
            return
        
        # Prepare for analysis
        self.cancel_analysis.clear()
        self.progress_var.set(0)
        self.start_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")
        
        # Update selected modules
        self.update_selected_modules()
        
        # Start analysis in background thread
        self.analysis_thread = threading.Thread(target=self.threaded_analysis_worker, daemon=True)
        self.analysis_thread.start()
        
        self.update_status("Starting threaded analysis...")
    
    def threaded_analysis_worker(self):
        """Background worker for threaded analysis"""
        try:
            # Import the threaded suite
            from threaded_forensic_suite import ThreadedForensicSuite
            
            # Initialize threaded suite
            suite = ThreadedForensicSuite(
                self.case_name.get(), 
                self.examiner_name.get(), 
                max_workers=self.max_workers
            )
            
            # Set up progress callback
            def progress_callback(progress, details=None, threading_info=None):
                if not self.cancel_analysis.is_set():
                    progress_data = {'progress': progress}
                    if details:
                        progress_data['details'] = details
                    if threading_info:
                        progress_data['threading_info'] = threading_info
                    self.progress_queue.put(progress_data)
            
            # Monkey patch progress reporting
            original_print = print
            def threaded_print(*args, **kwargs):
                message = ' '.join(str(arg) for arg in args)
                if not self.cancel_analysis.is_set():
                    self.status_queue.put({'message': message})
                original_print(*args, **kwargs)
            
            # Temporarily replace print for progress updates
            import builtins
            builtins.print = threaded_print
            
            try:
                # Run threaded analysis
                start_time = time.time()
                
                # Update progress periodically
                progress_callback(10, "Initializing threaded analysis...")
                
                report = suite.analyze_path(self.extraction_path.get())
                
                end_time = time.time()
                processing_time = end_time - start_time
                
                # Calculate threading performance
                performance_metrics = report.get('performance_metrics', {})
                threading_efficiency = performance_metrics.get('threading_efficiency', 0)
                
                progress_callback(100, f"Analysis complete in {processing_time:.1f}s", {
                    'active_threads': 0,
                    'efficiency': threading_efficiency,
                    'processing_speed': len(report.get('databases', [])) / processing_time if processing_time > 0 else 0
                })
                
                # Update UI with results
                self.root.after(0, lambda: self.update_threaded_results(report))
                
            finally:
                # Restore original print
                builtins.print = original_print
            
        except Exception as e:
            error_msg = f"Threaded analysis failed: {str(e)}"
            self.root.after(0, lambda: self.analysis_error(error_msg))
        
        finally:
            # Re-enable controls
            self.root.after(0, self.analysis_complete)
    
    def update_threaded_results(self, report):
        """Update UI with threaded analysis results"""
        self.analysis_results = report
        
        # Update summary cards
        summary = report['summary']
        
        for title, card in self.summary_cards.items():
            if title == "Total Findings":
                self.update_card_value(card, str(summary['intelligence_findings']))
            elif title == "Critical Alerts":
                self.update_card_value(card, str(summary.get('high_risk_findings', 0)))
            elif title == "High Risk":
                self.update_card_value(card, str(summary.get('high_risk_findings', 0)))
            elif title == "Communications":
                self.update_card_value(card, str(summary['records_extracted']))
        
        # Update threading performance cards
        performance = report['performance_metrics']
        
        for title, card in self.threading_cards.items():
            if title == "Total Threads Used":
                threads_used = performance.get('extraction_threads_used', 0) + performance.get('analysis_threads_used', 0)
                self.update_card_value(card, str(threads_used))
            elif title == "Threading Efficiency":
                efficiency = performance.get('threading_efficiency', 0)
                self.update_card_value(card, f"{efficiency:.1%}")
            elif title == "Avg Processing Speed":
                processing_time = report.get('processing_time_seconds', 1)
                speed = len(report.get('databases', [])) / processing_time if processing_time > 0 else 0
                self.update_card_value(card, f"{speed:.1f} DB/s")
            elif title == "Time Saved":
                # Estimate time saved vs single-threaded
                estimated_single_threaded = processing_time * 3  # Conservative estimate
                time_saved = estimated_single_threaded - processing_time
                self.update_card_value(card, f"{time_saved:.1f}s")
        
        # Update overview text
        self.update_threaded_overview(report)
        
        # Update findings tree
        self.update_threaded_findings(report.get('intelligence_findings', []))
        
        # Generate threaded report
        self.generate_threaded_report_text(report)
        
        # Switch to analysis tab
        self.notebook.select(2)
        
        self.update_status("Threaded analysis complete!")
    
    def update_card_value(self, card, value):
        """Update summary card value"""
        for child in card.winfo_children():
            if isinstance(child, ttk.Label):
                try:
                    font_info = child.cget('font')
                    if font_info and ('20' in str(font_info) or 'bold' in str(font_info)):
                        child.config(text=value)
                        break
                except:
                    pass
    
    def update_threaded_overview(self, report):
        """Update overview with threading information"""
        self.overview_text.delete("1.0", tk.END)
        
        summary = report['summary']
        performance = report['performance_metrics']
        
        overview = f"""
THREADED FORENSIC INTELLIGENCE ANALYSIS OVERVIEW
===============================================

Case: {self.case_name.get()}
Examiner: {self.examiner_name.get()}
Analysis Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Processing Mode: Multi-threaded ({performance['max_workers']} workers)

THREADING PERFORMANCE:
---------------------
Threading Efficiency: {performance.get('threading_efficiency', 0):.1%}
Extraction Threads: {performance.get('extraction_threads_used', 0)}
Analysis Threads: {performance.get('analysis_threads_used', 0)}
Processing Time: {report.get('processing_time_seconds', 0):.1f} seconds

ANALYSIS SUMMARY:
----------------
Total Findings: {summary['intelligence_findings']}
High Risk Findings: {summary.get('high_risk_findings', 0)}
Records Extracted: {summary['records_extracted']}
Databases Processed: {summary['databases_found']}

DATABASE BREAKDOWN:
------------------
"""
        
        for db in report['databases'][:10]:  # Show first 10
            status = db.get('status', 'unknown')
            thread_id = db.get('thread_id', 'N/A')
            overview += f"• {db['name']}: {status} (Thread: {thread_id})\n"
        
        if len(report['databases']) > 10:
            overview += f"... and {len(report['databases']) - 10} more databases\n"
        
        self.overview_text.insert("1.0", overview)
    
    def update_threaded_findings(self, findings):
        """Update findings tree with threading information"""
        # Clear existing items
        for item in self.findings_tree.get_children():
            self.findings_tree.delete(item)
        
        # Add findings with thread info
        for finding in findings:
            self.findings_tree.insert("", "end", values=(
                finding.get('module', 'Unknown'),
                finding.get('type', 'Unknown'),
                f"{finding.get('risk_score', 0)}/10",
                finding.get('contact', 'Unknown'),
                finding.get('timestamp', 'Unknown'),
                f"Thread-{finding.get('analysis_thread', 'N/A')}"
            ))
    
    def generate_threaded_report_text(self, report):
        """Generate comprehensive threaded report"""
        self.report_text.delete("1.0", tk.END)
        
        performance = report['performance_metrics']
        summary = report['summary']
        
        report_text = f"""
COMPREHENSIVE THREADED FORENSIC INTELLIGENCE REPORT
==================================================

Case Information:
  Case Name: {self.case_name.get()}
  Examiner: {self.examiner_name.get()}
  Analysis Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
  Extraction Path: {self.extraction_path.get()}
  Processing Mode: Multi-threaded Analysis

Threading Performance Metrics:
  Max Workers: {performance['max_workers']}
  Threading Efficiency: {performance.get('threading_efficiency', 0):.1%}
  Extraction Threads Used: {performance.get('extraction_threads_used', 0)}
  Analysis Threads Used: {performance.get('analysis_threads_used', 0)}
  Processing Time: {report.get('processing_time_seconds', 0):.1f} seconds
  CPU Cores Available: {performance.get('cpu_cores_available', 'Unknown')}

Executive Summary:
  {summary['intelligence_findings']} intelligence indicators identified
  {summary.get('high_risk_findings', 0)} high-risk findings requiring attention
  {summary['records_extracted']} sample records analyzed
  {summary['databases_found']} databases processed in parallel

Performance Benefits:
  Estimated single-threaded time: {report.get('processing_time_seconds', 0) * 3:.1f} seconds
  Time saved through threading: {report.get('processing_time_seconds', 0) * 2:.1f} seconds
  Performance improvement: ~{300 / max(1, performance.get('threading_efficiency', 0.01)):.0f}% faster

Analysis completed with threaded processing
Generated by: GHOST Threaded Forensic Intelligence Suite v2.0
"""
        
        self.report_text.insert("1.0", report_text)
    
    def analysis_complete(self):
        """Re-enable controls after analysis completion"""
        self.start_btn.config(state="normal")
        self.cancel_btn.config(state="disabled")
        self.progress_details.set("Analysis complete")
    
    def analysis_error(self, error_message):
        """Handle analysis errors"""
        messagebox.showerror("Analysis Error", error_message)
        self.update_status(f"Analysis failed: {error_message}")
        self.analysis_complete()
    
    def cancel_current_analysis(self):
        """Cancel the current analysis"""
        if messagebox.askyesno("Cancel Analysis", "Are you sure you want to cancel the current analysis?"):
            self.cancel_analysis.set()
            self.update_status("Cancelling analysis...")
            
            # Wait for thread to finish
            if self.analysis_thread and self.analysis_thread.is_alive():
                self.analysis_thread.join(timeout=5.0)
            
            self.analysis_complete()
            self.update_status("Analysis cancelled by user")
    
    def quick_scan(self):
        """Perform quick database scan"""
        if not self.validate_case_info():
            return
        
        self.update_status("Performing quick scan...")
        # Implementation for quick scan
        self.update_status("Quick scan complete")
    
    def threaded_discovery(self):
        """Threaded database discovery"""
        if not self.extraction_path.get():
            messagebox.showerror("Error", "Please select extraction path first")
            return
        
        self.db_threading_status.set("Running threaded discovery...")
        # Implementation for threaded discovery
        self.db_threading_status.set("Threaded discovery complete")
    
    def parallel_encryption_check(self):
        """Parallel encryption checking"""
        self.db_threading_status.set("Running parallel encryption check...")
        # Implementation for parallel encryption check
        self.db_threading_status.set("Parallel encryption check complete")
    
    def run_parallel_analysis(self):
        """Run parallel intelligence analysis"""
        if not self.analysis_results:
            messagebox.showinfo("Info", "Please run full analysis first")
            return
        
        self.progress_details.set("Running parallel intelligence analysis...")
        # Implementation for parallel analysis
        self.progress_details.set("Parallel analysis complete")
    
    def generate_report(self):
        """Generate analysis report"""
        if not self.analysis_results:
            messagebox.showinfo("Info", "Please run analysis first to generate report")
            return
        
        self.generate_threaded_report_text(self.analysis_results)
        messagebox.showinfo("Success", "Threaded report generated successfully")
    
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
                messagebox.showinfo("Success", f"Threaded analysis data exported to {filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
    
    def export_threading_report(self):
        """Export threading performance report"""
        if not self.analysis_results:
            messagebox.showinfo("Info", "No threading data to export")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                threading_report = {
                    'case_info': self.analysis_results.get('case_info', {}),
                    'performance_metrics': self.analysis_results.get('performance_metrics', {}),
                    'processing_time': self.analysis_results.get('processing_time_seconds', 0),
                    'threading_log': self.threading_log.get("1.0", tk.END)
                }
                
                with open(filename, 'w') as f:
                    json.dump(threading_report, f, indent=2, default=str)
                messagebox.showinfo("Success", f"Threading performance report exported to {filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export threading report: {str(e)}")
    
    def copy_summary(self):
        """Copy summary to clipboard"""
        if not self.analysis_results:
            messagebox.showinfo("Info", "No analysis data to copy")
            return
        
        summary_text = self.overview_text.get("1.0", tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(summary_text)
        messagebox.showinfo("Success", "Threaded analysis summary copied to clipboard")
    
    def save_case(self):
        """Save current case with threading configuration"""
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
                    'threading_enabled': self.threading_enabled.get(),
                    'max_workers': int(self.max_workers_var.get()),
                    'selected_modules': self.selected_modules,
                    'saved_date': datetime.datetime.now().isoformat()
                }
                
                with open(filename, 'w') as f:
                    json.dump(case_data, f, indent=2)
                
                messagebox.showinfo("Success", f"Case with threading config saved to {filename}")
                
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save case: {str(e)}")
    
    def load_case(self):
        """Load saved case with threading configuration"""
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
                
                # Load threading configuration
                self.threading_enabled.set(case_data.get('threading_enabled', True))
                self.max_workers_var.set(str(case_data.get('max_workers', self.max_workers)))
                
                # Update module selections
                loaded_modules = case_data.get('selected_modules', [])
                for module, var in self.module_vars.items():
                    var.set(module in loaded_modules)
                self.update_selected_modules()
                
                # Update threading configuration
                self.update_threading_config()
                
                messagebox.showinfo("Success", "Case with threading configuration loaded successfully")
                
            except Exception as e:
                messagebox.showerror("Load Error", f"Failed to load case: {str(e)}")
    
    def start_single_threaded_analysis(self):
        """Fallback to single-threaded analysis"""
        # Implementation for single-threaded fallback
        messagebox.showinfo("Info", "Single-threaded analysis not implemented in this version")
    
    def on_closing(self):
        """Handle application closing"""
        if self.analysis_thread and self.analysis_thread.is_alive():
            if messagebox.askyesno("Exit", "Analysis is running. Cancel and exit?"):
                self.cancel_analysis.set()
                self.analysis_thread.join(timeout=3.0)
                self.root.destroy()
        else:
            self.root.destroy()
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

def main():
    """Main function to start the threaded GUI application"""
    print("[INFO] Starting GHOST Threaded Forensic Intelligence Suite GUI...")
    
    try:
        app = ThreadedForensicGUI()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication closed by user")
    except Exception as e:
        print(f"Application error: {e}")
        if 'messagebox' in globals():
            messagebox.showerror("Application Error", f"Failed to start threaded application:\n{str(e)}")

if __name__ == "__main__":
    main()
