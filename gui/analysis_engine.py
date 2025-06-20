#!/usr/bin/env python3
"""
GHOST Evidence Analysis - Analysis Engine Wrapper
Handles integration with the forensic analysis backend
"""

import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Callable
import threading

# Try to import the forensic suite
try:
    from ghost_forensic_suite import FocusedForensicSuite
    FORENSIC_SUITE_AVAILABLE = True
except ImportError:
    FORENSIC_SUITE_AVAILABLE = False
    print("[WARNING] Forensic suite not available - using demo mode")

class AnalysisEngine:
    """Wrapper for the forensic analysis engine"""
    
    def __init__(self):
        self.cancel_flag = threading.Event()
        
        # Event callbacks
        self.on_progress_update: Optional[Callable] = None
        self.on_analysis_complete: Optional[Callable] = None
        self.on_analysis_error: Optional[Callable] = None
    
    def analyze_evidence(self, extraction_path: str, case_name: str, examiner_name: str) -> Dict[str, Any]:
        """Analyze evidence and return results"""
        try:
            if FORENSIC_SUITE_AVAILABLE:
                return self._run_real_analysis(extraction_path, case_name, examiner_name)
            else:
                return self._run_demo_analysis(extraction_path, case_name, examiner_name)
        
        except Exception as e:
            if self.on_analysis_error:
                self.on_analysis_error(str(e))
            raise
    
    def _run_real_analysis(self, extraction_path: str, case_name: str, examiner_name: str) -> Dict[str, Any]:
        """Run real forensic analysis"""
        self._update_progress(5, 'Initializing forensic analysis...')
        
        # Initialize forensic suite
        suite = FocusedForensicSuite(case_name, examiner_name)
        
        self._update_progress(10, 'Starting evidence analysis...')
        
        # Run analysis with progress callbacks
        def progress_callback(progress, message):
            if not self.cancel_flag.is_set():
                self._update_progress(progress, message)
        
        # Monkey patch progress reporting
        original_print = print
        def analysis_print(*args, **kwargs):
            message = ' '.join(str(arg) for arg in args)
            if not self.cancel_flag.is_set() and message.startswith('['):
                # Extract progress from forensic suite messages
                if 'STEP' in message:
                    if '1' in message:
                        progress_callback(20, 'Discovering evidence files...')
                    elif '2' in message:
                        progress_callback(40, 'Extracting evidence data...')
                    elif '3' in message:
                        progress_callback(60, 'Analyzing communications...')
                    elif '4' in message:
                        progress_callback(80, 'Processing multimedia...')
                    elif '5' in message:
                        progress_callback(90, 'Generating report...')
            original_print(*args, **kwargs)
        
        # Temporarily replace print
        import builtins
        builtins.print = analysis_print
        
        try:
            # Run the analysis
            report = suite.analyze_extraction(extraction_path)
            
            self._update_progress(100, 'Analysis complete!')
            
            return report
            
        finally:
            # Restore original print
            builtins.print = original_print
    
    def _run_demo_analysis(self, extraction_path: str, case_name: str, examiner_name: str) -> Dict[str, Any]:
        """Run demo analysis with fake data"""
        import time
        
        self._update_progress(10, 'Demo mode - generating sample data...')
        time.sleep(0.5)
        
        self._update_progress(30, 'Creating sample communications...')
        time.sleep(0.5)
        
        self._update_progress(50, 'Generating sample multimedia data...')
        time.sleep(0.5)
        
        self._update_progress(70, 'Creating sample location data...')
        time.sleep(0.5)
        
        self._update_progress(90, 'Finalizing demo report...')
        time.sleep(0.5)
        
        # Generate comprehensive demo data
        demo_report = self._generate_demo_report(extraction_path, case_name, examiner_name)
        
        self._update_progress(100, 'Demo analysis complete!')
        
        return demo_report
    
    def _generate_demo_report(self, extraction_path: str, case_name: str, examiner_name: str) -> Dict[str, Any]:
        """Generate comprehensive demo report"""
        return {
            'case_information': {
                'case_name': case_name,
                'examiner': examiner_name,
                'analysis_date': datetime.datetime.now().isoformat(),
                'source_path': extraction_path,
                'tool_version': 'GHOST Evidence Analysis Interface (Demo Mode)'
            },
            
            'executive_summary': {
                'priority_level': 'MEDIUM PRIORITY',
                'priority_reason': 'Demo analysis with sample indicators',
                'evidence_types_found': [
                    'Text Messages (25)',
                    'Call Logs (18)', 
                    'Photos (47)',
                    'Location Data (156)',
                    'App Data (3 apps)'
                ],
                'key_statistics': {
                    'total_communications': 43,
                    'unique_contacts': 12,
                    'investigation_keywords': 3,
                    'multimedia_files': 52,
                    'location_points': 156
                },
                'immediate_actions': [
                    'Review messages with investigation keywords',
                    'Analyze communication patterns with top contacts',
                    'Examine photo metadata for location intelligence'
                ]
            },
            
            'evidence_summary': {
                'communications': {
                    'messages': 25,
                    'calls': 18,
                    'contacts': 12
                },
                'multimedia': {
                    'photos': 47,
                    'videos': 5
                },
                'digital_activity': {
                    'browser_records': 89,
                    'location_points': 156,
                    'app_data': 3,
                    'databases': 8
                }
            },
            
            'communication_intelligence': {
                'message_analysis': {
                    'message_count': 25,
                    'unique_contacts': 8,
                    'keyword_mentions': {
                        'meet': [
                            {'contact': 'John Doe', 'timestamp': '2025-06-19T14:30:00', 'context': 'Can we meet tomorrow?'},
                            {'contact': 'Jane Smith', 'timestamp': '2025-06-18T09:15:00', 'context': 'Meeting at 3pm'}
                        ],
                        'money': [
                            {'contact': 'Mike Johnson', 'timestamp': '2025-06-17T16:45:00', 'context': 'Need money for gas'}
                        ]
                    },
                    'top_contacts': [
                        ('John Doe', 8),
                        ('Jane Smith', 6),
                        ('Mike Johnson', 4),
                        ('Sarah Wilson', 3),
                        ('Tom Brown', 2)
                    ]
                },
                'call_analysis': {
                    'call_count': 18,
                    'unique_numbers': 7,
                    'total_duration_hours': 2.3,
                    'top_contacts': [
                        ('John Doe', 5),
                        ('Jane Smith', 4),
                        ('Mike Johnson', 3),
                        ('Work', 2)
                    ]
                }
            },
            
            'app_intelligence': {
                'apps_found': 3,
                'app_summary': {
                    'WhatsApp': {
                        'files_discovered': 15,
                        'data_available': True,
                        'investigation_priority': 'High'
                    },
                    'Instagram': {
                        'files_discovered': 8,
                        'data_available': True,
                        'investigation_priority': 'Medium'
                    },
                    'Safari': {
                        'files_discovered': 12,
                        'data_available': True,
                        'investigation_priority': 'Low'
                    }
                }
            },
            
            'investigative_leads': [
                {
                    'type': 'Communication Pattern',
                    'priority': 'High',
                    'description': 'Frequent communication with John Doe (13 total interactions)',
                    'action_required': 'Investigate relationship and communication content'
                },
                {
                    'type': 'Keyword Alert',
                    'priority': 'Medium',
                    'description': 'Multiple mentions of meetings in messages',
                    'action_required': 'Analyze meeting locations and timing patterns'
                },
                {
                    'type': 'App Data',
                    'priority': 'High',
                    'description': 'WhatsApp data available for deep analysis',
                    'action_required': 'Extract and analyze WhatsApp messages and media'
                }
            ],
            
            'raw_evidence_data': {
                'messages': [
                    {
                        'timestamp': '2025-06-19T14:30:00Z',
                        'contact': 'John Doe',
                        'text': 'Can we meet tomorrow at the usual place?',
                        'is_from_me': False,
                        'service': 'SMS',
                        'source_file': 'sms.db'
                    },
                    {
                        'timestamp': '2025-06-19T14:32:00Z',
                        'contact': 'John Doe',
                        'text': 'Sure, what time works for you?',
                        'is_from_me': True,
                        'service': 'SMS',
                        'source_file': 'sms.db'
                    },
                    {
                        'timestamp': '2025-06-18T09:15:00Z',
                        'contact': 'Jane Smith',
                        'text': 'Meeting at 3pm today, don\'t forget',
                        'is_from_me': False,
                        'service': 'SMS',
                        'source_file': 'sms.db'
                    },
                    {
                        'timestamp': '2025-06-17T16:45:00Z',
                        'contact': 'Mike Johnson',
                        'text': 'Need money for gas, can you help?',
                        'is_from_me': False,
                        'service': 'SMS',
                        'source_file': 'sms.db'
                    }
                ],
                'calls': [
                    {
                        'timestamp': '2025-06-19T15:00:00Z',
                        'address': '555-0123',
                        'contact': 'John Doe',
                        'duration': 180,
                        'type': 'outgoing',
                        'source_file': 'call_history.db'
                    },
                    {
                        'timestamp': '2025-06-18T10:30:00Z',
                        'address': '555-0124',
                        'contact': 'Jane Smith',
                        'duration': 95,
                        'type': 'incoming',
                        'source_file': 'call_history.db'
                    }
                ],
                'photos': [
                    {
                        'filename': 'IMG_2025_001.jpg',
                        'path': '/Photos/IMG_2025_001.jpg',
                        'size': 2457600,
                        'date_created': '2025-06-19T12:00:00Z',
                        'date_modified': '2025-06-19T12:00:00Z',
                        'exif': {
                            'gps_latitude': '40.7128',
                            'gps_longitude': '-74.0060',
                            'camera_make': 'Apple',
                            'camera_model': 'iPhone 14'
                        }
                    },
                    {
                        'filename': 'IMG_2025_002.jpg',
                        'path': '/Photos/IMG_2025_002.jpg',
                        'size': 1843200,
                        'date_created': '2025-06-18T16:30:00Z',
                        'date_modified': '2025-06-18T16:30:00Z',
                        'exif': {
                            'camera_make': 'Apple',
                            'camera_model': 'iPhone 14'
                        }
                    }
                ],
                'videos': [
                    {
                        'filename': 'VID_2025_001.mp4',
                        'path': '/Videos/VID_2025_001.mp4',
                        'size': 15728640,
                        'date_created': '2025-06-17T14:00:00Z',
                        'date_modified': '2025-06-17T14:00:00Z',
                        'duration': 45
                    }
                ],
                'locations': [
                    {
                        'timestamp': '2025-06-19T12:00:00Z',
                        'latitude': '40.7128',
                        'longitude': '-74.0060',
                        'accuracy': '5.0',
                        'source': 'GPS'
                    },
                    {
                        'timestamp': '2025-06-18T09:30:00Z',
                        'latitude': '40.7589',
                        'longitude': '-73.9851',
                        'accuracy': '8.0',
                        'source': 'WiFi'
                    }
                ],
                'contacts': [
                    {
                        'first_name': 'John',
                        'last_name': 'Doe',
                        'phone': '555-0123',
                        'email': 'john.doe@email.com'
                    },
                    {
                        'first_name': 'Jane',
                        'last_name': 'Smith',
                        'phone': '555-0124',
                        'email': 'jane.smith@email.com'
                    },
                    {
                        'first_name': 'Mike',
                        'last_name': 'Johnson',
                        'phone': '555-0125'
                    }
                ],
                'apps': {
                    'WhatsApp': {
                        'files': [
                            'WhatsApp/Databases/msgstore.db',
                            'WhatsApp/Databases/wa.db',
                            'WhatsApp/Media/WhatsApp Images/'
                        ]
                    },
                    'Instagram': {
                        'files': [
                            'Instagram/instagram.db',
                            'Instagram/Cache/'
                        ]
                    },
                    'Safari': {
                        'files': [
                            'Safari/History.db',
                            'Safari/Downloads.plist'
                        ]
                    }
                }
            }
        }
    
    def cancel_analysis(self):
        """Cancel the current analysis"""
        self.cancel_flag.set()
    
    def _update_progress(self, progress: int, message: str):
        """Update analysis progress"""
        if self.on_progress_update and not self.cancel_flag.is_set():
            self.on_progress_update(progress, message)
