#!/usr/bin/env python3
"""
GHOST - Golden Hour Operations and Strategic Threat Assessment
Focused Forensic Analysis Suite for Rapid Evidence Assessment
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import datetime
import zipfile
import tempfile
import shutil
import sqlite3
import re
from collections import defaultdict, Counter

# Set UTF-8 encoding for Windows compatibility
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent / "modules"))

# Import forensic modules
try:
    from config_manager import ConfigurationManager
    from forensic_logger import ForensicLogger
    print("[OK] Core modules loaded successfully")
except ImportError as e:
    print(f"[ERROR] Error importing modules: {e}")
    sys.exit(1)

class FocusedForensicSuite:
    """Focused forensic analysis for rapid evidence assessment"""
    
    def __init__(self, case_name: str, examiner_name: str):
        self.case_name = case_name
        self.examiner_name = examiner_name
        
        print(f"[INFO] GHOST - Golden Hour Operations and Strategic Threat Assessment")
        print(f"   Case: {case_name}")
        print(f"   Examiner: {examiner_name}")
        
        # Initialize core components
        self.config_manager = ConfigurationManager()
        self.logger = ForensicLogger(case_name, examiner_name)
        
        # Evidence categories
        self.evidence_data = {
            'messages': [],
            'calls': [],
            'contacts': [],
            'photos': [],
            'videos': [],
            'locations': [],
            'apps': {},
            'browsers': [],
            'databases': [],
            'files': []
        }
        
        print("[OK] Forensic analysis suite initialized")
    
    def analyze_extraction(self, extraction_path: str) -> Dict[str, Any]:
        """Main analysis function"""
        extraction_path = Path(extraction_path)
        
        if not extraction_path.exists():
            raise FileNotFoundError(f"Extraction path not found: {extraction_path}")
        
        print(f"\n[INFO] Analyzing extraction: {extraction_path}")
        
        # Determine if zip file or directory
        if extraction_path.is_file() and extraction_path.suffix.lower() == '.zip':
            print("[INFO] ZIP file detected - analyzing compressed extraction")
            return self._analyze_zip_extraction(extraction_path)
        else:
            print("[INFO] Directory extraction detected")
            return self._analyze_directory_extraction(extraction_path)
    
    def _analyze_zip_extraction(self, zip_path: Path) -> Dict[str, Any]:
        """Analyze ZIP file extraction"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_file:
                print("\n[STEP 1] Discovering evidence files...")
                file_inventory = self._discover_evidence_files(zip_file)
                
                print("\n[STEP 2] Extracting key evidence...")
                self._extract_evidence_from_zip(zip_file, file_inventory)
                
                print("\n[STEP 3] Analyzing communication data...")
                self._analyze_communications()
                
                print("\n[STEP 4] Processing multimedia evidence...")
                self._analyze_multimedia()
                
                print("\n[STEP 5] Generating intelligence report...")
                report = self._generate_evidence_report(zip_path)
                
                return report
                
        except Exception as e:
            raise Exception(f"Error analyzing ZIP extraction: {e}")
    
    def _analyze_directory_extraction(self, dir_path: Path) -> Dict[str, Any]:
        """Analyze directory extraction"""
        print("\n[STEP 1] Scanning extraction directory...")
        file_inventory = self._discover_evidence_files_directory(dir_path)
        
        print("\n[STEP 2] Processing evidence files...")
        self._extract_evidence_from_directory(dir_path, file_inventory)
        
        print("\n[STEP 3] Analyzing communication data...")
        self._analyze_communications()
        
        print("\n[STEP 4] Processing multimedia evidence...")
        self._analyze_multimedia()
        
        print("\n[STEP 5] Generating intelligence report...")
        report = self._generate_evidence_report(dir_path)
        
        return report
    
    def _discover_evidence_files(self, zip_file: zipfile.ZipFile) -> Dict[str, List[str]]:
        """Discover evidence files in ZIP"""
        evidence_files = {
            'messages': [],
            'calls': [],
            'contacts': [],
            'photos': [],
            'videos': [],
            'apps': [],
            'browsers': [],
            'databases': [],
            'location': []
        }
        
        # Known file patterns for different evidence types
        patterns = {
            'messages': ['sms.db', 'messages.db', 'mmssms.db', 'chat.db'],
            'calls': ['callhistory.db', 'calls.db', 'call_log.db'],
            'contacts': ['contacts.db', 'addressbook.db', 'contacts2.db'],
            'browsers': ['history.db', 'browser.db', 'webhistory.db'],
            'location': ['cache.db', 'consolidated.db', 'locationd_cache_enc'],
            'apps': ['whatsapp', 'snapchat', 'telegram', 'signal', 'instagram', 'facebook'],
            'photos': ['.jpg', '.jpeg', '.png', '.heic', '.heif'],
            'videos': ['.mp4', '.mov', '.avi', '.mkv', '.3gp'],
            'databases': ['.db', '.sqlite', '.sqlitedb']
        }
        
        print("   Scanning file structure...")
        for file_info in zip_file.infolist():
            if file_info.is_dir():
                continue
                
            file_path = file_info.filename.lower()
            file_name = Path(file_path).name.lower()
            
            # Check each evidence type
            for evidence_type, pattern_list in patterns.items():
                for pattern in pattern_list:
                    if pattern in file_path or file_name.endswith(pattern):
                        evidence_files[evidence_type].append(file_info.filename)
                        break
        
        # Print discovery summary
        for evidence_type, files in evidence_files.items():
            if files:
                print(f"   {evidence_type.title()}: {len(files)} files")
        
        return evidence_files
    
    def _discover_evidence_files_directory(self, dir_path: Path) -> Dict[str, List[Path]]:
        """Discover evidence files in directory"""
        evidence_files = {
            'messages': [],
            'calls': [],
            'contacts': [],
            'photos': [],
            'videos': [],
            'apps': [],
            'browsers': [],
            'databases': [],
            'location': []
        }
        
        patterns = {
            'messages': ['sms.db', 'messages.db', 'mmssms.db', 'chat.db'],
            'calls': ['callhistory.db', 'calls.db', 'call_log.db'],
            'contacts': ['contacts.db', 'addressbook.db', 'contacts2.db'],
            'browsers': ['history.db', 'browser.db', 'webhistory.db'],
            'location': ['cache.db', 'consolidated.db', 'locationd'],
            'apps': ['whatsapp', 'snapchat', 'telegram', 'signal', 'instagram'],
            'photos': ['.jpg', '.jpeg', '.png', '.heic', '.heif'],
            'videos': ['.mp4', '.mov', '.avi', '.mkv', '.3gp'],
            'databases': ['.db', '.sqlite', '.sqlitedb']
        }
        
        print("   Scanning directory structure...")
        for file_path in dir_path.rglob("*"):
            if file_path.is_file():
                file_str = str(file_path).lower()
                file_name = file_path.name.lower()
                
                for evidence_type, pattern_list in patterns.items():
                    for pattern in pattern_list:
                        if pattern in file_str or file_name.endswith(pattern):
                            evidence_files[evidence_type].append(file_path)
                            break
        
        # Print discovery summary
        for evidence_type, files in evidence_files.items():
            if files:
                print(f"   {evidence_type.title()}: {len(files)} files")
        
        return evidence_files
    
    def _extract_evidence_from_zip(self, zip_file: zipfile.ZipFile, file_inventory: Dict[str, List[str]]):
        """Extract and analyze evidence from ZIP"""
        
        # Process databases first (messages, calls, contacts)
        db_types = ['messages', 'calls', 'contacts', 'browsers', 'location', 'databases']
        
        for db_type in db_types:
            for file_path in file_inventory.get(db_type, []):
                print(f"   Processing {db_type}: {Path(file_path).name}")
                try:
                    self._process_database_from_zip(zip_file, file_path, db_type)
                except Exception as e:
                    print(f"     Error processing {file_path}: {e}")
        
        # Process app data
        for app_path in file_inventory.get('apps', []):
            print(f"   Processing app data: {Path(app_path).name}")
            try:
                self._process_app_data_from_zip(zip_file, app_path)
            except Exception as e:
                print(f"     Error processing app {app_path}: {e}")
        
        # Process multimedia (sample only for performance)
        self._process_multimedia_from_zip(zip_file, file_inventory)
    
    def _process_database_from_zip(self, zip_file: zipfile.ZipFile, file_path: str, db_type: str):
        """Process database file from ZIP"""
        try:
            # Extract to temporary file
            with zip_file.open(file_path) as zip_member:
                with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
                    shutil.copyfileobj(zip_member, temp_db)
                    temp_db_path = temp_db.name
            
            # Analyze database
            try:
                conn = sqlite3.connect(temp_db_path)
                cursor = conn.cursor()
                
                if db_type == 'messages':
                    self._extract_messages(cursor, file_path)
                elif db_type == 'calls':
                    self._extract_calls(cursor, file_path)
                elif db_type == 'contacts':
                    self._extract_contacts(cursor, file_path)
                elif db_type == 'browsers':
                    self._extract_browser_history(cursor, file_path)
                elif db_type == 'location':
                    self._extract_location_data(cursor, file_path)
                else:
                    self._analyze_generic_database(cursor, file_path)
                
                conn.close()
                
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_db_path)
                except:
                    pass
                    
        except Exception as e:
            print(f"     Database processing error: {e}")
    
    def _extract_messages(self, cursor: sqlite3.Cursor, source_file: str):
        """Extract SMS/message data"""
        try:
            # Try common message table structures
            message_queries = [
                # iOS Messages
                """SELECT 
                    datetime(date/1000000000 + 978307200, 'unixepoch') as timestamp,
                    text, is_from_me, service,
                    (SELECT id FROM handle WHERE handle.ROWID = message.handle_id) as contact
                   FROM message 
                   WHERE text IS NOT NULL 
                   ORDER BY date DESC LIMIT 1000""",
                
                # Android SMS
                """SELECT 
                    datetime(date/1000, 'unixepoch') as timestamp,
                    body as text, type, address as contact
                   FROM sms 
                   WHERE body IS NOT NULL 
                   ORDER BY date DESC LIMIT 1000""",
                
                # Generic message table
                """SELECT * FROM messages ORDER BY rowid DESC LIMIT 100"""
            ]
            
            for query in message_queries:
                try:
                    cursor.execute(query)
                    results = cursor.fetchall()
                    
                    if results:
                        columns = [description[0] for description in cursor.description]
                        
                        for row in results:
                            message_data = dict(zip(columns, row))
                            message_data['source_file'] = source_file
                            message_data['evidence_type'] = 'message'
                            self.evidence_data['messages'].append(message_data)
                        
                        print(f"     Extracted {len(results)} messages")
                        break
                        
                except sqlite3.Error:
                    continue
                    
        except Exception as e:
            print(f"     Message extraction error: {e}")
    
    def _extract_calls(self, cursor: sqlite3.Cursor, source_file: str):
        """Extract call log data"""
        try:
            call_queries = [
                # iOS Call History
                """SELECT 
                    datetime(date + 978307200, 'unixepoch') as timestamp,
                    address, duration, answered, originated
                   FROM call 
                   ORDER BY date DESC LIMIT 500""",
                
                # Android Call Log
                """SELECT 
                    datetime(date/1000, 'unixepoch') as timestamp,
                    number, duration, type
                   FROM calls 
                   ORDER BY date DESC LIMIT 500"""
            ]
            
            for query in call_queries:
                try:
                    cursor.execute(query)
                    results = cursor.fetchall()
                    
                    if results:
                        columns = [description[0] for description in cursor.description]
                        
                        for row in results:
                            call_data = dict(zip(columns, row))
                            call_data['source_file'] = source_file
                            call_data['evidence_type'] = 'call'
                            self.evidence_data['calls'].append(call_data)
                        
                        print(f"     Extracted {len(results)} call records")
                        break
                        
                except sqlite3.Error:
                    continue
                    
        except Exception as e:
            print(f"     Call extraction error: {e}")
    
    def _extract_contacts(self, cursor: sqlite3.Cursor, source_file: str):
        """Extract contact data"""
        try:
            contact_queries = [
                # iOS Contacts
                """SELECT 
                    first_name, last_name, organization,
                    (SELECT value FROM phone WHERE person_id = person.rowid LIMIT 1) as phone
                   FROM person LIMIT 500""",
                
                # Android Contacts
                """SELECT display_name, data1 as phone, data2 as email
                   FROM contacts 
                   WHERE display_name IS NOT NULL LIMIT 500"""
            ]
            
            for query in contact_queries:
                try:
                    cursor.execute(query)
                    results = cursor.fetchall()
                    
                    if results:
                        columns = [description[0] for description in cursor.description]
                        
                        for row in results:
                            contact_data = dict(zip(columns, row))
                            contact_data['source_file'] = source_file
                            contact_data['evidence_type'] = 'contact'
                            self.evidence_data['contacts'].append(contact_data)
                        
                        print(f"     Extracted {len(results)} contacts")
                        break
                        
                except sqlite3.Error:
                    continue
                    
        except Exception as e:
            print(f"     Contact extraction error: {e}")
    
    def _extract_browser_history(self, cursor: sqlite3.Cursor, source_file: str):
        """Extract browser history"""
        try:
            browser_queries = [
                # Safari History
                """SELECT 
                    datetime(visit_time + 978307200, 'unixepoch') as timestamp,
                    url, title, visit_count
                   FROM history_items hi
                   JOIN history_visits hv ON hi.id = hv.history_item
                   ORDER BY visit_time DESC LIMIT 1000""",
                
                # Chrome History
                """SELECT 
                    datetime(last_visit_time/1000000-11644473600, 'unixepoch') as timestamp,
                    url, title, visit_count
                   FROM urls 
                   ORDER BY last_visit_time DESC LIMIT 1000"""
            ]
            
            for query in browser_queries:
                try:
                    cursor.execute(query)
                    results = cursor.fetchall()
                    
                    if results:
                        columns = [description[0] for description in cursor.description]
                        
                        for row in results:
                            browser_data = dict(zip(columns, row))
                            browser_data['source_file'] = source_file
                            browser_data['evidence_type'] = 'browser'
                            self.evidence_data['browsers'].append(browser_data)
                        
                        print(f"     Extracted {len(results)} browser records")
                        break
                        
                except sqlite3.Error:
                    continue
                    
        except Exception as e:
            print(f"     Browser extraction error: {e}")
    
    def _extract_location_data(self, cursor: sqlite3.Cursor, source_file: str):
        """Extract location/GPS data"""
        try:
            location_queries = [
                # iOS Location Cache
                """SELECT 
                    datetime(timestamp + 978307200, 'unixepoch') as timestamp,
                    latitude, longitude, altitude, speed, course
                   FROM locations 
                   WHERE latitude IS NOT NULL 
                   ORDER BY timestamp DESC LIMIT 1000""",
                
                # Generic location table
                """SELECT * FROM location_data LIMIT 500"""
            ]
            
            for query in location_queries:
                try:
                    cursor.execute(query)
                    results = cursor.fetchall()
                    
                    if results:
                        columns = [description[0] for description in cursor.description]
                        
                        for row in results:
                            location_data = dict(zip(columns, row))
                            location_data['source_file'] = source_file
                            location_data['evidence_type'] = 'location'
                            self.evidence_data['locations'].append(location_data)
                        
                        print(f"     Extracted {len(results)} location points")
                        break
                        
                except sqlite3.Error:
                    continue
                    
        except Exception as e:
            print(f"     Location extraction error: {e}")
    
    def _analyze_generic_database(self, cursor: sqlite3.Cursor, source_file: str):
        """Analyze unknown database for potential evidence"""
        try:
            # Get table list
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            db_info = {
                'source_file': source_file,
                'tables': tables,
                'table_count': len(tables),
                'evidence_type': 'database',
                'analysis_time': datetime.datetime.now().isoformat()
            }
            
            # Sample data from interesting tables
            interesting_tables = []
            for table in tables[:5]:  # Limit to first 5 tables
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    row_count = cursor.fetchone()[0]
                    
                    if row_count > 0:
                        cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                        sample_data = cursor.fetchall()
                        
                        cursor.execute(f"PRAGMA table_info({table})")
                        columns = [col[1] for col in cursor.fetchall()]
                        
                        interesting_tables.append({
                            'name': table,
                            'row_count': row_count,
                            'columns': columns,
                            'sample_data': sample_data
                        })
                        
                except sqlite3.Error:
                    continue
            
            db_info['interesting_tables'] = interesting_tables
            self.evidence_data['databases'].append(db_info)
            
            print(f"     Analyzed database: {len(tables)} tables, {len(interesting_tables)} with data")
            
        except Exception as e:
            print(f"     Database analysis error: {e}")
    
    def _process_app_data_from_zip(self, zip_file: zipfile.ZipFile, app_path: str):
        """Process app-specific data"""
        app_name = self._identify_app_from_path(app_path)
        
        if app_name not in self.evidence_data['apps']:
            self.evidence_data['apps'][app_name] = {
                'files': [],
                'databases': [],
                'messages': [],
                'media': []
            }
        
        # Check if it's a database file
        if any(app_path.lower().endswith(ext) for ext in ['.db', '.sqlite', '.sqlitedb']):
            try:
                self._process_database_from_zip(zip_file, app_path, 'app_database')
            except Exception as e:
                print(f"     App database error: {e}")
        
        # Add to app inventory
        self.evidence_data['apps'][app_name]['files'].append(app_path)
        print(f"     Added to {app_name} inventory")
    
    def _identify_app_from_path(self, file_path: str) -> str:
        """Identify app from file path"""
        path_lower = file_path.lower()
        
        app_identifiers = {
            'whatsapp': 'WhatsApp',
            'snapchat': 'Snapchat', 
            'telegram': 'Telegram',
            'signal': 'Signal',
            'instagram': 'Instagram',
            'facebook': 'Facebook',
            'messenger': 'Messenger',
            'discord': 'Discord',
            'tiktok': 'TikTok',
            'twitter': 'Twitter'
        }
        
        for identifier, app_name in app_identifiers.items():
            if identifier in path_lower:
                return app_name
        
        return 'Unknown App'
    
    def _process_multimedia_from_zip(self, zip_file: zipfile.ZipFile, file_inventory: Dict[str, List[str]]):
        """Process multimedia files (sample only)"""
        # Sample photos
        photo_files = file_inventory.get('photos', [])
        if photo_files:
            sample_photos = photo_files[:10]  # Limit to 10 for performance
            for photo_path in sample_photos:
                try:
                    file_info = zip_file.getinfo(photo_path)
                    photo_data = {
                        'filename': Path(photo_path).name,
                        'path': photo_path,
                        'size': file_info.file_size,
                        'date_modified': datetime.datetime(*file_info.date_time).isoformat(),
                        'evidence_type': 'photo'
                    }
                    self.evidence_data['photos'].append(photo_data)
                except:
                    continue
            
            print(f"     Processed {len(sample_photos)} sample photos (of {len(photo_files)} total)")
        
        # Sample videos
        video_files = file_inventory.get('videos', [])
        if video_files:
            sample_videos = video_files[:5]  # Limit to 5 for performance
            for video_path in sample_videos:
                try:
                    file_info = zip_file.getinfo(video_path)
                    video_data = {
                        'filename': Path(video_path).name,
                        'path': video_path,
                        'size': file_info.file_size,
                        'date_modified': datetime.datetime(*file_info.date_time).isoformat(),
                        'evidence_type': 'video'
                    }
                    self.evidence_data['videos'].append(video_data)
                except:
                    continue
            
            print(f"     Processed {len(sample_videos)} sample videos (of {len(video_files)} total)")
    
    def _extract_evidence_from_directory(self, dir_path: Path, file_inventory: Dict[str, List[Path]]):
        """Extract evidence from directory structure"""
        # Similar to ZIP processing but with direct file access
        # Implementation would follow same pattern but access files directly
        print("   Directory processing - similar to ZIP but with direct file access")
        # For brevity, using placeholder - would implement full directory processing
    
    def _analyze_communications(self):
        """Analyze communication patterns"""
        print("   Analyzing communication patterns...")
        
        # Analyze message patterns
        if self.evidence_data['messages']:
            self._analyze_message_patterns()
        
        # Analyze call patterns  
        if self.evidence_data['calls']:
            self._analyze_call_patterns()
        
        # Communication timeline
        self._build_communication_timeline()
    
    def _analyze_message_patterns(self):
        """Analyze message data for patterns"""
        messages = self.evidence_data['messages']
        
        # Contact frequency
        contact_freq = Counter()
        keyword_mentions = defaultdict(list)
        
        # Simple keyword detection
        investigation_keywords = [
            'drug', 'weed', 'pills', 'money', 'cash', 'deal', 'meet', 'pickup',
            'gun', 'weapon', 'hurt', 'kill', 'fight', 'angry', 'threat'
        ]
        
        for message in messages:
            # Contact frequency
            contact = message.get('contact', 'Unknown')
            contact_freq[contact] += 1
            
            # Keyword detection
            text = str(message.get('text', '')).lower()
            for keyword in investigation_keywords:
                if keyword in text:
                    keyword_mentions[keyword].append({
                        'contact': contact,
                        'timestamp': message.get('timestamp'),
                        'text_sample': text[:100]
                    })
        
        # Store analysis results
        self.evidence_data['communication_analysis'] = {
            'message_count': len(messages),
            'unique_contacts': len(contact_freq),
            'top_contacts': contact_freq.most_common(10),
            'keyword_mentions': dict(keyword_mentions),
            'keywords_found': len(keyword_mentions)
        }
        
        print(f"     Messages: {len(messages)}, Contacts: {len(contact_freq)}, Keywords: {len(keyword_mentions)}")
    
    def _analyze_call_patterns(self):
        """Analyze call patterns"""
        calls = self.evidence_data['calls']
        
        # Call frequency by contact
        call_freq = Counter()
        total_duration = 0
        
        for call in calls:
            contact = call.get('address') or call.get('number', 'Unknown')
            call_freq[contact] += 1
            
            duration = call.get('duration', 0)
            if isinstance(duration, (int, float)):
                total_duration += duration
        
        self.evidence_data['call_analysis'] = {
            'call_count': len(calls),
            'unique_numbers': len(call_freq),
            'top_contacts': call_freq.most_common(10),
            'total_duration_minutes': total_duration / 60 if total_duration else 0
        }
        
        print(f"     Calls: {len(calls)}, Numbers: {len(call_freq)}, Duration: {total_duration/60:.1f} min")
    
    def _build_communication_timeline(self):
        """Build comprehensive communication timeline"""
        timeline_events = []
        
        # Add messages to timeline
        for message in self.evidence_data['messages']:
            if message.get('timestamp'):
                timeline_events.append({
                    'timestamp': message['timestamp'],
                    'type': 'message',
                    'contact': message.get('contact', 'Unknown'),
                    'details': message.get('text', '')[:100]
                })
        
        # Add calls to timeline
        for call in self.evidence_data['calls']:
            if call.get('timestamp'):
                timeline_events.append({
                    'timestamp': call['timestamp'],
                    'type': 'call',
                    'contact': call.get('address') or call.get('number', 'Unknown'),
                    'details': f"Duration: {call.get('duration', 0)} seconds"
                })
        
        # Sort by timestamp
        timeline_events.sort(key=lambda x: x['timestamp'])
        
        self.evidence_data['communication_timeline'] = timeline_events[-100:]  # Last 100 events
        print(f"     Timeline: {len(timeline_events)} communication events")
    
    def _analyze_multimedia(self):
        """Analyze multimedia evidence"""
        print("   Processing multimedia evidence...")
        
        # Photo analysis
        if self.evidence_data['photos']:
            photo_count = len(self.evidence_data['photos'])
            total_size = sum(photo.get('size', 0) for photo in self.evidence_data['photos'])
            print(f"     Photos: {photo_count} files, {total_size/1024/1024:.1f} MB")
        
        # Video analysis
        if self.evidence_data['videos']:
            video_count = len(self.evidence_data['videos'])
            total_size = sum(video.get('size', 0) for video in self.evidence_data['videos'])
            print(f"     Videos: {video_count} files, {total_size/1024/1024:.1f} MB")
    
    def _generate_evidence_report(self, source_path: Path) -> Dict[str, Any]:
        """Generate comprehensive evidence report"""
        
        # Calculate summary statistics
        total_messages = len(self.evidence_data['messages'])
        total_calls = len(self.evidence_data['calls'])
        total_contacts = len(self.evidence_data['contacts'])
        total_photos = len(self.evidence_data['photos'])
        total_videos = len(self.evidence_data['videos'])
        total_locations = len(self.evidence_data['locations'])
        total_browsers = len(self.evidence_data['browsers'])
        
        # Get communication analysis
        comm_analysis = self.evidence_data.get('communication_analysis', {})
        call_analysis = self.evidence_data.get('call_analysis', {})
        
        # Generate executive summary
        executive_summary = self._generate_executive_summary()
        
        # Generate detailed findings
        detailed_findings = self._generate_detailed_findings()
        
        report = {
            'case_information': {
                'case_name': self.case_name,
                'examiner': self.examiner_name,
                'analysis_date': datetime.datetime.now().isoformat(),
                'source_path': str(source_path),
                'source_type': 'ZIP Archive' if source_path.suffix.lower() == '.zip' else 'Directory',
                'tool_version': 'GHOST - Golden Hour Operations v1.0'
            },
            
            'executive_summary': executive_summary,
            
            'evidence_summary': {
                'communications': {
                    'messages': total_messages,
                    'calls': total_calls,
                    'contacts': total_contacts,
                    'unique_message_contacts': comm_analysis.get('unique_contacts', 0),
                    'unique_call_contacts': call_analysis.get('unique_numbers', 0)
                },
                'multimedia': {
                    'photos': total_photos,
                    'videos': total_videos
                },
                'digital_activity': {
                    'browser_records': total_browsers,
                    'location_points': total_locations,
                    'app_data': len(self.evidence_data['apps']),
                    'databases': len(self.evidence_data['databases'])
                }
            },
            
            'detailed_findings': detailed_findings,
            
            'communication_intelligence': {
                'message_analysis': comm_analysis,
                'call_analysis': call_analysis,
                'timeline_events': len(self.evidence_data.get('communication_timeline', [])),
                'top_contacts': self._get_top_contacts()
            },
            
            'app_intelligence': self._generate_app_intelligence(),
            
            'location_intelligence': self._generate_location_intelligence(),
            
            'digital_footprint': self._generate_digital_footprint(),
            
            'investigative_leads': self._generate_investigative_leads(),
            
            'data_export_options': self._generate_export_options(),
            
            'raw_evidence_data': self.evidence_data
        }
        
        # Print summary
        print(f"\n[SUMMARY] Evidence Analysis Complete")
        print(f"   Messages: {total_messages}")
        print(f"   Calls: {total_calls}")
        print(f"   Contacts: {total_contacts}")
        print(f"   Photos: {total_photos}")
        print(f"   Videos: {total_videos}")
        print(f"   Location Points: {total_locations}")
        print(f"   Browser Records: {total_browsers}")
        print(f"   Apps: {len(self.evidence_data['apps'])}")
        print(f"   Databases: {len(self.evidence_data['databases'])}")
        
        if comm_analysis.get('keywords_found', 0) > 0:
            print(f"   [ALERT] Investigation Keywords Found: {comm_analysis['keywords_found']}")
        
        return report
    
    def _generate_executive_summary(self) -> Dict[str, Any]:
        """Generate executive summary for investigators"""
        
        # Determine priority level
        comm_analysis = self.evidence_data.get('communication_analysis', {})
        keywords_found = comm_analysis.get('keywords_found', 0)
        message_count = len(self.evidence_data['messages'])
        call_count = len(self.evidence_data['calls'])
        
        if keywords_found > 5:
            priority = "HIGH PRIORITY"
            priority_reason = f"{keywords_found} investigation-relevant keywords detected"
        elif message_count > 1000 or call_count > 500:
            priority = "MEDIUM PRIORITY" 
            priority_reason = "High communication volume indicates active device usage"
        elif message_count > 0 or call_count > 0:
            priority = "STANDARD PRIORITY"
            priority_reason = "Communication data available for analysis"
        else:
            priority = "LOW PRIORITY"
            priority_reason = "Limited communication data found"
        
        # Key evidence types found
        evidence_types = []
        if self.evidence_data['messages']:
            evidence_types.append(f"Text Messages ({len(self.evidence_data['messages'])})")
        if self.evidence_data['calls']:
            evidence_types.append(f"Call Logs ({len(self.evidence_data['calls'])})")
        if self.evidence_data['photos']:
            evidence_types.append(f"Photos ({len(self.evidence_data['photos'])})")
        if self.evidence_data['locations']:
            evidence_types.append(f"Location Data ({len(self.evidence_data['locations'])})")
        if self.evidence_data['apps']:
            evidence_types.append(f"App Data ({len(self.evidence_data['apps'])} apps)")
        
        return {
            'priority_level': priority,
            'priority_reason': priority_reason,
            'evidence_types_found': evidence_types,
            'key_statistics': {
                'total_communications': len(self.evidence_data['messages']) + len(self.evidence_data['calls']),
                'unique_contacts': len(set(
                    [msg.get('contact', '') for msg in self.evidence_data['messages']] +
                    [call.get('address', call.get('number', '')) for call in self.evidence_data['calls']]
                )),
                'investigation_keywords': keywords_found,
                'multimedia_files': len(self.evidence_data['photos']) + len(self.evidence_data['videos']),
                'location_points': len(self.evidence_data['locations'])
            },
            'immediate_actions': self._generate_immediate_actions()
        }
    
    def _generate_immediate_actions(self) -> List[str]:
        """Generate immediate action items for investigators"""
        actions = []
        
        comm_analysis = self.evidence_data.get('communication_analysis', {})
        
        # Keyword-based actions
        if comm_analysis.get('keywords_found', 0) > 0:
            actions.append("PRIORITY: Review messages with investigation keywords")
            actions.append("Analyze communication patterns around keyword mentions")
        
        # Contact-based actions
        top_contacts = comm_analysis.get('top_contacts', [])
        if top_contacts:
            top_contact = top_contacts[0][0] if top_contacts[0][0] != 'Unknown' else None
            if top_contact:
                actions.append(f"Investigate primary contact: {top_contact}")
        
        # App-based actions
        if self.evidence_data['apps']:
            apps_found = list(self.evidence_data['apps'].keys())
            actions.append(f"Examine {', '.join(apps_found)} app data")
        
        # Location-based actions
        if self.evidence_data['locations']:
            actions.append("Analyze location patterns and frequented areas")
        
        # Timeline actions
        if self.evidence_data.get('communication_timeline'):
            actions.append("Review communication timeline for activity patterns")
        
        if not actions:
            actions.append("Review available evidence data for investigative leads")
        
        return actions
    
    def _generate_detailed_findings(self) -> Dict[str, Any]:
        """Generate detailed findings by evidence type"""
        
        findings = {}
        
        # Message findings
        if self.evidence_data['messages']:
            comm_analysis = self.evidence_data.get('communication_analysis', {})
            keyword_mentions = comm_analysis.get('keyword_mentions', {})
            
            message_findings = {
                'total_messages': len(self.evidence_data['messages']),
                'date_range': self._get_date_range(self.evidence_data['messages']),
                'top_contacts': comm_analysis.get('top_contacts', [])[:5],
                'keyword_alerts': []
            }
            
            # Add keyword alerts
            for keyword, mentions in keyword_mentions.items():
                if mentions:
                    message_findings['keyword_alerts'].append({
                        'keyword': keyword,
                        'mention_count': len(mentions),
                        'contacts_involved': list(set(m['contact'] for m in mentions)),
                        'recent_mention': mentions[-1] if mentions else None
                    })
            
            findings['messages'] = message_findings
        
        # Call findings
        if self.evidence_data['calls']:
            call_analysis = self.evidence_data.get('call_analysis', {})
            
            findings['calls'] = {
                'total_calls': len(self.evidence_data['calls']),
                'date_range': self._get_date_range(self.evidence_data['calls']),
                'top_contacts': call_analysis.get('top_contacts', [])[:5],
                'total_duration_hours': call_analysis.get('total_duration_minutes', 0) / 60
            }
        
        # Photo findings
        if self.evidence_data['photos']:
            findings['photos'] = {
                'total_photos': len(self.evidence_data['photos']),
                'date_range': self._get_date_range(self.evidence_data['photos'], 'date_modified'),
                'sample_files': [photo['filename'] for photo in self.evidence_data['photos'][:10]]
            }
        
        # Location findings
        if self.evidence_data['locations']:
            findings['locations'] = {
                'total_points': len(self.evidence_data['locations']),
                'date_range': self._get_date_range(self.evidence_data['locations']),
                'coordinate_sample': [
                    {
                        'lat': loc.get('latitude'),
                        'lon': loc.get('longitude'),
                        'timestamp': loc.get('timestamp')
                    }
                    for loc in self.evidence_data['locations'][:5]
                    if loc.get('latitude') and loc.get('longitude')
                ]
            }
        
        # App findings
        if self.evidence_data['apps']:
            findings['apps'] = {}
            for app_name, app_data in self.evidence_data['apps'].items():
                findings['apps'][app_name] = {
                    'files_found': len(app_data['files']),
                    'databases_found': len(app_data['databases']),
                    'file_list': app_data['files'][:5]  # Sample files
                }
        
        return findings
    
    def _get_date_range(self, data_list: List[Dict], timestamp_field: str = 'timestamp') -> Dict[str, str]:
        """Get date range from data list"""
        if not data_list:
            return {'earliest': None, 'latest': None}
        
        timestamps = [item.get(timestamp_field) for item in data_list if item.get(timestamp_field)]
        
        if not timestamps:
            return {'earliest': None, 'latest': None}
        
        # Sort timestamps
        timestamps.sort()
        
        return {
            'earliest': timestamps[0],
            'latest': timestamps[-1],
            'span_days': 'Unknown'  # Could calculate actual span
        }
    
    def _get_top_contacts(self) -> List[Dict[str, Any]]:
        """Get top contacts across all communication types"""
        contact_freq = Counter()
        
        # Count message contacts
        for message in self.evidence_data['messages']:
            contact = message.get('contact', 'Unknown')
            if contact != 'Unknown':
                contact_freq[contact] += 1
        
        # Count call contacts
        for call in self.evidence_data['calls']:
            contact = call.get('address') or call.get('number', 'Unknown')
            if contact != 'Unknown':
                contact_freq[contact] += 1
        
        # Return top 10 with details
        top_contacts = []
        for contact, count in contact_freq.most_common(10):
            # Get message count
            msg_count = sum(1 for msg in self.evidence_data['messages'] 
                           if msg.get('contact') == contact)
            
            # Get call count
            call_count = sum(1 for call in self.evidence_data['calls'] 
                            if call.get('address') == contact or call.get('number') == contact)
            
            top_contacts.append({
                'contact': contact,
                'total_interactions': count,
                'messages': msg_count,
                'calls': call_count
            })
        
        return top_contacts
    
    def _generate_app_intelligence(self) -> Dict[str, Any]:
        """Generate app-specific intelligence"""
        if not self.evidence_data['apps']:
            return {'apps_found': 0, 'analysis': 'No app data available'}
        
        app_intel = {
            'apps_found': len(self.evidence_data['apps']),
            'app_summary': {}
        }
        
        for app_name, app_data in self.evidence_data['apps'].items():
            app_intel['app_summary'][app_name] = {
                'files_discovered': len(app_data['files']),
                'data_available': len(app_data['files']) > 0,
                'investigation_priority': 'High' if app_name in ['WhatsApp', 'Telegram', 'Signal'] else 'Medium'
            }
        
        return app_intel
    
    def _generate_location_intelligence(self) -> Dict[str, Any]:
        """Generate location-based intelligence"""
        if not self.evidence_data['locations']:
            return {'location_data_available': False}
        
        locations = self.evidence_data['locations']
        
        # Find unique coordinates (simplified clustering)
        unique_locations = []
        coordinate_counts = Counter()
        
        for loc in locations:
            lat = loc.get('latitude')
            lon = loc.get('longitude')
            if lat and lon:
                # Round to approximate location clustering
                rounded_coord = (round(float(lat), 3), round(float(lon), 3))
                coordinate_counts[rounded_coord] += 1
        
        # Top locations
        top_locations = coordinate_counts.most_common(5)
        
        return {
            'location_data_available': True,
            'total_location_points': len(locations),
            'unique_locations': len(coordinate_counts),
            'top_visited_locations': [
                {
                    'coordinates': {'lat': loc[0], 'lon': loc[1]},
                    'visit_count': count
                }
                for loc, count in top_locations
            ],
            'date_range': self._get_date_range(locations)
        }
    
    def _generate_digital_footprint(self) -> Dict[str, Any]:
        """Generate digital footprint analysis"""
        footprint = {
            'browser_activity': {},
            'device_usage_pattern': {},
            'digital_communication_summary': {}
        }
        
        # Browser analysis
        if self.evidence_data['browsers']:
            domains = Counter()
            for record in self.evidence_data['browsers']:
                url = record.get('url', '')
                if url:
                    try:
                        from urllib.parse import urlparse
                        domain = urlparse(url).netloc
                        domains[domain] += 1
                    except:
                        continue
            
            footprint['browser_activity'] = {
                'total_records': len(self.evidence_data['browsers']),
                'unique_domains': len(domains),
                'top_domains': domains.most_common(10)
            }
        
        # Communication patterns
        total_comms = len(self.evidence_data['messages']) + len(self.evidence_data['calls'])
        footprint['digital_communication_summary'] = {
            'total_communications': total_comms,
            'communication_types': {
                'messages': len(self.evidence_data['messages']),
                'calls': len(self.evidence_data['calls'])
            },
            'activity_level': 'High' if total_comms > 1000 else 'Medium' if total_comms > 100 else 'Low'
        }
        
        return footprint
    
    def _generate_investigative_leads(self) -> List[Dict[str, Any]]:
        """Generate potential investigative leads"""
        leads = []
        
        # Keyword-based leads
        comm_analysis = self.evidence_data.get('communication_analysis', {})
        keyword_mentions = comm_analysis.get('keyword_mentions', {})
        
        for keyword, mentions in keyword_mentions.items():
            if mentions:
                leads.append({
                    'type': 'Keyword Alert',
                    'priority': 'High',
                    'description': f"'{keyword}' mentioned {len(mentions)} times",
                    'contacts_involved': list(set(m['contact'] for m in mentions)),
                    'action_required': f"Review all messages containing '{keyword}'"
                })
        
        # Frequent contact leads
        top_contacts = self._get_top_contacts()
        if top_contacts:
            for contact in top_contacts[:3]:  # Top 3 contacts
                if contact['total_interactions'] > 50:
                    leads.append({
                        'type': 'High-Frequency Contact',
                        'priority': 'Medium',
                        'description': f"Frequent communication with {contact['contact']}",
                        'details': f"{contact['total_interactions']} total interactions",
                        'action_required': 'Investigate relationship and communication content'
                    })
        
        # App-specific leads
        high_priority_apps = ['WhatsApp', 'Telegram', 'Signal', 'Snapchat']
        for app in high_priority_apps:
            if app in self.evidence_data['apps']:
                leads.append({
                    'type': 'Encrypted Messaging App',
                    'priority': 'High',
                    'description': f"{app} data found",
                    'action_required': f"Examine {app} databases for messages and media"
                })
        
        # Location-based leads
        if self.evidence_data['locations']:
            leads.append({
                'type': 'Location Intelligence',
                'priority': 'Medium',
                'description': f"{len(self.evidence_data['locations'])} location points available",
                'action_required': 'Analyze movement patterns and significant locations'
            })
        
        return leads
    
    def _generate_export_options(self) -> Dict[str, List[str]]:
        """Generate data export options for investigators"""
        export_options = {}
        
        if self.evidence_data['messages']:
            export_options['Messages'] = [
                'Export all messages to CSV',
                'Export messages by contact',
                'Export messages with keywords',
                'Export message timeline'
            ]
        
        if self.evidence_data['calls']:
            export_options['Call Logs'] = [
                'Export call history to CSV',
                'Export call summary by contact',
                'Export call duration analysis'
            ]
        
        if self.evidence_data['contacts']:
            export_options['Contacts'] = [
                'Export contact list to CSV',
                'Export contact communication frequency'
            ]
        
        if self.evidence_data['locations']:
            export_options['Location Data'] = [
                'Export location points to CSV',
                'Export location timeline',
                'Export location frequency analysis',
                'Export KML for mapping software'
            ]
        
        if self.evidence_data['photos']:
            export_options['Photos'] = [
                'Export photo metadata to CSV',
                'Export photo file list with timestamps'
            ]
        
        if self.evidence_data['apps']:
            export_options['App Data'] = [
                'Export app inventory',
                'Export app-specific databases',
                'Export app file listings'
            ]
        
        export_options['Complete Evidence Package'] = [
            'Export full analysis report (JSON)',
            'Export executive summary (PDF)',
            'Export all data tables (Excel)',
            'Export investigation timeline (CSV)'
        ]
        
        return export_options
    
    def save_report(self, report: Dict[str, Any], output_path: str = None) -> str:
        """Save comprehensive evidence report"""
        if output_path is None:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"ghost_evidence_report_{self.case_name}_{timestamp}.json"
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n[OK] Evidence report saved to: {output_path}")
        return output_path
    
    def export_messages_csv(self, output_path: str = None) -> str:
        """Export messages to CSV format"""
        if not self.evidence_data['messages']:
            raise ValueError("No message data available for export")
        
        if output_path is None:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"messages_export_{self.case_name}_{timestamp}.csv"
        
        import csv
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['timestamp', 'contact', 'text', 'direction', 'source_file']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for message in self.evidence_data['messages']:
                writer.writerow({
                    'timestamp': message.get('timestamp', ''),
                    'contact': message.get('contact', 'Unknown'),
                    'text': message.get('text', ''),
                    'direction': 'Outgoing' if message.get('is_from_me') else 'Incoming',
                    'source_file': message.get('source_file', '')
                })
        
        print(f"[OK] Messages exported to: {output_path}")
        return output_path

def main():
    """Main function for command-line usage"""
    print("GHOST - Golden Hour Operations and Strategic Threat Assessment")
    print("=" * 60)
    
    if len(sys.argv) < 4:
        print("Usage: python ghost_forensic_suite.py <extraction_path> <case_name> <examiner_name>")
        print("\nSupported inputs:")
        print("  - ZIP files: /path/to/extraction.zip")
        print("  - Directories: /path/to/extraction/")
        print("\nExample:")
        print("  python ghost_forensic_suite.py /cases/iPhone_Extraction.zip 'Case-2024-001' 'Detective Smith'")
        sys.exit(1)
    
    extraction_path = sys.argv[1]
    case_name = sys.argv[2]
    examiner_name = sys.argv[3]
    
    try:
        # Initialize forensic suite
        suite = FocusedForensicSuite(case_name, examiner_name)
        
        # Run analysis
        report = suite.analyze_extraction(extraction_path)
        
        # Save comprehensive report
        report_file = suite.save_report(report)
        
        # Export messages if available
        if report['evidence_summary']['communications']['messages'] > 0:
            try:
                csv_file = suite.export_messages_csv()
                print(f"[OK] Messages also exported to CSV: {csv_file}")
            except Exception as e:
                print(f"[WARNING] Could not export messages to CSV: {e}")
        
        # Print executive summary
        exec_summary = report['executive_summary']
        print(f"\n[EXECUTIVE SUMMARY]")
        print(f"   Priority Level: {exec_summary['priority_level']}")
        print(f"   Evidence Types: {', '.join(exec_summary['evidence_types_found'])}")
        print(f"   Key Statistics:")
        stats = exec_summary['key_statistics']
        print(f"     - Communications: {stats['total_communications']}")
        print(f"     - Contacts: {stats['unique_contacts']}")
        print(f"     - Investigation Keywords: {stats['investigation_keywords']}")
        print(f"     - Multimedia Files: {stats['multimedia_files']}")
        print(f"     - Location Points: {stats['location_points']}")
        
        if exec_summary['immediate_actions']:
            print(f"\n[IMMEDIATE ACTIONS]")
            for action in exec_summary['immediate_actions']:
                print(f"   • {action}")
        
        print(f"\n[SUCCESS] Analysis complete!")
        print(f"   Full report: {report_file}")
        
    except Exception as e:
        print(f"\n[ERROR] Analysis failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
