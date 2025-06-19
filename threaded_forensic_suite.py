#!/usr/bin/env python3
"""
Threaded Forensic Intelligence Suite - Enhanced Performance
Multi-threaded analysis for faster processing of zip files and large datasets
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
import threading
import concurrent.futures
import time
from queue import Queue

# Set UTF-8 encoding for Windows compatibility
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent / "modules"))

# Import the fixed modules
try:
    from config_manager import ConfigurationManager
    from database_inspector import DatabaseInspector
    from encryption_detector import EncryptionDetector
    from intelligence_modules import IntelligenceModuleFactory
    from forensic_logger import ForensicLogger
    from data_extractor import DataExtractor
    print("[OK] All modules imported successfully")
except ImportError as e:
    print(f"[ERROR] Error importing modules: {e}")
    print("Make sure all module files are in the 'modules' directory")
    sys.exit(1)

class ThreadedForensicSuite:
    """Multi-threaded forensic intelligence suite for enhanced performance"""
    
    def __init__(self, case_name: str, examiner_name: str, max_workers: int = None):
        self.case_name = case_name
        self.examiner_name = examiner_name
        
        # Threading configuration
        self.max_workers = max_workers or min(8, (os.cpu_count() or 1) + 4)
        self.progress_lock = threading.Lock()
        self.results_lock = threading.Lock()
        
        print(f"[INFO] Initializing Threaded Forensic Intelligence Suite")
        print(f"   Case: {case_name}")
        print(f"   Examiner: {examiner_name}")
        print(f"   Max Workers: {self.max_workers}")
        
        # Initialize core components
        try:
            self.config_manager = ConfigurationManager()
            self.logger = ForensicLogger(case_name, examiner_name)
            
            # Create thread-safe components
            self.module_factory = IntelligenceModuleFactory(
                self.config_manager.keywords,
                self.config_manager.modules,
                self.logger
            )
            
            print("[OK] All components initialized successfully")
            
        except Exception as e:
            print(f"[ERROR] Error initializing components: {e}")
            raise
        
        # Results storage
        self.analysis_results = {}
    
    def analyze_path(self, extraction_path: str) -> Dict[str, Any]:
        """Analyze path with threading support"""
        original_path = Path(extraction_path)
        
        if not original_path.exists():
            raise FileNotFoundError(f"Path not found: {original_path}")
        
        print(f"\n[INFO] Starting threaded analysis of: {original_path}")
        start_time = time.time()
        
        # Check if it's a zip file
        if original_path.is_file() and original_path.suffix.lower() == '.zip':
            print("[INFO] Zip file detected - using threaded zip analysis...")
            result = self._analyze_zip_threaded(original_path)
        else:
            print("[INFO] Directory analysis with threading...")
            result = self._analyze_directory_threaded(original_path)
        
        end_time = time.time()
        processing_time = end_time - start_time
        result['processing_time_seconds'] = round(processing_time, 2)
        
        print(f"\n[OK] Threaded analysis complete in {processing_time:.2f} seconds!")
        return result
    
    def _analyze_zip_threaded(self, zip_path: Path) -> Dict[str, Any]:
        """Multi-threaded zip file analysis"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_file:
                # Step 1: Threaded database discovery
                print("\n[STEP 1] Threaded Database Discovery")
                databases = self._discover_databases_threaded(zip_file, zip_path)
                
                # Step 2: Parallel database analysis
                print("\n[STEP 2] Parallel Database Analysis")
                analyzed_databases = self._analyze_databases_threaded(zip_file, databases)
                
                # Step 3: Concurrent sample extraction
                print("\n[STEP 3] Concurrent Sample Extraction")
                extracted_data = self._extract_samples_threaded(zip_file, analyzed_databases)
                
                # Step 4: Parallel intelligence analysis
                print("\n[STEP 4] Parallel Intelligence Analysis")
                intelligence_findings = self._run_intelligence_threaded(extracted_data)
                
                # Step 5: Generate report
                print("\n[STEP 5] Report Generation")
                report = self._generate_threaded_report(zip_path, databases, extracted_data, intelligence_findings)
                
                return report
                
        except Exception as e:
            raise Exception(f"Error in threaded zip analysis: {e}")
    
    def _discover_databases_threaded(self, zip_file: zipfile.ZipFile, zip_path: Path) -> List[Dict[str, Any]]:
        """Threaded database discovery in zip"""
        discovered = []
        db_patterns = ['.db', '.sqlite', '.sqlitedb', '.sqlite3']
        
        # Get all potential database files
        potential_files = []
        for file_info in zip_file.infolist():
            if not file_info.is_dir():
                file_name = Path(file_info.filename).name.lower()
                if any(file_name.endswith(pattern) for pattern in db_patterns):
                    potential_files.append(file_info)
        
        print(f"   Found {len(potential_files)} potential database files")
        
        # Process in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(self._process_zip_entry, file_info, zip_path): file_info
                for file_info in potential_files
            }
            
            for future in concurrent.futures.as_completed(future_to_file):
                try:
                    db_info = future.result()
                    if db_info:
                        discovered.append(db_info)
                        print(f"   - {db_info['name']} ({db_info['size']} bytes)")
                except Exception as e:
                    file_info = future_to_file[future]
                    print(f"   [ERROR] Processing {file_info.filename}: {e}")
        
        return discovered
    
    def _process_zip_entry(self, file_info: zipfile.ZipInfo, zip_path: Path) -> Optional[Dict[str, Any]]:
        """Process individual zip entry for database info"""
        try:
            return {
                'name': Path(file_info.filename).stem,
                'path': file_info.filename,
                'zip_path': zip_path,
                'size': file_info.file_size,
                'compressed_size': file_info.compress_size,
                'type': 'zip_contained',
                'compression_ratio': file_info.compress_size / file_info.file_size if file_info.file_size > 0 else 0,
                'thread_id': threading.current_thread().ident
            }
        except Exception:
            return None
    
    def _analyze_databases_threaded(self, zip_file: zipfile.ZipFile, databases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parallel database header analysis"""
        analyzed = []
        analyzed_lock = threading.Lock()
        
        def analyze_single_db(db_info):
            """Analyze single database in thread"""
            thread_result = db_info.copy()
            file_path = db_info['path']
            
            try:
                # Read header for analysis
                with zip_file.open(file_path) as db_file:
                    header = db_file.read(1024)
                
                # SQLite format check
                if header.startswith(b'SQLite format 3'):
                    thread_result['format'] = 'sqlite'
                    thread_result['status'] = 'sqlite_detected'
                    
                    # Entropy analysis for encryption
                    if len(header) >= 100:
                        entropy = self._calculate_header_entropy(header[16:100])
                        thread_result['entropy'] = entropy
                        thread_result['encryption_suspected'] = entropy > 7.5
                    else:
                        thread_result['encryption_suspected'] = False
                else:
                    thread_result['format'] = 'unknown'
                    thread_result['status'] = 'not_sqlite'
                
                with analyzed_lock:
                    print(f"   [THREAD-{threading.current_thread().ident}] Analyzed: {db_info['name']}")
                
            except Exception as e:
                thread_result['status'] = 'error'
                thread_result['error'] = str(e)
            
            return thread_result
        
        # Run analysis in parallel
        print(f"   Analyzing {len(databases)} databases with {self.max_workers} threads...")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_db = {executor.submit(analyze_single_db, db): db for db in databases}
            
            for future in concurrent.futures.as_completed(future_to_db):
                try:
                    result = future.result()
                    analyzed.append(result)
                except Exception as e:
                    db = future_to_db[future]
                    print(f"   [ERROR] Analysis failed for {db['name']}: {e}")
        
        # Summary
        sqlite_count = len([db for db in analyzed if db.get('format') == 'sqlite'])
        encrypted_count = len([db for db in analyzed if db.get('encryption_suspected')])
        print(f"   Results: {sqlite_count} SQLite, {encrypted_count} encrypted")
        
        return analyzed
    
    def _extract_samples_threaded(self, zip_file: zipfile.ZipFile, databases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Concurrent sample data extraction"""
        extracted_data = {}
        extraction_lock = threading.Lock()
        
        # Filter viable databases
        viable_databases = [db for db in databases if 
                          db.get('status') == 'sqlite_detected' and 
                          not db.get('encryption_suspected', False)]
        
        if not viable_databases:
            print("   No viable databases found for sampling")
            return extracted_data
        
        # Limit concurrent extractions to avoid resource exhaustion
        max_concurrent = min(len(viable_databases), 4)
        viable_databases = viable_databases[:max_concurrent]
        
        def extract_single_database(db_info):
            """Extract samples from single database"""
            db_name = db_info['name']
            file_path = db_info['path']
            thread_id = threading.current_thread().ident
            
            try:
                # Extract to temporary file
                with zip_file.open(file_path) as zip_member:
                    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
                        shutil.copyfileobj(zip_member, temp_db)
                        temp_db_path = temp_db.name
                
                # Quick sampling
                try:
                    import sqlite3
                    conn = sqlite3.connect(temp_db_path)
                    cursor = conn.cursor()
                    
                    # Get tables
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = [row[0] for row in cursor.fetchall()]
                    
                    db_data = []
                    tables_processed = 0
                    
                    for table_name in tables[:3]:  # Limit tables per database
                        try:
                            cursor.execute(f"SELECT * FROM {table_name} LIMIT 2")
                            rows = cursor.fetchall()
                            if rows:
                                cursor.execute(f"PRAGMA table_info({table_name})")
                                columns = [col[1] for col in cursor.fetchall()]
                                
                                for row in rows:
                                    record = dict(zip(columns, row))
                                    record['_table'] = table_name
                                    record['_source_thread'] = thread_id
                                    db_data.append(record)
                                
                                tables_processed += 1
                        except:
                            continue
                    
                    conn.close()
                    
                    if db_data:
                        result = {
                            'data': db_data,
                            'record_count': len(db_data),
                            'source_path': f"{db_info['zip_path']}::{file_path}",
                            'tables_sampled': tables_processed,
                            'extraction_thread': thread_id
                        }
                        
                        with extraction_lock:
                            extracted_data[db_name] = result
                            print(f"   [THREAD-{thread_id}] Extracted {len(db_data)} records from {db_name}")
                        
                        return result
                
                finally:
                    # Cleanup
                    try:
                        os.unlink(temp_db_path)
                    except:
                        pass
                        
            except Exception as e:
                with extraction_lock:
                    print(f"   [THREAD-{thread_id}] Error extracting {db_name}: {e}")
            
            return None
        
        # Run extractions concurrently
        print(f"   Extracting samples from {len(viable_databases)} databases...")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            futures = [executor.submit(extract_single_database, db) for db in viable_databases]
            
            # Wait for completion
            concurrent.futures.wait(futures)
        
        total_records = sum(data['record_count'] for data in extracted_data.values())
        print(f"   Extracted {total_records} total sample records")
        
        return extracted_data
    
    def _run_intelligence_threaded(self, extracted_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parallel intelligence module execution"""
        if not extracted_data:
            print("   No data available for intelligence analysis")
            return []
        
        # Prepare communication data
        communications = []
        for db_name, db_data in extracted_data.items():
            for record in db_data['data']:
                comm = {
                    'source': db_name,
                    'timestamp': datetime.datetime.now().isoformat(),
                    'content': str(record),
                    'contact': 'Unknown',
                    'type': 'DATA_RECORD',
                    'extraction_thread': record.get('_source_thread')
                }
                communications.append(comm)
        
        print(f"   Running intelligence analysis on {len(communications)} communications")
        
        # Get available modules
        available_modules = self.module_factory.get_available_modules()
        all_findings = []
        findings_lock = threading.Lock()
        
        def run_intelligence_module(module_name):
            """Run single intelligence module"""
            thread_id = threading.current_thread().ident
            try:
                module = self.module_factory.create_module(module_name)
                if module:
                    module_findings = module.analyze(communications)
                    
                    # Add thread metadata
                    for finding in module_findings:
                        finding['analysis_thread'] = thread_id
                        finding['analysis_timestamp'] = datetime.datetime.now().isoformat()
                    
                    with findings_lock:
                        all_findings.extend(module_findings)
                        print(f"   [THREAD-{thread_id}] {module_name}: {len(module_findings)} indicators")
                    
                    return module_findings
            except Exception as e:
                with findings_lock:
                    print(f"   [THREAD-{thread_id}] Error in {module_name}: {e}")
            return []
        
        # Run modules in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(available_modules)) as executor:
            futures = [executor.submit(run_intelligence_module, module) for module in available_modules]
            concurrent.futures.wait(futures)
        
        print(f"   Intelligence analysis complete: {len(all_findings)} total findings")
        return all_findings
    
    def _calculate_header_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy for encryption detection"""
        if len(data) == 0:
            return 0
        
        byte_counts = [0] * 256
        for byte in data:
            byte_counts[byte] += 1
        
        entropy = 0
        data_len = len(data)
        for count in byte_counts:
            if count > 0:
                probability = count / data_len
                entropy -= probability * (probability.bit_length() - 1)
        
        return min(entropy, 8.0)
    
    def _generate_threaded_report(self, zip_path: Path, databases: List[Dict[str, Any]], 
                                 extracted_data: Dict[str, Any], 
                                 intelligence_findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate report with threading performance metrics"""
        
        # Calculate threading statistics
        extraction_threads = set()
        analysis_threads = set()
        
        for data in extracted_data.values():
            if 'extraction_thread' in data:
                extraction_threads.add(data['extraction_thread'])
        
        for finding in intelligence_findings:
            if 'analysis_thread' in finding:
                analysis_threads.add(finding['analysis_thread'])
        
        # Standard statistics
        total_dbs = len(databases)
        sqlite_dbs = len([db for db in databases if db.get('format') == 'sqlite'])
        encrypted_dbs = len([db for db in databases if db.get('encryption_suspected')])
        total_findings = len(intelligence_findings)
        
        report = {
            'case_info': {
                'case_name': self.case_name,
                'examiner': self.examiner_name,
                'analysis_date': datetime.datetime.now().isoformat(),
                'tool_version': 'GHOST Threaded Analysis v1.0',
                'processing_mode': 'multi_threaded'
            },
            'performance_metrics': {
                'max_workers': self.max_workers,
                'extraction_threads_used': len(extraction_threads),
                'analysis_threads_used': len(analysis_threads),
                'cpu_cores_available': os.cpu_count() or 1,
                'threading_efficiency': len(extraction_threads) / self.max_workers if self.max_workers > 0 else 0
            },
            'summary': {
                'zip_file_size_mb': round(zip_path.stat().st_size / (1024*1024), 2),
                'databases_found': total_dbs,
                'sqlite_databases': sqlite_dbs,
                'encrypted_databases': encrypted_dbs,
                'databases_sampled': len(extracted_data),
                'records_extracted': sum(data['record_count'] for data in extracted_data.values()),
                'intelligence_findings': total_findings,
                'high_risk_findings': len([f for f in intelligence_findings if f.get('risk_score', 0) >= 7])
            },
            'databases': databases,
            'extracted_data_summary': {
                name: {
                    'record_count': data['record_count'],
                    'source': data['source_path'],
                    'extraction_thread': data.get('extraction_thread')
                }
                for name, data in extracted_data.items()
            },
            'intelligence_findings': intelligence_findings,
            'recommendations': self._generate_threaded_recommendations(databases, intelligence_findings)
        }
        
        # Print performance summary
        metrics = report['performance_metrics']
        summary = report['summary']
        
        print(f"\n[SUMMARY] THREADED ANALYSIS RESULTS")
        print(f"   Processing Mode: Multi-threaded ({self.max_workers} max workers)")
        print(f"   Threading Efficiency: {metrics['threading_efficiency']:.1%}")
        print(f"   Databases Processed: {total_dbs} ({sqlite_dbs} SQLite)")
        print(f"   Intelligence Findings: {total_findings}")
        if summary['high_risk_findings'] > 0:
            print(f"   [WARNING] High Risk: {summary['high_risk_findings']} findings")
        
        return report
    
    def _generate_threaded_recommendations(self, databases: List[Dict[str, Any]], 
                                         findings: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations including threading insights"""
        recommendations = []
        
        # Performance recommendations
        sqlite_count = len([db for db in databases if db.get('format') == 'sqlite'])
        if sqlite_count > self.max_workers:
            recommendations.append(f"Consider increasing thread count for {sqlite_count} databases (current: {self.max_workers})")
        
        # Standard recommendations
        encrypted_count = len([db for db in databases if db.get('encryption_suspected')])
        if encrypted_count > 0:
            recommendations.append(f"PRIORITY: {encrypted_count} encrypted databases require specialized processing")
        
        if findings:
            high_risk = len([f for f in findings if f.get('risk_score', 0) >= 7])
            if high_risk > 0:
                recommendations.append(f"URGENT: {high_risk} high-risk indicators need immediate investigation")
        
        recommendations.append("Threaded analysis completed - consider full extraction for comprehensive results")
        
        return recommendations
    
    def save_report(self, report: Dict[str, Any], output_path: str = None) -> str:
        """Save threaded analysis report"""
        if output_path is None:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"threaded_forensic_report_{self.case_name}_{timestamp}.json"
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n[OK] Threaded analysis report saved to: {output_path}")
        return output_path

def main():
    """Main function with threading support"""
    print("[INFO] GHOST - Threaded Golden Hour Operations")
    print("=" * 50)
    
    if len(sys.argv) < 4:
        print("Usage: python threaded_forensic_suite.py <path> <case_name> <examiner_name> [max_workers]")
        print("\nSupported inputs:")
        print("  - Directory: /path/to/extraction/")
        print("  - Zip file:  /path/to/extraction.zip")
        print("\nOptional parameters:")
        print("  - max_workers: Maximum thread count (default: auto-detect)")
        print("\nExamples:")
        print("  python threaded_forensic_suite.py /cases/iPhone.zip 'Case-001' 'Det. Smith'")
        print("  python threaded_forensic_suite.py /cases/Android/ 'Case-002' 'Det. Jones' 16")
        sys.exit(1)
    
    input_path = sys.argv[1]
    case_name = sys.argv[2]
    examiner_name = sys.argv[3]
    max_workers = int(sys.argv[4]) if len(sys.argv) > 4 else None
    
    try:
        # Initialize threaded suite
        suite = ThreadedForensicSuite(case_name, examiner_name, max_workers)
        
        # Run threaded analysis
        report = suite.analyze_path(input_path)
        
        # Save report
        output_file = suite.save_report(report)
        
        # Performance summary
        processing_time = report.get('processing_time_seconds', 0)
        performance = report['performance_metrics']
        
        print(f"\n[SUCCESS] Threaded analysis complete!")
        print(f"   Processing Time: {processing_time} seconds")
        print(f"   Threading Efficiency: {performance['threading_efficiency']:.1%}")
        print(f"   Full report: {output_file}")
        
    except Exception as e:
        print(f"\n[ERROR] Threaded analysis failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
