# modules/forensic_logger.py
"""
Forensic Logger Module
Maintains chain of custody and audit trail
"""

import logging
import datetime
import hashlib
from pathlib import Path
from typing import List, Dict, Any
import json

class ForensicLogger:
    """Maintains forensic audit trail and chain of custody"""
    
    def __init__(self, case_name: str, examiner_name: str):
        self.case_name = case_name
        self.examiner_name = examiner_name
        self.start_time = datetime.datetime.now()
        
        # Chain of custody entries
        self.chain_of_custody = []
        
        # Setup logging
        self.log_filename = f"forensic_log_{case_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - [FORENSIC] - %(message)s',
            handlers=[
                logging.FileHandler(self.log_filename),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger('ForensicIntel')
        
        # Initialize chain of custody
        self._initialize_chain_of_custody()
    
    def _initialize_chain_of_custody(self):
        """Initialize forensic chain of custody"""
        initial_entry = {
            'timestamp': datetime.datetime.now().isoformat(),
            'action': 'ANALYSIS_INITIATED',
            'examiner': self.examiner_name,
            'case': self.case_name,
            'tool': 'Modular Forensic Intelligence Suite v2.0',
            'details': 'Forensic analysis session initiated'
        }
        
        self.chain_of_custody.append(initial_entry)
        self.log_action("CHAIN_OF_CUSTODY", "Analysis session initiated")
    
    def log_action(self, action: str, details: str, file_hash: str = None):
        """Log forensic action with hash verification"""
        timestamp = datetime.datetime.now().isoformat()
        
        # Create chain of custody entry
        custody_entry = {
            'timestamp': timestamp,
            'action': action,
            'examiner': self.examiner_name,
            'case': self.case_name,
            'details': details
        }
        
        if file_hash:
            custody_entry['file_hash'] = file_hash
        
        self.chain_of_custody.append(custody_entry)
        
        # Log to file
        message = f"ACTION: {action} | DETAILS: {details}"
        if file_hash:
            message += f" | FILE_HASH: {file_hash}"
        
        self.logger.info(message)
    
    def log_database_access(self, db_path: str, operation: str, record_count: int = None):
        """Log database access for chain of custody"""
        file_hash = self.calculate_file_hash(Path(db_path))
        
        details = f"Database {operation}: {db_path}"
        if record_count is not None:
            details += f" | Records processed: {record_count}"
        
        self.log_action("DATABASE_ACCESS", details, file_hash)
    
    def log_evidence_item(self, evidence_type: str, source_path: str, description: str):
        """Log evidence item in chain of custody"""
        file_hash = self.calculate_file_hash(Path(source_path)) if Path(source_path).exists() else None
        
        details = f"Evidence type: {evidence_type} | Source: {source_path} | Description: {description}"
        self.log_action("EVIDENCE_ITEM", details, file_hash)
    
    def log_intelligence_finding(self, module_name: str, finding_type: str, risk_score: int):
        """Log intelligence finding"""
        details = f"Module: {module_name} | Type: {finding_type} | Risk Score: {risk_score}"
        self.log_action("INTELLIGENCE_FINDING", details)
    
    def calculate_file_hash(self, file_path: Path, algorithm: str = 'sha256') -> str:
        """Calculate file hash for integrity verification"""
        try:
            hash_obj = hashlib.new(algorithm)
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except Exception as e:
            return f"ERROR: {str(e)}"
    
    def get_analysis_duration(self) -> float:
        """Get analysis duration in seconds"""
        return (datetime.datetime.now() - self.start_time).total_seconds()
    
    def finalize_chain_of_custody(self, total_findings: int, databases_processed: int):
        """Finalize chain of custody with summary"""
        final_entry = {
            'timestamp': datetime.datetime.now().isoformat(),
            'action': 'ANALYSIS_COMPLETED',
            'examiner': self.examiner_name,
            'case': self.case_name,
            'analysis_duration_seconds': self.get_analysis_duration(),
            'total_findings': total_findings,
            'databases_processed': databases_processed,
            'tool_version': 'Modular Forensic Intelligence Suite v2.0'
        }
        
        self.chain_of_custody.append(final_entry)
        self.log_action("ANALYSIS_COMPLETE", f"Analysis completed with {total_findings} findings")
    
    def export_chain_of_custody(self, output_path: str = None):
        """Export chain of custody to JSON file"""
        if output_path is None:
            output_path = f"chain_of_custody_{self.case_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        custody_export = {
            'case_name': self.case_name,
            'examiner': self.examiner_name,
            'export_date': datetime.datetime.now().isoformat(),
            'log_file': self.log_filename,
            'total_entries': len(self.chain_of_custody),
            'chain_of_custody': self.chain_of_custody
        }
        
        with open(output_path, 'w') as f:
            json.dump(custody_export, f, indent=2)
        
        self.log_action("CUSTODY_EXPORT", f"Chain of custody exported to {output_path}")
        return output_path
    
    def verify_log_integrity(self) -> Dict[str, Any]:
        """Verify the integrity of the forensic log"""
        verification_result = {
            'log_file': self.log_filename,
            'file_exists': Path(self.log_filename).exists(),
            'entries_count': len(self.chain_of_custody),
            'time_span': None,
            'integrity_verified': False
        }
        
        if self.chain_of_custody:
            first_entry =
