#!/usr/bin/env python3
"""
Modular Forensic Intelligence Suite
Clean separation of concerns with pluggable components

Modules:
- config_manager.py: Configuration management
- database_inspector.py: Database analysis and inspection  
- pattern_analyzer.py: Data pattern recognition
- encryption_detector.py: Encryption detection and bypass
- intelligence_modules.py: Crime-specific analysis modules
- forensic_logger.py: Chain of custody and logging
- data_extractor.py: Database extraction with schema mapping
- report_generator.py: Intelligence reporting and visualization
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import datetime

# Add modules directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "modules"))

# Core module imports
from config_manager import ConfigurationManager
from database_inspector import DatabaseInspector
from pattern_analyzer import PatternAnalyzer
from encryption_detector import EncryptionDetector
from intelligence_modules import IntelligenceModuleFactory
from forensic_logger import ForensicLogger
from data_extractor import DataExtractor
from report_generator import ReportGenerator

class ForensicIntelligenceSuite:
    """Main orchestrator for the modular forensic intelligence suite"""
    
    def __init__(self, case_name: str, examiner_name: str, config_dir: str = "forensic_configs"):
        self.case_name = case_name
        self.examiner_name = examiner_name
        
        # Initialize core components
        self.config_manager = ConfigurationManager(config_dir)
        self.logger = ForensicLogger(case_name, examiner_name)
        self.inspector = DatabaseInspector(self.logger)
        self.pattern_analyzer = PatternAnalyzer()
        self.encryption_detector = EncryptionDetector()
        self.data_extractor = DataExtractor(self.config_manager, self.logger)
        self.report_generator = ReportGenerator(case_name, examiner_name)
        
        # Initialize intelligence module factory
        self.module_factory = IntelligenceModuleFactory(
            self.config_manager.keywords,
            self.config_manager.modules,
            self.logger
        )
        
        # Analysis results
        self.extracted_data = {}
        self.intelligence_findings = []
        self.analysis_metadata = {}
        
        self.logger.log_action("SUITE_INITIALIZED", f"Forensic suite initialized for case {case_name}")
    
    def analyze_extraction(self, extraction_path: str, selected_modules: List[str] = None) -> Dict[str, Any]:
        """Main analysis pipeline"""
        extraction_path = Path(extraction_path)
        
        if not extraction_path.exists():
            raise FileNotFoundError(f"Extraction path not found: {extraction_path}")
        
        self.logger.log_action("ANALYSIS_START", f"Starting analysis of {extraction_path}")
        
        # Step 1: Discovery phase
        discovered_databases = self._discover_databases(extraction_path)
        
        # Step 2: Database inspection and configuration
        configured_databases = self._inspect_and_configure_databases(discovered_databases)
        
        # Step 3: Data extraction
        self._extract_data_from_databases(configured_databases)
        
        # Step 4: Intelligence analysis
        self._run_intelligence_analysis(selected_modules)
        
        # Step 5: Generate comprehensive report
        report = self._generate_final_report()
        
        self.logger.log_action("ANALYSIS_COMPLETE", f"Analysis completed for {self.case_name}")
        
        return report
    
    def _discover_databases(self, extraction_path: Path) -> List[Dict[str, Any]]:
        """Discover all potential databases in the extraction"""
        self.logger.log_action("DISCOVERY_START", "Starting database discovery phase")
        
        discovered = []
        
        # Look for configured database paths
        for db_name, db_config in self.config_manager.data_paths.items():
            db_path = self.data_extractor.find_database_file(extraction_path, db_config)
            if db_path:
                discovered.append({
                    'name': db_name,
                    'path': db_path,
                    'config': db_config,
                    'source': 'configured'
                })
                self.logger.log_action("DB_DISCOVERED", f"Found configured database: {db_name} at {db_path}")
        
        # Look for additional SQLite databases
        additional_dbs = list(extraction_path.rglob("*.db")) + list(extraction_path.rglob("*.sqlite")) + list(extraction_path.rglob("*.sqlitedb"))
        
        for db_path in additional_dbs:
            # Skip if already found in configured databases
            if not any(str(db_path) == str(d['path']) for d in discovered):
                discovered.append({
                    'name': f"unknown_{db_path.stem}",
                    'path': db_path,
                    'config': None,
                    'source': 'discovered'
                })
                self.logger.log_action("DB_DISCOVERED", f"Found additional database: {db_path}")
        
        self.logger.log_action("DISCOVERY_COMPLETE", f"Discovered {len(discovered)} databases")
        return discovered
    
    def _inspect_and_configure_databases(self, discovered_databases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Inspect databases and generate configurations for unknown ones"""
        self.logger.log_action("INSPECTION_START", "Starting database inspection phase")
        
        configured = []
        
        for db_info in discovered_databases:
            db_path = db_info['path']
            
            # Check for encryption first
            encryption_info = self.encryption_detector.detect_encryption(db_path)
            
            if encryption_info['is_encrypted']:
                self.logger.log_action("ENCRYPTED_DB", f"Encrypted database detected: {db_path}")
                db_info['encryption'] = encryption_info
                db_info['status'] = 'encrypted'
                configured.append(db_info)
                continue
            
            # Inspect database structure
            inspection_result = self.inspector.inspect_database(db_path)
            
            if inspection_result.get('error'):
                self.logger.log_action("INSPECTION_ERROR", f"Failed to inspect {db_path}: {inspection_result['error']}")
                db_info['status'] = 'error'
                configured.append(db_info)
                continue
            
            # Analyze patterns
            pattern_analysis = self.pattern_analyzer.analyze_database_patterns(db_path, inspection_result)
            
            # Generate or use existing configuration
            if db_info['source'] == 'configured':
                db_info['schema'] = self.config_manager.schemas.get(db_info['name'])
                db_info['status'] = 'configured'
            else:
                # Generate configuration for unknown database
                generated_config = self.inspector.generate_smart_configuration(
                    inspection_result, pattern_analysis, db_info['name']
                )
                db_info['schema'] = generated_config
                db_info['status'] = 'auto_configured'
                
                # Optionally save generated config
                if generated_config.get('confidence', 'low') in ['high', 'medium']:
                    self._save_generated_config(db_info['name'], generated_config)
            
            db_info['inspection'] = inspection_result
            db_info['patterns'] = pattern_analysis
            configured.append(db_info)
        
        self.logger.log_action("INSPECTION_COMPLETE", f"Configured {len(configured)} databases")
        return configured
    
    def _extract_data_from_databases(self, configured_databases: List[Dict[str, Any]]):
        """Extract data from all configured databases"""
        self.logger.log_action("EXTRACTION_START", "Starting data extraction phase")
        
        for db_info in configured_databases:
            if db_info['status'] in ['encrypted', 'error']:
                continue
            
            db_name = db_info['name']
            db_path = db_info['path']
            schema = db_info.get('schema')
            
            if not schema:
                self.logger.log_action("EXTRACTION_SKIP", f"No schema available for {db_name}")
                continue
            
            try:
                extracted_data = self.data_extractor.extract_from_database(db_path, schema)
                self.extracted_data[db_name] = {
                    'data': extracted_data,
                    'source_path': str(db_path),
                    'extraction_time': datetime.datetime.now().isoformat(),
                    'record_count': len(extracted_data)
                }
                
                self.logger.log_action("EXTRACTION_SUCCESS", f"Extracted {len(extracted_data)} records from {db_name}")
                
            except Exception as e:
                self.logger.log_action("EXTRACTION_ERROR", f"Failed to extract from {db_name}: {str(e)}")
        
        total_records = sum(data['record_count'] for data in self.extracted_data.values())
        self.logger.log_action("EXTRACTION_COMPLETE", f"Extracted {total_records} total records")
    
    def _run_intelligence_analysis(self, selected_modules: List[str] = None):
        """Run intelligence analysis on extracted data"""
        self.logger.log_action("INTELLIGENCE_START", "Starting intelligence analysis phase")
        
        if selected_modules is None:
            selected_modules = list(self.config_manager.modules.keys())
        
        # Consolidate all communication data
        all_communications = self._consolidate_communications()
        
        if not all_communications:
            self.logger.log_action("INTELLIGENCE_SKIP", "No communication data found for analysis")
            return
        
        # Run each selected module
        for module_name in selected_modules:
            if not self.config_manager.modules.get(module_name, {}).get('enabled', True):
                continue
            
            try:
                module = self.module_factory.create_module(module_name)
                if module:
                    findings = module.analyze(all_communications)
                    
                    # Add metadata to findings
                    for finding in findings:
                        finding['analysis_metadata'] = {
                            'module_version': module.version,
                            'analysis_time': datetime.datetime.now().isoformat(),
                            'case_name': self.case_name,
                            'examiner': self.examiner_name
                        }
                    
                    self.intelligence_findings.extend(findings)
                    self.logger.log_action("MODULE_COMPLETE", f"{module_name} found {len(findings)} indicators")
                
            except Exception as e:
                self.logger.log_action("MODULE_ERROR", f"Error in {module_name}: {str(e)}")
        
        self.logger.log_action("INTELLIGENCE_COMPLETE", f"Found {len(self.intelligence_findings)} total indicators")
    
    def _consolidate_communications(self) -> List[Dict[str, Any]]:
        """Consolidate communication data from all sources"""
        communications = []
        
        for db_name, db_data in self.extracted_data.items():
            for record in db_data['data']:
                # Normalize communication record
                normalized = self._normalize_communication_record(record, db_name)
                if normalized:
                    communications.append(normalized)
        
        return communications
    
    def _normalize_communication_record(self, record: Dict[str, Any], source: str) -> Optional[Dict[str, Any]]:
        """Normalize a communication record to standard format"""
        # This would need to be enhanced based on different database schemas
        base_record = {
            'source': source,
            'timestamp': record.get('timestamp', ''),
            'content': record.get('text', ''),
            'contact': record.get('contact', 'Unknown'),
            'direction': record.get('direction', 'Unknown'),
            'type': 'MESSAGE'  # Default, could be CALL, etc.
        }
        
        # Only return if we have meaningful content
        if base_record['content'] or base_record['contact'] != 'Unknown':
            return base_record
        
        return None
    
    def _generate_final_report(self) -> Dict[str, Any]:
        """Generate comprehensive final report"""
        self.logger.log_action("REPORT_START", "Generating final report")
        
        report = self.report_generator.generate_comprehensive_report(
            extracted_data=self.extracted_data,
            intelligence_findings=self.intelligence_findings,
            analysis_metadata={
                'databases_analyzed': len(self.extracted_data),
                'total_records': sum(data['record_count'] for data in self.extracted_data.values()),
                'modules_run': len(set(f.get('module', 'unknown') for f in self.intelligence_findings)),
                'analysis_duration': self.logger.get_analysis_duration()
            }
        )
        
        self.logger.log_action("REPORT_COMPLETE", "Final report generated")
        return report
    
    def _save_generated_config(self, db_name: str, config: Dict[str, Any]):
        """Save auto-generated configuration for future use"""
        config_file = Path("forensic_configs") / "auto_generated" / f"{db_name}_config.json"
        config_file.parent.mkdir(exist_ok=True)
        
        with open(config_file, 'w') as f:
            json.dump({db_name: config}, f, indent=2)
        
        self.logger.log_action("CONFIG_SAVED", f"Auto-generated config saved: {config_file}")

# Command-line interface
def main():
    """Main command-line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Modular Forensic Intelligence Suite")
    
    # Analysis mode
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Run forensic analysis')
    analyze_parser.add_argument('extraction_path', help='Path to forensic extraction')
    analyze_parser.add_argument('case_name', help='Case name/identifier')
    analyze_parser.add_argument('examiner_name', help='Examiner name')
    analyze_parser.add_argument('--modules', help='Comma-separated list of intelligence modules')
    analyze_parser.add_argument('--config-dir', default='forensic_configs', help='Configuration directory')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Configuration management')
    config_parser.add_argument('action', choices=[
        'init', 'inspect', 'add-keywords', 'update-schema', 
        'export', 'import', 'list', 'validate'
    ])
    config_parser.add_argument('--config-dir', default='forensic_configs', help='Configuration directory')
    config_parser.add_argument('--db-path', help='Database path for inspection')
    config_parser.add_argument('--module', help='Module name')
    config_parser.add_argument('--category', help='Keyword category')
    config_parser.add_argument('--keywords', help='Comma-separated keywords')
    config_parser.add_argument('--file', help='File path for import/export')
    
    # Module command
    module_parser = subparsers.add_parser('module', help='Module management')
    module_parser.add_argument('action', choices=['list', 'info', 'test'])
    module_parser.add_argument('--name', help='Module name')
    module_parser.add_argument('--config-dir', default='forensic_configs', help='Configuration directory')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'analyze':
            # Run analysis
            selected_modules = None
            if args.modules:
                selected_modules = [m.strip() for m in args.modules.split(',')]
            
            suite = ForensicIntelligenceSuite(
                args.case_name, 
                args.examiner_name, 
                args.config_dir
            )
            
            report = suite.analyze_extraction(args.extraction_path, selected_modules)
            
            print(f"\n✅ Analysis complete for case: {args.case_name}")
            print(f"📊 Report generated with {len(report.get('intelligence_findings', []))} findings")
            
        elif args.command == 'config':
            # Configuration management
            from config_cli import handle_config_command
            handle_config_command(args)
            
        elif args.command == 'module':
            # Module management
            from module_cli import handle_module_command
            handle_module_command(args)
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()