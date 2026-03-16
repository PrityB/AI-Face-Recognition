import os
import sys

# Add the parent directory to the path so we can import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.face_recognition.model import FaceRecognizer
from models.liveness_detection.model import LivenessDetector
from models.document_verification.ocr_engine import OCREngine
from models.document_verification.document_classifier import DocumentClassifier
from models.fraud_detection.risk_scorer import RiskScorer
import numpy as np

class VerificationPipeline:
    """
    Orchestrates the individual AI models into a cohesive verification flow.
    """
    def __init__(self):
        print("Initializing Verification Pipeline (Loading Models)...")
        # Initialize all models (This takes time/memory so we do it once)
        self.face_recognizer = FaceRecognizer()
        self.liveness_detector = LivenessDetector()
        self.ocr_engine = OCREngine()
        self.doc_classifier = DocumentClassifier()
        self.risk_scorer = RiskScorer()
        print("Pipeline Ready.")

    def run_face_comparison(self, img1: np.ndarray, img2: np.ndarray) -> dict:
        return self.face_recognizer.compare_faces(img1, img2)

    def run_liveness_check(self, face_img: np.ndarray) -> dict:
        # First extract the face crop if it's a full image
        crops = self.face_recognizer.detector.extract_face_crops(face_img)
        if not crops:
            return {"error": "No face found for liveness check", "is_live": False}
            
        return self.liveness_detector.predict_liveness(crops[0])

    def run_document_verification(self, doc_img: np.ndarray) -> dict:
        # Check quality first
        quality = self.doc_classifier.assess_quality(doc_img)
        if not quality['is_acceptable']:
            return {"error": quality['error'], "quality": quality}
            
        # Run OCR
        data = self.ocr_engine.parse_document(doc_img)
        return {
            "document_data": data,
            "quality": quality
        }

    def run_full_kyc(self, face_img: np.ndarray, doc_img: np.ndarray, id_headshot_img: np.ndarray = None) -> dict:
        """
        End to end KYC workflow.
        1. Compare live face against ID document face
        2. Check liveness of live face
        3. OCR the document
        4. Score risk
        """
        # If id_headshot_img is not provided, we extract it from doc_img (simplified here)
        compare_target = id_headshot_img if id_headshot_img is not None else doc_img
        
        # 1. Matching
        match_result = self.run_face_comparison(face_img, compare_target)
        
        # 2. Liveness
        liveness_result = self.run_liveness_check(face_img)
        
        # 3. Document
        doc_result = self.run_document_verification(doc_img)
        
        # 4. Risk Scoring
        risk_input = {
            "face_match_confidence": match_result.get("confidence", 0.0),
            "liveness_score": liveness_result.get("liveness_score", 0.0),
            "document_glare": doc_result.get("quality", {}).get("glare_percentage", 1.0)
        }
        
        risk_result = self.risk_scorer.evaluate_risk(risk_input)
        
        # Final decision
        kyc_approved = (
            match_result.get("match", False) and 
            liveness_result.get("is_live", False) and 
            risk_result.get("risk_level") in ["LOW", "MEDIUM"]
        )
        
        return {
            "kyc_approved": kyc_approved,
            "face_match": match_result,
            "liveness": liveness_result,
            "document": doc_result,
            "risk": risk_result
        }
