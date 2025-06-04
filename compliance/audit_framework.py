import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, asdict
import hashlib
import uuid

class ComplianceFramework(Enum):
    """Government compliance frameworks"""
    FISMA = "FISMA"  # Federal Information Security Management Act
    NIST = "NIST_800_53"  # NIST Special Publication 800-53
    SOC2 = "SOC2"  # Service Organization Control 2
    CJIS = "CJIS"  # Criminal Justice Information Services
    HIPAA = "HIPAA"  # Health Insurance Portability and Accountability Act
    FedRAMP = "FedRAMP"  # Federal Risk and Authorization Management Program

class AuditLevel(Enum):
    """Audit logging levels"""
    MINIMAL = "minimal"  # Basic operations only
    STANDARD = "standard"  # Standard government requirements
    DETAILED = "detailed"  # Comprehensive logging for high-security environments
    FORENSIC = "forensic"  # Full forensic-level logging

@dataclass
class AuditEvent:
    """Standardized audit event structure"""
    event_id: str
    timestamp: datetime
    event_type: str
    user_id: Optional[str]
    session_id: Optional[str]
    source_ip: str
    user_agent: Optional[str]
    resource_accessed: str
    action_performed: str
    result: str  # SUCCESS, FAILURE, PARTIAL
    pii_involved: bool
    data_classification: str
    compliance_tags: List[str]
    risk_score: int  # 1-10 scale
    additional_details: Dict[str, Any]

class ComplianceAuditor:
    """Main compliance and audit management system"""
    
    def __init__(self, frameworks: List[ComplianceFramework], audit_level: AuditLevel = AuditLevel.STANDARD):
        self.frameworks = frameworks
        self.audit_level = audit_level
        self.audit_events: List[AuditEvent] = []
        self.compliance_requirements = self._load_compliance_requirements()
        
    def _load_compliance_requirements(self) -> Dict:
        """Load compliance requirements for selected frameworks"""
        requirements = {
            "data_retention": {},
            "access_controls": {},
            "encryption_standards": {},
            "audit_requirements": {},
            "incident_response": {}
        }
        
        for framework in self.frameworks:
            if framework == ComplianceFramework.FISMA:
                requirements.update(self._get_fisma_requirements())
            elif framework == ComplianceFramework.NIST:
                requirements.update(self._get_nist_requirements())
            elif framework == ComplianceFramework.SOC2:
                requirements.update(self._get_soc2_requirements())
            elif framework == ComplianceFramework.CJIS:
                requirements.update(self._get_cjis_requirements())
        
        return requirements
    
    def _get_fisma_requirements(self) -> Dict:
        """FISMA compliance requirements"""
        return {
            "data_retention": {
                "call_recordings": {"days": 30, "encryption": True},
                "audit_logs": {"years": 3, "immutable": True},
                "incident_reports": {"years": 7, "secure_storage": True}
            },
            "access_controls": {
                "multi_factor_auth": True,
                "role_based_access": True,
                "least_privilege": True,
                "session_timeout": 30  # minutes
            },
            "encryption_standards": {
                "data_at_rest": "AES-256",
                "data_in_transit": "TLS 1.3",
                "key_management": "FIPS 140-2 Level 3"
            },
            "audit_requirements": {
                "real_time_monitoring": True,
                "log_integrity": True,
                "automated_alerts": True
            }
        }
    
    def _get_nist_requirements(self) -> Dict:
        """NIST 800-53 requirements"""
        return {
            "access_control": {
                "AC-2": "Account Management",
                "AC-3": "Access Enforcement", 
                "AC-6": "Least Privilege",
                "AC-7": "Unsuccessful Logon Attempts"
            },
            "audit_accountability": {
                "AU-2": "Event Logging",
                "AU-3": "Content of Audit Records",
                "AU-6": "Audit Review, Analysis, and Reporting",
                "AU-9": "Protection of Audit Information"
            },
            "identification_authentication": {
                "IA-2": "Identification and Authentication",
                "IA-5": "Authenticator Management"
            }
        }
    
    def _get_soc2_requirements(self) -> Dict:
        """SOC 2 Type II requirements"""
        return {
            "security": {
                "logical_access": True,
                "network_security": True,
                "system_monitoring": True
            },
            "availability": {
                "system_uptime": 99.9,
                "disaster_recovery": True,
                "backup_procedures": True
            },
            "processing_integrity": {
                "data_validation": True,
                "error_handling": True,
                "system_monitoring": True
            },
            "confidentiality": {
                "data_encryption": True,
                "access_restrictions": True,
                "secure_disposal": True
            }
        }
    
    def _get_cjis_requirements(self) -> Dict:
        """Criminal Justice Information Services requirements"""
        return {
            "physical_security": {
                "controlled_access": True,
                "visitor_controls": True,
                "maintenance_controls": True
            },
            "personnel_security": {
                "background_checks": True,
                "training_requirements": True,
                "access_agreements": True
            },
            "technical_security": {
                "user_identification": True,
                "authentication": "advanced",
                "encryption": "FIPS 140-2",
                "malware_protection": True
            }
        }
    
    def log_audit_event(self, 
                       event_type: str,
                       user_id: Optional[str] = None,
                       session_id: Optional[str] = None,
                       source_ip: str = "unknown",
                       resource_accessed: str = "",
                       action_performed: str = "",
                       result: str = "SUCCESS",
                       pii_involved: bool = False,
                       additional_details: Optional[Dict] = None) -> str:
        """Log an audit event with compliance tracking"""
        
        event_id = str(uuid.uuid4())
        
        # Determine compliance tags based on event type
        compliance_tags = self._determine_compliance_tags(event_type, pii_involved)
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(event_type, result, pii_involved)
        
        # Determine data classification
        data_classification = "RESTRICTED" if pii_involved else "INTERNAL"
        
        audit_event = AuditEvent(
            event_id=event_id,
            timestamp=datetime.utcnow(),
            event_type=event_type,
            user_id=user_id,
            session_id=session_id,
            source_ip=source_ip,
            user_agent=additional_details.get("user_agent") if additional_details else None,
            resource_accessed=resource_accessed,
            action_performed=action_performed,
            result=result,
            pii_involved=pii_involved,
            data_classification=data_classification,
            compliance_tags=compliance_tags,
            risk_score=risk_score,
            additional_details=additional_details or {}
        )
        
        self.audit_events.append(audit_event)
        
        # Real-time compliance checking
        self._check_compliance_violations(audit_event)
        
        # Store in persistent audit log
        self._store_audit_event(audit_event)
        
        return event_id
    
    def _determine_compliance_tags(self, event_type: str, pii_involved: bool) -> List[str]:
        """Determine which compliance frameworks apply to this event"""
        tags = []
        
        # FISMA applies to all government systems
        if ComplianceFramework.FISMA in self.frameworks:
            tags.append("FISMA")
        
        # NIST controls apply to most events
        if ComplianceFramework.NIST in self.frameworks:
            tags.append("NIST_800_53")
        
        # PII-related events trigger additional compliance
        if pii_involved:
            tags.extend(["PRIVACY_ACT", "DATA_PROTECTION"])
        
        # Voice/telecom specific
        if "voice" in event_type.lower() or "call" in event_type.lower():
            tags.append("TELECOM_COMPLIANCE")
        
        return tags
    
    def _calculate_risk_score(self, event_type: str, result: str, pii_involved: bool) -> int:
        """Calculate risk score for the event (1-10 scale)"""
        base_score = 1
        
        # Event type risk
        high_risk_events = ["authentication_failure", "unauthorized_access", "data_breach", "system_compromise"]
        if any(risk_event in event_type.lower() for risk_event in high_risk_events):
            base_score += 5
        
        # Result risk
        if result == "FAILURE":
            base_score += 3
        elif result == "PARTIAL":
            base_score += 1
        
        # PII involvement
        if pii_involved:
            base_score += 2
        
        return min(base_score, 10)
    
    def _check_compliance_violations(self, event: AuditEvent):
        """Check for immediate compliance violations"""
        violations = []
        
        # Check for multiple failed authentication attempts
        if event.event_type == "authentication_failure":
            recent_failures = [
                e for e in self.audit_events[-50:] 
                if e.event_type == "authentication_failure" 
                and e.source_ip == event.source_ip
                and e.timestamp > datetime.utcnow() - timedelta(minutes=15)
            ]
            
            if len(recent_failures) >= 5:
                violations.append({
                    "type": "EXCESSIVE_FAILED_LOGINS",
                    "severity": "HIGH",
                    "description": f"5+ failed login attempts from {event.source_ip}",
                    "action_required": "BLOCK_IP_ADDRESS"
                })
        
        # Check for PII access outside business hours
        if event.pii_involved and event.timestamp.hour < 8 or event.timestamp.hour > 18:
            violations.append({
                "type": "AFTER_HOURS_PII_ACCESS",
                "severity": "MEDIUM",
                "description": "PII accessed outside normal business hours",
                "action_required": "ADDITIONAL_VERIFICATION"
            })
        
        # Report violations
        for violation in violations:
            self._report_compliance_violation(violation, event)
    
    def _report_compliance_violation(self, violation: Dict, event: AuditEvent):
        """Report compliance violation to administrators"""
        violation_report = {
            "violation_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "related_event_id": event.event_id,
            "violation_type": violation["type"],
            "severity": violation["severity"],
            "description": violation["description"],
            "recommended_action": violation["action_required"],
            "compliance_frameworks": event.compliance_tags
        }
        
        # In production, this would:
        # - Send alerts to security team
        # - Create incident tickets
        # - Trigger automated responses
        print(f"COMPLIANCE VIOLATION: {json.dumps(violation_report, indent=2)}")
    
    def _store_audit_event(self, event: AuditEvent):
        """Store audit event in tamper-proof storage"""
        # Create tamper-proof hash
        event_data = json.dumps(asdict(event), sort_keys=True, default=str)
        event_hash = hashlib.sha256(event_data.encode()).hexdigest()
        
        # In production, this would:
        # - Write to append-only audit database
        # - Store in blockchain for immutability
        # - Replicate to secure backup locations
        # - Send to SIEM system
        
        audit_record = {
            "event": asdict(event),
            "hash": event_hash,
            "stored_at": datetime.utcnow().isoformat()
        }
        
        # For now, write to local audit log
        with open("audit_log.jsonl", "a") as f:
            f.write(json.dumps(audit_record) + "\n")
    
    def generate_compliance_report(self, start_date: datetime, end_date: datetime) -> Dict:
        """Generate comprehensive compliance report"""
        relevant_events = [
            event for event in self.audit_events
            if start_date <= event.timestamp <= end_date
        ]
        
        report = {
            "report_id": str(uuid.uuid4()),
            "generated_at": datetime.utcnow().isoformat(),
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "frameworks": [f.value for f in self.frameworks],
            "summary": {
                "total_events": len(relevant_events),
                "high_risk_events": len([e for e in relevant_events if e.risk_score >= 7]),
                "pii_events": len([e for e in relevant_events if e.pii_involved]),
                "failed_events": len([e for e in relevant_events if e.result == "FAILURE"])
            },
            "compliance_status": self._assess_compliance_status(relevant_events),
            "recommendations": self._generate_compliance_recommendations(relevant_events)
        }
        
        return report
    
    def _assess_compliance_status(self, events: List[AuditEvent]) -> Dict:
        """Assess overall compliance status"""
        status = {}
        
        for framework in self.frameworks:
            framework_events = [
                e for e in events 
                if framework.value in e.compliance_tags
            ]
            
            status[framework.value] = {
                "compliant": True,  # Simplified for example
                "events_reviewed": len(framework_events),
                "violations_found": 0,  # Would calculate actual violations
                "score": 95  # Compliance score out of 100
            }
        
        return status
    
    def _generate_compliance_recommendations(self, events: List[AuditEvent]) -> List[str]:
        """Generate compliance improvement recommendations"""
        recommendations = []
        
        # Check for common issues
        high_risk_events = [e for e in events if e.risk_score >= 7]
        if len(high_risk_events) > 10:
            recommendations.append(
                "Consider implementing additional security controls due to high number of high-risk events"
            )
        
        pii_events = [e for e in events if e.pii_involved]
        if len(pii_events) > 100:
            recommendations.append(
                "Review PII handling procedures and consider additional data minimization techniques"
            )
        
        return recommendations

# Voice service specific audit events
class VoiceServiceAuditor(ComplianceAuditor):
    """Specialized auditor for voice service compliance"""
    
    def log_call_event(self, call_id: str, caller_number: str, action: str, 
                      pii_detected: bool = False, transcript_summary: str = ""):
        """Log voice call specific audit events"""
        
        # Sanitize caller number for logging
        sanitized_number = f"XXX-XXX-{caller_number[-4:]}" if len(caller_number) >= 4 else "XXX-XXX-XXXX"
        
        return self.log_audit_event(
            event_type=f"voice_call_{action}",
            session_id=call_id,
            resource_accessed="voice_service",
            action_performed=action,
            result="SUCCESS",
            pii_involved=pii_detected,
            additional_details={
                "caller_number_masked": sanitized_number,
                "transcript_length": len(transcript_summary),
                "has_transcript": bool(transcript_summary),
                "call_duration": None,  # Would be calculated
                "service_used": "brushy_creek_mud"
            }
        )
    
    def log_ai_interaction(self, session_id: str, prompt_type: str, 
                          contains_pii: bool, response_classification: str):
        """Log AI interaction audit events"""
        
        return self.log_audit_event(
            event_type="ai_interaction",
            session_id=session_id,
            resource_accessed="ai_service",
            action_performed=prompt_type,
            result="SUCCESS",
            pii_involved=contains_pii,
            additional_details={
                "ai_model": "gpt-4",
                "prompt_classification": prompt_type,
                "response_classification": response_classification,
                "tokens_used": None  # Would track actual usage
            }
        )

# Integration helper
def setup_compliance_auditing(frameworks: Optional[List[str]] = None) -> VoiceServiceAuditor:
    """Setup compliance auditing for voice service"""
    
    if frameworks is None:
        # Default government compliance frameworks
        frameworks = [
            ComplianceFramework.FISMA,
            ComplianceFramework.NIST,
            ComplianceFramework.SOC2
        ]
    else:
        frameworks = [ComplianceFramework(f) for f in frameworks]
    
    return VoiceServiceAuditor(
        frameworks=frameworks,
        audit_level=AuditLevel.STANDARD
    )

# Example usage
if __name__ == "__main__":
    # Setup auditor
    auditor = setup_compliance_auditing()
    
    # Example call audit
    call_id = auditor.log_call_event(
        call_id="call_123456",
        caller_number="5125551234",
        action="incoming_call_received",
        pii_detected=True,
        transcript_summary="Customer asking about water bill"
    )
    
    # Example AI interaction audit
    ai_id = auditor.log_ai_interaction(
        session_id="call_123456",
        prompt_type="customer_service_query",
        contains_pii=True,
        response_classification="standard_response"
    )
    
    # Generate compliance report
    report = auditor.generate_compliance_report(
        start_date=datetime.utcnow() - timedelta(days=30),
        end_date=datetime.utcnow()
    )
    
    print("Compliance Report Generated:")
    print(json.dumps(report, indent=2)) 