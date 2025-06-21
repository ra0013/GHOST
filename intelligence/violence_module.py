
# intelligence/violence_intelligence.py
"""
Intelligence Modules
Pluggable crime-specific analysis modules
"""

import re
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter



class DomesticViolenceModule(BaseIntelligenceModule):
    """Domestic violence detection module"""
    
    def __init__(self, keywords: Dict[str, Any], config: Dict[str, Any], logger=None):
        super().__init__("Domestic Violence Intelligence", keywords, config, logger)
    
    def analyze(self, communications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze for domestic violence indicators"""
        self.log_analysis(f"Analyzing {len(communications)} communications")
        
        findings = []
        all_keywords = []
        
        # Collect all violence keywords
        for category, keyword_list in self.keywords.items():
            if isinstance(keyword_list, list):
                all_keywords.extend(keyword_list)
        
        for comm in communications:
            content = comm.get('content', '').lower()
            if not content:
                continue
            
            matched_keywords = [kw for kw in all_keywords if kw.lower() in content]
            
            if matched_keywords:
                risk_score = self.calculate_risk_score(matched_keywords, content)
                
                finding = {
                    'module': self.name,
                    'type': 'DOMESTIC_VIOLENCE_INDICATOR',
                    'timestamp': comm['timestamp'],
                    'contact': comm.get('contact', 'Unknown'),
                    'direction': comm.get('direction', 'Unknown'),
                    'risk_score': risk_score,
                    'indicators': {
                        'violence_keywords': matched_keywords,
                        'content_sample': content[:100] + '...' if len(content) > 100 else content
                    },
                    'original_communication': comm
                }
                
                findings.append(finding)
        
        self.log_analysis(f"Found {len(findings)} domestic violence indicators")
        return findings
    
    def calculate_risk_score(self, keywords: List[str], content: str) -> int:
        """Calculate domestic violence risk score"""
        score = 2
        
        # Direct threats = highest risk
        threat_terms = ['hurt you', 'kill you', 'beat you', 'destroy you']
        if any(term in keywords for term in threat_terms):
            score += 5
        
        # Control language
        control_terms = ['belong to me', 'property', 'cant leave', 'control']
        if any(term in keywords for term in control_terms):
            score += 3
        
        # Multiple indicators
        if len(keywords) > 2:
            score += 2
        
        return min(score, 10)
