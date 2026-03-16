import httpx
from fastapi import UploadFile
from typing import Dict, Any
import os

from app.core.config import settings

class VerificationService:
    """
    Service layer that orchestrates calls to the AI Engine and updates the DB.
    """
    def __init__(self):
        self.ai_url = settings.AI_ENGINE_URL
        # In a real app we'd inject a DB session here
        
    async def call_ai_engine(self, endpoint: str, files: dict) -> dict:
        """Helper to post multipart files to the AI Engine."""
        # Using HTTPX for async external calls
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(f"{self.ai_url}{endpoint}", files=files)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Error calling AI Engine: {e}")
                raise Exception(f"AI Engine Error: {str(e)}")

    async def verify_face(self, live_image: bytes, id_image: bytes) -> dict:
        files = {
            'image1': ('live.jpg', live_image, 'image/jpeg'),
            'image2': ('id.jpg', id_image, 'image/jpeg')
        }
        return await self.call_ai_engine("/predict/face", files)

    async def check_liveness(self, live_image: bytes) -> dict:
        files = {
            'image': ('live.jpg', live_image, 'image/jpeg')
        }
        return await self.call_ai_engine("/predict/liveness", files)

    async def verify_document(self, doc_image: bytes) -> dict:
        files = {
            'image': ('doc.jpg', doc_image, 'image/jpeg')
        }
        return await self.call_ai_engine("/predict/document", files)
        
    async def run_full_kyc(self, user_id: str, live_image: bytes, doc_image: bytes) -> dict:
        """
        Orchestrates full KYC: Face Match -> Liveness -> OCR -> Risk Score.
        Calls the macro AI engine endpoint.
        """
        files = {
            'face_image': ('live.jpg', live_image, 'image/jpeg'),
            'doc_image': ('doc.jpg', doc_image, 'image/jpeg')
        }
        result = await self.call_ai_engine("/predict/kyc", files)
        
        # NOTE: Here we would persist `result` to the PostgreSQL DB
        # user = db.query(User).filter(User.user_identifier == user_id).first()
        # verification = Verification(user_id=user.id, risk_score=result['risk']['risk_score']...)
        # db.add(verification)
        # db.commit()
        
        return result
