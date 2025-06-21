
# intelligence/trafficking_module.py
"""
Trafficking Modules
Pluggable crime-specific analysis modules
"""

import re
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter


class HumanTraffickingModule(BaseIntelligenceModule):
    """Human trafficking detection module"""
    
    def __init__(self, keywords: Dict[str, Any], config: Dict[str, Any], logger=None):
        super().__init__("Human Trafficking Intelligence", keywords, config, logger)
    
    def analyze(self, communications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze for human trafficking indicators"""
        self.log_analysis(f"Analyzing {len(communications)} communications")
        
        findings = []
        all_keywords = []
        
        # Collect all trafficking keywords
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
                    'type': 'HUMAN_TRAFFICKING_INDICATOR',
                    'timestamp': comm['timestamp'],
                    'contact': comm.get('contact', 'Unknown'),
                    'direction': comm.get('direction', 'Unknown'),
                    'risk_score': risk_score,
                    'indicators': {
                        'trafficking_keywords': matched_keywords,
                        'content_sample': content[:100] + '...' if len(content) > 100 else content
                    },
                    'original_communication': comm
                }
                
                findings.append(finding)
        
        self.log_analysis(f"Found {len(findings)} trafficking indicators")
        return findings
    
    def calculate_risk_score(self, keywords: List[str], content: str) -> int:
        """Calculate trafficking risk score"""
        score = 2  # Base score for any indicators
        
        # High-risk control language
        control_terms = ['owe me', 'belong to me', 'property', 'debt']
        if any(term in keywords for term in control_terms):
            score += 4
        
        # Multiple indicators
        if len(keywords) > 2:
            score += 2
        
        # Movement indicators
        movement_terms = ['ticket', 'drive you', 'pick you up', 'new city']
        if any(term in keywords for term in movement_terms):
            score += 2
        
        return min(score, 10)

