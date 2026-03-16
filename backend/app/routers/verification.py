from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import Dict, Any

from app.models.schemas import FaceVerificationResult, LivenessResult, DocumentResult, KYCResult
from app.services.verification_service import VerificationService

router = APIRouter()

# Dependency
def get_service():
    return VerificationService()

@router.post("/face", response_model=FaceVerificationResult)
async def verify_face(
    live_image: UploadFile = File(...), 
    id_image: UploadFile = File(...),
    service: VerificationService = Depends(get_service)
):
    try:
        live_bytes = await live_image.read()
        id_bytes = await id_image.read()
        
        result = await service.verify_face(live_bytes, id_bytes)
        
        return FaceVerificationResult(
            success=True,
            message="Face comparison complete",
            match=result.get("match", False),
            confidence=result.get("confidence", 0.0)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/liveness", response_model=LivenessResult)
async def check_liveness(
    image: UploadFile = File(...),
    service: VerificationService = Depends(get_service)
):
    try:
        img_bytes = await image.read()
        
        result = await service.check_liveness(img_bytes)
        
        return LivenessResult(
            success=True,
            message="Liveness check complete",
            is_live=result.get("is_live", False),
            liveness_score=result.get("liveness_score", 0.0)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/document", response_model=DocumentResult)
async def verify_document(
    image: UploadFile = File(...),
    service: VerificationService = Depends(get_service)
):
    try:
        img_bytes = await image.read()
        
        result = await service.verify_document(img_bytes)
        
        if "error" in result:
            return DocumentResult(
                success=False,
                message=result["error"],
                doc_type="UNKNOWN",
                extracted_data={}
            )
            
        doc_data = result.get("document_data", {})
        return DocumentResult(
            success=True,
            message="Document parsed successfully",
            doc_type=doc_data.get("doc_type", "UNKNOWN"),
            extracted_data=doc_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/complete", response_model=KYCResult)
async def full_kyc_workflow(
    user_id: str = Form(...),
    live_image: UploadFile = File(...),
    doc_image: UploadFile = File(...),
    service: VerificationService = Depends(get_service)
):
    """
    Run the entire KYC pipeline (Face match + Liveness + Doc OCR + Risk Score).
    Updates user KYC status in DB.
    """
    try:
        l_bytes = await live_image.read()
        d_bytes = await doc_image.read()
        
        result = await service.run_full_kyc(user_id, l_bytes, d_bytes)
        
        kyc_status = "APPROVED" if result.get("kyc_approved") else "REJECTED"
        risk_data = result.get("risk", {})
        
        return KYCResult(
            success=True,
            message=f"KYC Verification {kyc_status}",
            kyc_status=kyc_status,
            risk_score=risk_data.get("risk_score", 100.0),
            risk_level=risk_data.get("risk_level", "CRITICAL"),
            details=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
