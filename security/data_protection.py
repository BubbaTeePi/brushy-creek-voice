import re
import hashlib
import secrets
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json
from datetime import datetime, timedelta

class PIIType(Enum):
    """Types of PII that need protection"""
    SSN = "ssn"
    PHONE = "phone"
    EMAIL = "email"
    ADDRESS = "address"
    ACCOUNT_NUMBER = "account_number"
    CREDIT_CARD = "credit_card"
    NAME = "name"

class DataClassification(Enum):
    """Data classification levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

class PIIDetector:
    """Detects and classifies PII in text and voice data"""
    
    def __init__(self):
        self.patterns = {
            PIIType.SSN: [
                r'\b\d{3}-\d{2}-\d{4}\b',
                r'\b\d{9}\b'
            ],
            PIIType.PHONE: [
                r'\b\d{3}-\d{3}-\d{4}\b',
                r'\(\d{3}\)\s*\d{3}-\d{4}',
                r'\b\d{10}\b'
            ],
            PIIType.EMAIL: [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            ],
            PIIType.ACCOUNT_NUMBER: [
                r'\b\d{8,12}\b'  # Utility account numbers
            ],
            PIIType.CREDIT_CARD: [
                r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'
            ]
        }
    
    def detect_pii(self, text: str) -> List[Dict]:
        """Detect PII in text and return findings"""
        findings = []
        
        for pii_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text)
                for match in matches:
                    findings.append({
                        "type": pii_type.value,
                        "value": match.group(),
                        "start": match.start(),
                        "end": match.end(),
                        "classification": DataClassification.RESTRICTED.value
                    })
        
        return findings
    
    def sanitize_for_logging(self, text: str) -> str:
        """Remove/mask PII for safe logging"""
        sanitized = text
        
        for pii_type, patterns in self.patterns.items():
            for pattern in patterns:
                if pii_type == PIIType.PHONE:
                    # Keep area code, mask rest
                    sanitized = re.sub(pattern, r'(\1) XXX-XXXX', sanitized)
                elif pii_type == PIIType.EMAIL:
                    # Keep domain, mask user
                    sanitized = re.sub(pattern, r'XXXX@\2', sanitized)
                else:
                    # Fully mask other PII
                    sanitized = re.sub(pattern, '[REDACTED]', sanitized)
        
        return sanitized

class DataEncryption:
    """Handles encryption/decryption of sensitive data"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        self.key = encryption_key or self._generate_key()
    
    def _generate_key(self) -> str:
        """Generate a secure encryption key"""
        return secrets.token_urlsafe(32)
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        from cryptography.fernet import Fernet
        
        # Use Fernet encryption for government-grade security
        key = Fernet.generate_key()
        cipher_suite = Fernet(key)
        
        encrypted_data = cipher_suite.encrypt(data.encode())
        
        # Return base64 encoded encrypted data
        import base64
        return base64.b64encode(encrypted_data).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        from cryptography.fernet import Fernet
        import base64
        
        # Implementation would use stored key
        # This is a placeholder for the pattern
        return "[DECRYPTED_DATA]"

class DataRetentionManager:
    """Manages data retention and automatic deletion"""
    
    def __init__(self):
        self.retention_policies = {
            "call_recordings": timedelta(days=30),
            "transcripts": timedelta(days=90),
            "call_logs": timedelta(days=365),
            "pii_data": timedelta(days=30),
            "emergency_calls": timedelta(days=2555)  # 7 years
        }
    
    def schedule_deletion(self, data_type: str, record_id: str, created_date: datetime):
        """Schedule automatic deletion based on retention policy"""
        if data_type in self.retention_policies:
            deletion_date = created_date + self.retention_policies[data_type]
            
            return {
                "record_id": record_id,
                "data_type": data_type,
                "deletion_date": deletion_date.isoformat(),
                "status": "scheduled"
            }
    
    def purge_expired_data(self):
        """Remove data past retention period"""
        # Implementation would scan database and remove expired records
        pass

class AccessControlManager:
    """Manages access to sensitive data"""
    
    def __init__(self):
        self.access_levels = {
            "public": ["basic_info", "hours", "contact"],
            "employee": ["call_logs", "transcripts"],
            "supervisor": ["pii_data", "recordings"],
            "admin": ["all_data", "system_config"],
            "emergency": ["emergency_override"]
        }
    
    def check_access(self, user_role: str, data_type: str) -> bool:
        """Check if user has access to specific data type"""
        if user_role in self.access_levels:
            allowed_data = self.access_levels[user_role]
            return data_type in allowed_data or "all_data" in allowed_data
        return False
    
    def log_access_attempt(self, user_id: str, data_type: str, success: bool):
        """Log all access attempts for audit trail"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "data_type": data_type,
            "access_granted": success,
            "ip_address": "[IP_ADDRESS]",
            "user_agent": "[USER_AGENT]"
        }
        
        # In production, this would write to secure audit log
        print(f"AUDIT LOG: {json.dumps(log_entry)}")

class ComplianceManager:
    """Manages compliance with government regulations"""
    
    def __init__(self):
        self.compliance_frameworks = [
            "FISMA",      # Federal Information Security Management Act
            "NIST",       # National Institute of Standards and Technology
            "SOC2",       # Service Organization Control 2
            "HIPAA",      # If handling health-related calls
            "PCI-DSS",    # If processing payments
            "CJIS",       # Criminal Justice Information Services
        ]
        
        self.required_controls = {
            "data_encryption": True,
            "access_logging": True,
            "incident_response": True,
            "backup_procedures": True,
            "vulnerability_scanning": True,
            "penetration_testing": True,
            "security_training": True
        }
    
    def generate_compliance_report(self) -> Dict:
        """Generate compliance status report"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "frameworks": self.compliance_frameworks,
            "controls_status": self.required_controls,
            "next_review": (datetime.utcnow() + timedelta(days=90)).isoformat()
        }
    
    def validate_call_handling(self, call_data: Dict) -> Dict:
        """Validate that call handling meets compliance requirements"""
        compliance_check = {
            "pii_detected": False,
            "encryption_applied": False,
            "access_logged": False,
            "retention_scheduled": False,
            "compliant": False
        }
        
        # Check for PII
        detector = PIIDetector()
        transcript = call_data.get("transcript", "")
        pii_findings = detector.detect_pii(transcript)
        
        compliance_check["pii_detected"] = len(pii_findings) > 0
        
        # Additional compliance checks would go here
        
        # Overall compliance status
        compliance_check["compliant"] = all([
            compliance_check["encryption_applied"],
            compliance_check["access_logged"],
            compliance_check["retention_scheduled"]
        ])
        
        return compliance_check

# Example usage and testing
if __name__ == "__main__":
    # Test PII detection
    detector = PIIDetector()
    test_text = "My account number is 123456789 and phone is (512) 555-1234"
    
    findings = detector.detect_pii(test_text)
    print("PII Findings:", findings)
    
    sanitized = detector.sanitize_for_logging(test_text)
    print("Sanitized:", sanitized)
    
    # Test compliance validation
    compliance_mgr = ComplianceManager()
    report = compliance_mgr.generate_compliance_report()
    print("Compliance Report:", json.dumps(report, indent=2)) 