# modules/encryption_detector.py
"""
Encryption Detector Module
Detects database encryption and suggests bypass methods
"""

import sqlite3
import math
from pathlib import Path
from typing import Dict, List, Any

class EncryptionDetector:
    """Detects database encryption and provides bypass suggestions"""
    
    def __init__(self):
        self.encryption_signatures = {
            'sqlcipher': [b'SQLite format 3\x00', b'SQLCipher'],
            'see': [b'** This file contains an SQLite'],
            'encrypted_markers': [b'\x00\x00\x00\x00', b'\xFF\xFF\xFF\xFF'],
            'custom_encryption': []
        }
        
        self.common_passwords = [
            '',  # Empty password
            'password',
            'admin',
            '123456',
            'default',
            'user',
            'root',
            'test'
        ]
    
    def detect_encryption(self, db_path: Path) -> Dict[str, Any]:
        """Detect if database is encrypted and what type"""
        encryption_info = {
            'is_encrypted': False,
            'encryption_type': 'none',
            'confidence': 0,
            'indicators': [],
            'bypass_suggestions': [],
            'file_path': str(db_path),
            'file_size': 0
        }
        
        try:
            # Get file size
            encryption_info['file_size'] = db_path.stat().st_size
            
            # Read header for analysis
            with open(db_path, 'rb') as f:
                header = f.read(1024)
            
            # Check for SQLite header
            if header.startswith(b'SQLite format 3'):
                encryption_info['indicators'].append('Valid SQLite header found')
                
                # Try to open database - if it fails, might be encrypted
                try:
                    conn = sqlite3.connect(str(db_path))
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master LIMIT 1")
                    cursor.fetchone()
                    conn.close()
                    
                    # Successfully opened - not encrypted
                    encryption_info['encryption_type'] = 'none'
                    encryption_info['indicators'].append('Database opened successfully - no encryption')
                    
                except sqlite3.DatabaseError as e:
                    error_msg = str(e).lower()
                    if 'file is not a database' in error_msg or 'file is encrypted' in error_msg:
                        encryption_info['is_encrypted'] = True
                        encryption_info['encryption_type'] = 'unknown'
                        encryption_info['confidence'] = 70
                        encryption_info['indicators'].append('SQLite header present but cannot read database - likely encrypted')
            
            # Check for known encryption signatures
            for enc_type, signatures in self.encryption_signatures.items():
                for signature in signatures:
                    if signature in header:
                        encryption_info['is_encrypted'] = True
                        encryption_info['encryption_type'] = enc_type
                        encryption_info['confidence'] = 90
                        encryption_info['indicators'].append(f'{enc_type} signature detected')
                        break
            
            # Calculate entropy (high entropy suggests encryption)
            entropy = self._calculate_entropy(header)
            encryption_info['entropy'] = entropy
            
            if entropy > 7.5:  # High entropy threshold
                if not encryption_info['is_encrypted']:
                    encryption_info['is_encrypted'] = True
                    encryption_info['encryption_type'] = 'unknown'
                    encryption_info['confidence'] = max(encryption_info['confidence'], 60)
                encryption_info['indicators'].append(f'High entropy detected: {entropy:.2f}/8.0')
            
            # Generate bypass suggestions if encrypted
            if encryption_info['is_encrypted']:
                encryption_info['bypass_suggestions'] = self._get_bypass_suggestions(
                    encryption_info['encryption_type']
                )
            
        except Exception as e:
            encryption_info['error'] = str(e)
        
        return encryption_info
    
    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy of data"""
        if len(data) == 0:
            return 0
        
        # Count byte frequencies
        byte_counts = [0] * 256
        for byte in data:
            byte_counts[byte] += 1
        
        # Calculate entropy
        entropy = 0
        data_len = len(data)
        for count in byte_counts:
            if count > 0:
                probability = count / data_len
                entropy -= probability * math.log2(probability)
        
        return entropy
    
    def _get_bypass_suggestions(self, encryption_type: str) -> List[str]:
        """Get bypass suggestions based on encryption type"""
        suggestions = []
        
        if encryption_type == 'sqlcipher':
            suggestions.extend([
                "Try common passwords with SQLCipher CLI",
                "Look for encryption key in iOS Keychain extraction",
                "Check app's Info.plist for encryption hints",
                "Search for hardcoded keys in app binary",
                "Try bundle identifier as password",
                "Look for key derivation from device UDID",
                "Check app preferences for stored passwords"
            ])
            
        elif encryption_type == 'see':
            suggestions.extend([
                "SQLite Encryption Extension - look for license key",
                "Check for key derivation from device identifiers",
                "Look for encryption key in app preferences",
                "Try common SEE activation codes"
            ])
            
        else:  # Unknown encryption
            suggestions.extend([
                "Analyze with hex editor to identify encryption scheme",
                "Look for encryption keys in iOS Keychain",
                "Check app source code or reverse engineer binary",
                "Try common encryption passwords",
                "Look for key derivation from device identifiers",
                "Check for custom encryption implementation",
                "Try brute force with password dictionary"
            ])
        
        return suggestions
    
    def attempt_password_bypass(self, db_path: Path, additional_passwords: List[str] = None) -> Dict[str, Any]:
        """Attempt to bypass encryption with common passwords"""
        bypass_result = {
            'success': False,
            'working_password': None,
            'passwords_tried': 0,
            'method': 'sqlcipher_password_attempt'
        }
        
        # Combine common passwords with additional ones
        password_list = self.common_passwords.copy()
        if additional_passwords:
            password_list.extend(additional_passwords)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_passwords = []
        for pwd in password_list:
            if pwd not in seen:
                seen.add(pwd)
                unique_passwords.append(pwd)
        
        # Try each password
        for password in unique_passwords:
            bypass_result['passwords_tried'] += 1
            
            if self._try_sqlcipher_password(db_path, password):
                bypass_result['success'] = True
                bypass_result['working_password'] = password if password else '[empty password]'
                break
        
        return bypass_result
    
    def _try_sqlcipher_password(self, db_path: Path, password: str) -> bool:
        """Try to open database with SQLCipher password"""
        try:
            # This would require pysqlcipher3 or similar
            # For demonstration, we'll use basic sqlite3
            # In production, you'd use: import pysqlcipher3.dbapi2 as sqlite
            
            conn = sqlite3.connect(str(db_path))
            
            # Execute PRAGMA key (this won't work with standard sqlite3)
            # conn.execute(f"PRAGMA key = '{password}'")
            
            # Try to read schema
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master LIMIT 1")
            cursor.fetchone()
            
            conn.close()
            return True
            
        except Exception:
            return False
    
    def generate_password_dictionary(self, extraction_path: Path, app_info: Dict[str, Any] = None) -> List[str]:
        """Generate password dictionary based on extraction context"""
        passwords = self.common_passwords.copy()
        
        # Add app-specific passwords
        if app_info:
            bundle_id = app_info.get('bundle_id', '')
            app_name = app_info.get('app_name', '')
            
            if bundle_id:
                passwords.extend([
                    bundle_id,
                    bundle_id.split('.')[-1],  # Last component
                    bundle_id.replace('.', ''),  # No dots
                ])
            
            if app_name:
                passwords.extend([
                    app_name.lower(),
                    app_name.replace(' ', ''),
                    app_name.replace(' ', '_')
                ])
        
        # Look for potential passwords in extraction
        potential_passwords = self._extract_potential_passwords(extraction_path)
        passwords.extend(potential_passwords)
        
        # Remove duplicates
        return list(set(passwords))
    
    def _extract_potential_passwords(self, extraction_path: Path) -> List[str]:
        """Extract potential passwords from extraction files"""
        potential_passwords = []
        
        # Check common locations for passwords/keys
        password_files = [
            "var/mobile/Library/Preferences/*.plist",
            "var/mobile/Library/Keychain/*",
            "var/mobile/Applications/*/Info.plist"
        ]
        
        for pattern in password_files:
            try:
                for file_path in extraction_path.glob(pattern):
                    if file_path.is_file() and file_path.stat().st_size < 1000000:  # Skip large files
                        file_passwords = self._extract_passwords_from_file(file_path)
                        potential_passwords.extend(file_passwords)
            except Exception:
                continue
        
        return potential_passwords[:50]  # Limit to reasonable number
    
    def _extract_passwords_from_file(self, file_path: Path) -> List[str]:
        """Extract potential passwords from a file"""
        passwords = []
        
        try:
            # Read file as text (ignore binary files that can't be decoded)
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(1000)  # First 1000 chars
            
            # Look for password-like strings
            import re
            
            # Find strings that might be passwords (6-20 chars, alphanumeric)
            password_patterns = [
                r'\b[A-Za-z0-9]{6,20}\b',  # Basic alphanumeric
                r'["\'][A-Za-z0-9!@#$%^&*()_+\-=\[\]{}|;:,.<>?]{6,30}["\']',  # Quoted strings
            ]
            
            for pattern in password_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    # Clean up quotes
                    clean_match = match.strip('\'"')
                    if 6 <= len(clean_match) <= 20:
                        passwords.append(clean_match)
        
        except Exception:
            pass
        
        return passwords[:10]  # Limit per file
    
    def analyze_encryption_strength(self, db_path: Path) -> Dict[str, Any]:
        """Analyze encryption strength and provide assessment"""
        analysis = {
            'file_path': str(db_path),
            'encryption_strength': 'unknown',
            'bypass_difficulty': 'unknown',
            'recommended_approach': [],
            'time_estimate': 'unknown'
        }
        
        encryption_info = self.detect_encryption(db_path)
        
        if not encryption_info['is_encrypted']:
            analysis['encryption_strength'] = 'none'
            analysis['bypass_difficulty'] = 'trivial'
            analysis['time_estimate'] = 'immediate'
            return analysis
        
        encryption_type = encryption_info['encryption_type']
        entropy = encryption_info.get('entropy', 0)
        
        # Assess strength based on type and entropy
        if encryption_type == 'sqlcipher':
            analysis['encryption_strength'] = 'strong'
            analysis['bypass_difficulty'] = 'moderate'
            analysis['time_estimate'] = 'minutes to hours'
            analysis['recommended_approach'] = [
                'Try common passwords first',
                'Extract keys from iOS Keychain',
                'Analyze app binary for hardcoded keys',
                'Dictionary attack with app-specific passwords'
            ]
            
        elif encryption_type == 'see':
            analysis['encryption_strength'] = 'strong'
            analysis['bypass_difficulty'] = 'difficult'
            analysis['time_estimate'] = 'hours to days'
            analysis['recommended_approach'] = [
                'Look for SEE license key',
                'Reverse engineer key derivation',
                'Contact vendor for assistance'
            ]
            
        elif entropy > 7.5:
            analysis['encryption_strength'] = 'strong'
            analysis['bypass_difficulty'] = 'very difficult'
            analysis['time_estimate'] = 'days to weeks'
            analysis['recommended_approach'] = [
                'Identify encryption algorithm',
                'Look for implementation vulnerabilities',
                'Seek specialized cryptographic assistance'
            ]
            
        else:
            analysis['encryption_strength'] = 'weak'
            analysis['bypass_difficulty'] = 'easy'
            analysis['time_estimate'] = 'minutes'
            analysis['recommended_approach'] = [
                'Try simple password bypass',
                'Look for encoding rather than encryption',
                'Check for obfuscation techniques'
            ]
        
        return analysis
