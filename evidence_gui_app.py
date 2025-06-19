#!/usr/bin/env python3
"""
GHOST GUI - Evidence-Focused Forensic Analysis Interface
Professional interface for investigators focused on evidence extraction and analysis
"""

import sys
import os
from pathlib import Path
import json
import datetime
import threading
import queue
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

# Import the focused forensic suite
try:
    from ghost_forensic_suite import FocusedForensicSuite
    print("[OK] Evidence analysis engine loaded")
except ImportError:
    try:
        # Fallback to modules if available
        from config_manager import ConfigurationManager
        from forensic_logger import ForensicLogger
        print("[OK] Core modules loaded (basic mode)")
    except ImportError as e:
        print(f"[ERROR] Could not load forensic modules: {e}")
        print("Make sure ghost_forensic_suite.py and modules are available")

class EvidenceAnalysisGUI:
    """Evidence-focused GUI for GHOST forensic analysis"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_main_window()
        
        # Application state
        self.case_name = tk.StringVar()
        self.examiner_name = tk.StringVar()
        self.extraction_path = tk.StringVar()
        
        # Analysis state
        self.analysis_thread = None
        self.analysis_results = None
        self.progress_queue = queue.Queue()
        self.status_queue = queue.Queue()
        
        # Status variables
        self.status_var = tk.StringVar(value="Ready for evidence analysis")
        self.progress_var = tk.DoubleVar()
        self.time_var = tk.StringVar()
        
        # Create interface
        self.setup_styling()
        self.create_widgets()
        
        # Start update loops
        self.update_time()
        self.check_queues()
    
    def setup_main_window(self):
        """Configure main window"""
        self.root.title("GHOST - Evidence Analysis Interface")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # Configure responsive design
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
        
        # Evidence-focused color scheme
        colors = {
            'primary': '#2E4A72',      # Investigation blue
            'accent': '#C7102E',       # Alert red
            'success': '#228B22',      # Evidence green
            'text': '#333333'          # Dark gray
        }
        
        # Configure styles
        self.style.configure('Title.TLabel', 
                           font=('Arial', 16, 'bold'), 
                           foreground=colors['primary'])
        
        self.style.configure('Header.TLabel', 
                           font=('Arial', 12, 'bold'), 
                           foreground=colors['text'])
        
        self.style.configure('Evidence.TLabel',
                           font=('Arial', 10, 'bold'),
                           foreground=colors['success'])
        
        self.style.configure('Alert.TLabel',
                           font=('Arial', 10, 'bold'),
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
        
        # Create tabs
        self.create_case_setup_tab()
        self.create_evidence_overview_tab()
        self.create_communications_tab()
        self.create_multimedia_tab()
        self.create_apps_locations_tab()
        self.create_report_tab()
        
        # Status bar
        self.create_status_bar(main_frame)
    
    def create_title_bar(self, parent):
        """Create title bar"""
        title_frame = ttk.Frame(parent)
        title_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        title_frame.grid_columnconfigure(1, weight=1)
        
        # Main title
        title = ttk.Label(title_frame, 
                         text="GHOST - Evidence Analysis Interface", 
                         style='Title.TLabel')
        title.grid(row=0, column=0, sticky="w")
        
        # Subtitle
        subtitle = ttk.Label(title_frame, 
                           text="Golden Hour Operations and Strategic Threat Assessment")
        subtitle.grid(row=0, column=1, sticky="e")
    
    def create_case_setup_tab(self):
        """Create case setup and analysis tab"""
        case_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(case_frame, text="Case Setup")
        
        case_frame.grid_columnconfigure(0, weight=1)
        
        # Case Information
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
        
        ttk.Button(path_frame, text="Browse...", command=self.browse_extraction).grid(row=0, column=1)
        
        # File type indicator
        self.file_type_var = tk.StringVar(value="No extraction selected")
        ttk.Label(info_frame, textvariable=self.file_type_var).grid(
            row=3, column=1, sticky="w", padx=(10, 0), pady=(5, 0))
        
        # Analysis Controls
        analysis_frame = ttk.LabelFrame(case_frame, text="Evidence Analysis", padding="15")
        analysis_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(analysis_frame, variable=self.progress_var, 
                                          mode='determinate')
        self.progress_bar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        analysis_frame.grid_columnconfigure(0, weight=1)
        
        # Control buttons
        button_frame = ttk.Frame(analysis_frame)
        button_frame.grid(row=1, column=0, sticky="ew")
        
        self.analyze_btn = ttk.Button(button_frame, text="Start Evidence Analysis", 
                                     command=self.start_evidence_analysis)
        self.analyze_btn.pack(side="left", padx=(0, 10))
        
        self.cancel_btn = ttk.Button(button_frame, text="Cancel", 
                                    command=self.cancel_analysis, state="disabled")
        self.cancel_btn.pack(side="left", padx=(0, 10))
        
        ttk.Button(button_frame, text="Save Case", 
                  command=self.save_case).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="Load Case", 
                  command=self.load_case).pack(side="left")
        
        # Analysis Status
        status_frame = ttk.LabelFrame(case_frame, text="Analysis Status", padding="15")
        status_frame.grid(row=2, column=0, sticky="ew")
        
        self.analysis_status_text = scrolledtext.ScrolledText(status_frame, height=8, font=('Consolas', 9))
        self.analysis_status_text.pack(fill="both", expand=True)
    
    def create_evidence_overview_tab(self):
        """Create evidence overview tab"""
        overview_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(overview_frame, text="Evidence Overview")
        
        # Summary cards
        cards_frame = ttk.Frame(overview_frame)
        cards_frame.pack(fill="x", pady=(0, 20))
        
        self.evidence_cards = {}
        card_data = [
            ("Messages", "0"),
            ("Calls", "0"), 
            ("Photos", "0"),
            ("Apps", "0"),
            ("Locations", "0"),
            ("Alerts", "0")
        ]
        
        for i, (title, value) in enumerate(card_data):
            card = self.create_evidence_card(cards_frame, title, value)
            card.grid(row=0, column=i, padx=5, sticky="ew")
            self.evidence_cards[title] = card
            cards_frame.grid_columnconfigure(i, weight=1)
        
        # Executive Summary
        exec_frame = ttk.LabelFrame(overview_frame, text="Executive Summary")
        exec_frame.pack(fill="both", expand=True)
        
        self.executive_summary_text = scrolledtext.ScrolledText(exec_frame, font=('Arial', 10))
        self.executive_summary_text.pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_evidence_card(self, parent, title, value):
        """Create evidence summary card"""
        card_frame = ttk.LabelFrame(parent, text=title)
        
        # Value label
        value_label = ttk.Label(card_frame, text=value, font=('Arial', 18, 'bold'))
        value_label.pack(pady=10)
        
        # Store reference to value label for updates
        card_frame.value_label = value_label
        
        return card_frame
    
    def create_communications_tab(self):
        """Create communications analysis tab"""
        comm_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(comm_frame, text="Communications")
        
        comm_frame.grid_rowconfigure(1, weight=1)
        comm_frame.grid_columnconfigure(0, weight=1)
        
        # Controls
        controls = ttk.Frame(comm_frame)
        controls.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        ttk.Button(controls, text="Export Messages", 
                  command=self.export_messages).pack(side="left", padx=(0, 10))
        ttk.Button(controls, text="Export Calls", 
                  command=self.export_calls).pack(side="left", padx=(0, 10))
        ttk.Button(controls, text="View Timeline", 
                  command=self.view_timeline).pack(side="left")
        
        # Communications notebook
        comm_notebook = ttk.Notebook(comm_frame)
        comm_notebook.grid(row=1, column=0, sticky="nsew")
        
        # Messages tab
        messages_frame = ttk.Frame(comm_notebook)
        comm_notebook.add(messages_frame, text="Messages")
        self.create_messages_view(messages_frame)
        
        # Calls tab
        calls_frame = ttk.Frame(comm_notebook)
        comm_notebook.add(calls_frame, text="Calls")
        self.create_calls_view(calls_frame)
        
        # Contacts tab
        contacts_frame = ttk.Frame(comm_notebook)
        comm_notebook.add(contacts_frame, text="Contacts")
        self.create_contacts_view(contacts_frame)
    
    def create_messages_view(self, parent):
        """Create messages view"""
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        # Messages treeview
        columns = ("Timestamp", "Contact", "Direction", "Message", "Keywords")
        self.messages_tree = ttk.Treeview(parent, columns=columns, show="headings")
        
        for col in columns:
            self.messages_tree.heading(col, text=col)
            if col == "Message":
                self.messages_tree.column(col, width=300)
            else:
                self.messages_tree.column(col, width=120)
        
        # Scrollbars
        msg_v_scroll = ttk.Scrollbar(parent, orient="vertical", command=self.messages_tree.yview)
        msg_h_scroll = ttk.Scrollbar(parent, orient="horizontal", command=self.messages_tree.xview)
        self.messages_tree.configure(yscrollcommand=msg_v_scroll.set, xscrollcommand=msg_h_scroll.set)
        
        # Grid layout
        self.messages_tree.grid(row=0, column=0, sticky="nsew", padx=(10, 0), pady=10)
        msg_v_scroll.grid(row=0, column=1, sticky="ns", pady=10)
        msg_h_scroll.grid(row=1, column=0, sticky="ew", padx=(10, 0))
    
    def create_calls_view(self, parent):
        """Create calls view"""
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        # Calls treeview
        columns = ("Timestamp", "Contact", "Duration", "Type")
        self.calls_tree = ttk.Treeview(parent, columns=columns, show="headings")
        
        for col in columns:
            self.calls_tree.heading(col, text=col)
            self.calls_tree.column(col, width=150)
        
        # Scrollbars
        call_v_scroll = ttk.Scrollbar(parent, orient="vertical", command=self.calls_tree.yview)
        self.calls_tree.configure(yscrollcommand=call_v_scroll.set)
        
        # Grid layout
        self.calls_tree.grid(row=0, column=0, sticky="nsew", padx=(10, 0), pady=10)
        call_v_scroll.grid(row=0, column=1, sticky="ns", pady=10)
    
    def create_contacts_view(self, parent):
        """Create contacts view"""
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        # Contacts treeview
        columns = ("Name", "Phone", "Messages", "Calls", "Last Contact")
        self.contacts_tree = ttk.Treeview(parent, columns=columns, show="headings")
        
        for col in columns:
            self.contacts_tree.heading(col, text=col)
            self.contacts_tree.column(col, width=150)
        
        # Scrollbar
        contact_scroll = ttk.Scrollbar(parent, orient="vertical", command=self.contacts_tree.yview)
        self.contacts_tree.configure(yscrollcommand=contact_scroll.set)
        
        # Grid layout
        self.contacts_tree.grid(row=0, column=0, sticky="nsew", padx=(10, 0), pady=10)
        contact_scroll.grid(row=0, column=1, sticky="ns", pady=10)
    
    def create_multimedia_tab(self):
        """Create multimedia evidence tab"""
        media_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(media_frame, text="Photos & Videos")
        
        media_frame.grid_rowconfigure(1, weight=1)
        media_frame.grid_columnconfigure(0, weight=1)
        
        # Controls
        controls = ttk.Frame(media_frame)
        controls.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        ttk.Button(controls, text="Export Photo List", 
                  command=self.export_photos).pack(side="left", padx=(0, 10))
        ttk.Button(controls, text="Export Video List", 
                  command=self.export_videos).pack(side="left")
        
        # Media notebook
        media_notebook = ttk.Notebook(media_frame)
        media_notebook.grid(row=1, column=0, sticky="nsew")
        
        # Photos tab
        photos_frame = ttk.Frame(media_notebook)
        media_notebook.add(photos_frame, text="Photos")
        self.create_media_view(photos_frame, "photos")
        
        # Videos tab
        videos_frame = ttk.Frame(media_notebook)
        media_notebook.add(videos_frame, text="Videos")
        self.create_media_view(videos_frame, "videos")
    
    def create_media_view(self, parent, media_type):
        """Create media file view"""
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        # Media treeview
        columns = ("Filename", "Size", "Date Modified", "Path")
        tree = ttk.Treeview(parent, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            if col == "Path":
                tree.column(col, width=300)
            else:
                tree.column(col, width=150)
        
        # Store tree reference
        if media_type == "photos":
            self.photos_tree = tree
        else:
            self.videos_tree = tree
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        h_scroll = ttk.Scrollbar(parent, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # Grid layout
        tree.grid(row=0, column=0, sticky="nsew", padx=(10, 0), pady=10)
        v_scroll.grid(row=0, column=1, sticky="ns", pady=10)
        h_scroll.grid(row=1, column=0, sticky="ew", padx=(10, 0))
    
    def create_apps_locations_tab(self):
        """Create apps and locations tab"""
        apps_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(apps_frame, text="Apps & Locations")
        
        apps_frame.grid_rowconfigure(0, weight=1)
        apps_frame.grid_columnconfigure(0, weight=1)
        
        # Apps and locations notebook
        apps_notebook = ttk.Notebook(apps_frame)
        apps_notebook.grid(row=0, column=0, sticky="nsew")
        
        # Apps tab
        apps_tab_frame = ttk.Frame(apps_notebook)
        apps_notebook.add(apps_tab_frame, text="App Data")
        self.create_apps_view(apps_tab_frame)
        
        # Locations tab
        locations_frame = ttk.Frame(apps_notebook)
        apps_notebook.add(locations_frame, text="Location Data")
        self.create_locations_view(locations_frame)
    
    def create_apps_view(self, parent):
        """Create apps view"""
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        # Controls
        controls = ttk.Frame(parent)
        controls.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        ttk.Button(controls, text="Export App Data", 
                  command=self.export_app_data).pack(side="left")
        
        # Apps treeview
        columns = ("App Name", "Files Found", "Priority", "Data Available")
        self.apps_tree = ttk.Treeview(parent, columns=columns, show="headings")
        
        for col in columns:
            self.apps_tree.heading(col, text=col)
            self.apps_tree.column(col, width=150)
        
        # Scrollbar
        apps_scroll = ttk.Scrollbar(parent, orient="vertical", command=self.apps_tree.yview)
        self.apps_tree.configure(yscrollcommand=apps_scroll.set)
        
        # Grid layout
        self.apps_tree.grid(row=1, column=0, sticky="nsew", padx=(10, 0), pady=10)
        apps_scroll.grid(row=1, column=1, sticky="ns", pady=10)
    
    def create_locations_view(self, parent):
        """Create locations view"""
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        # Controls
        controls = ttk.Frame(parent)
        controls.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        ttk.Button(controls, text="Export Locations", 
                  command=self.export_locations).pack(side="left", padx=(0, 10))
        ttk.Button(controls, text="View Map", 
                  command=self.view_map).pack(side="left")
        
        # Locations treeview
        columns = ("Timestamp", "Latitude", "Longitude", "Accuracy")
        self.locations_tree = ttk.Treeview(parent, columns=columns, show="headings")
        
        for col in columns:
            self.locations_tree.heading(col, text=col)
            self.locations_tree.column(col, width=150)
        
        # Scrollbar
        loc_scroll = ttk.Scrollbar(parent, orient="vertical", command=self.locations_tree.yview)
        self.locations_tree.configure(yscrollcommand=loc_scroll.set)
        
        # Grid layout
        self.locations_tree.grid(row=1, column=0, sticky="nsew", padx=(10, 0), pady=10)
        loc_scroll.grid(row=1, column=1, sticky="ns", pady=10)
    
    def create_report_tab(self):
        """Create report and export tab"""
        report_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(report_frame, text="Reports & Export")
        
        report_frame.grid_rowconfigure(1, weight=1)
        report_frame.grid_columnconfigure(0, weight=1)
        
        # Export controls
        export_frame = ttk.Frame(report_frame)
        export_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        ttk.Button(export_frame, text="Export Full Report (JSON)", 
                  command=self.export_full_report).pack(side="left", padx=(0, 10))
        ttk.Button(export_frame, text="Export Executive Summary", 
                  command=self.export_executive_summary).pack(side="left", padx=(0, 10))
        ttk.Button(export_frame, text="Export All Data (CSV)", 
                  command=self.export_all_csv).pack(side="left")
        
        # Report display
        report_label_frame = ttk.LabelFrame(report_frame, text="Generated Report")
        report_label_frame.grid(row=1, column=0, sticky="nsew")
        report_label_frame.grid_rowconfigure(0, weight=1)
        report_label_frame.grid_columnconfigure(0, weight=1)
        
        self.report_text = scrolledtext.ScrolledText(report_label_frame, font=('Consolas', 9))
        self.report_text.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    
    def create_status_bar(self, parent):
        """Create status bar"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        status_frame.grid_columnconfigure(0, weight=1)
        
        # Status message
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.grid(row=0, column=0, sticky="w")
        
        # Current time
        time_label = ttk.Label(status_frame, textvariable=self.time_var)
        time_label.grid(row=0, column=1, sticky="e")
    
    # Event handlers and methods
    
    def update_time(self):
        """Update time display"""
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_var.set(current_time)
        self.root.after(1000, self.update_time)
    
    def check_queues(self):
        """Check for updates from background threads"""
        try:
            # Check progress updates
            while not self.progress_queue.empty():
                progress_data = self.progress_queue.get_nowait()
                self.progress_var.set(progress_data.get('progress', 0))
                
                if 'message' in progress_data:
                    self.log_analysis_message(progress_data['message'])
            
            # Check status updates
            while not self.status_queue.empty():
                status_data = self.status_queue.get_nowait()
                self.status_var.set(status_data.get('message', ''))
        
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.check_queues)
    
    def browse_extraction(self):
        """Browse for extraction path"""
        # Allow both files and directories
        file_path = filedialog.askopenfilename(
            title="Select Extraction ZIP File",
            filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")]
        )
        
        if not file_path:
            dir_path = filedialog.askdirectory(title="Select Extraction Directory")
            if dir_path:
                file_path = dir_path
        
        if file_path:
            self.extraction_path.set(file_path)
            
            # Update file type indicator
            path_obj = Path(file_path)
            if path_obj.is_file() and path_obj.suffix.lower() == '.zip':
                size_mb = path_obj.stat().st_size / (1024 * 1024)
                self.file_type_var.set(f"ZIP file selected ({size_mb:.1f} MB)")
            elif path_obj.is_dir():
                self.file_type_var.set("Directory selected")
            else:
                self.file_type_var.set("File selected")
    
    def validate_case_info(self):
        """Validate case information"""
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
    
    def start_evidence_analysis(self):
        """Start evidence analysis"""
        if not self.validate_case_info():
            return
        
        # Confirm analysis
        if not messagebox.askyesno("Start Analysis", 
                                  "Start evidence analysis? This may take several minutes."):
            return
        
        # Prepare for analysis
        self.analyze_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")
        self.progress_var.set(0)
        self.clear_analysis_log()
        
        # Start analysis thread
        self.analysis_thread = threading.Thread(target=self.analysis_worker, daemon=True)
        self.analysis_thread.start()
    
    def analysis_worker(self):
        """Background analysis worker"""
        try:
            # Update status
            self.status_queue.put({'message': 'Initializing evidence analysis...'})
            self.progress_queue.put({'progress': 5, 'message': 'Starting analysis...'})
            
            # Initialize forensic suite
            suite = FocusedForensicSuite(self.case_name.get(), self.examiner_name.get())
            
            self.progress_queue.put({'progress': 10, 'message': 'Evidence analysis engine initialized'})
            
            # Run analysis
            self.progress_queue.put({'progress': 20, 'message': 'Analyzing extraction...'})
            report = suite.analyze_extraction(self.extraction_path.get())
            
            self.progress_queue.put({'progress': 90, 'message': 'Generating report...'})
            
            # Update UI with results
            self.root.after(0, lambda: self.update_analysis_results(report))
            self.progress_queue.put({'progress': 100, 'message': 'Analysis complete!'})
            
        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            self.root.after(0, lambda: self.analysis_error(error_msg))
        
        finally:
            # Re-enable controls
            self.root.after(0, self.analysis_complete)
    
    def update_analysis_results(self, report):
        """Update GUI with analysis results"""
        self.analysis_results = report
        
        # Update evidence cards
        evidence_summary = report['evidence_summary']
        
        self.update_card_value("Messages", evidence_summary['communications']['messages'])
        self.update_card_value("Calls", evidence_summary['communications']['calls'])
        self.update_card_value("Photos", evidence_summary['multimedia']['photos'])
        self.update_card_value("Apps", evidence_summary['digital_activity']['app_data'])
        self.update_card_value("Locations", evidence_summary['digital_activity']['location_points'])
        
        # Calculate alerts
        comm_analysis = report.get('communication_intelligence', {}).get('message_analysis', {})
        alerts = comm_analysis.get('keywords_found', 0)
        self.update_card_value("Alerts", alerts)
        
        # Update executive summary
        self.update_executive_summary(report)
        
        # Update data views
        self.update_communications_data(report)
        self.update_multimedia_data(report)
        self.update_apps_locations_data(report)
        
        # Generate report text
        self.generate_report_text(report)
        
        # Switch to overview tab
        self.notebook.select(1)
        
        self.status_var.set("Evidence analysis complete - review results")
    
    def update_card_value(self, card_name, value):
        """Update evidence card value"""
        if card_name in self.evidence_cards:
            card = self.evidence_cards[card_name]
            card.value_label.config(text=str(value))
    
    def update_executive_summary(self, report):
        """Update executive summary display"""
        self.executive_summary_text.delete("1.0", tk.END)
        
        exec_summary = report['executive_summary']
        comm_intel = report.get('communication_intelligence', {})
        
        summary_text = f"""EVIDENCE ANALYSIS SUMMARY
{'-' * 50}

PRIORITY LEVEL: {exec_summary['priority_level']}
Reason: {exec_summary['priority_reason']}

EVIDENCE TYPES FOUND:
{chr(10).join(f'• {evidence}' for evidence in exec_summary['evidence_types_found'])}

KEY STATISTICS:
• Total Communications: {exec_summary['key_statistics']['total_communications']}
• Unique Contacts: {exec_summary['key_statistics']['unique_contacts']}
• Investigation Keywords: {exec_summary['key_statistics']['investigation_keywords']}
• Multimedia Files: {exec_summary['key_statistics']['multimedia_files']}
• Location Points: {exec_summary['key_statistics']['location_points']}

IMMEDIATE ACTIONS REQUIRED:
{chr(10).join(f'• {action}' for action in exec_summary['immediate_actions'])}

COMMUNICATION ANALYSIS:
"""
        
        # Add communication details
        msg_analysis = comm_intel.get('message_analysis', {})
        if msg_analysis:
            summary_text += f"• Messages Analyzed: {msg_analysis.get('message_count', 0)}\n"
            summary_text += f"• Unique Message Contacts: {msg_analysis.get('unique_contacts', 0)}\n"
            
            # Top contacts
            top_contacts = msg_analysis.get('top_contacts', [])
            if top_contacts:
                summary_text += "\nTOP MESSAGE CONTACTS:\n"
                for contact, count in top_contacts[:5]:
                    summary_text += f"• {contact}: {count} messages\n"
            
            # Keywords found
            keyword_mentions = msg_analysis.get('keyword_mentions', {})
            if keyword_mentions:
                summary_text += f"\nINVESTIGATION KEYWORDS DETECTED:\n"
                for keyword, mentions in keyword_mentions.items():
                    summary_text += f"• '{keyword}': {len(mentions)} mentions\n"
        
        # Add call analysis
        call_analysis = comm_intel.get('call_analysis', {})
        if call_analysis:
            summary_text += f"\nCALL ANALYSIS:\n"
            summary_text += f"• Total Calls: {call_analysis.get('call_count', 0)}\n"
            summary_text += f"• Unique Numbers: {call_analysis.get('unique_numbers', 0)}\n"
            summary_text += f"• Total Duration: {call_analysis.get('total_duration_hours', 0):.1f} hours\n"
        
        # Add investigative leads
        investigative_leads = report.get('investigative_leads', [])
        if investigative_leads:
            summary_text += f"\nINVESTIGATIVE LEADS ({len(investigative_leads)}):\n"
            for lead in investigative_leads[:5]:  # Show first 5
                summary_text += f"• {lead['type']}: {lead['description']}\n"
        
        self.executive_summary_text.insert("1.0", summary_text)
    
    def update_communications_data(self, report):
        """Update communications tabs with data"""
        raw_data = report.get('raw_evidence_data', {})
        
        # Update messages
        messages = raw_data.get('messages', [])
        self.messages_tree.delete(*self.messages_tree.get_children())
        
        # Get keyword mentions for highlighting
        comm_analysis = report.get('communication_intelligence', {}).get('message_analysis', {})
        keyword_mentions = comm_analysis.get('keyword_mentions', {})
        keywords_found = set(keyword_mentions.keys())
        
        for message in messages[:500]:  # Limit display for performance
            timestamp = message.get('timestamp', 'Unknown')
            contact = message.get('contact', 'Unknown')
            text = message.get('text', '')
            direction = 'Outgoing' if message.get('is_from_me') else 'Incoming'
            
            # Check for keywords
            text_lower = text.lower()
            found_keywords = [kw for kw in keywords_found if kw in text_lower]
            keywords_str = ', '.join(found_keywords) if found_keywords else ''
            
            # Truncate message for display
            display_text = text[:100] + '...' if len(text) > 100 else text
            
            self.messages_tree.insert("", "end", values=(
                timestamp, contact, direction, display_text, keywords_str
            ))
        
        # Update calls
        calls = raw_data.get('calls', [])
        self.calls_tree.delete(*self.calls_tree.get_children())
        
        for call in calls[:500]:  # Limit display
            timestamp = call.get('timestamp', 'Unknown')
            contact = call.get('address') or call.get('number', 'Unknown')
            duration = call.get('duration', 0)
            call_type = call.get('type', 'Unknown')
            
            # Format duration
            if isinstance(duration, (int, float)):
                duration_str = f"{int(duration)}s"
            else:
                duration_str = str(duration)
            
            self.calls_tree.insert("", "end", values=(
                timestamp, contact, duration_str, call_type
            ))
        
        # Update contacts
        contacts = raw_data.get('contacts', [])
        top_contacts = report.get('communication_intelligence', {}).get('top_contacts', [])
        
        self.contacts_tree.delete(*self.contacts_tree.get_children())
        
        # Create contact summary with communication stats
        contact_stats = {}
        for contact_info in top_contacts:
            contact_stats[contact_info['contact']] = contact_info
        
        for contact in contacts[:100]:  # Limit display
            name = contact.get('first_name', '') + ' ' + contact.get('last_name', '')
            if not name.strip():
                name = contact.get('display_name', 'Unknown')
            
            phone = contact.get('phone', 'Unknown')
            
            # Get communication stats
            stats = contact_stats.get(phone, {})
            messages = stats.get('messages', 0)
            calls = stats.get('calls', 0)
            
            self.contacts_tree.insert("", "end", values=(
                name.strip(), phone, messages, calls, 'Unknown'
            ))
    
    def update_multimedia_data(self, report):
        """Update multimedia tabs with data"""
        raw_data = report.get('raw_evidence_data', {})
        
        # Update photos
        photos = raw_data.get('photos', [])
        self.photos_tree.delete(*self.photos_tree.get_children())
        
        for photo in photos:
            filename = photo.get('filename', 'Unknown')
            size = photo.get('size', 0)
            date_modified = photo.get('date_modified', 'Unknown')
            path = photo.get('path', 'Unknown')
            
            # Format size
            if isinstance(size, (int, float)) and size > 0:
                if size > 1024 * 1024:
                    size_str = f"{size / (1024 * 1024):.1f} MB"
                else:
                    size_str = f"{size / 1024:.1f} KB"
            else:
                size_str = "Unknown"
            
            self.photos_tree.insert("", "end", values=(
                filename, size_str, date_modified, path
            ))
        
        # Update videos
        videos = raw_data.get('videos', [])
        self.videos_tree.delete(*self.videos_tree.get_children())
        
        for video in videos:
            filename = video.get('filename', 'Unknown')
            size = video.get('size', 0)
            date_modified = video.get('date_modified', 'Unknown')
            path = video.get('path', 'Unknown')
            
            # Format size
            if isinstance(size, (int, float)) and size > 0:
                if size > 1024 * 1024:
                    size_str = f"{size / (1024 * 1024):.1f} MB"
                else:
                    size_str = f"{size / 1024:.1f} KB"
            else:
                size_str = "Unknown"
            
            self.videos_tree.insert("", "end", values=(
                filename, size_str, date_modified, path
            ))
    
    def update_apps_locations_data(self, report):
        """Update apps and locations data"""
        raw_data = report.get('raw_evidence_data', {})
        app_intel = report.get('app_intelligence', {})
        
        # Update apps
        apps = raw_data.get('apps', {})
        self.apps_tree.delete(*self.apps_tree.get_children())
        
        app_summary = app_intel.get('app_summary', {})
        
        for app_name, app_data in apps.items():
            files_found = len(app_data.get('files', []))
            priority = app_summary.get(app_name, {}).get('investigation_priority', 'Medium')
            data_available = 'Yes' if files_found > 0 else 'No'
            
            self.apps_tree.insert("", "end", values=(
                app_name, files_found, priority, data_available
            ))
        
        # Update locations
        locations = raw_data.get('locations', [])
        self.locations_tree.delete(*self.locations_tree.get_children())
        
        for location in locations[:1000]:  # Limit for performance
            timestamp = location.get('timestamp', 'Unknown')
            latitude = location.get('latitude', 'Unknown')
            longitude = location.get('longitude', 'Unknown')
            accuracy = location.get('accuracy', 'Unknown')
            
            self.locations_tree.insert("", "end", values=(
                timestamp, latitude, longitude, accuracy
            ))
    
    def generate_report_text(self, report):
        """Generate comprehensive report text"""
        self.report_text.delete("1.0", tk.END)
        
        case_info = report['case_information']
        exec_summary = report['executive_summary']
        evidence_summary = report['evidence_summary']
        
        report_text = f"""GHOST EVIDENCE ANALYSIS REPORT
{'=' * 50}

CASE INFORMATION:
Case Name: {case_info['case_name']}
Examiner: {case_info['examiner']}
Analysis Date: {case_info['analysis_date']}
Source: {case_info['source_path']}
Tool Version: {case_info['tool_version']}

EXECUTIVE SUMMARY:
Priority Level: {exec_summary['priority_level']}
Priority Reason: {exec_summary['priority_reason']}

Evidence Types Found:
{chr(10).join(f'• {evidence}' for evidence in exec_summary['evidence_types_found'])}

EVIDENCE SUMMARY:
Communications:
• Messages: {evidence_summary['communications']['messages']}
• Calls: {evidence_summary['communications']['calls']}  
• Contacts: {evidence_summary['communications']['contacts']}

Multimedia:
• Photos: {evidence_summary['multimedia']['photos']}
• Videos: {evidence_summary['multimedia']['videos']}

Digital Activity:
• Browser Records: {evidence_summary['digital_activity']['browser_records']}
• Location Points: {evidence_summary['digital_activity']['location_points']}
• Apps with Data: {evidence_summary['digital_activity']['app_data']}
• Databases: {evidence_summary['digital_activity']['databases']}

INVESTIGATIVE LEADS:
"""
        
        # Add investigative leads
        leads = report.get('investigative_leads', [])
        for i, lead in enumerate(leads, 1):
            report_text += f"{i}. {lead['type']} - {lead['priority']}\n"
            report_text += f"   Description: {lead['description']}\n"
            report_text += f"   Action Required: {lead['action_required']}\n\n"
        
        # Add export options
        export_options = report.get('data_export_options', {})
        if export_options:
            report_text += "DATA EXPORT OPTIONS:\n"
            for category, options in export_options.items():
                report_text += f"\n{category}:\n"
                for option in options:
                    report_text += f"• {option}\n"
        
        report_text += f"\nReport generated by GHOST Evidence Analysis Interface"
        
        self.report_text.insert("1.0", report_text)
    
    def analysis_complete(self):
        """Re-enable controls after analysis"""
        self.analyze_btn.config(state="normal")
        self.cancel_btn.config(state="disabled")
    
    def analysis_error(self, error_message):
        """Handle analysis errors"""
        messagebox.showerror("Analysis Error", error_message)
        self.status_var.set(f"Analysis failed: {error_message}")
        self.log_analysis_message(f"ERROR: {error_message}")
    
    def cancel_analysis(self):
        """Cancel current analysis"""
        if messagebox.askyesno("Cancel Analysis", "Cancel the current analysis?"):
            # Note: This is a simple cancel - in a real implementation you'd need
            # proper thread cancellation
            self.status_var.set("Analysis cancelled by user")
            self.analysis_complete()
    
    def log_analysis_message(self, message):
        """Log message to analysis status"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.analysis_status_text.insert(tk.END, log_entry)
        self.analysis_status_text.see(tk.END)
    
    def clear_analysis_log(self):
        """Clear analysis log"""
        self.analysis_status_text.delete("1.0", tk.END)
    
    # Export functions
    
    def export_messages(self):
        """Export messages to CSV"""
        if not self.analysis_results:
            messagebox.showinfo("Info", "No analysis data available for export")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                # Use the forensic suite's export function
                suite = FocusedForensicSuite(self.case_name.get(), self.examiner_name.get())
                suite.evidence_data = self.analysis_results['raw_evidence_data']
                suite.export_messages_csv(filename)
                messagebox.showinfo("Success", f"Messages exported to {filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export messages: {e}")
    
    def export_calls(self):
        """Export calls to CSV"""
        messagebox.showinfo("Info", "Call export feature coming soon")
    
    def export_photos(self):
        """Export photo list"""
        messagebox.showinfo("Info", "Photo export feature coming soon")
    
    def export_videos(self):
        """Export video list"""
        messagebox.showinfo("Info", "Video export feature coming soon")
    
    def export_app_data(self):
        """Export app data"""
        messagebox.showinfo("Info", "App data export feature coming soon")
    
    def export_locations(self):
        """Export location data"""
        messagebox.showinfo("Info", "Location export feature coming soon")
    
    def export_full_report(self):
        """Export full analysis report"""
        if not self.analysis_results:
            messagebox.showinfo("Info", "No analysis data available for export")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.analysis_results, f, indent=2, default=str)
                messagebox.showinfo("Success", f"Full report exported to {filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export report: {e}")
    
    def export_executive_summary(self):
        """Export executive summary"""
        messagebox.showinfo("Info", "Executive summary export coming soon")
    
    def export_all_csv(self):
        """Export all data as CSV files"""
        messagebox.showinfo("Info", "Bulk CSV export feature coming soon")
    
    def view_timeline(self):
        """View communication timeline"""
        messagebox.showinfo("Info", "Timeline view feature coming soon")
    
    def view_map(self):
        """View location data on map"""
        messagebox.showinfo("Info", "Map view feature coming soon")
    
    def save_case(self):
        """Save case configuration"""
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
                    'saved_date': datetime.datetime.now().isoformat()
                }
                
                with open(filename, 'w') as f:
                    json.dump(case_data, f, indent=2)
                
                messagebox.showinfo("Success", f"Case saved to {filename}")
                
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save case: {e}")
    
    def load_case(self):
        """Load saved case configuration"""
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
                
                messagebox.showinfo("Success", "Case loaded successfully")
                
            except Exception as e:
                messagebox.showerror("Load Error", f"Failed to load case: {e}")
    
    def on_closing(self):
        """Handle application closing"""
        if self.analysis_thread and self.analysis_thread.is_alive():
            if messagebox.askyesno("Exit", "Analysis is running. Exit anyway?"):
                self.root.destroy()
        else:
            self.root.destroy()
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

def main():
    """Main function to start the evidence analysis GUI"""
    print("[INFO] Starting GHOST Evidence Analysis Interface...")
    
    try:
        app = EvidenceAnalysisGUI()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication closed by user")
    except Exception as e:
        print(f"Application error: {e}")
        if 'messagebox' in globals():
            messagebox.showerror("Application Error", f"Failed to start application:\n{str(e)}")

if __name__ == "__main__":
    main()
