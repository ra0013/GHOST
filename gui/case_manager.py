#!/usr/bin/env python3
"""
GHOST Evidence Analysis - Case Manager
Handles case information, validation, and persistence
"""

import json
import datetime
from pathlib import Path
from tkinter import messagebox
from typing import Dict, Any, Optional, Callable

class CaseManager:
    """Manages case information and validation"""
    
    def __init__(self):
        # Case data storage
        self._case_data = {
            'case_name': '',
            'examiner_name': '',
            'extraction_path': '',
            'created_date': None,
            'last_modified': None
        }
        
        # Event callbacks
        self.on_case_loaded: Optional[Callable] = None
        self.on_case_saved: Optional[Callable] = None
        self.on_case_changed: Optional[Callable] = None
    
    def set_case_name(self, case_name: str):
        """Set case name"""
        self._case_data['case_name'] = case_name.strip()
        self._notify_case_changed()
    
    def set_examiner_name(self, examiner_name: str):
        """Set examiner name"""
        self._case_data['examiner_name'] = examiner_name.strip()
        self._notify_case_changed()
    
    def set_extraction_path(self, extraction_path: str):
        """Set extraction path"""
        self._case_data['extraction_path'] = extraction_path.strip()
        self._notify_case_changed()
    
    def get_case_info(self) -> Dict[str, Any]:
        """Get current case information"""
        return self._case_data.copy()
    
    def get_case_name(self) -> str:
        """Get case name"""
        return self._case_data['case_name']
    
    def get_examiner_name(self) -> str:
        """Get examiner name"""
        return self._case_data['examiner_name']
    
    def get_extraction_path(self) -> str:
        """Get extraction path"""
        return self._case_data['extraction_path']
    
    def validate_case_info(self) -> bool:
        """Validate current case information"""
        errors = []
        
        if not self._case_data['case_name']:
            errors.append("Please enter a case name")
        
        if not self._case_data['examiner_name']:
            errors.append("Please enter examiner name")
        
        if not self._case_data['extraction_path']:
            errors.append("Please select extraction path")
        else:
            extraction_path = Path(self._case_data['extraction_path'])
            if not extraction_path.exists():
                errors.append("Extraction path does not exist")
        
        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return False
        
        return True
    
    def save_case(self, filename: str) -> bool:
        """Save case to file"""
        try:
            case_data = self._case_data.copy()
            case_data['saved_date'] = datetime.datetime.now().isoformat()
            case_data['version'] = '1.0'
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(case_data, f, indent=2)
            
            self._case_data['last_modified'] = case_data['saved_date']
            
            if self.on_case_saved:
                self.on_case_saved(filename)
            
            return True
            
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save case: {str(e)}")
            return False
    
    def load_case(self, filename: str) -> bool:
        """Load case from file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                case_data = json.load(f)
            
            # Validate loaded data
            required_fields = ['case_name', 'examiner_name', 'extraction_path']
            for field in required_fields:
                if field not in case_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Update case data
            self._case_data.update(case_data)
            self._case_data['last_modified'] = datetime.datetime.now().isoformat()
            
            if self.on_case_loaded:
                self.on_case_loaded(self._case_data)
            
            return True
            
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load case: {str(e)}")
            return False
    
    def create_new_case(self):
        """Create a new case (reset current data)"""
        old_data = self._case_data.copy()
        
        self._case_data = {
            'case_name': '',
            'examiner_name': old_data.get('examiner_name', ''),  # Keep examiner name
            'extraction_path': '',
            'created_date': datetime.datetime.now().isoformat(),
            'last_modified': None
        }
        
        self._notify_case_changed()
    
    def get_case_summary(self) -> str:
        """Get a text summary of the case"""
        if not self._case_data['case_name']:
            return "No case loaded"
        
        summary = f"Case: {self._case_data['case_name']}\n"
        summary += f"Examiner: {self._case_data['examiner_name']}\n"
        summary += f"Extraction: {self._case_data['extraction_path']}\n"
        
        if self._case_data.get('created_date'):
            summary += f"Created: {self._case_data['created_date']}\n"
        
        if self._case_data.get('last_modified'):
            summary += f"Modified: {self._case_data['last_modified']}\n"
        
        return summary
    
    def is_case_loaded(self) -> bool:
        """Check if a case is currently loaded"""
        return bool(self._case_data['case_name'] and 
                   self._case_data['examiner_name'] and 
                   self._case_data['extraction_path'])
    
    def get_extraction_type(self) -> str:
        """Determine the type of extraction"""
        if not self._case_data['extraction_path']:
            return "Unknown"
        
        path = Path(self._case_data['extraction_path'])
        
        if path.is_file():
            if path.suffix.lower() == '.zip':
                return "ZIP Archive"
            else:
                return "File"
        elif path.is_dir():
            return "Directory"
        else:
            return "Unknown"
    
    def get_extraction_size(self) -> str:
        """Get the size of the extraction"""
        if not self._case_data['extraction_path']:
            return "Unknown"
        
        try:
            path = Path(self._case_data['extraction_path'])
            
            if path.is_file():
                size_bytes = path.stat().st_size
                return self._format_file_size(size_bytes)
            elif path.is_dir():
                # Calculate directory size
                total_size = sum(
                    f.stat().st_size 
                    for f in path.rglob('*') 
                    if f.is_file()
                )
                return self._format_file_size(total_size)
        except Exception:
            pass
        
        return "Unknown"
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        
        return f"{size_bytes:.1f} PB"
    
    def _notify_case_changed(self):
        """Notify that case data has changed"""
        if self.on_case_changed:
            self.on_case_changed(self._case_data)
    
    def export_case_info(self) -> Dict[str, Any]:
        """Export case information for reports"""
        return {
            'case_name': self._case_data['case_name'],
            'examiner': self._case_data['examiner_name'],
            'analysis_date': datetime.datetime.now().isoformat(),
            'source_path': self._case_data['extraction_path'],
            'source_type': self.get_extraction_type(),
            'source_size': self.get_extraction_size(),
            'tool_version': 'GHOST Evidence Analysis Interface v1.0'
        }
