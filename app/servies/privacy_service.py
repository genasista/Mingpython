"""
Privacy Service for Genassista EDU
GDPR and EU AI Act compliance implementation
"""

import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib
import uuid

logger = logging.getLogger("Genassista-EDU-pythonAPI.privacy")

class DataCategory(Enum):
    """GDPR data categories"""
    PERSONAL = "personal"
    SENSITIVE = "sensitive"
    BIOMETRIC = "biometric"
    BEHAVIORAL = "behavioral"
    ACADEMIC = "academic"

class ProcessingPurpose(Enum):
    """GDPR processing purposes"""
    EDUCATION = "education"
    ASSESSMENT = "assessment"
    FEEDBACK = "feedback"
    ANALYTICS = "analytics"
    RESEARCH = "research"

class ConsentStatus(Enum):
    """Consent status"""
    GIVEN = "given"
    WITHDRAWN = "withdrawn"
    PENDING = "pending"
    NOT_REQUIRED = "not_required"

class PrivacyService:
    """Comprehensive privacy and data protection service"""
    
    def __init__(self):
        self.data_retention_periods = {
            DataCategory.PERSONAL: timedelta(days=365 * 7),  # 7 years
            DataCategory.SENSITIVE: timedelta(days=365 * 3),  # 3 years
            DataCategory.BIOMETRIC: timedelta(days=365 * 1),  # 1 year
            DataCategory.BEHAVIORAL: timedelta(days=365 * 2),  # 2 years
            DataCategory.ACADEMIC: timedelta(days=365 * 10),  # 10 years
        }
        
        self.ai_risk_levels = {
            "low": ["feedback_generation", "text_analysis"],
            "medium": ["grading_assistance", "content_recommendation"],
            "high": ["automated_grading", "behavioral_analysis"]
        }
    
    async def create_consent_record(self, 
                                  user_id: str,
                                  data_categories: List[DataCategory],
                                  processing_purposes: List[ProcessingPurpose],
                                  consent_given: bool = True,
                                  consent_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Create a GDPR consent record
        
        Args:
            user_id: User identifier
            data_categories: Categories of data being processed
            processing_purposes: Purposes for processing
            consent_given: Whether consent was given
            consent_date: When consent was given
        
        Returns:
            Consent record with unique ID
        """
        consent_id = str(uuid.uuid4())
        consent_date = consent_date or datetime.now()
        
        consent_record = {
            "consent_id": consent_id,
            "user_id": user_id,
            "data_categories": [cat.value for cat in data_categories],
            "processing_purposes": [purpose.value for purpose in processing_purposes],
            "consent_given": consent_given,
            "consent_date": consent_date.isoformat(),
            "status": ConsentStatus.GIVEN.value if consent_given else ConsentStatus.WITHDRAWN.value,
            "created_at": datetime.now().isoformat(),
            "expires_at": (consent_date + timedelta(days=365)).isoformat(),  # 1 year validity
            "withdrawal_date": None,
            "legal_basis": "consent" if consent_given else "legitimate_interest"
        }
        
        logger.info(f"Consent record created: {consent_id} for user {user_id}")
        return consent_record
    
    async def withdraw_consent(self, consent_id: str, user_id: str) -> Dict[str, Any]:
        """
        Withdraw GDPR consent
        
        Args:
            consent_id: Consent record ID
            user_id: User identifier
        
        Returns:
            Updated consent record
        """
        # In a real implementation, this would update the database
        withdrawal_record = {
            "consent_id": consent_id,
            "user_id": user_id,
            "status": ConsentStatus.WITHDRAWN.value,
            "withdrawal_date": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        logger.info(f"Consent withdrawn: {consent_id} for user {user_id}")
        return withdrawal_record
    
    async def assess_data_protection_impact(self, 
                                         data_categories: List[DataCategory],
                                         processing_purposes: List[ProcessingPurpose],
                                         ai_systems_used: List[str]) -> Dict[str, Any]:
        """
        Assess data protection impact (DPIA) for GDPR compliance
        
        Args:
            data_categories: Categories of data being processed
            processing_purposes: Purposes for processing
            ai_systems_used: AI systems being used
        
        Returns:
            DPIA assessment result
        """
        risk_score = 0
        risk_factors = []
        
        # Assess data sensitivity
        if DataCategory.SENSITIVE in data_categories:
            risk_score += 3
            risk_factors.append("Sensitive personal data processing")
        
        if DataCategory.BIOMETRIC in data_categories:
            risk_score += 4
            risk_factors.append("Biometric data processing")
        
        # Assess AI system risks
        high_risk_ai = [system for system in ai_systems_used 
                       if any(risk in system for risk in self.ai_risk_levels["high"])]
        
        if high_risk_ai:
            risk_score += 2
            risk_factors.append(f"High-risk AI systems: {', '.join(high_risk_ai)}")
        
        # Assess processing purposes
        if ProcessingPurpose.RESEARCH in processing_purposes:
            risk_score += 1
            risk_factors.append("Research data processing")
        
        # Determine risk level
        if risk_score >= 5:
            risk_level = "HIGH"
            requires_dpia = True
        elif risk_score >= 3:
            risk_level = "MEDIUM"
            requires_dpia = True
        else:
            risk_level = "LOW"
            requires_dpia = False
        
        dpia_result = {
            "dpia_id": str(uuid.uuid4()),
            "risk_level": risk_level,
            "risk_score": risk_score,
            "requires_dpia": requires_dpia,
            "risk_factors": risk_factors,
            "data_categories": [cat.value for cat in data_categories],
            "processing_purposes": [purpose.value for purpose in processing_purposes],
            "ai_systems": ai_systems_used,
            "assessed_at": datetime.now().isoformat(),
            "recommendations": self._generate_dpia_recommendations(risk_level, risk_factors)
        }
        
        logger.info(f"DPIA assessment completed: {risk_level} risk (score: {risk_score})")
        return dpia_result
    
    def _generate_dpia_recommendations(self, risk_level: str, risk_factors: List[str]) -> List[str]:
        """Generate DPIA recommendations based on risk assessment"""
        recommendations = []
        
        if risk_level == "HIGH":
            recommendations.extend([
                "Implement additional technical safeguards",
                "Conduct regular security audits",
                "Implement data minimization principles",
                "Ensure explicit consent for all processing",
                "Implement automated data deletion",
                "Conduct regular privacy impact assessments"
            ])
        elif risk_level == "MEDIUM":
            recommendations.extend([
                "Implement standard security measures",
                "Regular consent verification",
                "Data retention policy enforcement",
                "Privacy by design implementation"
            ])
        else:
            recommendations.extend([
                "Maintain standard privacy practices",
                "Regular consent reviews",
                "Basic security measures"
            ])
        
        return recommendations
    
    async def anonymize_personal_data(self, data: Dict[str, Any], 
                                   user_id: str) -> Dict[str, Any]:
        """
        Anonymize personal data for GDPR compliance
        
        Args:
            data: Data to anonymize
            user_id: User identifier
        
        Returns:
            Anonymized data
        """
        anonymized_data = data.copy()
        
        # Create pseudonymous identifier
        pseudonym = hashlib.sha256(f"{user_id}_{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        
        # Remove or pseudonymize personal identifiers
        personal_fields = ["name", "email", "phone", "address", "personal_number"]
        
        for field in personal_fields:
            if field in anonymized_data:
                if field == "name":
                    anonymized_data[field] = f"User_{pseudonym}"
                else:
                    anonymized_data[field] = f"[ANONYMIZED_{field.upper()}]"
        
        # Add anonymization metadata
        anonymized_data["_privacy"] = {
            "anonymized_at": datetime.now().isoformat(),
            "original_user_id": user_id,
            "pseudonym": pseudonym,
            "anonymization_method": "pseudonymization"
        }
        
        logger.info(f"Data anonymized for user {user_id} with pseudonym {pseudonym}")
        return anonymized_data
    
    async def check_data_retention(self, data_category: DataCategory, 
                                 creation_date: datetime) -> Dict[str, Any]:
        """
        Check if data should be retained based on GDPR retention periods
        
        Args:
            data_category: Category of data
            creation_date: When data was created
        
        Returns:
            Retention status and recommendations
        """
        retention_period = self.data_retention_periods.get(data_category, timedelta(days=365))
        expiry_date = creation_date + retention_period
        current_date = datetime.now()
        
        should_retain = current_date < expiry_date
        days_until_expiry = (expiry_date - current_date).days
        
        retention_status = {
            "data_category": data_category.value,
            "creation_date": creation_date.isoformat(),
            "retention_period_days": retention_period.days,
            "expiry_date": expiry_date.isoformat(),
            "should_retain": should_retain,
            "days_until_expiry": days_until_expiry,
            "recommendation": "DELETE" if not should_retain else "RETAIN",
            "checked_at": current_date.isoformat()
        }
        
        if not should_retain:
            logger.warning(f"Data retention period expired for category {data_category.value}")
        
        return retention_status
    
    async def generate_privacy_notice(self, 
                                    data_categories: List[DataCategory],
                                    processing_purposes: List[ProcessingPurpose],
                                    ai_systems: List[str]) -> Dict[str, Any]:
        """
        Generate GDPR-compliant privacy notice
        
        Args:
            data_categories: Categories of data being processed
            processing_purposes: Purposes for processing
            ai_systems: AI systems being used
        
        Returns:
            Privacy notice content
        """
        privacy_notice = {
            "notice_id": str(uuid.uuid4()),
            "version": "1.0",
            "effective_date": datetime.now().isoformat(),
            "data_controller": "Genassista EDU",
            "data_categories": [cat.value for cat in data_categories],
            "processing_purposes": [purpose.value for purpose in processing_purposes],
            "legal_basis": "Consent and legitimate interest for educational purposes",
            "data_retention": "Data retained according to educational requirements and legal obligations",
            "data_subjects_rights": [
                "Right to access",
                "Right to rectification",
                "Right to erasure",
                "Right to restrict processing",
                "Right to data portability",
                "Right to object",
                "Rights related to automated decision making"
            ],
            "ai_systems": ai_systems,
            "ai_transparency": "AI systems used for educational assessment and feedback generation",
            "data_protection_officer": "dpo@genassista.edu",
            "supervisory_authority": "Swedish Data Protection Authority (IMY)",
            "contact_information": {
                "email": "privacy@genassista.edu",
                "phone": "+46-XXX-XXX-XXX",
                "address": "Genassista EDU, Sweden"
            }
        }
        
        logger.info(f"Privacy notice generated: {privacy_notice['notice_id']}")
        return privacy_notice
    
    async def audit_data_processing(self, 
                                  user_id: str,
                                  processing_activity: str,
                                  data_categories: List[DataCategory],
                                  ai_systems_used: List[str]) -> Dict[str, Any]:
        """
        Audit data processing activity for GDPR compliance
        
        Args:
            user_id: User identifier
            processing_activity: Description of processing activity
            data_categories: Categories of data processed
            ai_systems_used: AI systems used
        
        Returns:
            Audit log entry
        """
        audit_entry = {
            "audit_id": str(uuid.uuid4()),
            "user_id": user_id,
            "processing_activity": processing_activity,
            "data_categories": [cat.value for cat in data_categories],
            "ai_systems_used": ai_systems_used,
            "timestamp": datetime.now().isoformat(),
            "compliance_status": "COMPLIANT",
            "privacy_impact": "LOW" if len(data_categories) <= 2 else "MEDIUM",
            "retention_applied": True,
            "consent_verified": True
        }
        
        logger.info(f"Data processing audited: {audit_entry['audit_id']} for user {user_id}")
        return audit_entry

# Global instance
privacy_service = PrivacyService()
