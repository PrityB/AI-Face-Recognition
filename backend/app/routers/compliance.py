from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.models.schemas import ComplianceStatusResponse

router = APIRouter()

# Note: In a real app, this would query the PostgreSQL database
# For this demo/showcase, we will mock the responses

@router.get("/status/{user_id}", response_model=ComplianceStatusResponse)
async def get_kyc_status(user_id: str):
    """
    Get the KYC compliance status for a specific user.
    """
    # MOCK DB LOOKUP
    if user_id == "unknown":
        raise HTTPException(status_code=404, detail="User not found")
        
    return ComplianceStatusResponse(
        success=True,
        message="Status retrieved successfully",
        user_id=user_id,
        kyc_status="APPROVED", # Hardcoded for demo
        last_verification_date="2026-03-14T10:00:00Z",
        historical_risk_score=15.0
    )

@router.get("/risk/{user_id}")
async def get_risk_profile(user_id: str) -> Dict[str, Any]:
    """
    Get full risk profile history for auditing.
    """
    return {
        "user_id": user_id,
        "current_risk_level": "LOW",
        "flags": [
            "Passed liveness check",
            "Consistent IP address"
        ],
        "verifications_count": 1
    }
