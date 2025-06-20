```python
#!/usr/bin/env python3
"""
GHOST Evidence Analysis Interface
Graphical interface for forensic evidence analysis
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import json
import datetime
import threading
import queue
import sys
import os
from pathlib import Path
import time
try:
    from modules import ghost_forensic_suite
except ImportError:
    try:
        from modules import config_manager
        from modules import forensic_logger
    except ImportError as e:
        print(f"[ERROR] Could not load forensic modules: {e}")
        ghost_forensic_suite = None

from enhanced_forensic_exports import add_enhanced_export_methods, ForensicReportGenerator

class EvidenceAnalysisGUI:
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
        
        # Add enhanced export methods
        add_enhanced_export_methods(self)
        
        # Start update loops
        self.update_time()
        self.check_queues()

    def setup_main_window(self):
        self.root.title("GHOST Evidence Analysis Interface")
        self.root.geometry("1280x720")
        self.root.minsize(1024, 600)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

    def setup_styling(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TNotebook', tabposition='n')
        self.style.configure('TButton', padding=5)
        self.style.configure('TLabel', padding=3)
        self.style.configure('TFrame', padding=10)

    def create_widgets(self):
        # Main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

        # Notebook (tabs)
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=0, column=0, sticky="nsew")

        # Create tabs
        self.create_case_setup_tab()
        self.create_evidence_overview_tab()
        self.create_communications_tab()
        self.create_multimedia_tab()
        self.create_apps_locations_tab()
        self.create_reports_tab()

        # Status bar
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        
        ttk.Label(self.status_frame, text="Status:").grid(row=0, column=0, sticky="w")
        ttk.Label(self.status_frame, textvariable=self.status_var).grid(row=0, column=1, sticky="w")
        
        ttk.Label(self.status_frame, text="Progress:").grid(row=0, column=2, sticky="w", padx=(20, 0))
        self.progress_bar = ttk.Progressbar(self.status_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=3, sticky="ew", padx=(0, 20))
        
        ttk.Label(self.status_frame, textvariable=self.time_var).grid(row=0, column=4, sticky="e")
        
        self.status_frame.columnconfigure(3, weight=1)
        self.status_frame.columnconfigure(4, weight=1)

    def create_case_setup_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Case Setup")
        
        # Case Information
        info_frame = ttk.LabelFrame(tab, text="Case Information", padding=10)
        info_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        info_frame.columnconfigure(1, weight=1)
        
        ttk.Label(info_frame, text="Case Name:").grid(row=0, column=0, sticky="w")
        ttk.Entry(info_frame, textvariable=self.case_name).grid(row=0, column=1, sticky="ew", padx=5)
        
        ttk.Label(info_frame, text="Examiner Name:").grid(row=1, column=0, sticky="w")
        ttk.Entry(info_frame, textvariable=self.examiner_name).grid(row=1, column=1, sticky="ew", padx=5)
        
        ttk.Label(info_frame, text="Extraction Path:").grid(row=2, column=0, sticky="w")
        ttk.Entry(info_frame, textvariable=self.extraction_path).grid(row=2, column=1, sticky="ew", padx=5)
        ttk.Button(info_frame, text="Browse", command=self.browse_extraction_path).grid(row=2, column=2, padx=5)
        
        # Analysis Controls
        controls_frame = ttk.LabelFrame(tab, text="Analysis Controls", padding=10)
        controls_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        ttk.Button(controls_frame, text="Start Evidence Analysis", command=self.start_analysis).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(controls_frame, text="Cancel Analysis", command=self.cancel_analysis).grid(row=0, column=1, padx=5, pady=5)
        
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)

    def create_evidence_overview_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Evidence Overview")
        
        self.overview_text = tk.Text(tab, height=20, wrap="word")
        self.overview_text.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=self.overview_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.overview_text['yscrollcommand'] = scrollbar.set
        
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(0, weight=1)

    def create_communications_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Communications")
        
        # Call Logs
        calls_frame = ttk.LabelFrame(tab, text="Call Logs", padding=10)
        calls_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
        
        self.calls_listbox = tk.Listbox(calls_frame, height=10)
        self.calls_listbox.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(calls_frame, orient="vertical", command=self.calls_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.calls_listbox['yscrollcommand'] = scrollbar.set
        
        ttk.Button(calls_frame, text="Export Detailed Call Logs", command=lambda: self.export_detailed_call_logs()).grid(row=1, column=0, pady=5)
        
        # Messages
        messages_frame = ttk.LabelFrame(tab, text="Messages", padding=10)
        messages_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)
        
        self.messages_listbox = tk.Listbox(messages_frame, height=10)
        self.messages_listbox.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(messages_frame, orient="vertical", command=self.messages_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.messages_listbox['yscrollcommand'] = scrollbar.set
        
        # Export Buttons
        export_frame = ttk.Frame(tab)
        export_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        ttk.Button(export_frame, text="Export Complete Package", command=lambda: self.export_comprehensive_package()).grid(row=0, column=0, padx=5)
        ttk.Button(export_frame, text="Export Network Analysis", command=lambda: self.export_network_analysis()).grid(row=0, column=1, padx=5)
        ttk.Button(export_frame, text="Export Device Interactions", command=lambda: self.export_device_interactions()).grid(row=0, column=2, padx=5)
        
        tab.columnconfigure(0, weight=1)
        tab.columnconfigure(1, weight=1)
        tab.rowconfigure(0, weight=1)

    def create_multimedia_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Multimedia")
        
        self.multimedia_text = tk.Text(tab, height=20, wrap="word")
        self.multimedia_text.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=self.multimedia_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.multimedia_text['yscrollcommand'] = scrollbar.set
        
        ttk.Button(tab, text="Export Multimedia Inventory", command=lambda: self.export_multimedia_inventory()).grid(row=1, column=0, pady=5)
        
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(0, weight=1)

    def create_apps_locations_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Apps & Locations")
        
        self.apps_locations_text = tk.Text(tab, height=20, wrap="word")
        self.apps_locations_text.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=self.apps_locations_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.apps_locations_text['yscrollcommand'] = scrollbar.set
        
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(0, weight=1)

    def create_reports_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Reports")
        
        self.reports_text = tk.Text(tab, height=20, wrap="word")
        self.reports_text.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=self.reports_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.reports_text['yscrollcommand'] = scrollbar.set
        
        ttk.Button(tab, text="Generate Executive Summary", command=self.generate_executive_summary).grid(row=1, column=0, pady=5)
        ttk.Button(tab, text="Generate Detailed Report", command=self.generate_detailed_report).grid(row=2, column=0, pady=5)
        
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(0, weight=1)

    def browse_extraction_path(self):
        path = filedialog.askopenfilename(filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")])
        if not path:
            path = filedialog.askdirectory()
        if path:
            self.extraction_path.set(path)

    def start_analysis(self):
        if not self.case_name.get():
            messagebox.showerror("Error", "Please enter a case name")
            return
        if not self.examiner_name.get():
            messagebox.showerror("Error", "Please enter an examiner name")
            return
        if not self.extraction_path.get():
            messagebox.showerror("Error", "Please select an extraction path")
            return
            
        if self.analysis_thread and self.analysis_thread.is_alive():
            messagebox.showinfo("Info", "Analysis is already running")
            return
            
        self.status_var.set("Starting analysis...")
        self.progress_var.set(0)
        self.analysis_thread = threading.Thread(target=self.analysis_worker)
        self.analysis_thread.daemon = True
        self.analysis_thread.start()

    def cancel_analysis(self):
        if self.analysis_thread and self.analysis_thread.is_alive():
            messagebox.showinfo("Info", "Analysis cancellation not implemented")
        else:
            messagebox.showinfo("Info", "No analysis running")

    def analysis_worker(self):
        try:
            self.status_queue.put({'message': 'Initializing evidence analysis...'})
            self.progress_queue.put({'progress': 5, 'message': 'Starting analysis...'})
            
            if ghost_forensic_suite:
                suite = ghost_forensic_suite.FocusedForensicSuite(
                    case_name=self.case_name.get(),
                    examiner=self.examiner_name.get(),
                    source_path=self.extraction_path.get()
                )
                
                report = suite.run_analysis(
                    progress_callback=lambda p, m: self.progress_queue.put({'progress': p, 'message': m}),
                    status_callback=lambda m: self.status_queue.put({'message': m})
                )
                
                self.root.after(0, lambda: self.update_analysis_results(report))
            else:
                # Simulate results for testing
                report = {
                    'raw_evidence_data': {
                        'calls': [
                            {
                                'timestamp': '2025-06-19T10:00:00Z',
                                'address': '1234567890',
                                'duration': 300,
                                'type': 'incoming',
                                'contact': 'John Doe',
                                'service_provider': 'Verizon',
                                'cell_tower': 'TOWER123',
                                'latitude': '40.7128',
                                'longitude': '-74.0060',
                                'quality': 'Good',
                                'roaming': 'No',
                                'conference': False
                            }
                        ],
                        'photos': [
                            {
                                'filename': 'photo.jpg',
                                'size': 1048576,
                                'date_created': '2025-06-19T09:00:00Z',
                                'date_modified': '2025-06-19T09:00:00Z',
                                'path': '/photos/photo.jpg',
                                'exif': {
                                    'width': 1920,
                                    'height': 1080,
                                    'gps_latitude': '40.7128',
                                    'gps_longitude': '-74.0060',
                                    'camera_make': 'Canon',
                                    'camera_model': 'EOS R',
                                    'flash_fired': False
                                }
                            }
                        ],
                        'videos': [],
                        'audio': [],
                        'wifi_networks': [
                            {
                                'ssid': 'TestWiFi',
                                'bssid': '00:11:22:33:44:55',
                                'frequency': 2400,
                                'channel': 1,
                                'signal_strength': -60,
                                'security': 'WPA2',
                                'encryption': 'AES',
                                'connection_count': 50,
                                'data_usage': 500
                            }
                        ],
                        'cellular_networks': [],
                        'bluetooth_devices': [
                            {
                                'name': 'BT_Headset',
                                'device_id': 'BT123',
                                'mac_address': 'AA:BB:CC:DD:EE:FF',
                                'device_class': 'audio',
                                'paired': True,
                                'connection_count': 10,
                                'data_transferred': 100
                            }
                        ],
                        'usb_devices': [],
                        'nfc_interactions': [],
                        'airdrop_transfers': [],
                        'paired_devices': [],
                        'messages': [{'timestamp': '2025-06-19T10:05:00Z', 'contact': 'John Doe', 'text': 'Test message', 'is_from_me': True, 'service': 'SMS'}],
                        'contacts': [{'first_name': 'John', 'last_name': 'Doe', 'phone': '1234567890'}]
                    },
                    'evidence_summary': {
                        'communications': {'messages': 1, 'calls': 1, 'contacts': 1},
                        'multimedia': {'photos': 1, 'videos': 0},
                        'digital_activity': {'location_points': 0, 'app_data': 0, 'browser_records': 0, 'databases': 0}
                    },
                    'executive_summary': {
                        'priority_level': 'Low',
                        'priority_reason': 'Test data',
                        'evidence_types_found': ['Calls', 'Photos', 'WiFi', 'Bluetooth', 'Messages', 'Contacts'],
                        'key_statistics': {
                            'total_communications': 2,
                            'unique_contacts': 1,
                            'investigation_keywords': 0,
                            'multimedia_files': 1,
                            'location_points': 0
                        },
                        'immediate_actions': []
                    },
                    'communication_intelligence': {
                        'message_analysis': {'message_count': 1, 'unique_contacts': 1, 'keyword_mentions': {}},
                        'call_analysis': {'call_count': 1, 'unique_numbers': 1, 'total_duration_hours': 0.08},
                        'top_contacts': [{'contact': '1234567890', 'messages': 1, 'calls': 1}]
                    },
                    'app_intelligence': {'app_summary': {}},
                    'investigative_leads': [],
                    'case_information': {
                        'case_name': self.case_name.get(),
                        'examiner': self.examiner_name.get(),
                        'analysis_date': datetime.datetime.now().isoformat(),
                        'source_path': self.extraction_path.get() or 'Test',
                        'tool_version': 'GHOST v1.0'
                    }
                }
                
                self.progress_queue.put({'progress': 90, 'message': 'Generating report...'})
                self.root.after(0, lambda: self.update_analysis_results(report))
            
            self.progress_queue.put({'progress': 100, 'message': 'Analysis complete!'})
        
        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            self.root.after(0, lambda: self.analysis_error(error_msg))
        
        finally:
            self.root.after(0, self.analysis_complete)

    def update_analysis_results(self, report):
        self.analysis_results = report
        self.update_ui_with_results()

    def update_ui_with_results(self):
        # Clear existing content
        self.overview_text.delete(1.0, tk.END)
        self.calls_listbox.delete(0, tk.END)
        self.messages_listbox.delete(0, tk.END)
        self.multimedia_text.delete(1.0, tk.END)
        self.apps_locations_text.delete(1.0, tk.END)
        self.reports_text.delete(1.0, tk.END)
        
        # Update overview
        if self.analysis_results:
            summary = self.analysis_results.get('evidence_summary', {})
            overview_text = f"Evidence Summary:\n\n"
            overview_text += f"Communications:\n"
            overview_text += f"  Messages: {summary.get('communications', {}).get('messages', 0)}\n"
            overview_text += f"  Calls: {summary.get('communications', {}).get('calls', 0)}\n"
            overview_text += f"  Contacts: {summary.get('communications', {}).get('contacts', 0)}\n"
            overview_text += f"\nMultimedia:\n"
            overview_text += f"  Photos: {summary.get('multimedia', {}).get('photos', 0)}\n"
            overview_text += f"  Videos: {summary.get('multimedia', {}).get('videos', 0)}\n"
            overview_text += f"\nDigital Activity:\n"
            overview_text += f"  Location Points: {summary.get('digital_activity', {}).get('location_points', 0)}\n"
            overview_text += f"  App Data: {summary.get('digital_activity', {}).get('app_data', 0)}\n"
            self.overview_text.insert(tk.END, overview_text)
            
            # Update calls
            for call in self.analysis_results.get('raw_evidence_data', {}).get('calls', []):
                call_str = f"{call.get('timestamp', '')} - {call.get('contact', 'Unknown')} ({call.get('type', '')})"
                self.calls_listbox.insert(tk.END, call_str)
            
            # Update messages
            for msg in self.analysis_results.get('raw_evidence_data', {}).get('messages', []):
                msg_str = f"{msg.get('timestamp', '')} - {msg.get('contact', 'Unknown')}: {msg.get('text', '')}"
                self.messages_listbox.insert(tk.END, msg_str)
            
            # Update multimedia
            multimedia_text = "Multimedia Files:\n\n"
            for photo in self.analysis_results.get('raw_evidence_data', {}).get('photos', []):
                multimedia_text += f"Photo: {photo.get('filename', 'Unknown')} ({photo.get('size', 0)} bytes)\n"
            for video in self.analysis_results.get('raw_evidence_data', {}).get('videos', []):
                multimedia_text += f"Video: {video.get('filename', 'Unknown')} ({video.get('size', 0)} bytes)\n"
            self.multimedia_text.insert(tk.END, multimedia_text)
            
            # Update apps and locations
            apps_locations_text = "Apps & Locations:\n\n"
            for wifi in self.analysis_results.get('raw_evidence_data', {}).get('wifi_networks', []):
                apps_locations_text += f"WiFi: {wifi.get('ssid', 'Unknown')} (BSSID: {wifi.get('bssid', '')})\n"
            for loc in self.analysis_results.get('raw_evidence_data', {}).get('locations', []):
                apps_locations_text += f"Location: ({loc.get('latitude', '')}, {loc.get('longitude', '')})\n"
            self.apps_locations_text.insert(tk.END, apps_locations_text)

    def analysis_error(self, message):
        self.status_var.set(message)
        self.progress_var.set(0)
        messagebox.showerror("Analysis Error", message)

    def analysis_complete(self):
        self.status_var.set("Analysis complete")
        self.analysis_thread = None

    def generate_executive_summary(self):
        if not self.analysis_results:
            messagebox.showinfo("Info", "No analysis data available for report")
            return
            
        generator = ForensicReportGenerator(self.case_name.get(), self.examiner_name.get(), self.analysis_results)
        report = generator.generate_executive_summary_report()
        
        self.reports_text.delete(1.0, tk.END)
        self.reports_text.insert(tk.END, report)
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Executive Summary"
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(report)
                messagebox.showinfo("Success", f"Executive summary saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save report: {e}")

    def generate_detailed_report(self):
        if not self.analysis_results:
            messagebox.showinfo("Info", "No analysis data available for report")
            return
            
        generator = ForensicReportGenerator(self.case_name.get(), self.examiner_name.get(), self.analysis_results)
        report = generator.generate_detailed_report()
        
        self.reports_text.delete(1.0, tk.END)
        self.reports_text.insert(tk.END, report)
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Detailed Report"
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(report)
                messagebox.showinfo("Success", f"Detailed report saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save report: {e}")

    def update_time(self):
        self.time_var.set(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.root.after(1000, self.update_time)

    def check_queues(self):
        try:
            while True:
                status = self.status_queue.get_nowait()
                self.status_var.set(status.get('message', ''))
        except queue.Empty:
            pass
            
        try:
            while True:
                progress = self.progress_queue.get_nowait()
                self.progress_var.set(progress.get('progress', 0))
                self.status_var.set(progress.get('message', ''))
        except queue.Empty:
            pass
            
        self.root.after(100, self.check_queues)

def main():
    print("[INFO] Starting GHOST Evidence Analysis Interface...")
    app = EvidenceAnalysisGUI()
    app.root.mainloop()

if __name__ == "__main__":
    main()
```
