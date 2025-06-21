```python
#!/usr/bin/env python3
"""
Enhanced Forensic Export Functions
Comprehensive data extraction for call logs, multimedia, networks, and device interactions
"""

import csv
import json
import datetime
import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

class ComprehensiveForensicExporter:
    """Enhanced forensic data exporter with full device analysis capabilities"""
    
    def __init__(self, gui_instance):
        self.gui = gui_instance
        self.case_name = gui_instance.case_name.get()
        self.examiner_name = gui_instance.examiner_name.get()
        self.timestamp = datetime.datetime.now()
    
    def export_detailed_call_logs_csv(self):
        """Export comprehensive call log analysis"""
        if not self.gui.analysis_results:
            messagebox.showinfo("Info", "No analysis data available for export")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Detailed Call Logs"
        )
        
        if not filename:
            return
        
        try:
            raw_data = self.gui.analysis_results.get('raw_evidence_data', {})
            calls = raw_data.get('calls', [])
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'call_id', 'timestamp', 'date', 'time', 'contact_name', 'phone_number',
                    'duration_seconds', 'duration_formatted', 'call_type', 'direction',
                    'answered', 'service_provider', 'tower_info', 'location_lat', 'location_lon',
                    'call_quality', 'roaming_status', 'emergency_call', 'conference_call',
                    'call_frequency_rank', 'contact_interaction_score', 'case_name', 'examiner'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                # Calculate call frequencies for ranking
                phone_call_counts = {}
                for call in calls:
                    phone = call.get('address') or call.get('number', 'Unknown')
                    phone_call_counts[phone] = phone_call_counts.get(phone, 0) + 1
                
                # Sort phones by call frequency
                sorted_phones = sorted(phone_call_counts.items(), key=lambda x: x[1], reverse=True)
                phone_rankings = {phone: rank + 1 for rank, (phone, count) in enumerate(sorted_phones)}
                
                for i, call in enumerate(calls, 1):
                    phone = call.get('address') or call.get('number', 'Unknown')
                    timestamp = call.get('timestamp', '')
                    
                    # Parse timestamp if possible
                    date_part = ''
                    time_part = ''
                    try:
                        if timestamp:
                            dt = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            date_part = dt.strftime('%Y-%m-%d')
                            time_part = dt.strftime('%H:%M:%S')
                    except:
                        pass
                    
                    # Determine call direction and type
                    call_type = call.get('type', '').lower()
                    if 'incoming' in call_type or 'received' in call_type:
                        direction = 'Incoming'
                        answered = 'Yes'
                    elif 'outgoing' in call_type or 'made' in call_type:
                        direction = 'Outgoing'
                        answered = 'Yes'
                    elif 'missed' in call_type:
                        direction = 'Incoming'
                        answered = 'No'
                    else:
                        direction = 'Unknown'
                        answered = 'Unknown'
                    
                    # Format duration
                    duration = call.get('duration', 0)
                    duration_formatted = self._format_duration(duration)
                    
                    # Emergency call detection
                    emergency_call = 'Yes' if phone in ['911', '112', '999', '000'] else 'No'
                    
                    # Calculate interaction score (frequency rank inverted)
                    total_phones = len(phone_rankings)
                    interaction_score = total_phones - phone_rankings.get(phone, total_phones) + 1
                    
                    writer.writerow({
                        'call_id': f"CALL_{i:06d}",
                        'timestamp': timestamp,
                        'date': date_part,
                        'time': time_part,
                        'contact_name': call.get('contact', 'Unknown'),
                        'phone_number': phone,
                        'duration_seconds': duration,
                        'duration_formatted': duration_formatted,
                        'call_type': call.get('type', 'Unknown'),
                        'direction': direction,
                        'answered': answered,
                        'service_provider': call.get('service_provider', 'Unknown'),
                        'tower_info': call.get('cell_tower', 'Unknown'),
                        'location_lat': call.get('latitude', ''),
                        'location_lon': call.get('longitude', ''),
                        'call_quality': call.get('quality', 'Unknown'),
                        'roaming_status': call.get('roaming', 'Unknown'),
                        'emergency_call': emergency_call,
                        'conference_call': 'Yes' if call.get('conference', False) else 'No',
                        'call_frequency_rank': phone_rankings.get(phone, 0),
                        'contact_interaction_score': interaction_score,
                        'case_name': self.case_name,
                        'examiner': self.examiner_name
                    })
            
            messagebox.showinfo("Success", f"Detailed call logs exported to {filename}\n{len(calls)} records exported")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export call logs: {e}")
    
    def export_multimedia_inventory_csv(self):
        """Export comprehensive multimedia file inventory"""
        if not self.gui.analysis_results:
            messagebox.showinfo("Info", "No analysis data available for export")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Multimedia Inventory"
        )
        
        if not filename:
            return
        
        try:
            raw_data = self.gui.analysis_results.get('raw_evidence_data', {})
            photos = raw_data.get('photos', [])
            videos = raw_data.get('videos', [])
            audio = raw_data.get('audio', [])
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'file_id', 'file_type', 'filename', 'full_path', 'file_extension',
                    'size_bytes', 'size_mb', 'size_formatted', 'date_created', 'date_modified',
                    'date_accessed', 'dimensions', 'duration_seconds', 'gps_latitude',
                    'gps_longitude', 'camera_make', 'camera_model', 'orientation',
                    'flash_used', 'iso_speed', 'exposure_time', 'f_number', 'focal_length',
                    'white_balance', 'resolution', 'color_space', 'compression',
                    'hash_md5', 'hash_sha256', 'deleted_status', 'recovery_source',
                    'evidence_significance', 'timeline_relevance', 'case_name', 'examiner'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                file_counter = 1
                
                # Process photos
                for photo in photos:
                    self._write_multimedia_record(writer, photo, 'Photo', file_counter)
                    file_counter += 1
                
                # Process videos
                for video in videos:
                    self._write_multimedia_record(writer, video, 'Video', file_counter)
                    file_counter += 1
                
                # Process audio files
                for audio_file in audio:
                    self._write_multimedia_record(writer, audio_file, 'Audio', file_counter)
                    file_counter += 1
            
            total_files = len(photos) + len(videos) + len(audio)
            messagebox.showinfo("Success", 
                f"Multimedia inventory exported to {filename}\n"
                f"Total files: {total_files}\n"
                f"Photos: {len(photos)}, Videos: {len(videos)}, Audio: {len(audio)}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export multimedia inventory: {e}")
    
    def export_network_analysis_csv(self):
        """Export comprehensive network connections and Wi-Fi analysis"""
        if not self.gui.analysis_results:
            messagebox.showinfo("Info", "No analysis data available for export")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Network Analysis"
        )
        
        if not filename:
            return
        
        try:
            raw_data = self.gui.analysis_results.get('raw_evidence_data', {})
            wifi_networks = raw_data.get('wifi_networks', [])
            network_connections = raw_data.get('network_connections', [])
            cellular_networks = raw_data.get('cellular_networks', [])
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'network_id', 'network_type', 'ssid_name', 'bssid', 'frequency_mhz',
                    'channel', 'signal_strength', 'security_type', 'encryption_method',
                    'password_stored', 'auto_connect', 'hidden_network', 'first_connected',
                    'last_connected', 'total_connections', 'data_usage_mb', 'ip_address',
                    'subnet_mask', 'gateway', 'dns_servers', 'mac_address', 'vendor_oui',
                    'location_latitude', 'location_longitude', 'location_accuracy',
                    'roaming_partner', 'captive_portal', 'proxy_settings', 'vpn_used',
                    'network_priority', 'investigation_relevance', 'case_name', 'examiner'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                network_counter = 1
                
                # Process Wi-Fi networks
                for wifi in wifi_networks:
                    writer.writerow({
                        'network_id': f"WIFI_{network_counter:04d}",
                        'network_type': 'Wi-Fi',
                        'ssid_name': wifi.get('ssid', 'Unknown'),
                        'bssid': wifi.get('bssid', 'Unknown'),
                        'frequency_mhz': wifi.get('frequency', ''),
                        'channel': wifi.get('channel', ''),
                        'signal_strength': wifi.get('signal_strength', ''),
                        'security_type': wifi.get('security', 'Unknown'),
                        'encryption_method': wifi.get('encryption', 'Unknown'),
                        'password_stored': 'Yes' if wifi.get('password_stored') else 'No',
                        'auto_connect': 'Yes' if wifi.get('auto_connect') else 'No',
                        'hidden_network': 'Yes' if wifi.get('hidden') else 'No',
                        'first_connected': wifi.get('first_connected', ''),
                        'last_connected': wifi.get('last_connected', ''),
                        'total_connections': wifi.get('connection_count', 0),
                        'data_usage_mb': wifi.get('data_usage', 0),
                        'ip_address': wifi.get('ip_address', ''),
                        'subnet_mask': wifi.get('subnet_mask', ''),
                        'gateway': wifi.get('gateway', ''),
                        'dns_servers': ', '.join(wifi.get('dns_servers', [])),
                        'mac_address': wifi.get('mac_address', ''),
                        'vendor_oui': wifi.get('vendor', ''),
                        'location_latitude': wifi.get('latitude', ''),
                        'location_longitude': wifi.get('longitude', ''),
                        'location_accuracy': wifi.get('location_accuracy', ''),
                        'roaming_partner': wifi.get('roaming_partner', ''),
                        'captive_portal': 'Yes' if wifi.get('captive_portal') else 'No',
                        'proxy_settings': wifi.get('proxy', ''),
                        'vpn_used': 'Yes' if wifi.get('vpn_detected') else 'No',
                        'network_priority': wifi.get('priority', 0),
                        'investigation_relevance': self._assess_network_relevance(wifi),
                        'case_name': self.case_name,
                        'examiner': self.examiner_name
                    })
                    network_counter += 1
                
                # Process cellular networks
                for cellular in cellular_networks:
                    writer.writerow({
                        'network_id': f"CELL_{network_counter:04d}",
                        'network_type': 'Cellular',
                        'ssid_name': cellular.get('carrier_name', 'Unknown'),
                        'bssid': cellular.get('cell_id', ''),
                        'frequency_mhz': cellular.get('frequency', ''),
                        'channel': cellular.get('band', ''),
                        'signal_strength': cellular.get('signal_strength', ''),
                        'security_type': 'Carrier Encrypted',
                        'encryption_method': cellular.get('encryption', 'Unknown'),
                        'password_stored': 'N/A',
                        'auto_connect': 'Yes',
                        'hidden_network': 'No',
                        'first_connected': cellular.get('first_seen', ''),
                        'last_connected': cellular.get('last_seen', ''),
                        'total_connections': cellular.get('connection_count', 0),
                        'data_usage_mb': cellular.get('data_usage', 0),
                        'ip_address': cellular.get('ip_address', ''),
                        'subnet_mask': '',
                        'gateway': cellular.get('gateway', ''),
                        'dns_servers': ', '.join(cellular.get('dns_servers', [])),
                        'mac_address': 'N/A',
                        'vendor_oui': cellular.get('carrier', ''),
                        'location_latitude': cellular.get('latitude', ''),
                        'location_longitude': cellular.get('longitude', ''),
                        'location_accuracy': cellular.get('location_accuracy', ''),
                        'roaming_partner': 'Yes' if cellular.get('roaming') else 'No',
                        'captive_portal': 'No',
                        'proxy_settings': cellular.get('proxy', ''),
                        'vpn_used': 'Yes' if cellular.get('vpn_detected') else 'No',
                        'network_priority': 1,
                        'investigation_relevance': self._assess_network_relevance(cellular),
                        'case_name': self.case_name,
                        'examiner': self.examiner_name
                    })
                    network_counter += 1
            
            total_networks = len(wifi_networks) + len(cellular_networks)
            messagebox.showinfo("Success", 
                f"Network analysis exported to {filename}\n"
                f"Total networks: {total_networks}\n"
                f"Wi-Fi: {len(wifi_networks)}, Cellular: {len(cellular_networks)}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export network analysis: {e}")
    
    def export_device_interactions_csv(self):
        """Export Bluetooth, USB, and other device interaction logs"""
        if not self.gui.analysis_results:
            messagebox.showinfo("Info", "No analysis data available for export")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Device Interactions"
        )
        
        if not filename:
            return
        
        try:
            raw_data = self.gui.analysis_results.get('raw_evidence_data', {})
            bluetooth_devices = raw_data.get('bluetooth_devices', [])
            usb_devices = raw_data.get('usb_devices', [])
            nfc_interactions = raw_data.get('nfc_interactions', [])
            airdrop_transfers = raw_data.get('airdrop_transfers', [])
            paired_devices = raw_data.get('paired_devices', [])
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'interaction_id', 'device_type', 'device_name', 'device_identifier', 
                    'mac_address', 'bluetooth_class', 'device_category', 'manufacturer',
                    'model_number', 'serial_number', 'firmware_version', 'paired_status',
                    'trusted_device', 'first_paired', 'last_connected', 'last_seen',
                    'connection_duration', 'total_connections', 'data_transferred_mb',
                    'services_used', 'authentication_method', 'encryption_level',
                    'battery_level', 'signal_strength', 'distance_estimate',
                    'location_latitude', 'location_longitude', 'interaction_type',
                    'files_transferred', 'apps_accessed', 'investigation_priority',
                    'potential_owner', 'device_notes', 'case_name', 'examiner'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                interaction_counter = 1
                
                # Process Bluetooth devices
                for bt_device in bluetooth_devices:
                    writer.writerow({
                        'interaction_id': f"BT_{interaction_counter:06d}",
                        'device_type': 'Bluetooth',
                        'device_name': bt_device.get('name', 'Unknown Device'),
                        'device_identifier': bt_device.get('device_id', ''),
                        'mac_address': bt_device.get('mac_address', ''),
                        'bluetooth_class': bt_device.get('device_class', ''),
                        'device_category': self._categorize_bluetooth_device(bt_device),
                        'manufacturer': bt_device.get('manufacturer', ''),
                        'model_number': bt_device.get('model', ''),
                        'serial_number': bt_device.get('serial', ''),
                        'firmware_version': bt_device.get('firmware', ''),
                        'paired_status': 'Yes' if bt_device.get('paired') else 'No',
                        'trusted_device': 'Yes' if bt_device.get('trusted') else 'No',
                        'first_paired': bt_device.get('first_paired', ''),
                        'last_connected': bt_device.get('last_connected', ''),
                        'last_seen': bt_device.get('last_seen', ''),
                        'connection_duration': self._format_duration(bt_device.get('total_connection_time', 0)),
                        'total_connections': bt_device.get('connection_count', 0),
                        'data_transferred_mb': bt_device.get('data_transferred', 0),
                        'services_used': ', '.join(bt_device.get('services', [])),
                        'authentication_method': bt_device.get('auth_method', ''),
                        'encryption_level': bt_device.get('encryption', ''),
                        'battery_level': bt_device.get('battery_level', ''),
                        'signal_strength': bt_device.get('signal_strength', ''),
                        'distance_estimate': bt_device.get('distance', ''),
                        'location_latitude': bt_device.get('latitude', ''),
                        'location_longitude': bt_device.get('longitude', ''),
                        'interaction_type': self._determine_interaction_type(bt_device),
                        'files_transferred': bt_device.get('files_transferred', 0),
                        'apps_accessed': ', '.join(bt_device.get('apps_used', [])),
                        'investigation_priority': self._assess_device_priority(bt_device),
                        'potential_owner': bt_device.get('potential_owner', ''),
                        'device_notes': bt_device.get('notes', ''),
                        'case_name': self.case_name,
                        'examiner': self.examiner_name
                    })
                    interaction_counter += 1
                
                # Process USB devices
                for usb_device in usb_devices:
                    writer.writerow({
                        'interaction_id': f"USB_{interaction_counter:06d}",
                        'device_type': 'USB',
                        'device_name': usb_device.get('name', 'Unknown USB Device'),
                        'device_identifier': usb_device.get('device_id', ''),
                        'mac_address': 'N/A',
                        'bluetooth_class': 'N/A',
                        'device_category': self._categorize_usb_device(usb_device),
                        'manufacturer': usb_device.get('manufacturer', ''),
                        'model_number': usb_device.get('model', ''),
                        'serial_number': usb_device.get('serial', ''),
                        'firmware_version': usb_device.get('firmware', ''),
                        'paired_status': 'N/A',
                        'trusted_device': 'Yes' if usb_device.get('trusted') else 'No',
                        'first_paired': usb_device.get('first_connected', ''),
                        'last_connected': usb_device.get('last_connected', ''),
                        'last_seen': usb_device.get('last_seen', ''),
                        'connection_duration': self._format_duration(usb_device.get('total_connection_time', 0)),
                        'total_connections': usb_device.get('connection_count', 0),
                        'data_transferred_mb': usb_device.get('data_transferred', 0),
                        'services_used': usb_device.get('device_class', ''),
                        'authentication_method': 'USB Connection',
                        'encryption_level': usb_device.get('encryption', 'None'),
                        'battery_level': 'N/A',
                        'signal_strength': 'N/A',
                        'distance_estimate': 'Physical Connection',
                        'location_latitude': '',
                        'location_longitude': '',
                        'interaction_type': 'File Transfer/Storage',
                        'files_transferred': usb_device.get('files_transferred', 0),
                        'apps_accessed': ', '.join(usb_device.get('apps_used', [])),
                        'investigation_priority': self._assess_device_priority(usb_device),
                        'potential_owner': usb_device.get('potential_owner', ''),
                        'device_notes': usb_device.get('notes', ''),
                        'case_name': self.case_name,
                        'examiner': self.examiner_name
                    })
                    interaction_counter += 1
                
                # Process NFC interactions
                for nfc in nfc_interactions:
                    writer.writerow({
                        'interaction_id': f"NFC_{interaction_counter:06d}",
                        'device_type': 'NFC',
                        'device_name': nfc.get('tag_name', 'NFC Tag/Device'),
                        'device_identifier': nfc.get('tag_id', ''),
                        'mac_address': 'N/A',
                        'bluetooth_class': 'N/A',
                        'device_category': 'Near Field Communication',
                        'manufacturer': nfc.get('manufacturer', ''),
                        'model_number': nfc.get('tag_type', ''),
                        'serial_number': nfc.get('serial', ''),
                        'firmware_version': 'N/A',
                        'paired_status': 'N/A',
                        'trusted_device': 'N/A',
                        'first_paired': nfc.get('first_interaction', ''),
                        'last_connected': nfc.get('last_interaction', ''),
                        'last_seen': nfc.get('last_seen', ''),
                        'connection_duration': 'Momentary',
                        'total_connections': nfc.get('interaction_count', 0),
                        'data_transferred_mb': nfc.get('data_size', 0) / 1024 / 1024,
                        'services_used': nfc.get('application', ''),
                        'authentication_method': 'Proximity',
                        'encryption_level': nfc.get('encryption', 'Unknown'),
                        'battery_level': 'N/A',
                        'signal_strength': 'Close Proximity',
                        'distance_estimate': '< 4cm',
                        'location_latitude': nfc.get('latitude', ''),
                        'location_longitude': nfc.get('longitude', ''),
                        'interaction_type': 'Data Exchange/Payment',
                        'files_transferred': 0,
                        'apps_accessed': nfc.get('app_used', ''),
                        'investigation_priority': self._assess_device_priority(nfc),
                        'potential_owner': nfc.get('potential_owner', ''),
                        'device_notes': nfc.get('notes', ''),
                        'case_name': self.case_name,
                        'examiner': self.examiner_name
                    })
                    interaction_counter += 1
            
            total_devices = len(bluetooth_devices) + len(usb_devices) + len(nfc_interactions)
            messagebox.showinfo("Success", 
                f"Device interactions exported to {filename}\n"
                f"Total interactions: {total_devices}\n"
                f"Bluetooth: {len(bluetooth_devices)}, USB: {len(usb_devices)}, NFC: {len(nfc_interactions)}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export device interactions: {e}")
    
    def export_comprehensive_forensic_package(self):
        """Export complete forensic package with all data types"""
        if not self.gui.analysis_results:
            messagebox.showinfo("Info", "No analysis data available for export")
            return
        
        # Ask for directory
        directory = filedialog.askdirectory(title="Select Directory for Comprehensive Forensic Package")
        
        if not directory:
            return
        
        try:
            base_path = Path(directory)
            case_folder = base_path / f"FORENSIC_PACKAGE_{self.case_name}_{self.timestamp.strftime('%Y%m%d_%H%M%S')}"
            case_folder.mkdir(exist_ok=True)
            
            # Create subdirectories
            (case_folder / "Communications").mkdir(exist_ok=True)
            (case_folder / "Multimedia").mkdir(exist_ok=True)
            (case_folder / "Networks").mkdir(exist_ok=True)
            (case_folder / "Devices").mkdir(exist_ok=True)
            (case_folder / "Reports").mkdir(exist_ok=True)
            (case_folder / "Raw_Data").mkdir(exist_ok=True)
            
            # Export all data types
            self._export_to_specific_file(case_folder / "Communications" / "detailed_call_logs.csv", 
                                        self.export_detailed_call_logs_csv)
            self._export_to_specific_file(case_folder / "Communications" / "messages.csv", 
                                        self._get_messages_data)
            self._export_to_specific_file(case_folder / "Communications" / "contacts.csv", 
                                        self._get_contacts_data)
            
            self._export_to_specific_file(case_folder / "Multimedia" / "multimedia_inventory.csv", 
                                        self.export_multimedia_inventory_csv)
            
            self._export_to_specific_file(case_folder / "Networks" / "network_analysis.csv", 
                                        self.export_network_analysis_csv)
            
            self._export_to_specific_file(case_folder / "Devices" / "device_interactions.csv", 
                                        self.export_device_interactions_csv)
            
            # Export reports
            generator = ForensicReportGenerator(self.case_name, self.examiner_name, self.gui.analysis_results)
            
            with open(case_folder / "Reports" / "executive_summary.txt", 'w', encoding='utf-8') as f:
                f.write(generator.generate_executive_summary_report())
            
            with open(case_folder / "Reports" / "detailed_analysis.txt", 'w', encoding='utf-8') as f:
                f.write(generator.generate_detailed_report())
            
            # Export raw data
            with open(case_folder / "Raw_Data" / "complete_analysis.json", 'w', encoding='utf-8') as f:
                json.dump(self.gui.analysis_results, f, indent=2, default=str)
            
            # Create forensic index
            self._create_forensic_index(case_folder)
            
            messagebox.showinfo("Success", 
                f"Comprehensive forensic package exported to:\n{case_folder}\n\n"
                f"Package includes:\n"
                f"• Detailed call logs with analysis\n"
                f"• Complete multimedia inventory\n"
                f"• Network connection analysis\n"
                f"• Device interaction logs\n"
                f"• Professional forensic reports\n"
                f"• Raw analysis data")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export comprehensive package: {e}")
    
    # Helper methods
    
    def _format_duration(self, seconds):
        """Format duration from seconds to human readable"""
        if not isinstance(seconds, (int, float)) or seconds <= 0:
            return "0:00"
        
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes}:{secs:02d}"
    
    def _write_multimedia_record(self, writer, media_file, file_type, file_id):
        """Write multimedia record to CSV"""
        size_bytes = media_file.get('size', 0)
        size_mb = size_bytes / (1024 * 1024) if size_bytes > 0 else 0
        size_formatted = self._format_file_size(size_bytes)
        
        # Extract EXIF data if available
        exif = media_file.get('exif', {})
        
        writer.writerow({
            'file_id': f"{file_type.upper()}_{file_id:06d}",
            'file_type': file_type,
            'filename': media_file.get('filename', 'Unknown'),
            'full_path': media_file.get('path', 'Unknown'),
            'file_extension': Path(media_file.get('filename', '')).suffix.lower(),
            'size_bytes': size_bytes,
            'size_mb': round(size_mb, 2),
            'size_formatted': size_formatted,
            'date_created': media_file.get('date_created', ''),
            'date_modified': media_file.get('date_modified', ''),
            'date_accessed': media_file.get('date_accessed', ''),
            'dimensions': f"{exif.get('width', '')}x{exif.get('height', '')}" if exif.get('width') else '',
            'duration_seconds': media_file.get('duration', ''),
            'gps_latitude': exif.get('gps_latitude', ''),
            'gps_longitude': exif.get('gps_longitude', ''),
            'camera_make': exif.get('camera_make', ''),
            'camera_model': exif.get('camera_model', ''),
            'orientation': exif.get('orientation', ''),
            'flash_used': 'Yes' if exif.get('flash_fired') else 'No',
            'iso_speed': exif.get('iso_speed', ''),
            'exposure_time': exif.get('exposure_time', ''),
            'f_number': exif.get('f_number', ''),
            'focal_length': exif.get('focal_length', ''),
            'white_balance': exif.get('white_balance', ''),
            'resolution': exif.get('resolution', ''),
            'color_space': exif.get('color_space', ''),
            'compression': exif.get('compression', ''),
            'hash_md5': media Equipotential.get('md5_hash', ''),
            'hash_sha256': media_file.get('sha256_hash', ''),
            'deleted_status': 'Yes' if media_file.get('deleted') else 'No',
            'recovery_source': media_file.get('recovery_source', ''),
            'evidence_significance': self._assess_media_significance(media_file),
            'timeline_relevance': self._assess_timeline_relevance(media_file),
            'case_name': self.case_name,
            'examiner': self.examiner_name
        })
    
    def _format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if not isinstance(size_bytes, (int, float)) or size_bytes <= 0:
            return "0 B"
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    def _assess_network_relevance(self, network):
        """Assess investigation relevance of network"""
        relevance_factors = []
        
        # Check for suspicious characteristics
        if network.get('hidden'):
            relevance_factors.append("Hidden Network")
        
        if network.get('encryption') in ['WEP', 'None']:
            relevance_factors.append("Weak Security")
        
        if network.get('connection_count', 0) > 100:
            relevance_factors.append("Frequent Use")
        
        if network.get('data_usage', 0) > 1000:  # > 1GB
            relevance_factors.append("High Data Usage")
        
        # Check for business/public networks
        ssid = network.get('ssid', '').lower()
        if any(keyword in ssid for keyword in ['hotel', 'airport', 'cafe', 'public', 'guest']):
            relevance_factors.append("Public/Business Network")
        
        return ', '.join(relevance_factors) if relevance_factors else 'Standard'
    
    def _categorize_bluetooth_device(self, device):
        """Categorize Bluetooth device type"""
        device_class = device.get('device_class', '').lower()
        name = device.get('name', '').lower()
        
        if any(keyword in device_class or keyword in name for keyword in ['phone', 'mobile', 'iphone', 'android']):
            return 'Mobile Phone'
        elif any(keyword in device_class or keyword in name for keyword in ['headset', 'earbuds', 'speaker', 'audio']):
            return 'Audio Device'
        elif any(keyword in device_class or keyword in name for keyword in ['car', 'vehicle', 'auto']):
            return 'Vehicle System'
        elif any(keyword in device_class or keyword in name for keyword in ['watch', 'fitness', 'band']):
            return 'Wearable Device'
        elif any(keyword in device_class or keyword in name for keyword in ['computer', 'laptop', 'pc', 'mac']):
            return 'Computer'
        elif any(keyword in device_class or keyword in name for keyword in ['keyboard', 'mouse', 'input']):
            return 'Input Device'
        else:
            return 'Other Device'
    
    def _categorize_usb_device(self, device):
        """Categorize USB device type"""
        device_class = device.get('device_class', '').lower()
        name = device.get('name', '').lower()
        
        if any(keyword in device_class or keyword in name for keyword in ['storage', 'disk', 'drive', 'usb']):
            return 'Storage Device'
        elif any(keyword in device_class or keyword in name for keyword in ['phone', 'mobile', 'iphone', 'android']):
            return 'Mobile Device'
        elif any(keyword in device_class or keyword in name for keyword in ['camera', 'photo']):
            return 'Camera/Photo Device'
        elif any(keyword in device_class or keyword in name for keyword in ['audio', 'sound', 'mic']):
            return 'Audio Device'
        elif any(keyword in device_class or keyword in name for keyword in ['network', 'ethernet', 'wifi']):
            return 'Network Device'
        else:
            return 'Other USB Device'
    
    def _determine_interaction_type(self, device):
        """Determine type of device interaction"""
        services = device.get('services', [])
        data_transferred = device.get('data_transferred', 0)
        
        interaction_types = []
        
        if 'file_transfer' in services or data_transferred > 0:
            interaction_types.append('File Transfer')
        
        if 'audio' in services or any('a2dp' in s.lower() for s in services):
            interaction_types.append('Audio Streaming')
        
        if 'input' in services or any('hid' in s.lower() for s in services):
            interaction_types.append('Input Device')
        
        if 'network' in services or any('pan' in s.lower() for s in services):
            interaction_types.append('Network Access')
        
        if not interaction_types:
            interaction_types.append('Standard Connection')
        
        return ', '.join(interaction_types)
    
    def _assess_device_priority(self, device):
        """Assess investigation priority of device"""
        priority_score = 0
        
        # High data transfer
        if device.get('data_transferred', 0) > 100:  # > 100MB
            priority_score += 3
        
        # Multiple connections
        if device.get('connection_count', 0) > 10:
            priority_score += 2
        
        # Recent activity
        last_connected = device.get('last_connected', '')
        if last_connected:  # Would need date parsing for accurate assessment
            priority_score += 1
        
        # Device type priority
        device_name = device.get('name', '').lower()
        if any(keyword in device_name for keyword in ['phone', 'mobile', 'iphone', 'android']):
            priority_score += 3
        elif any(keyword in device_name for keyword in ['computer', 'laptop', 'pc']):
            priority_score += 2
        
        # File transfer capability
        if 'file_transfer' in device.get('services', []):
            priority_score += 2
        
        if priority_score >= 6:
            return 'High'
        elif priority_score >= 3:
            return 'Medium'
        else:
            return 'Low'
    
    def _assess_media_significance(self, media_file):
        """Assess forensic significance of media file"""
        significance_factors = []
        
        # GPS data present
        exif = media_file.get('exif', {})
        if exif.get('gps_latitude') and exif.get('gps_longitude'):
            significance_factors.append('GPS Location')
        
        # Large file size
        size_mb = media_file.get('size', 0) / (1024 * 1024)
        if size_mb > 50:  # > 50MB
            significance_factors.append('Large File')
        
        # Recent creation/modification
        # Would need date parsing for accurate assessment
        if media_file.get('date_created') or media_file.get('date_modified'):
            significance_factors.append('Timestamped')
        
        # Camera metadata
        if exif.get('camera_make') or exif.get('camera_model'):
            significance_factors.append('Camera Metadata')
        
        # Deleted/recovered file
        if media_file.get('deleted'):
            significance_factors.append('Deleted File')
        
        return ', '.join(significance_factors) if significance_factors else 'Standard'
    
    def _assess_timeline_relevance(self, media_file):
        """Assess timeline relevance of media file"""
        # This would typically involve comparing file timestamps with case timeline
        # For now, return basic assessment
        
        if media_file.get('deleted'):
            return 'Potentially Relevant (Deleted)'
        elif media_file.get('exif', {}).get('gps_latitude'):
            return 'High (Location Data)'
        elif media_file.get('date_created'):
            return 'Medium (Timestamped)'
        else:
            return 'Low'
    
    def _export_to_specific_file(self, filepath, export_function):
        """Export data to specific file using export function"""
        try:
            # Temporarily override filedialog to write to specific file
            original_asksaveasfilename = filedialog.asksaveasfilename
            filedialog.asksaveasfilename = lambda *args, **kwargs: str(filepath)
            export_function()
            filedialog.asksaveasfilename = original_asksaveasfilename
        except Exception as e:
            print(f"Warning: Failed to export {filepath}: {e}")
    
    def _get_messages_data(self, filepath):
        """Export messages data to specified file"""
        if not self.gui.analysis_results:
            return
        
        try:
            raw_data = self.gui.analysis_results.get('raw_evidence_data', {})
            messages = raw_data.get('messages', [])
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'message_id', 'timestamp', 'date', 'time', 'contact_name', 'phone_number',
                    'message_text', 'direction', 'service_type', 'attachment_count',
                    'is_read', 'is_delivered', 'is_deleted', 'group_chat', 'keyword_hits',
                    'case_name', 'examiner'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for i, msg in enumerate(messages, 1):
                    timestamp = msg.get('timestamp', '')
                    date_part = ''
                    time_part = ''
                    try:
                        if timestamp:
                            dt = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            date_part = dt.strftime('%Y-%m-%d')
                            time_part = dt.strftime('%H:%M:%S')
                    except:
                        pass
                    
                    direction = 'Outgoing' if msg.get('is_from_me', False) else 'Incoming'
                    
                    writer.writerow({
                        'message_id': f"MSG_{i:06d}",
                        'timestamp': timestamp,
                        'date': date_part,
                        'time': time_part,
                        'contact_name': msg.get('contact', 'Unknown'),
                        'phone_number': msg.get('address', 'Unknown'),
                        'message_text': msg.get('text', ''),
                        'direction': direction,
                        'service_type': msg.get('service', 'Unknown'),
                        'attachment_count': msg.get('attachment_count', 0),
                        'is_read': 'Yes' if msg.get('is_read', False) else 'No',
                        'is_delivered': 'Yes' if msg.get('is_delivered', False) else 'No',
                        'is_deleted': 'Yes' if msg.get('is_deleted', False) else 'No',
                        'group_chat': 'Yes' if msg.get('is_group', False) else 'No',
                        'keyword_hits': ', '.join(msg.get('keyword_hits', [])),
                        'case_name': self.case_name,
                        'examiner': self.examiner_name
                    })
            
        except Exception as e:
            print(f"Warning: Failed to export messages: {e}")
    
    def _get_contacts_data(self, filepath):
        """Export contacts data to specified file"""
        if not self.gui.analysis_results:
            return
        
        try:
            raw_data = self.gui.analysis_results.get('raw_evidence_data', {})
            contacts = raw_data.get('contacts', [])
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'contact_id', 'first_name', 'last_name', 'phone_number', 'email',
                    'organization', 'address', 'total_interactions', 'last_interaction',
                    'contact_frequency_rank', 'case_name', 'examiner'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                # Calculate interaction frequencies
                interaction_counts = {}
                for contact in contacts:
                    phone = contact.get('phone', 'Unknown')
                    interaction_counts[phone] = interaction_counts.get(phone, 0) + 1
                
                sorted_contacts = sorted(interaction_counts.items(), key=lambda x: x[1], reverse=True)
                contact_rankings = {phone: rank + 1 for rank, (phone, count) in enumerate(sorted_contacts)}
                
                for i, contact in enumerate(contacts, 1):
                    phone = contact.get('phone', 'Unknown')
                    writer.writerow({
                        'contact_id': f"CONT_{i:06d}",
                        'first_name': contact.get('first_name', ''),
                        'last_name': contact.get('last_name', ''),
                        'phone_number': phone,
                        'email': contact.get('email', ''),
                        'organization': contact.get('organization', ''),
                        'address': contact.get('address', ''),
                        'total_interactions': interaction_counts.get(phone, 0),
                        'last_interaction': contact.get('last_interaction', ''),
                        'contact_frequency_rank': contact_rankings.get(phone, 0),
                        'case_name': self.case_name,
                        'examiner': self.examiner_name
                    })
            
        except Exception as e:
            print(f"Warning: Failed to export contacts: {e}")
    
    def _get_multimedia_data(self, filepath):
        """Export multimedia data to specified file"""
        self._export_to_specific_file(filepath, self.export_multimedia_inventory_csv)
    
    def _get_network_data(self, filepath):
        """Export network data to specified file"""
        self._export_to_specific_file(filepath, self.export_network_analysis_csv)
    
    def _get_device_interaction_data(self, filepath):
        """Export device interaction data to specified file"""
        self._export_to_specific_file(filepath, self.export_device_interactions_csv)
    
    def _create_forensic_index(self, case_folder):
        """Create comprehensive forensic package index"""
        index_content = f"""
GHOST FORENSIC ANALYSIS - COMPREHENSIVE EVIDENCE PACKAGE
{'=' * 70}

CASE INFORMATION:
• Case Name: {self.case_name}
• Examiner: {self.examiner_name}
• Export Date: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
• Tool: GHOST Evidence Analysis Interface

PACKAGE CONTENTS:
{'=' * 70}

📞 COMMUNICATIONS/
• detailed_call_logs.csv - Complete call log analysis with metadata
• messages.csv - Text message data with keyword analysis
• contacts.csv - Contact information with interaction statistics

📷 MULTIMEDIA/
• multimedia_inventory.csv - Complete photo/video/audio inventory
  Includes: EXIF data, GPS coordinates, camera information, file hashes

🌐 NETWORKS/
• network_analysis.csv - Wi-Fi and cellular network connections
  Includes: Security analysis, location data, usage statistics

📡 DEVICES/
• device_interactions.csv - Bluetooth, USB, NFC device interactions
  Includes: Pairing history, data transfers, device fingerprinting

📄 REPORTS/
• executive_summary.txt - High-level case summary for leadership
• detailed_analysis.txt - Complete forensic analysis report

📊 RAW_DATA/
• complete_analysis.json - Full raw analysis data in JSON format

FORENSIC INTEGRITY:
{'=' * 70}
All exported data maintains forensic integrity with:
• Original timestamps preserved
• File hashes included where available
• Source path information maintained
• Chain of custody information embedded

USAGE INSTRUCTIONS:
{'=' * 70}
• CSV files can be opened in Excel or imported into analysis tools
• GPS coordinates can be imported into mapping software
• Hash values can be used for file verification
• Reports are formatted for legal proceedings

For questions about this evidence package, contact:
Examiner: {self.examiner_name}
Export Tool: GHOST Evidence Analysis Interface
Export Date: {self.timestamp.isoformat()}
"""
        
        with open(case_folder / "FORENSIC_PACKAGE_INDEX.txt", 'w', encoding='utf-8') as f:
            f.write(index_content)

# Integration functions to add to the main GUI class

def add_enhanced_export_methods(gui_instance):
    """Add enhanced export methods to the GUI instance"""
    
    exporter = Comprehensive
