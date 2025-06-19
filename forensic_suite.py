#!/usr/bin/env python3
"""
Forensic Intelligence Suite - Working Main Module
Simplified version with core functionality
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import datetime

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
    print("✅ All modules imported successfully")
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    print("Make sure all module files are in the 'modules' directory")
    sys.exit(1)

class SimplifiedForensicSuite:
    """Simplified forensic intelligence suite for testing"""
    
    def __init__(self, case_name: str, examiner_name: str):
        self.case_name = case_name
        self.examiner_name = examiner_name
        
        print(f"🔍 Initializing Forensic Intelligence Suite")
        print(f"   Case: {case_name}")
        print(f"   Examiner: {examiner_name}")
        
        # Initialize core components
        try:
            self.config_manager = ConfigurationManager()
            self.logger = ForensicLogger(case_name, examiner_name)
            self.inspector = DatabaseInspector(self.logger)
            self.encryption_detector = EncryptionDetector()
            self.data_extractor = DataExtractor(self.config_manager, self.logger)
            
            # Initialize intelligence module factory
            self.module_factory = IntelligenceModuleFactory(
                self.config_manager.keywords,
                self.config_manager.modules,
                self.logger
            )
            
            print("✅ All components initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing components: {e}")
            raise
        
        # Results storage
        self.analysis_results = {}
    
    def analyze_path(self, extraction_path: str) -> Dict[str, Any]:
        """Analyze a forensic extraction path"""
        extraction_path = Path(extraction_path)
        
        if not extraction_path.exists():
            raise FileNotFoundError(f"Path not found: {extraction_path}")
        
        print(f"\n🔍 Starting analysis of: {extraction_path}")
        
        # Step 1: Discover databases
        print("\n📁 Step 1: Database Discovery")
        databases = self._discover_databases(extraction_path)
        
        # Step 2: Analyze discovered databases
        print("\n🔍 Step 2: Database Analysis")
        analyzed_databases = self._analyze_databases(databases)
        
        # Step 3: Extract sample data
        print("\n📊 Step 3: Data Extraction")
        extracted_data = self._extract_sample_data(analyzed_databases)
        
        # Step 4: Run intelligence analysis (simplified)
        print("\n🧠 Step 4: Intelligence Analysis")
        intelligence_findings = self._run_basic_intelligence(extracted_data)
        
        # Step 5: Generate report
        print("\n📋 Step 5: Report Generation")
        report = self._generate_simple_report(databases, extracted_data, intelligence_findings)
        
        print("\n✅ Analysis complete!")
        return report
    
    def _discover_databases(self, extraction_path: Path) -> List[Dict[str, Any]]:
        """Discover database files in extraction"""
        discovered = []
        
        # Look for SQLite databases
        db_patterns = ["*.db", "*.sqlite", "*.sqlitedb"]
        
        for pattern in db_patterns:
            for db_path in extraction_path.rglob(pattern):
                discovered.append({
                    'name': db_path.stem,
                    'path': db_path,
                    'size': db_path.stat().st_size if db_path.exists() else 0,
                    'type': 'discovered'
                })
        
        print(f"   Found {len(discovered)} database files")
        for db in discovered[:5]:  # Show first 5
            print(f"   - {db['name']} ({db['size']} bytes)")
        
        return discovered
    
    def _analyze_databases(self, databases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze database structure and check encryption"""
        analyzed = []
        
        for db_info in databases:
            db_path = db_info['path']
            
            print(f"   Analyzing: {db_info['name']}")
            
            # Check encryption
            encryption_info = self.encryption_detector.detect_encryption(db_path)
            db_info['encryption'] = encryption_info
            
            if encryption_info['is_encrypted']:
                print(f"     ⚠️  Encrypted database detected")
                db_info['status'] = 'encrypted'
            else:
                # Inspect structure
                try:
                    inspection = self.inspector.inspect_database(db_path)
                    db_info['inspection'] = inspection
                    db_info['status'] = 'analyzed'
                    
                    table_count = inspection.get('table_count', 0)
                    print(f"     ✅ {table_count} tables found")
                    
                except Exception as e:
                    print(f"     ❌ Error: {e}")
                    db_info['status'] = 'error'
                    db_info['error'] = str(e)
            
            analyzed.append(db_info)
        
        return analyzed
    
    def _extract_sample_data(self, databases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract sample data from databases"""
        extracted_data = {}
        
        for db_info in databases:
            if db_info['status'] != 'analyzed':
                continue
            
            db_name = db_info['name']
            db_path = db_info['path']
            
            print(f"   Extracting from: {db_name}")
            
            try:
                # Get sample data from each table
                inspection = db_info.get('inspection', {})
                tables = inspection.get('tables', {})
                
                db_data = []
                for table_name, table_info in tables.items():
                    if table_info.get('row_count', 0) > 0:
                        sample_data = self.data_extractor.extract_sample_data(
                            db_path, table_name, limit=5
                        )
                        if sample_data:
                            db_data.extend(sample_data)
                
                if db_data:
                    extracted_data[db_name] = {
                        'data': db_data,
                        'record_count': len(db_data),
                        'source_path': str(db_path)
                    }
                    print(f"     ✅ {len(db_data)} sample records extracted")
                
            except Exception as e:
                print(f"     ❌ Extraction error: {e}")
        
        return extracted_data
    
    def _run_basic_intelligence(self, extracted_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Run basic intelligence analysis on extracted data"""
        findings = []
        
        # Create mock communication data for analysis
        communications = []
        for db_name, db_data in extracted_data.items():
            for record in db_data['data']:
                # Try to normalize record to communication format
                comm = {
                    'source': db_name,
                    'timestamp': datetime.datetime.now().isoformat(),
                    'content': str(record),  # Simple string conversion
                    'contact': 'Unknown',
                    'type': 'DATA_RECORD'
                }
                communications.append(comm)
        
        if not communications:
            print("   No communications found for analysis")
            return findings
        
        print(f"   Analyzing {len(communications)} records")
        
        # Run available intelligence modules
        available_modules = self.module_factory.get_available_modules()
        
        for module_name in available_modules:
            try:
                module = self.module_factory.create_module(module_name)
                if module:
                    module_findings = module.analyze(communications)
                    findings.extend(module_findings)
                    print(f"     {module_name}: {len(module_findings)} indicators")
            except Exception as e:
                print(f"     ❌ {module_name} error: {e}")
        
        return findings
    
    def _generate_simple_report(self, databases: List[Dict[str, Any]], 
                               extracted_data: Dict[str, Any],
                               intelligence_findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a simple analysis report"""
        
        # Calculate summary stats
        total_dbs = len(databases)
        encrypted_dbs = len([db for db in databases if db.get('encryption', {}).get('is_encrypted')])
        analyzed_dbs = len([db for db in databases if db['status'] == 'analyzed'])
        total_records = sum(data['record_count'] for data in extracted_data.values())
        total_findings = len(intelligence_findings)
        
        # Risk assessment
        high_risk_findings = [f for f in intelligence_findings if f.get('risk_score', 0) >= 7]
        medium_risk_findings = [f for f in intelligence_findings if 4 <= f.get('risk_score', 0) < 7]
        
        report = {
            'case_info': {
                'case_name': self.case_name,
                'examiner': self.examiner_name,
                'analysis_date': datetime.datetime.now().isoformat(),
                'tool_version': 'Simplified Forensic Intelligence Suite v1.0'
            },
            'summary': {
                'databases_found': total_dbs,
                'databases_encrypted': encrypted_dbs,
                'databases_analyzed': analyzed_dbs,
                'records_extracted': total_records,
                'intelligence_findings': total_findings,
                'high_risk_findings': len(high_risk_findings),
                'medium_risk_findings': len(medium_risk_findings)
            },
            'databases': databases,
            'extracted_data_summary': {
                name: {'record_count': data['record_count'], 'source': data['source_path']}
                for name, data in extracted_data.items()
            },
            'intelligence_findings': intelligence_findings,
            'recommendations': self._generate_recommendations(intelligence_findings)
        }
        
        # Print summary
        print(f"\n📊 ANALYSIS SUMMARY")
        print(f"   Databases Found: {total_dbs}")
        print(f"   Databases Analyzed: {analyzed_dbs}")
        print(f"   Encrypted Databases: {encrypted_dbs}")
        print(f"   Records Extracted: {total_records}")
        print(f"   Intelligence Findings: {total_findings}")
        if high_risk_findings:
            print(f"   ⚠️  High Risk Findings: {len(high_risk_findings)}")
        
        return report
    
    def _generate_recommendations(self, findings: List[Dict[str, Any]]) -> List[str]:
        """Generate simple recommendations based on findings"""
        recommendations = []
        
        if not findings:
            recommendations.append("No intelligence indicators detected in sample data")
            recommendations.append("Consider running full forensic analysis with larger dataset")
            return recommendations
        
        high_risk_count = len([f for f in findings if f.get('risk_score', 0) >= 7])
        if high_risk_count > 0:
            recommendations.append(f"URGENT: {high_risk_count} high-risk indicators require immediate investigation")
        
        # Module-specific recommendations
        modules_with_findings = set(f.get('module', 'Unknown') for f in findings)
        
        if 'Narcotics Intelligence' in modules_with_findings:
            recommendations.append("Drug-related activity detected - consider DEA coordination")
        
        if 'Financial Fraud Intelligence' in modules_with_findings:
            recommendations.append("Financial fraud indicators - review transaction records")
        
        recommendations.append("Expand analysis to full dataset for comprehensive results")
        
        return recommendations
    
    def save_report(self, report: Dict[str, Any], output_path: str = None):
        """Save report to JSON file"""
        if output_path is None:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"forensic_report_{self.case_name}_{timestamp}.json"
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n💾 Report saved to: {output_path}")
        return output_path

def main():
    """Main function for command-line usage"""
    print("🔍 GHOST - Golden Hour Operations and Strategic Threat Assessment")
    print("=" * 60)
    
    if len(sys.argv) < 4:
        print("Usage: python forensic_suite_simple.py <extraction_path> <case_name> <examiner_name>")
        print("\nExample:")
        print("  python forensic_suite_simple.py /path/to/extraction 'Case-2024-001' 'Detective Smith'")
        sys.exit(1)
    
    extraction_path = sys.argv[1]
    case_name = sys.argv[2]
    examiner_name = sys.argv[3]
    
    try:
        # Initialize suite
        suite = SimplifiedForensicSuite(case_name, examiner_name)
        
        # Run analysis
        report = suite.analyze_path(extraction_path)
        
        # Save report
        output_file = suite.save_report(report)
        
        print(f"\n🎯 Analysis complete! Key findings:")
        summary = report['summary']
        print(f"   • {summary['databases_found']} databases discovered")
        print(f"   • {summary['intelligence_findings']} intelligence indicators found")
        
        if summary['high_risk_findings'] > 0:
            print(f"   • ⚠️  {summary['high_risk_findings']} HIGH RISK findings!")
        
        print(f"\n📄 Full report saved to: {output_file}")
        
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        sys.exit(1)

def test_suite():
    """Test function to verify the suite works"""
    print("🧪 Testing Forensic Intelligence Suite...")
    
    # Create test directory structure
    test_dir = Path("test_extraction")
    test_dir.mkdir(exist_ok=True)
    
    # Create a simple test database
    test_db = test_dir / "test_messages.db"
    
    import sqlite3
    conn = sqlite3.connect(str(test_db))
    cursor = conn.cursor()
    
    # Create test table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS message (
            ROWID INTEGER PRIMARY KEY,
            date INTEGER,
            text TEXT,
            is_from_me INTEGER,
            service TEXT,
            handle_id INTEGER
        )
    """)
    
    # Insert test data
    test_messages = [
        (1640995200, "Hey, you got that stuff?", 0, "SMS", 1),
        (1640995260, "Yeah, meet me at the usual spot", 1, "SMS", 1),
        (1640995320, "Bring $200 for the gram", 0, "SMS", 1),
        (1640995380, "On my way", 1, "SMS", 1),
    ]
    
    cursor.executemany(
        "INSERT INTO message (date, text, is_from_me, service, handle_id) VALUES (?, ?, ?, ?, ?)",
        test_messages
    )
    
    conn.commit()
    conn.close()
    
    print(f"✅ Created test database: {test_db}")
    
    # Run analysis
    try:
        suite = SimplifiedForensicSuite("TEST-001", "Test Examiner")
        report = suite.analyze_path(str(test_dir))
        suite.save_report(report, "test_report.json")
        
        print("✅ Test completed successfully!")
        print("📄 Test report saved as: test_report.json")
        
        # Cleanup
        test_db.unlink()
        test_dir.rmdir()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        # Cleanup on failure
        if test_db.exists():
            test_db.unlink()
        if test_dir.exists():
            test_dir.rmdir()
        raise

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_suite()
    else:
        main()
