# modules/pattern_analyzer.py
"""
Pattern Analyzer Module
Analyzes data patterns to identify content types and intelligence value
"""

import re
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict

class PatternAnalyzer:
    """Analyzes data patterns in databases to understand content types"""
    
    def __init__(self):
        self.pattern_definitions = {
            'timestamps': {
                'cocoa_time': r'^\d{9,10}$',  # Cocoa timestamp (seconds since 2001)
                'unix_time': r'^\d{10}$',     # Unix timestamp  
                'milliseconds': r'^\d{13}$',  # Milliseconds since epoch
                'iso_date': r'^\d{4}-\d{2}-\d{2}',
                'human_readable': r'\d{1,2}/\d{1,2}/\d{4}'
            },
            'phone_numbers': {
                'us_format': r'^\+?1?[2-9]\d{2}[2-9]\d{2}\d{4}$',
                'international': r'^\+\d{1,3}\d{4,14}$',
                'formatted': r'^\(\d{3}\)\s?\d{3}-\d{4}$'
            },
            'identifiers': {
                'uuid': r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
                'bundle_id': r'^[a-z]+(\.[a-z][a-z0-9]*)+$',
                'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            },
            'crypto_addresses': {
                'bitcoin': r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$|^bc1[a-z0-9]{39,59}$',
                'ethereum': r'^0x[a-fA-F0-9]{40}$',
                'monero': r'^4[0-9AB][1-9A-HJ-NP-Za-km-z]{93}$'
            },
            'social_media': {
                'twitter_handle': r'^@[A-Za-z0-9_]{1,15}$',
                'instagram_handle': r'^@[A-Za-z0-9_.]{1,30}$',
                'url': r'^https?://[^\s/$.?#].[^\s]*$'
            },
            'financial': {
                'credit_card': r'^[0-9]{4}[\s\-]?[0-9]{4}[\s\-]?[0-9]{4}[\s\-]?[0-9]{4}$',
                'ssn': r'^\d{3}-\d{2}-\d{4}$',
                'bank_account': r'^\d{8,17}$',
                'amount': r'^\$?\d+(\.\d{2})?$'
            }
        }
    
    def analyze_database_patterns(self, db_path: Path, inspection_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze patterns in database content"""
        pattern_analysis = {
            'database_path': str(db_path),
            'tables_analyzed': 0,
            'patterns_found': {},
            'intelligence_indicators': {},
            'content_classification': {}
        }
        
        if 'error' in inspection_result:
            pattern_analysis['error'] = inspection_result['error']
            return pattern_analysis
        
        tables = inspection_result.get('tables', {})
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            for table_name, table_info in tables.items():
                if table_info.get('row_count', 0) == 0:
                    continue
                
                table_patterns = self._analyze_table_patterns(cursor, table_name, table_info)
                if table_patterns:
                    pattern_analysis['patterns_found'][table_name] = table_patterns
                    pattern_analysis['tables_analyzed'] += 1
            
            conn.close()
            
            # Generate intelligence indicators based on patterns
            pattern_analysis['intelligence_indicators'] = self._generate_intelligence_indicators(
                pattern_analysis['patterns_found']
            )
            
            # Classify content types
            pattern_analysis['content_classification'] = self._classify_content_types(
                pattern_analysis['patterns_found']
            )
            
        except Exception as e:
            pattern_analysis['error'] = str(e)
        
        return pattern_analysis
    
    def _analyze_table_patterns(self, cursor, table_name: str, table_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze patterns in a specific table"""
        table_patterns = {}
        columns = table_info.get('columns', [])
        
        for column in columns:
            col_name = column['name']
            col_type = column['type']
            
            try:
                # Sample data from the column
                cursor.execute(f"SELECT DISTINCT {col_name} FROM {table_name} WHERE {col_name} IS NOT NULL LIMIT 100")
                sample_data = [str(row[0]) for row in cursor.fetchall()]
                
                if sample_data:
                    column_patterns = self._analyze_column_patterns(sample_data, col_name, col_type)
                    if column_patterns:
                        table_patterns[col_name] = column_patterns
                        
            except Exception as e:
                continue
        
        return table_patterns
    
    def _analyze_column_patterns(self, sample_data: List[str], col_name: str, col_type: str) -> Dict[str, Any]:
        """Analyze patterns in a specific column"""
        column_patterns = {}
        
        if not sample_data:
            return column_patterns
        
        # Analyze each pattern category
        for category, patterns in self.pattern_definitions.items():
            category_matches = self._check_pattern_category(sample_data, patterns)
            if category_matches:
                column_patterns[category] = category_matches
        
        # Add content analysis
        content_analysis = self._analyze_content_characteristics(sample_data, col_name)
        if content_analysis:
            column_patterns['content_analysis'] = content_analysis
        
        return column_patterns
    
    def _check_pattern_category(self, sample_data: List[str], patterns: Dict[str, str]) -> Dict[str, Any]:
        """Check if sample data matches patterns in a category"""
        category_results = {}
        
        for pattern_name, pattern_regex in patterns.items():
            matches = []
            for data_item in sample_data:
                if re.match(pattern_regex, data_item, re.IGNORECASE):
                    matches.append(data_item)
            
            if matches:
                match_ratio = len(matches) / len(sample_data)
                if match_ratio > 0.1:  # At least 10% match
                    category_results[pattern_name] = {
                        'match_count': len(matches),
                        'match_ratio': match_ratio,
                        'sample_matches': matches[:3],  # First 3 matches
                        'confidence': self._calculate_pattern_confidence(match_ratio, len(matches))
                    }
        
        return category_results
    
    def _calculate_pattern_confidence(self, match_ratio: float, match_count: int) -> str:
        """Calculate confidence level for pattern matching"""
        if match_ratio > 0.8 and match_count > 5:
            return 'high'
        elif match_ratio > 0.5 and match_count > 2:
            return 'medium'
        elif match_ratio > 0.1:
            return 'low'
        else:
            return 'very_low'
    
    def _analyze_content_characteristics(self, sample_data: List[str], col_name: str) -> Dict[str, Any]:
        """Analyze general content characteristics"""
        content_info = {}
        
        # Text length analysis
        lengths = [len(data) for data in sample_data]
        if lengths:
            content_info['length_stats'] = {
                'min': min(lengths),
                'max': max(lengths),
                'avg': sum(lengths) / len(lengths)
            }
        
        # Check for message-like content
        if 'text' in col_name.lower() or 'message' in col_name.lower() or 'body' in col_name.lower():
            long_text_count = len([d for d in sample_data if len(d) > 20])
            if long_text_count > 0:
                content_info['message_indicators'] = {
                    'likely_messages': True,
                    'long_text_count': long_text_count,
                    'avg_message_length': sum(len(d) for d in sample_data if len(d) > 20) / long_text_count
                }
        
        # Check for numeric patterns
        numeric_count = 0
        for data_item in sample_data:
            try:
                float(data_item)
                numeric_count += 1
            except ValueError:
                continue
        
        if numeric_count > len(sample_data) * 0.8:
            content_info['numeric_data'] = {
                'is_numeric': True,
                'numeric_ratio': numeric_count / len(sample_data)
            }
        
        # Check for encoded data (base64, hex, etc.)
        encoded_indicators = self._check_encoded_data(sample_data)
        if encoded_indicators:
            content_info['encoding_indicators'] = encoded_indicators
        
        return content_info
    
    def _check_encoded_data(self, sample_data: List[str]) -> Dict[str, Any]:
        """Check for encoded data patterns"""
        encoding_info = {}
        
        # Base64 pattern
        base64_pattern = r'^[A-Za-z0-9+/]*={0,2}$'
        base64_matches = [d for d in sample_data if len(d) > 10 and re.match(base64_pattern, d)]
        
        if len(base64_matches) > len(sample_data) * 0.3:
            encoding_info['base64_likely'] = {
                'match_count': len(base64_matches),
                'match_ratio': len(base64_matches) / len(sample_data)
            }
        
        # Hex pattern
        hex_pattern = r'^[0-9a-fA-F]+$'
        hex_matches = [d for d in sample_data if len(d) > 8 and len(d) % 2 == 0 and re.match(hex_pattern, d)]
        
        if len(hex_matches) > len(sample_data) * 0.3:
            encoding_info['hex_likely'] = {
                'match_count': len(hex_matches),
                'match_ratio': len(hex_matches) / len(sample_data)
            }
        
        return encoding_info
    
    def _generate_intelligence_indicators(self, patterns_found: Dict[str, Any]) -> Dict[str, Any]:
        """Generate intelligence indicators based on found patterns"""
        indicators = {
            'high_value_data': [],
            'communication_potential': 0,
            'financial_potential': 0,
            'crypto_potential': 0,
            'location_potential': 0,
            'overall_intelligence_score': 0
        }
        
        for table_name, table_patterns in patterns_found.items():
            for col_name, col_patterns in table_patterns.items():
                
                # Check for high-value patterns
                if 'crypto_addresses' in col_patterns:
                    indicators['high_value_data'].append(f"{table_name}.{col_name}: Cryptocurrency addresses")
                    indicators['crypto_potential'] += 50
                
                if 'phone_numbers' in col_patterns:
                    indicators['high_value_data'].append(f"{table_name}.{col_name}: Phone numbers")
                    indicators['communication_potential'] += 30
                
                if 'financial' in col_patterns:
                    indicators['high_value_data'].append(f"{table_name}.{col_name}: Financial data")
                    indicators['financial_potential'] += 40
                
                if 'social_media' in col_patterns:
                    indicators['high_value_data'].append(f"{table_name}.{col_name}: Social media data")
                    indicators['communication_potential'] += 20
                
                # Check for message content
                content_analysis = col_patterns.get('content_analysis', {})
                if content_analysis.get('message_indicators', {}).get('likely_messages'):
                    indicators['communication_potential'] += 40
        
        # Calculate overall score
        indicators['overall_intelligence_score'] = min(
            indicators['communication_potential'] + 
            indicators['financial_potential'] + 
            indicators['crypto_potential'] + 
            indicators['location_potential'],
            100
        )
        
        return indicators
    
    def _classify_content_types(self, patterns_found: Dict[str, Any]) -> Dict[str, List[str]]:
        """Classify tables by their content types"""
        classification = {
            'communication': [],
            'financial': [],
            'location': [],
            'media': [],
            'system': [],
            'unknown': []
        }
        
        for table_name, table_patterns in patterns_found.items():
            table_types = set()
            
            for col_name, col_patterns in table_patterns.items():
                if 'phone_numbers' in col_patterns or 'social_media' in col_patterns:
                    table_types.add('communication')
                
                if 'financial' in col_patterns or 'crypto_addresses' in col_patterns:
                    table_types.add('financial')
                
                content_analysis = col_patterns.get('content_analysis', {})
                if content_analysis.get('message_indicators', {}).get('likely_messages'):
                    table_types.add('communication')
            
            # Classify based on detected types
            if 'communication' in table_types:
                classification['communication'].append(table_name)
            elif 'financial' in table_types:
                classification['financial'].append(table_name)
            else:
                classification['unknown'].append(table_name)
        
        return classification
    
    def get_pattern_summary(self, pattern_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Get a summary of pattern analysis results"""
        if 'error' in pattern_analysis:
            return {'error': pattern_analysis['error']}
        
        summary = {
            'tables_analyzed': pattern_analysis.get('tables_analyzed', 0),
            'high_value_findings': len(pattern_analysis.get('intelligence_indicators', {}).get('high_value_data', [])),
            'intelligence_score': pattern_analysis.get('intelligence_indicators', {}).get('overall_intelligence_score', 0),
            'content_types_found': [],
            'recommended_analysis': []
        }
        
        # Get content types
        classification = pattern_analysis.get('content_classification', {})
        for content_type, tables in classification.items():
            if tables:
                summary['content_types_found'].append(content_type)
        
        # Recommend analysis based on findings
        intelligence = pattern_analysis.get('intelligence_indicators', {})
        
        if intelligence.get('communication_potential', 0) > 30:
            summary['recommended_analysis'].extend(['narcotics', 'fraud', 'domestic_violence'])
        
        if intelligence.get('financial_potential', 0) > 30:
            summary['recommended_analysis'].append('financial_fraud')
        
        if intelligence.get('crypto_potential', 0) > 30:
            summary['recommended_analysis'].append('cryptocurrency_analysis')
        
        summary['recommended_analysis'] = list(set(summary['recommended_analysis']))
        
        return summary