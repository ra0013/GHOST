#!/usr/bin/env python3
"""
GHOST Evidence Analysis - Main Window Controller
Coordinates all GUI components and manages application state
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import threading
import queue
from pathlib import Path

from .case_manager import CaseManager
from .analysis_engine import AnalysisEngine
from .tabs.case_setup_tab import CaseSetupTab
from .tabs.overview_tab import OverviewTab
from .tabs.communications_tab import CommunicationsTab
from .tabs.multimedia_tab import MultimediaTab
from .tabs.locations_tab import LocationsTab
from .tabs.reports_tab import ReportsTab
from .components.status_bar import StatusBar
from .styles.theme_manager import ThemeManager

class EvidenceAnalysisMainWindow:
    """Main window controller for GHOST Evidence Analysis Interface"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_main_window()
        
        # Initialize managers
        self.case_manager = CaseManager()
        self.analysis_engine = AnalysisEngine()
        self.theme_manager = ThemeManager()
        
        # Communication queues for threading
        self.progress_queue = queue.Queue()
        self.status_queue = queue.Queue()
        
        # Status variables
        self.status_var = tk.StringVar(value="Ready for evidence analysis")
        self.progress_var = tk.DoubleVar()
        self.time_var = tk.StringVar()
        
        # Application state
        self.analysis_thread = None
        self.analysis_results = None
        
        # Initialize GUI
        self.setup_styling()
        self.create_widgets()
        self.setup_event_handlers()
        
        # Start background tasks
        self.update_time()
        self.check_queues()
    
    def setup_main_window(self):
        """Configure the main application window"""
        self.root.title("GHOST - Evidence Analysis Interface")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # Configure responsive design
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_styling(self):
        """Apply theme and styling"""
        self.theme_manager.apply_theme(self.root)
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Title bar
        self.create_title_bar()
        
        # Main notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        
        # Create tabs
        self.create_tabs()
        
        # Status bar
        self.status_bar = StatusBar(
            self.main_frame,
            self.status_var,
            self.progress_var, 
            self.time_var
        )
        self.status_bar.grid(row=2, column=0, sticky="ew", pady=(10, 0))
    
    def create_title_bar(self):
        """Create the application title bar"""
        title_frame = ttk.Frame(self.main_frame)
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
    
    def create_tabs(self):
        """Create all application tabs"""
        # Case Setup Tab
        self.case_setup_tab = CaseSetupTab(
            self.notebook, 
            self.case_manager,
            self.start_analysis_callback,
            self.cancel_analysis_callback
        )
        self.notebook.add(self.case_setup_tab.frame, text="Case Setup")
        
        # Evidence Overview Tab
        self.overview_tab = OverviewTab(self.notebook)
        self.notebook.add(self.overview_tab.frame, text="Evidence Overview")
        
        # Communications Tab
        self.communications_tab = CommunicationsTab(self.notebook)
        self.notebook.add(self.communications_tab.frame, text="Communications")
        
        # Multimedia Tab
        self.multimedia_tab = MultimediaTab(self.notebook)
        self.notebook.add(self.multimedia_tab.frame, text="Photos & Videos")
        
        # Locations Tab
        self.locations_tab = LocationsTab(self.notebook)
        self.notebook.add(self.locations_tab.frame, text="Apps & Locations")
        
        # Reports Tab
        self.reports_tab = ReportsTab(self.notebook, self.case_manager)
        self.notebook.add(self.reports_tab.frame, text="Reports & Export")
    
    def setup_event_handlers(self):
        """Setup event handlers for cross-tab communication"""
        # Subscribe to case manager events
        self.case_manager.on_case_loaded = self.on_case_loaded
        self.case_manager.on_case_saved = self.on_case_saved
        
        # Subscribe to analysis engine events
        self.analysis_engine.on_progress_update = self.on_progress_update
        self.analysis_engine.on_analysis_complete = self.on_analysis_complete
        self.analysis_engine.on_analysis_error = self.on_analysis_error
    
    # Event Handlers
    
    def start_analysis_callback(self):
        """Callback for starting analysis"""
        if not self.case_manager.validate_case_info():
            return
        
        # Confirm analysis
        if not messagebox.askyesno("Start Analysis", 
                                  "Start evidence analysis? This may take several minutes."):
            return
        
        # Prepare UI for analysis
        self.case_setup_tab.set_analysis_running(True)
        self.progress_var.set(0)
        
        # Start analysis in background
        self.analysis_thread = threading.Thread(
            target=self.analysis_worker, 
            daemon=True
        )
        self.analysis_thread.start()
    
    def cancel_analysis_callback(self):
        """Callback for canceling analysis"""
        if messagebox.askyesno("Cancel Analysis", "Cancel the current analysis?"):
            self.analysis_engine.cancel_analysis()
            self.case_setup_tab.set_analysis_running(False)
            self.update_status("Analysis cancelled by user")
    
    def analysis_worker(self):
        """Background analysis worker"""
        try:
            # Get case information
            case_info = self.case_manager.get_case_info()
            
            # Run analysis
            results = self.analysis_engine.analyze_evidence(
                case_info['extraction_path'],
                case_info['case_name'],
                case_info['examiner_name']
            )
            
            # Update UI on main thread
            self.root.after(0, lambda: self.on_analysis_complete(results))
            
        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            self.root.after(0, lambda: self.on_analysis_error(error_msg))
    
    def on_case_loaded(self, case_data):
        """Handle case loaded event"""
        self.update_status(f"Case loaded: {case_data.get('case_name', 'Unknown')}")
    
    def on_case_saved(self, filename):
        """Handle case saved event"""
        self.update_status(f"Case saved to: {filename}")
    
    def on_progress_update(self, progress, message):
        """Handle analysis progress updates"""
        self.progress_queue.put({'progress': progress, 'message': message})
    
    def on_analysis_complete(self, results):
        """Handle analysis completion"""
        self.analysis_results = results
        self.case_setup_tab.set_analysis_running(False)
        
        # Update all tabs with results
        self.overview_tab.update_with_results(results)
        self.communications_tab.update_with_results(results)
        self.multimedia_tab.update_with_results(results)
        self.locations_tab.update_with_results(results)
        self.reports_tab.update_with_results(results)
        
        # Switch to overview tab
        self.notebook.select(1)
        
        self.update_status("Evidence analysis complete - review results")
    
    def on_analysis_error(self, error_message):
        """Handle analysis errors"""
        self.case_setup_tab.set_analysis_running(False)
        messagebox.showerror("Analysis Error", error_message)
        self.update_status(f"Analysis failed: {error_message}")
    
    # Background Tasks
    
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
                    self.case_setup_tab.log_analysis_message(progress_data['message'])
            
            # Check status updates
            while not self.status_queue.empty():
                status_data = self.status_queue.get_nowait()
                self.update_status(status_data.get('message', ''))
        
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.check_queues)
    
    # Utility Methods
    
    def update_status(self, message):
        """Update status bar message"""
        self.status_var.set(message)
        self.root.update_idletasks()
    
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

    def get_analysis_results(self):
        """Get current analysis results"""
        return self.analysis_results
