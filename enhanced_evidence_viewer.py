#!/usr/bin/env python3
"""
Enhanced Evidence Viewer - Interactive Evidence Review System
Thoughtful data examination with clickable media, detailed views, and smart organization
"""

import sys
import os
import subprocess
import webbrowser
from pathlib import Path
import json
import datetime
import threading
import queue
from typing import Dict, List, Any, Optional
import tempfile
import shutil

# GUI Framework
try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox, scrolledtext
    from tkinter import font as tkfont
    import tkinter.font as tkFont
except ImportError:
    print("Tkinter not available. Please install tkinter")
    sys.exit(1)

# Try to import PIL for image viewing
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
    print("[OK] PIL available for image viewing")
except ImportError:
    PIL_AVAILABLE = False
    print("[INFO] PIL not available - will use system viewer for images")

class MediaViewer:
    """Enhanced media viewer with preview capabilities"""
    
    def __init__(self, parent_gui):
        self.parent = parent_gui
        self.temp_dir = Path(tempfile.mkdtemp(prefix="ghost_media_"))
        
    def view_image(self, image_path, image_data=None):
        """View image with metadata overlay"""
        try:
            if PIL_AVAILABLE:
                self._view_image_with_pil(image_path, image_data)
            else:
                self._view_image_with_system(image_path)
        except Exception as e:
            messagebox.showerror("Image Viewer Error", f"Cannot view image: {e}")
    
    def _view_image_with_pil(self, image_path, image_data):
        """View image using PIL with metadata overlay"""
        viewer_window = tk.Toplevel(self.parent.root)
        viewer_window.title(f"Image Viewer - {Path(image_path).name}")
        viewer_window.geometry("1000x700")
        
        # Create main frame
        main_frame = ttk.Frame(viewer_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Image frame (left side)
        image_frame = ttk.Frame(main_frame)
        image_frame.pack(side="left", fill="both", expand=True)
        
        # Try to load and display image
        try:
            if os.path.exists(image_path):
                img = Image.open(image_path)
                
                # Resize image to fit display
                display_size = (600, 400)
                img.thumbnail(display_size, Image.Resampling.LANCZOS)
                
                photo = ImageTk.PhotoImage(img)
                
                # Image label
                img_label = ttk.Label(image_frame, image=photo)
                img_label.image = photo  # Keep a reference
                img_label.pack(pady=10)
                
                # Image info
                info_text = f"Original Size: {img.size[0]} x {img.size[1]}\n"
                info_text += f"File: {Path(image_path).name}"
                ttk.Label(image_frame, text=info_text).pack()
                
            else:
                ttk.Label(image_frame, text="Image file not found\nUsing metadata only").pack(pady=50)
                
        except Exception as e:
            ttk.Label(image_frame, text=f"Cannot load image:\n{e}").pack(pady=50)
        
        # Metadata frame (right side)
        metadata_frame = ttk.LabelFrame(main_frame, text="Image Metadata")
        metadata_frame.pack(side="right", fill="y", padx=(10, 0))
        
        # Metadata display
        metadata_text = scrolledtext.ScrolledText(metadata_frame, width=40, height=30, font=('Consolas', 9))
        metadata_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Populate metadata
        if image_data:
            metadata_content = self._format_image_metadata(image_data)
            metadata_text.insert("1.0", metadata_content)
        
        # Action buttons
        button_frame = ttk.Frame(viewer_window)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(button_frame, text="Open in System Viewer", 
                  command=lambda: self._view_image_with_system(image_path)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Show in Explorer", 
                  command=lambda: self._show_in_explorer(image_path)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Export Metadata", 
                  command=lambda: self._export_image_metadata(image_data)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Close", 
                  command=viewer_window.destroy).pack(side="right", padx=5)
    
    def _view_image_with_system(self, image_path):
        """Open image with system default viewer"""
        try:
            if os.path.exists(image_path):
                if sys.platform.startswith('win'):
                    os.startfile(image_path)
                elif sys.platform.startswith('darwin'):
                    subprocess.run(['open', image_path])
                else:
                    subprocess.run(['xdg-open', image_path])
            else:
                messagebox.showwarning("File Not Found", f"Image file not found:\n{image_path}")
        except Exception as e:
            messagebox.showerror("System Viewer Error", f"Cannot open image: {e}")
    
    def _format_image_metadata(self, image_data):
        """Format image metadata for display"""
        metadata = "IMAGE FORENSIC METADATA\n"
        metadata += "=" * 30 + "\n\n"
        
        # Basic file info
        metadata += "FILE INFORMATION:\n"
        metadata += f"Filename: {image_data.get('filename', 'Unknown')}\n"
        metadata += f"Path: {image_data.get('path', 'Unknown')}\n"
        metadata += f"Size: {self._format_file_size(image_data.get('size', 0))}\n"
        metadata += f"Modified: {image_data.get('date_modified', 'Unknown')}\n"
        metadata += f"Created: {image_data.get('date_created', 'Unknown')}\n\n"
        
        # EXIF data
        exif = image_data.get('exif', {})
        if exif:
            metadata += "EXIF DATA:\n"
            
            # Camera info
            if exif.get('camera_make') or exif.get('camera_model'):
                metadata += f"Camera: {exif.get('camera_make', '')} {exif.get('camera_model', '')}\n"
            
            # Technical details
            if exif.get('iso_speed'):
                metadata += f"ISO: {exif.get('iso_speed')}\n"
            if exif.get('f_number'):
                metadata += f"F-Stop: f/{exif.get('f_number')}\n"
            if exif.get('exposure_time'):
                metadata += f"Shutter: {exif.get('exposure_time')}\n"
            if exif.get('focal_length'):
                metadata += f"Focal Length: {exif.get('focal_length')}mm\n"
            
            # GPS location
            if exif.get('gps_latitude') and exif.get('gps_longitude'):
                metadata += f"\nGPS LOCATION:\n"
                metadata += f"Latitude: {exif.get('gps_latitude')}\n"
                metadata += f"Longitude: {exif.get('gps_longitude')}\n"
                metadata += f"Map Link: https://maps.google.com/maps?q={exif.get('gps_latitude')},{exif.get('gps_longitude')}\n"
            
            # Other EXIF
            metadata += f"\nOther EXIF:\n"
            for key, value in exif.items():
                if key not in ['camera_make', 'camera_model', 'iso_speed', 'f_number', 
                              'exposure_time', 'focal_length', 'gps_latitude', 'gps_longitude']:
                    metadata += f"{key}: {value}\n"
        
        # Forensic analysis
        metadata += f"\nFORENSIC ANALYSIS:\n"
        if image_data.get('md5_hash'):
            metadata += f"MD5: {image_data.get('md5_hash')}\n"
        if image_data.get('sha256_hash'):
            metadata += f"SHA256: {image_data.get('sha256_hash')}\n"
        
        metadata += f"Deleted: {'Yes' if image_data.get('deleted') else 'No'}\n"
        if image_data.get('recovery_source'):
            metadata += f"Recovery Source: {image_data.get('recovery_source')}\n"
        
        return metadata
    
    def view_video(self, video_path, video_data=None):
        """View video with metadata"""
        viewer_window = tk.Toplevel(self.parent.root)
        viewer_window.title(f"Video Viewer - {Path(video_path).name}")
        viewer_window.geometry("800x600")
        
        # Main frame
        main_frame = ttk.Frame(viewer_window, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Video info
        info_frame = ttk.LabelFrame(main_frame, text="Video Information")
        info_frame.pack(fill="x", pady=(0, 10))
        
        if video_data:
            info_text = f"File: {video_data.get('filename', 'Unknown')}\n"
            info_text += f"Size: {self._format_file_size(video_data.get('size', 0))}\n"
            info_text += f"Duration: {self._format_duration(video_data.get('duration', 0))}\n"
            info_text += f"Resolution: {video_data.get('width', '?')}x{video_data.get('height', '?')}\n"
            info_text += f"Created: {video_data.get('date_created', 'Unknown')}"
            
            ttk.Label(info_frame, text=info_text).pack(anchor="w", padx=10, pady=5)
        
        # Metadata frame
        metadata_frame = ttk.LabelFrame(main_frame, text="Video Metadata")
        metadata_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        metadata_text = scrolledtext.ScrolledText(metadata_frame, font=('Consolas', 9))
        metadata_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        if video_data:
            metadata_content = self._format_video_metadata(video_data)
            metadata_text.insert("1.0", metadata_content)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="Play Video", 
                  command=lambda: self._play_video(video_path)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Show in Explorer", 
                  command=lambda: self._show_in_explorer(video_path)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Export Metadata", 
                  command=lambda: self._export_video_metadata(video_data)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Close", 
                  command=viewer_window.destroy).pack(side="right", padx=5)
    
    def _format_video_metadata(self, video_data):
        """Format video metadata for display"""
        metadata = "VIDEO FORENSIC METADATA\n"
        metadata += "=" * 30 + "\n\n"
        
        # Basic info
        metadata += "FILE INFORMATION:\n"
        metadata += f"Filename: {video_data.get('filename', 'Unknown')}\n"
        metadata += f"Path: {video_data.get('path', 'Unknown')}\n"
        metadata += f"Size: {self._format_file_size(video_data.get('size', 0))}\n"
        metadata += f"Duration: {self._format_duration(video_data.get('duration', 0))}\n"
        metadata += f"Created: {video_data.get('date_created', 'Unknown')}\n"
        metadata += f"Modified: {video_data.get('date_modified', 'Unknown')}\n\n"
        
        # Technical details
        metadata += "TECHNICAL DETAILS:\n"
        if video_data.get('width') and video_data.get('height'):
            metadata += f"Resolution: {video_data.get('width')}x{video_data.get('height')}\n"
        if video_data.get('fps'):
            metadata += f"Frame Rate: {video_data.get('fps')} fps\n"
        if video_data.get('codec'):
            metadata += f"Codec: {video_data.get('codec')}\n"
        if video_data.get('bitrate'):
            metadata += f"Bitrate: {video_data.get('bitrate')}\n"
        
        # Location data
        if video_data.get('gps_latitude') and video_data.get('gps_longitude'):
            metadata += f"\nGPS LOCATION:\n"
            metadata += f"Latitude: {video_data.get('gps_latitude')}\n"
            metadata += f"Longitude: {video_data.get('gps_longitude')}\n"
            metadata += f"Map Link: https://maps.google.com/maps?q={video_data.get('gps_latitude')},{video_data.get('gps_longitude')}\n"
        
        # Forensic data
        metadata += f"\nFORENSIC ANALYSIS:\n"
        if video_data.get('md5_hash'):
            metadata += f"MD5: {video_data.get('md5_hash')}\n"
        if video_data.get('sha256_hash'):
            metadata += f"SHA256: {video_data.get('sha256_hash')}\n"
        
        metadata += f"Deleted: {'Yes' if video_data.get('deleted') else 'No'}\n"
        
        return metadata
    
    def _play_video(self, video_path):
        """Play video with system default player"""
        try:
            if os.path.exists(video_path):
                if sys.platform.startswith('win'):
                    os.startfile(video_path)
                elif sys.platform.startswith('darwin'):
                    subprocess.run(['open', video_path])
                else:
                    subprocess.run(['xdg-open', video_path])
            else:
                messagebox.showwarning("File Not Found", f"Video file not found:\n{video_path}")
        except Exception as e:
            messagebox.showerror("Video Player Error", f"Cannot play video: {e}")
    
    def _show_in_explorer(self, file_path):
        """Show file in system file explorer"""
        try:
            if os.path.exists(file_path):
                if sys.platform.startswith('win'):
                    subprocess.run(['explorer', '/select,', file_path])
                elif sys.platform.startswith('darwin'):
                    subprocess.run(['open', '-R', file_path])
                else:
                    subprocess.run(['xdg-open', os.path.dirname(file_path)])
            else:
                messagebox.showwarning("File Not Found", f"File not found:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Explorer Error", f"Cannot show in explorer: {e}")
    
    def _format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if not isinstance(size_bytes, (int, float)) or size_bytes <= 0:
            return "0 B"
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    def _format_duration(self, seconds):
        """Format duration from seconds"""
        if not isinstance(seconds, (int, float)) or seconds <= 0:
            return "0:00"
        
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes}:{secs:02d}"
    
    def _export_image_metadata(self, image_data):
        """Export image metadata to file"""
        if not image_data:
            messagebox.showinfo("No Data", "No metadata available to export")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Export Image Metadata"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self._format_image_metadata(image_data))
                messagebox.showinfo("Success", f"Metadata exported to {filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export metadata: {e}")
    
    def _export_video_metadata(self, video_data):
        """Export video metadata to file"""
        if not video_data:
            messagebox.showinfo("No Data", "No metadata available to export")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Export Video Metadata"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self._format_video_metadata(video_data))
                messagebox.showinfo("Success", f"Metadata exported to {filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export metadata: {e}")

class DetailedMessageViewer:
    """Enhanced message viewer with conversation threading"""
    
    def __init__(self, parent_gui):
        self.parent = parent_gui
    
    def view_conversation(self, contact, messages):
        """View complete conversation with a contact"""
        conv_window = tk.Toplevel(self.parent.root)
        conv_window.title(f"Conversation with {contact}")
        conv_window.geometry("800x600")
        
        # Main frame
        main_frame = ttk.Frame(conv_window, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Conversation info
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(info_frame, text=f"Conversation with: {contact}", 
                 font=('Arial', 12, 'bold')).pack(side="left")
        ttk.Label(info_frame, text=f"Messages: {len(messages)}", 
                 font=('Arial', 10)).pack(side="right")
        
        # Messages frame with scrollbar
        msg_frame = ttk.Frame(main_frame)
        msg_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Canvas and scrollbar for messages
        canvas = tk.Canvas(msg_frame, bg='white')
        scrollbar = ttk.Scrollbar(msg_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Display messages
        for i, message in enumerate(messages):
            self._create_message_bubble(scrollable_frame, message, i)
        
        # Update scroll region
        scrollable_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="Export Conversation", 
                  command=lambda: self._export_conversation(contact, messages)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Search in Conversation", 
                  command=lambda: self._search_conversation(messages)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Close", 
                  command=conv_window.destroy).pack(side="right", padx=5)
    
    def _create_message_bubble(self, parent, message, index):
        """Create a message bubble in the conversation"""
        # Message container
        msg_container = ttk.Frame(parent)
        msg_container.pack(fill="x", padx=5, pady=2)
        
        # Determine message direction and styling
        is_outgoing = message.get('is_from_me', False)
        bg_color = "#DCF8C6" if is_outgoing else "#FFFFFF"  # Green for outgoing, white for incoming
        
        # Message frame
        msg_frame = tk.Frame(msg_container, bg=bg_color, relief="raised", bd=1)
        
        if is_outgoing:
            msg_frame.pack(side="right", anchor="e", padx=(50, 0))
        else:
            msg_frame.pack(side="left", anchor="w", padx=(0, 50))
        
        # Message header
        header_text = f"{'You' if is_outgoing else message.get('contact', 'Unknown')} • {message.get('timestamp', 'Unknown time')}"
        header_label = tk.Label(msg_frame, text=header_text, bg=bg_color, 
                               font=('Arial', 8), fg='gray')
        header_label.pack(anchor="w", padx=5, pady=(2, 0))
        
        # Message text
        msg_text = message.get('text', '')
        if len(msg_text) > 500:  # Truncate very long messages
            msg_text = msg_text[:500] + "... [Click to view full]"
        
        text_label = tk.Label(msg_frame, text=msg_text, bg=bg_color, 
                             font=('Arial', 10), wraplength=300, justify="left")
        text_label.pack(anchor="w", padx=5, pady=(0, 2))
        
        # Click handler for full message view
        text_label.bind("<Button-1>", lambda e: self._view_full_message(message))
        
        # Keyword highlighting
        keywords = message.get('keywords_found', [])
        if keywords:
            keyword_label = tk.Label(msg_frame, text=f"🔍 Keywords: {', '.join(keywords)}", 
                                    bg=bg_color, font=('Arial', 8, 'italic'), fg='red')
            keyword_label.pack(anchor="w", padx=5, pady=(0, 2))
    
    def _view_full_message(self, message):
        """View full message in detail window"""
        detail_window = tk.Toplevel(self.parent.root)
        detail_window.title("Message Details")
        detail_window.geometry("600x400")
        
        # Main frame
        main_frame = ttk.Frame(detail_window, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Message details
        details_text = scrolledtext.ScrolledText(main_frame, font=('Arial', 10))
        details_text.pack(fill="both", expand=True, pady=(0, 10))
        
        # Format message details
        details_content = f"MESSAGE DETAILS\n"
        details_content += "=" * 30 + "\n\n"
        details_content += f"Contact: {message.get('contact', 'Unknown')}\n"
        details_content += f"Timestamp: {message.get('timestamp', 'Unknown')}\n"
        details_content += f"Direction: {'Outgoing' if message.get('is_from_me') else 'Incoming'}\n"
        details_content += f"Service: {message.get('service', 'Unknown')}\n"
        details_content += f"Character Count: {len(message.get('text', ''))}\n"
        
        keywords = message.get('keywords_found', [])
        if keywords:
            details_content += f"Keywords Found: {', '.join(keywords)}\n"
        
        details_content += f"\nMESSAGE TEXT:\n"
        details_content += "-" * 20 + "\n"
        details_content += message.get('text', 'No text available')
        
        details_text.insert("1.0", details_content)
        
        # Close button
        ttk.Button(main_frame, text="Close", command=detail_window.destroy).pack()
    
    def _export_conversation(self, contact, messages):
        """Export conversation to file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("HTML files", "*.html"), ("All files", "*.*")],
            title=f"Export Conversation with {contact}"
        )
        
        if not filename:
            return
        
        try:
            if filename.endswith('.html'):
                self._export_conversation_html(filename, contact, messages)
            else:
                self._export_conversation_text(filename, contact, messages)
            
            messagebox.showinfo("Success", f"Conversation exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export conversation: {e}")
    
    def _export_conversation_text(self, filename, contact, messages):
        """Export conversation as text file"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"CONVERSATION WITH {contact.upper()}\n")
            f.write("=" * 50 + "\n\n")
            
            for message in messages:
                timestamp = message.get('timestamp', 'Unknown time')
                direction = 'You' if message.get('is_from_me') else contact
                text = message.get('text', '')
                
                f.write(f"[{timestamp}] {direction}:\n")
                f.write(f"{text}\n\n")
                
                keywords = message.get('keywords_found', [])
                if keywords:
                    f.write(f"*** Keywords: {', '.join(keywords)} ***\n\n")
    
    def _export_conversation_html(self, filename, contact, messages):
        """Export conversation as HTML file"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Conversation with {contact}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .message {{ margin: 10px 0; padding: 10px; border-radius: 10px; max-width: 70%; }}
        .outgoing {{ background-color: #DCF8C6; margin-left: auto; text-align: right; }}
        .incoming {{ background-color: #F1F1F1; }}
        .timestamp {{ font-size: 12px; color: gray; }}
        .keywords {{ font-size: 12px; color: red; font-style: italic; }}
    </style>
</head>
<body>
    <h1>Conversation with {contact}</h1>
    <hr>
"""
        
        for message in messages:
            is_outgoing = message.get('is_from_me', False)
            css_class = "outgoing" if is_outgoing else "incoming"
            sender = "You" if is_outgoing else contact
            
            html_content += f"""
    <div class="message {css_class}">
        <div class="timestamp">{sender} • {message.get('timestamp', 'Unknown time')}</div>
        <div>{message.get('text', '').replace(chr(10), '<br>')}</div>
"""
            keywords = message.get('keywords_found', [])
            if keywords:
                html_content += f'        <div class="keywords">Keywords: {", ".join(keywords)}</div>'
            
            html_content += "    </div>\n"
        
        html_content += """
</body>
</html>
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _search_conversation(self, messages):
        """Search within conversation"""
        search_window = tk.Toplevel(self.parent.root)
        search_window.title("Search Conversation")
        search_window.geometry("400x300")
        
        # Search frame
        search_frame = ttk.Frame(search_window, padding="10")
        search_frame.pack(fill="x")
        
        ttk.Label(search_frame, text="Search for:").pack(anchor="w")
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var, width=40)
        search_entry.pack(fill="x", pady=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(search_window, text="Search Results")
        results_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        results_text = scrolledtext.ScrolledText(results_frame, font=('Arial', 9))
        results_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        def perform_search():
            query = search_var.get().lower()
            if not query:
                return
            
            results_text.delete("1.0", tk.END)
            found_count = 0
            
            for i, message in enumerate(messages):
                text = message.get('text', '').lower()
                if query in text:
                    found_count += 1
                    timestamp = message.get('timestamp', 'Unknown')
                    sender = 'You' if message.get('is_from_me') else message.get('contact', 'Unknown')
                    
                    results_text.insert(tk.END, f"[{timestamp}] {sender}:\n")
                    
                    # Highlight search term
                    original_text = message.get('text', '')
                    highlighted = original_text.replace(search_var.get(), f"**{search_var.get()}**")
                    results_text.insert(tk.END, f"{highlighted}\n\n")
            
            if found_count == 0:
                results_text.insert(tk.END, "No matches found.")
            else:
                results_text.insert("1.0", f"Found {found_count} matches:\n" + "="*30 + "\n\n")
        
        # Search button
        ttk.Button(search_frame, text="Search", command=perform_search).pack(pady=5)
        
        # Close button
        ttk.Button(search_window, text="Close", command=search_window.destroy).pack(pady=5)

class InteractiveLocationViewer:
    """Enhanced location viewer with mapping capabilities"""
    
    def __init__(self, parent_gui):
        self.parent = parent_gui
    
    def view_location_timeline(self, locations):
        """View location timeline with map links"""
        timeline_window = tk.Toplevel(self.parent.root)
        timeline_window.title("Location Timeline")
        timeline_window.geometry("1000x600")
        
        # Main frame
        main_frame = ttk.Frame(timeline_window, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Controls frame
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(controls_frame, text="Location Timeline Analysis", 
                 font=('Arial', 14, 'bold')).pack(side="left")
        ttk.Label(controls_frame, text=f"Total Points: {len(locations)}", 
                 font=('Arial', 10)).pack(side="right")
        
        # Timeline frame
        timeline_frame = ttk.Frame(main_frame)
        timeline_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Create treeview for locations
        columns = ("Time", "Location", "Accuracy", "Duration", "Actions")
        location_tree = ttk.Treeview(timeline_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        location_tree.heading("Time", text="Timestamp")
        location_tree.heading("Location", text="Coordinates")
        location_tree.heading("Accuracy", text="Accuracy (m)")
        location_tree.heading("Duration", text="Duration")
        location_tree.heading("Actions", text="Actions")
        
        location_tree.column("Time", width=150)
        location_tree.column("Location", width=200)
        location_tree.column("Accuracy", width=100)
        location_tree.column("Duration", width=100)
        location_tree.column("Actions", width=150)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(timeline_frame, orient="vertical", command=location_tree.yview)
        h_scrollbar = ttk.Scrollbar(timeline_frame, orient="horizontal", command=location_tree.xview)
        location_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Populate location data
        for i, location in enumerate(locations):
            timestamp = location.get('timestamp', 'Unknown')
            lat = location.get('latitude', 'Unknown')
            lon = location.get('longitude', 'Unknown')
            accuracy = location.get('accuracy', 'Unknown')
            
            # Calculate duration (time spent at location)
            duration = self._calculate_location_duration(locations, i)
            
            coordinates = f"{lat}, {lon}" if lat != 'Unknown' and lon != 'Unknown' else 'Unknown'
            
            item_id = location_tree.insert("", "end", values=(
                timestamp, coordinates, accuracy, duration, "View on Map"
            ))
            
            # Store location data with item
            location_tree.set(item_id, "location_data", location)
        
        # Pack treeview and scrollbars
        location_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        timeline_frame.grid_rowconfigure(0, weight=1)
        timeline_frame.grid_columnconfigure(0, weight=1)
        
        # Bind double-click to view on map
        def on_location_double_click(event):
            item = location_tree.selection()[0]
            location_data = location_tree.set(item, "location_data")
            if location_data:
                self._open_location_on_map(eval(location_data))
        
        location_tree.bind("<Double-1>", on_location_double_click)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="Export Timeline", 
                  command=lambda: self._export_location_timeline(locations)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="View All on Map", 
                  command=lambda: self._view_all_locations_on_map(locations)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Analyze Movement Patterns", 
                  command=lambda: self._analyze_movement_patterns(locations)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Close", 
                  command=timeline_window.destroy).pack(side="right", padx=5)
    
    def _calculate_location_duration(self, locations, index):
        """Calculate how long device stayed at a location"""
        # Simple duration calculation - would be more sophisticated in real implementation
        return "Unknown"  # Placeholder
    
    def _open_location_on_map(self, location):
        """Open location on Google Maps"""
        try:
            lat = location.get('latitude')
            lon = location.get('longitude')
            
            if lat and lon:
                map_url = f"https://maps.google.com/maps?q={lat},{lon}&z=17"
                webbrowser.open(map_url)
            else:
                messagebox.showwarning("No Location", "No GPS coordinates available for this location")
        except Exception as e:
            messagebox.showerror("Map Error", f"Cannot open map: {e}")
    
    def _view_all_locations_on_map(self, locations):
        """Create a map with all locations"""
        try:
            # Create a simple HTML map file
            html_content = self._generate_locations_map_html(locations)
            
            # Save to temp file and open
            temp_file = self.parent.temp_dir / "locations_map.html"
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            webbrowser.open(f"file://{temp_file}")
            
        except Exception as e:
            messagebox.showerror("Map Error", f"Cannot create map: {e}")
    
    def _generate_locations_map_html(self, locations):
        """Generate HTML map with all locations"""
        # Filter locations with valid GPS coordinates
        valid_locations = [loc for loc in locations 
                         if loc.get('latitude') and loc.get('longitude')]
        
        if not valid_locations:
            return "<html><body><h1>No valid GPS coordinates found</h1></body></html>"
        
        # Calculate center point
        avg_lat = sum(float(loc['latitude']) for loc in valid_locations) / len(valid_locations)
        avg_lon = sum(float(loc['longitude']) for loc in valid_locations) / len(valid_locations)
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>GHOST Location Timeline</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
    <style>
        body {{ margin: 0; font-family: Arial, sans-serif; }}
        #map {{ height: 100vh; width: 100%; }}
        .info-panel {{ position: absolute; top: 10px; right: 10px; background: white; 
                       padding: 10px; border-radius: 5px; z-index: 1000; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }}
    </style>
</head>
<body>
    <div class="info-panel">
        <h3>GHOST Location Analysis</h3>
        <p><strong>Total Locations:</strong> {len(valid_locations)}</p>
        <p><strong>Time Span:</strong> Analysis Period</p>
        <p>Click markers for details</p>
    </div>
    <div id="map"></div>
    
    <script>
        var map = L.map('map').setView([{avg_lat}, {avg_lon}], 13);
        
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '© OpenStreetMap contributors'
        }}).addTo(map);
        
        var locations = [
"""
        
        # Add location markers
        for i, location in enumerate(valid_locations):
            lat = location.get('latitude')
            lon = location.get('longitude')
            timestamp = location.get('timestamp', 'Unknown time')
            accuracy = location.get('accuracy', 'Unknown')
            
            html_content += f"""
            {{
                lat: {lat},
                lng: {lon},
                timestamp: "{timestamp}",
                accuracy: "{accuracy}",
                index: {i + 1}
            }},"""
        
        html_content += """
        ];
        
        locations.forEach(function(location, index) {
            var marker = L.marker([location.lat, location.lng]).addTo(map);
            var popupContent = '<b>Location #' + location.index + '</b><br>' +
                              'Time: ' + location.timestamp + '<br>' +
                              'Coordinates: ' + location.lat + ', ' + location.lng + '<br>' +
                              'Accuracy: ' + location.accuracy + 'm';
            marker.bindPopup(popupContent);
        });
        
        // Create polyline connecting locations (movement path)
        var latlngs = locations.map(function(loc) { return [loc.lat, loc.lng]; });
        var polyline = L.polyline(latlngs, {color: 'red', weight: 3, opacity: 0.7}).addTo(map);
        
        // Fit map to show all locations
        if (locations.length > 0) {
            var group = new L.featureGroup(locations.map(function(loc) {
                return L.marker([loc.lat, loc.lng]);
            }));
            map.fitBounds(group.getBounds().pad(0.1));
        }
    </script>
</body>
</html>
"""
        
        return html_content
    
    def _analyze_movement_patterns(self, locations):
        """Analyze movement patterns from location data"""
        analysis_window = tk.Toplevel(self.parent.root)
        analysis_window.title("Movement Pattern Analysis")
        analysis_window.geometry("600x500")
        
        # Main frame
        main_frame = ttk.Frame(analysis_window, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Analysis results
        analysis_text = scrolledtext.ScrolledText(main_frame, font=('Consolas', 9))
        analysis_text.pack(fill="both", expand=True, pady=(0, 10))
        
        # Perform analysis
        analysis_results = self._perform_movement_analysis(locations)
        analysis_text.insert("1.0", analysis_results)
        
        # Close button
        ttk.Button(main_frame, text="Close", command=analysis_window.destroy).pack()
    
    def _perform_movement_analysis(self, locations):
        """Perform movement pattern analysis"""
        analysis = "MOVEMENT PATTERN ANALYSIS\n"
        analysis += "=" * 40 + "\n\n"
        
        valid_locations = [loc for loc in locations 
                         if loc.get('latitude') and loc.get('longitude')]
        
        analysis += f"Total Location Points: {len(locations)}\n"
        analysis += f"Valid GPS Coordinates: {len(valid_locations)}\n\n"
        
        if len(valid_locations) < 2:
            analysis += "Insufficient location data for movement analysis.\n"
            return analysis
        
        # Calculate basic statistics
        latitudes = [float(loc['latitude']) for loc in valid_locations]
        longitudes = [float(loc['longitude']) for loc in valid_locations]
        
        lat_range = max(latitudes) - min(latitudes)
        lon_range = max(longitudes) - min(longitudes)
        
        analysis += f"GEOGRAPHICAL SPAN:\n"
        analysis += f"Latitude Range: {lat_range:.6f} degrees\n"
        analysis += f"Longitude Range: {lon_range:.6f} degrees\n\n"
        
        # Identify frequently visited areas
        analysis += f"MOVEMENT CHARACTERISTICS:\n"
        if lat_range < 0.01 and lon_range < 0.01:  # ~1km range
            analysis += "• Limited geographical movement (local area)\n"
        elif lat_range < 0.1 and lon_range < 0.1:  # ~10km range
            analysis += "• Moderate geographical movement (city/town area)\n"
        else:
            analysis += "• Extensive geographical movement (regional/long distance)\n"
        
        # Time-based analysis would go here
        analysis += f"\nFREQUENT LOCATIONS:\n"
        analysis += "• Analysis would identify clusters of repeated visits\n"
        analysis += "• Home/work location detection\n"
        analysis += "• Unusual location visits\n\n"
        
        analysis += f"INVESTIGATIVE NOTES:\n"
        analysis += "• Review locations during specific time periods\n"
        analysis += "• Cross-reference with communication timeline\n"
        analysis += "• Identify locations of interest for case\n"
        
        return analysis
    
    def _export_location_timeline(self, locations):
        """Export location timeline to file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("KML files", "*.kml"), ("All files", "*.*")],
            title="Export Location Timeline"
        )
        
        if not filename:
            return
        
        try:
            if filename.endswith('.kml'):
                self._export_locations_kml(filename, locations)
            else:
                self._export_locations_csv(filename, locations)
            
            messagebox.showinfo("Success", f"Location timeline exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export timeline: {e}")
    
    def _export_locations_csv(self, filename, locations):
        """Export locations to CSV file"""
        import csv
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['timestamp', 'latitude', 'longitude', 'accuracy', 'altitude', 
                         'speed', 'bearing', 'source', 'notes']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for location in locations:
                writer.writerow({
                    'timestamp': location.get('timestamp', ''),
                    'latitude': location.get('latitude', ''),
                    'longitude': location.get('longitude', ''),
                    'accuracy': location.get('accuracy', ''),
                    'altitude': location.get('altitude', ''),
                    'speed': location.get('speed', ''),
                    'bearing': location.get('bearing', ''),
                    'source': location.get('source', 'Unknown'),
                    'notes': location.get('notes', '')
                })
    
    def _export_locations_kml(self, filename, locations):
        """Export locations to KML file for Google Earth"""
        kml_content = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>GHOST Location Timeline</name>
    <description>Forensic location analysis from GHOST</description>
    
    <Style id="locationIcon">
      <IconStyle>
        <Icon>
          <href>http://maps.google.com/mapfiles/kml/pushpin/red-pushpin.png</href>
        </Icon>
      </IconStyle>
    </Style>
"""
        
        for i, location in enumerate(locations):
            if location.get('latitude') and location.get('longitude'):
                lat = location.get('latitude')
                lon = location.get('longitude')
                timestamp = location.get('timestamp', 'Unknown')
                accuracy = location.get('accuracy', 'Unknown')
                
                kml_content += f"""
    <Placemark>
      <name>Location {i + 1}</name>
      <description>
        Time: {timestamp}
        Accuracy: {accuracy}m
      </description>
      <styleUrl>#locationIcon</styleUrl>
      <Point>
        <coordinates>{lon},{lat},0</coordinates>
      </Point>
    </Placemark>"""
        
        kml_content += """
  </Document>
</kml>"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(kml_content)

class EnhancedEvidenceGUI:
    """Enhanced Evidence GUI with interactive viewing capabilities"""
    
    def __init__(self, base_gui):
        self.base_gui = base_gui
        self.media_viewer = MediaViewer(base_gui)
        self.message_viewer = DetailedMessageViewer(base_gui)
        self.location_viewer = InteractiveLocationViewer(base_gui)
        
        # Create temp directory for this session
        self.temp_dir = Path(tempfile.mkdtemp(prefix="ghost_evidence_"))
        base_gui.temp_dir = self.temp_dir
    
    def enhance_multimedia_view(self, photos_tree, videos_tree):
        """Enhance multimedia trees with clickable media"""
        # Bind double-click events
        photos_tree.bind("<Double-1>", lambda e: self._on_photo_double_click(photos_tree))
        videos_tree.bind("<Double-1>", lambda e: self._on_video_double_click(videos_tree))
        
        # Add context menus
        self._add_multimedia_context_menu(photos_tree, "photo")
        self._add_multimedia_context_menu(videos_tree, "video")
    
    def _on_photo_double_click(self, tree):
        """Handle photo double-click"""
        selection = tree.selection()
        if selection:
            item = selection[0]
            values = tree.item(item, "values")
            if values:
                filename = values[0]  # Assuming filename is first column
                # Get full photo data from analysis results
                photo_data = self._find_media_data(filename, "photos")
                if photo_data:
                    self.media_viewer.view_image(photo_data.get('path', ''), photo_data)
    
    def _on_video_double_click(self, tree):
        """Handle video double-click"""
        selection = tree.selection()
        if selection:
            item = selection[0]
            values = tree.item(item, "values")
            if values:
                filename = values[0]
                video_data = self._find_media_data(filename, "videos")
                if video_data:
                    self.media_viewer.view_video(video_data.get('path', ''), video_data)
    
    def _find_media_data(self, filename, media_type):
        """Find media data from analysis results"""
        if not self.base_gui.analysis_results:
            return None
        
        raw_data = self.base_gui.analysis_results.get('raw_evidence_data', {})
        media_list = raw_data.get(media_type, [])
        
        for media in media_list:
            if media.get('filename') == filename:
                return media
        
        return None
    
    def _add_multimedia_context_menu(self, tree, media_type):
        """Add context menu to multimedia tree"""
        context_menu = tk.Menu(tree, tearoff=0)
        context_menu.add_command(label=f"View {media_type.title()}", 
                               command=lambda: self._context_view_media(tree, media_type))
        context_menu.add_command(label="Show in Explorer", 
                               command=lambda: self._context_show_in_explorer(tree))
        context_menu.add_command(label="Export Metadata", 
                               command=lambda: self._context_export_metadata(tree, media_type))
        
        def show_context_menu(event):
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
        
        tree.bind("<Button-3>", show_context_menu)  # Right-click
    
    def enhance_messages_view(self, messages_tree):
        """Enhance messages view with conversation threading"""
        # Bind double-click for conversation view
        messages_tree.bind("<Double-1>", lambda e: self._on_message_double_click(messages_tree))
        
        # Add context menu
        context_menu = tk.Menu(messages_tree, tearoff=0)
        context_menu.add_command(label="View Conversation", 
                               command=lambda: self._context_view_conversation(messages_tree))
        context_menu.add_command(label="View Message Details", 
                               command=lambda: self._context_view_message_details(messages_tree))
        context_menu.add_command(label="Search Similar Messages", 
                               command=lambda: self._context_search_similar(messages_tree))
        
        def show_context_menu(event):
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
        
        messages_tree.bind("<Button-3>", show_context_menu)
    
    def _on_message_double_click(self, tree):
        """Handle message double-click to show conversation"""
        selection = tree.selection()
        if selection:
            item = selection[0]
            values = tree.item(item, "values")
            if values:
                contact = values[1]  # Assuming contact is second column
                self._show_conversation_with_contact(contact)
    
    def _show_conversation_with_contact(self, contact):
        """Show full conversation with specific contact"""
        if not self.base_gui.analysis_results:
            return
        
        # Get all messages with this contact
        raw_data = self.base_gui.analysis_results.get('raw_evidence_data', {})
        all_messages = raw_data.get('messages', [])
        
        contact_messages = [msg for msg in all_messages 
                          if msg.get('contact') == contact]
        
        if contact_messages:
            # Sort by timestamp
            contact_messages.sort(key=lambda x: x.get('timestamp', ''))
            self.message_viewer.view_conversation(contact, contact_messages)
        else:
            messagebox.showinfo("No Messages", f"No messages found with {contact}")
    
    def enhance_locations_view(self, locations_tree):
        """Enhance locations view with mapping"""
        # Bind double-click for map view
        locations_tree.bind("<Double-1>", lambda e: self._on_location_double_click(locations_tree))
        
        # Add context menu
        context_menu = tk.Menu(locations_tree, tearoff=0)
        context_menu.add_command(label="View on Map", 
                               command=lambda: self._context_view_on_map(locations_tree))
        context_menu.add_command(label="View Timeline", 
                               command=lambda: self._context_view_location_timeline())
        context_menu.add_command(label="Analyze Movement", 
                               command=lambda: self._context_analyze_movement())
        
        def show_context_menu(event):
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
        
        locations_tree.bind("<Button-3>", show_context_menu)
    
    def _on_location_double_click(self, tree):
        """Handle location double-click to show on map"""
        selection = tree.selection()
        if selection:
            item = selection[0]
            values = tree.item(item, "values")
            if len(values) >= 3:
                lat = values[1]  # Assuming lat is second column
                lon = values[2]  # Assuming lon is third column
                
                if lat != 'Unknown' and lon != 'Unknown':
                    map_url = f"https://maps.google.com/maps?q={lat},{lon}&z=17"
                    webbrowser.open(map_url)
    
    def _context_view_location_timeline(self):
        """Show location timeline view"""
        if not self.base_gui.analysis_results:
            return
        
        raw_data = self.base_gui.analysis_results.get('raw_evidence_data', {})
        locations = raw_data.get('locations', [])
        
        if locations:
            self.location_viewer.view_location_timeline(locations)
        else:
            messagebox.showinfo("No Data", "No location data available")
    
    def cleanup(self):
        """Cleanup temporary files"""
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"Warning: Could not cleanup temp directory: {e}")

# Integration function
def enhance_evidence_gui(base_gui_instance):
    """Enhance the base evidence GUI with interactive capabilities"""
    
    enhanced_gui = EnhancedEvidenceGUI(base_gui_instance)
    
    # Store reference for cleanup
    base_gui_instance.enhanced_gui = enhanced_gui
    
    # Enhance existing views when analysis results are updated
    original_update_multimedia = base_gui_instance.update_multimedia_data
    original_update_communications = base_gui_instance.update_communications_data
    original_update_locations = base_gui_instance.update_apps_locations_data
    
    def enhanced_update_multimedia(report):
        original_update_multimedia(report)
        if hasattr(base_gui_instance, 'photos_tree') and hasattr(base_gui_instance, 'videos_tree'):
            enhanced_gui.enhance_multimedia_view(base_gui_instance.photos_tree, 
                                               base_gui_instance.videos_tree)
    
    def enhanced_update_communications(report):
        original_update_communications(report)
        if hasattr(base_gui_instance, 'messages_tree'):
            enhanced_gui.enhance_messages_view(base_gui_instance.messages_tree)
    
    def enhanced_update_locations(report):
        original_update_locations(report)
        if hasattr(base_gui_instance, 'locations_tree'):
            enhanced_gui.enhance_locations_view(base_gui_instance.locations_tree)
    
    # Replace methods
    base_gui_instance.update_multimedia_data = enhanced_update_multimedia
    base_gui_instance.update_communications_data = enhanced_update_communications
    base_gui_instance.update_apps_locations_data = enhanced_update_locations
    
    # Add cleanup to window close
    original_on_closing = base_gui_instance.on_closing
    
    def enhanced_on_closing():
        enhanced_gui.cleanup()
        original_on_closing()
    
    base_gui_instance.on_closing = enhanced_on_closing
    base_gui_instance.root.protocol("WM_DELETE_WINDOW", enhanced_on_closing)
    
    print("✅ Enhanced evidence viewer integrated!")
    print("📸 Click photos/videos to view with metadata")
    print("💬 Double-click messages to see full conversations") 
    print("🗺️ Double-click locations to view on map")
    print("🎯 Right-click for context menus with more options")

# Usage: Add this to your evidence_gui_app.py:
# In your EvidenceAnalysisGUI.__init__ method, add after create_widgets():
# enhance_evidence_gui(self)
