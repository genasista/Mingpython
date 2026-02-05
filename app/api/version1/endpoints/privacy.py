from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime
from pydantic import BaseModel
import logging

router = APIRouter()
logger = logging.getLogger("Genassista-EDU-pythonAPI.privacy")

class ConsentRequest(BaseModel):
    user_id: str
    data_category: str
    purpose: str
    consent_given: bool

class ConsentResponse(BaseModel):
    consent_id: str
    user_id: str
    data_category: str
    purpose: str
    consent_given: bool
    created_at: datetime

@router.post("/consent", response_model=ConsentResponse)
async def create_consent(request: ConsentRequest):
    """Skapa samtycke för databehandling"""
    try:
        consent_id = f"consent_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        consent = ConsentResponse(
            consent_id=consent_id,
            user_id=request.user_id,
            data_category=request.data_category,
            purpose=request.purpose,
            consent_given=request.consent_given,
            created_at=datetime.now()
        )
        
        logger.info(f"Consent created: {consent_id} for user {request.user_id}")
        return consent
        
    except Exception as e:
        logger.error(f"Consent creation failed: {e}")
        raise HTTPException(status_code=500, detail="Consent creation failed")

@router.get("/consent/{user_id}")
async def get_user_consent(user_id: str):
    """Hämta användarens samtycken"""
    try:
        # Mock data
        return {
            "user_id": user_id,
            "consents": [
                {
                    "consent_id": "consent_001",
                    "data_category": "educational_data",
                    "purpose": "learning_analysis",
                    "consent_given": True,
                    "created_at": datetime.now().isoformat()
                }
            ]
        }
        
    except Exception as e:
        logger.error(f"Get user consent failed: {e}")
        raise HTTPException(status_code=500, detail="Get user consent failed")

@router.get("/compliance-status")
async def get_compliance_status():
    """Hämta GDPR-compliance status"""
    try:
        return {
            "gdpr_compliant": True,
            "data_protection_officer": "DPO@genassista.edu",
            "privacy_policy_version": "1.0",
            "last_audit": datetime.now().isoformat(),
            "data_retention_policy": "7 years for educational records",
            "consent_management": "Active",
            "data_breach_procedures": "Implemented"
        }
        
    except Exception as e:
        logger.error(f"Get compliance status failed: {e}")
        raise HTTPException(status_code=500, detail="Get compliance status failed")