
# intelligence/narcotics/module.py
"""
Narcotics Module
Pluggable crime-specific analysis modules
"""

import re
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter


class NarcoticsIntelligenceModule(BaseIntelligenceModule):
    """Narcotics trafficking intelligence module"""
    
    def __init__(self, keywords: Dict[str, Any], config: Dict[str, Any], logger=None):
        super().__init__("Narcotics Intelligence", keywords, config, logger)
        
        self.drug_patterns = [
            r'\b\d+\s*(gram|g|oz|ounce|lb|pound)\b',
            r'\$\d+\s*(each|per|for)',
            r'\b(front|fronted|credit)\b',
            r'\b(pickup|drop|meet)\s+(at|@)\s+\w+'
        ]
    
    def analyze(self, communications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze communications for narcotics indicators"""
        self.log_analysis(f"Analyzing {len(communications)} communications")
        
        findings = []
        all_keywords = []
        
        # Collect all narcotics keywords
        for category, keyword_list in self.keywords.items():
            if isinstance(keyword_list, list):
                all_keywords.extend(keyword_list)
        
        for comm in communications:
            content = comm.get('content', '').lower()
            if not content:
                continue
            
            # Check for keyword matches
            matched_keywords = [kw for kw in all_keywords if kw.lower() in content]
            
            # Check for pattern matches
            pattern_matches = []
            for pattern in self.drug_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                pattern_matches.extend(matches)
            
            if matched_keywords or pattern_matches:
                risk_score = self.calculate_risk_score(matched_keywords, content)
                
                finding = {
                    'module': self.name,
                    'type': 'NARCOTICS_INDICATOR',
                    'timestamp': comm['timestamp'],
                    'contact': comm.get('contact', 'Unknown'),
                    'direction': comm.get('direction', 'Unknown'),
                    'risk_score': risk_score,
                    'indicators': {
                        'matched_keywords': matched_keywords,
                        'pattern_matches': pattern_matches,
                        'content_sample': content[:100] + '...' if len(content) > 100 else content
                    },
                    'original_communication': comm
                }
                
                findings.append(finding)
        
        # Analyze distribution networks
        network_findings = self._analyze_distribution_networks(findings)
        findings.extend(network_findings)
        
        self.log_analysis(f"Found {len(findings)} narcotics indicators")
        return findings
    
    def calculate_risk_score(self, keywords: List[str], content: str) -> int:
        """Calculate risk score for narcotics indicators"""
        score = 1
        
        # High-risk drugs
        high_risk_drugs = ['fentanyl', 'fent', 'heroin', 'meth', 'crystal']
        if any(drug in keywords for drug in high_risk_drugs):
            score += self.config.get('risk_weights', {}).get('high_risk_drugs', 4)
        
        # Multiple drug types
        unique_drugs = set(keywords)
        if len(unique_drugs) > 2:
            score += self.config.get('risk_weights', {}).get('multiple_drugs', 2)
        
        # Quantity indicators
        if any(word in content for word in ['pound', 'kilo', 'brick']):
            score += self.config.get('risk_weights', {}).get('quantity_indicators', 3)
        
        # Money mentions
        if re.search(r'\$\d{3,}', content):
            score += 2
        
        return min(score, 10)
    
    def _analyze_distribution_networks(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze for distribution network patterns"""
        contact_activity = defaultdict(list)
        
        for finding in findings:
            contact = finding['contact']
            contact_activity[contact].append(finding)
        
        network_findings = []
        
        for contact, activities in contact_activity.items():
            if len(activities) > 3:  # Frequent drug-related communications
                network_finding = {
                    'module': self.name,
                    'type': 'DISTRIBUTION_NETWORK_NODE',
                    'contact': contact,
                    'activity_count': len(activities),
                    'risk_score': min(len(activities) + 3, 10),
                    'timespan': {
                        'first': min(a['timestamp'] for a in activities),
                        'last': max(a['timestamp'] for a in activities)
                    },
                    'description': f"High-frequency narcotics communications with {contact}"
                }
                network_findings.append(network_finding)
        
        return network_findings

