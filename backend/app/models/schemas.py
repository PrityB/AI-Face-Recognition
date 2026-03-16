from pydantic import BaseModel
from typing import Optional, Dict, Any

class BaseResponse(BaseModel):
    success: bool
    message: str = ""

# Verification Endpoints
class FaceVerificationResult(BaseResponse):
    match: bool
    confidence: float
    
class LivenessResult(BaseResponse):
    is_live: bool
    liveness_score: float
    
class DocumentResult(BaseResponse):
    doc_type: str
    extracted_data: Dict[str, Any]

# Full KYC Workflow
class KYCResult(BaseResponse):
    kyc_status: str # APPROVED, REJECTED
    risk_score: float
    risk_level: str
    details: Dict[str, Any]

# Compliance
class ComplianceStatusResponse(BaseResponse):
    user_id: str
    kyc_status: str
    last_verification_date: Optional[str] = None
    historical_risk_score: Optional[float] = None
