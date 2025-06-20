#!/usr/bin/env python3
"""
GHOST Evidence Analysis - Case Setup Tab
Handles case information input and analysis controls
"""

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
from pathlib import Path
import datetime
from typing import Callable

class CaseSetupTab:
    """Case setup and analysis control tab"""
    
    def __init__(self, parent, case_manager, start_analysis_callback: Callable, cancel_analysis_callback: Callable):
        self.parent = parent
        self.case_manager = case_manager
        self.start_analysis_callback = start_analysis_callback
        self.cancel_analysis_callback = cancel_analysis_callback
        
        # Create main frame
        self.frame = ttk.Frame(parent, padding="20")
        
        # Create widgets
        self.create_widgets()
        
        # Subscribe to case manager events
        self.case_manager.on_case_changed = self.on_case_changed
    
    def create_widgets(self):
        """Create all widgets for the case setup tab"""
        self.frame.grid_columnconfigure(0, weight=1)
        
        # Case Information Section
        self.create_case_info_section()
        
        # File Information Section
        self.create_file_info_section()
        
        # Analysis Controls Section
        self.create_analysis_controls_section()
        
        # Analysis Status Section
        self.create_analysis_status_section()
    
    def create_case_info_section(self):
        """Create case information input section"""
        info_frame = ttk.LabelFrame(self.frame, text="Case Information", padding="15")
        info_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        info_frame.grid_columnconfigure(1, weight=1)
        
        # Case name
        ttk.Label(info_frame, text="Case Name:", style='Header.TLabel').grid(
            row=0, column=0, sticky="w", pady=(0, 10))
        
        self.case_name_var = tk.StringVar()
        self.case_name_var.trace('w', self.on_case_name_changed)
        case_entry = ttk.Entry(info_frame, textvariable=self.case_name_var, width=40)
        case_entry.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=(0, 10))
        
        # Examiner name
        ttk.Label(info_frame, text="Examiner:", style='Header.TLabel').grid(
            row=1, column=0, sticky="w", pady=(0, 10))
        
        self.examiner_name_var = tk.StringVar()
        self.examiner_name_var.trace('w', self.on_examiner_name_changed)
        examiner_entry = ttk.Entry(info_frame, textvariable=self.examiner_name_var, width=40)
        examiner_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(0, 10))
        
        # Extraction path
        ttk.Label(info_frame, text="Extraction Path:", style='Header.TLabel').grid(
            row=2, column=0, sticky="w")
        
        path_frame = ttk.Frame(info_frame)
        path_frame.grid(row=2, column=1, sticky="ew", padx=(10, 0))
        path_frame.grid_columnconfigure(0, weight=1)
        
        self.extraction_path_var = tk.StringVar()
        self.extraction_path_var.trace('w', self.on_extraction_path_changed)
        path_entry = ttk.Entry(path_frame, textvariable=self.extraction_path_var)
        path_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        ttk.Button(path_frame, text="Browse...", command=self.browse_extraction_path).grid(row=0, column=1)
    
    def create_file_info_section(self):
        """Create file information display section"""
        file_info_frame = ttk.LabelFrame(self.frame, text="Extraction Information", padding="15")
        file_info_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        file_info_frame.grid_columnconfigure(1, weight=1)
        
        # File type
        ttk.Label(file_info_frame, text="Type:").grid(row=0, column=0, sticky="w", pady=5)
        self.file_type_var = tk.StringVar(value="No file selected")
        ttk.Label(file_info_frame, textvariable=self.file_type_var).grid(
            row=0, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # File size
        ttk.Label(file_info_frame, text="Size:").grid(row=1, column=0, sticky="w", pady=5)
        self.file_size_var = tk.StringVar(value="Unknown")
        ttk.Label(file_info_frame, textvariable=self.file_size_var).grid(
            row=1, column=1, sticky="w", padx=(10, 0), pady=5)
        
        # Recommended analysis
        ttk.Label(file_info_frame, text="Recommended:").grid(row=2, column=0, sticky="w", pady=5)
        self.recommended_var = tk.StringVar(value="Select extraction path")
        ttk.Label(file_info_frame, textvariable=self.recommended_var).grid(
            row=2, column=1, sticky="w", padx=(10, 0), pady=5)
    
    def create_analysis_controls_section(self):
        """Create analysis control buttons section"""
        controls_frame = ttk.LabelFrame(self.frame, text="Analysis Controls", padding="15")
        controls_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(controls_frame, variable=self.progress_var, 
                                          mode='determinate')
        self.progress_bar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        controls_frame.grid_columnconfigure(0, weight=1)
        
        # Control buttons
        button_frame = ttk.Frame(controls_frame)
        button_frame.grid(row=1, column=0, sticky="ew")
        
        self.analyze_btn = ttk.Button(button_frame, text="Start Evidence Analysis", 
                                     command=self.start_analysis_callback)
        self.analyze_btn.pack(side="left", padx=(0, 10))
        
        self.cancel_btn = ttk.Button(button_frame, text="Cancel", 
                                    command=self.cancel_analysis_callback, state="disabled")
        self.cancel_btn.pack(side="left", padx=(0, 10))
        
        ttk.Button(button_frame, text="Save Case", 
                  command=self.save_case).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="Load Case", 
                  command=self.load_case).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="New Case", 
                  command=self.new_case).pack(side="left")
    
    def create_analysis_status_section(self):
        """Create analysis status log section"""
        status_frame = ttk.LabelFrame(self.frame, text="Analysis Status", padding="15")
        status_frame.grid(row=3, column=0, sticky="nsew")
        self.frame.grid_rowconfigure(3, weight=1)
        
        self.analysis_status_text = scrolledtext.ScrolledText(status_frame, height=10, font=('Consolas', 9))
        self.analysis_status_text.pack(fill="both", expand=True)
        
        # Add initial message
        self.log_analysis_message("Ready for evidence analysis")
    
    # Event Handlers
    
    def on_case_name_changed(self, *args):
        """Handle case name changes"""
        self.case_manager.set_case_name(self.case_name_var.get())
    
    def on_examiner_name_changed(self, *args):
        """Handle examiner name changes"""
        self.case_manager.set_examiner_name(self.examiner_name_var.get())
    
    def on_extraction_path_changed(self, *args):
        """Handle extraction path changes"""
        path = self.extraction_path_var.get()
        self.case_manager.set_extraction_path(path)
        self.update_file_info(path)
    
    def on_case_changed(self, case_data):
        """Handle case data changes from case manager"""
        # Update UI without triggering change events
        self.case_name_var.set(case_data.get('case_name', ''))
        self.examiner_name_var.set(case_data.get('examiner_name', ''))
        self.extraction_path_var.set(case_data.get('extraction_path', ''))
        
        # Update file info
        self.update_file_info(case_data.get('extraction_path', ''))
    
    def browse_extraction_path(self):
        """Browse for extraction path"""
        # Try file first (ZIP files)
        file_path = filedialog.askopenfilename(
            title="Select Extraction ZIP File",
            filetypes=[
                ("ZIP files", "*.zip"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            # If no file selected, try directory
            dir_path = filedialog.askdirectory(title="Select Extraction Directory")
            if dir_path:
                file_path = dir_path
        
        if file_path:
            self.extraction_path_var.set(file_path)
    
    def update_file_info(self, file_path: str):
        """Update file information display"""
        if not file_path:
            self.file_type_var.set("No file selected")
            self.file_size_var.set("Unknown")
            self.recommended_var.set("Select extraction path")
            return
        
        path_obj = Path(file_path)
        
        if not path_obj.exists():
            self.file_type_var.set("File not found")
            self.file_size_var.set("Unknown")
            self.recommended_var.set("Invalid path")
            return
        
        # Update file type
        if path_obj.is_file():
            if path_obj.suffix.lower() == '.zip':
                self.file_type_var.set("ZIP Archive")
                self.recommended_var.set("Standard analysis recommended")
            else:
                self.file_type_var.set("File")
                self.recommended_var.set("May require special handling")
        elif path_obj.is_dir():
            self.file_type_var.set("Directory")
            self.recommended_var.set("Directory analysis")
        else:
            self.file_type_var.set("Unknown")
            self.recommended_var.set("Unknown file type")
        
        # Update file size
        try:
            if path_obj.is_file():
                size_bytes = path_obj.stat().st_size
                size_mb = size_bytes / (1024 * 1024)
                if size_mb > 100:
                    self.file_size_var.set(f"{size_mb:.1f} MB (Large file)")
                    self.recommended_var.set("Large extraction - may take time")
                else:
                    self.file_size_var.set(f"{size_mb:.1f} MB")
            elif path_obj.is_dir():
                # Count files in directory
                file_count = len([f for f in path_obj.rglob('*') if f.is_file()])
                self.file_size_var.set(f"{file_count} files")
                if file_count > 1000:
                    self.recommended_var.set("Large directory - comprehensive analysis")
        except Exception:
            self.file_size_var.set("Unable to determine size")
    
    def save_case(self):
        """Save current case"""
        if not self.case_manager.validate_case_info():
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Case Configuration"
        )
        
        if filename:
            if self.case_manager.save_case(filename):
                self.log_analysis_message(f"Case saved to {filename}")
    
    def load_case(self):
        """Load saved case"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Load Case Configuration"
        )
        
        if filename:
            if self.case_manager.load_case(filename):
                self.log_analysis_message(f"Case loaded from {filename}")
    
    def new_case(self):
        """Create new case"""
        from tkinter import messagebox
        
        if messagebox.askyesno("New Case", "Create a new case? Current data will be cleared."):
            self.case_manager.create_new_case()
            self.clear_analysis_log()
            self.log_analysis_message("New case created")
    
    def set_analysis_running(self, running: bool):
        """Set analysis running state"""
        if running:
            self.analyze_btn.config(state="disabled")
            self.cancel_btn.config(state="normal")
            self.progress_var.set(0)
        else:
            self.analyze_btn.config(state="normal")
            self.cancel_btn.config(state="disabled")
            self.progress_var.set(0)
    
    def log_analysis_message(self, message: str):
        """Log message to analysis status"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.analysis_status_text.insert(tk.END, log_entry)
        self.analysis_status_text.see(tk.END)
    
    def clear_analysis_log(self):
        """Clear analysis log"""
        self.analysis_status_text.delete("1.0", tk.END)
    
    def set_progress(self, progress: int):
        """Set analysis progress"""
        self.progress_var.set(progress)
