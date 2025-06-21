# intelligence/base_intelligence.py
"""
Intelligence Modules
Pluggable crime-specific analysis modules
"""

import re
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter

class BaseIntelligenceModule(ABC):
    """Base class for all intelligence modules"""
    
    def __init__(self, name: str, keywords: Dict[str, Any], config: Dict[str, Any], logger=None):
        self.name = name
        self.keywords = keywords
        self.config = config
        self.logger = logger
        self.version = "1.0"
        
    @abstractmethod
    def analyze(self, communications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze communications and return findings"""
        pass
    
    @abstractmethod
    def calculate_risk_score(self, indicators: List[str], content: str) -> int:
        """Calculate risk score for findings"""
        pass
    
    def log_analysis(self, message: str):
        """Log analysis activity"""
        if self.logger:
            self.logger.log_action(f"{self.name.upper()}_MODULE", message)

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

