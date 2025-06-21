#!/usr/bin/env python3
"""
Simple StatusBar component for GHOST GUI
"""

import tkinter as tk
from tkinter import ttk
import datetime

class StatusBar(ttk.Frame):
    """Simple status bar for GHOST GUI"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Status message
        self.status_var = tk.StringVar()
        self.status_var.set("GHOST Ready")
        
        self.status_label = ttk.Label(
            self, 
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        # Time display
        self.time_var = tk.StringVar()
        self.time_label = ttk.Label(
            self,
            textvariable=self.time_var,
            relief=tk.SUNKEN
        )
        self.time_label.pack(side=tk.RIGHT, padx=2)
        
        # Update time
        self.update_time()
    
    def set_status(self, message: str):
        """Set status message"""
        self.status_var.set(message)
        self.update_idletasks()
    
    def update_time(self):
        """Update time display"""
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        self.time_var.set(current_time)
        self.after(1000, self.update_time)

# For backwards compatibility
class GHOSTStatusBar(StatusBar):
    pass
