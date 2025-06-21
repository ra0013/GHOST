
# intelligence/fraud_.py
"""
Fraud Module
Pluggable crime-specific analysis modules
"""

import re
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter

class FinancialFraudModule(BaseIntelligenceModule):
    """Financial fraud detection module"""
    
    def __init__(self, keywords: Dict[str, Any], config: Dict[str, Any], logger=None):
        super().__init__("Financial Fraud Intelligence", keywords, config, logger)
        
        self.financial_patterns = [
            r'\$\d{4,}',  # Large dollar amounts
            r'\b\d{4}-\d{4}-\d{4}-\d{4}\b',  # Credit card patterns
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN patterns
            r'\b(routing|account)\s+number\b',
            r'\bwire\s+\$\d+\b'
        ]
    
    def analyze(self, communications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze for financial fraud indicators"""
        self.log_analysis(f"Analyzing {len(communications)} communications")
        
        findings = []
        all_keywords = []
        
        # Collect all fraud keywords
        for category, keyword_list in self.keywords.items():
            if isinstance(keyword_list, list):
                all_keywords.extend(keyword_list)
        
        for comm in communications:
            content = comm.get('content', '').lower()
            if not content:
                continue
            
            # Check fraud indicators
            matched_keywords = [kw for kw in all_keywords if kw.lower() in content]
            
            # Check financial patterns
            pattern_matches = []
            for pattern in self.financial_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                pattern_matches.extend(matches)
            
            if matched_keywords or pattern_matches:
                risk_score = self.calculate_risk_score(matched_keywords, content)
                
                finding = {
                    'module': self.name,
                    'type': 'FINANCIAL_FRAUD_INDICATOR',
                    'timestamp': comm['timestamp'],
                    'contact': comm.get('contact', 'Unknown'),
                    'direction': comm.get('direction', 'Unknown'),
                    'risk_score': risk_score,
                    'indicators': {
                        'fraud_keywords': matched_keywords,
                        'financial_patterns': pattern_matches,
                        'content_sample': content[:100] + '...' if len(content) > 100 else content
                    },
                    'original_communication': comm
                }
                
                findings.append(finding)
        
        self.log_analysis(f"Found {len(findings)} fraud indicators")
        return findings
    
    def calculate_risk_score(self, keywords: List[str], content: str) -> int:
        """Calculate fraud risk score"""
        score = 1
        
        # High-risk fraud types
        high_risk = ['gift card', 'wire transfer', 'western union', 'crypto']
        if any(term in keywords for term in high_risk):
            score += self.config.get('risk_weights', {}).get('gift_cards', 4)
        
        # Multiple financial elements
        if len(keywords) > 1:
            score += 3
        
        # Personal information requests
        pii_terms = ['ssn', 'social security', 'pin', 'password']
        if any(term in keywords for term in pii_terms):
            score += 3
        
        # Urgency indicators
        urgency = ['urgent', 'emergency', 'immediately', 'asap']
        if any(term in content for term in urgency):
            score += self.config.get('risk_weights', {}).get('urgency', 2)
        
        return min(score, 10)

