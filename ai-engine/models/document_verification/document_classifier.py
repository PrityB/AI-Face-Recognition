import cv2
import numpy as np

class DocumentClassifier:
    """
    Classifies the document quality and type before sending to OCR.
    Detects glare, blur, and verifies edges.
    """
    def __init__(self):
        self.glare_threshold = 240
        self.glare_percentage_allowed = 0.05 # 5% of pixels

    def detect_glare(self, image: np.ndarray) -> dict:
        """
        Detects if there is significant glare (e.g. from flash) on the document.
        """
        if image is None:
            return {"has_glare": False, "glare_percentage": 0.0}
            
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Count pixels that are very close to white (240-255)
        glare_pixels = cv2.countNonZero(cv2.inRange(gray, self.glare_threshold, 255))
        total_pixels = gray.size
        
        percentage = glare_pixels / total_pixels
        has_glare = percentage > self.glare_percentage_allowed
        
        return {
            "has_glare": has_glare,
            "glare_percentage": float(percentage)
        }
        
    def detect_document_edges(self, image: np.ndarray) -> bool:
        """
        Verify that we can actually see the document enclosed within the frame.
        Uses Canny Edge Detection and Contour finding.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, 75, 200)
        
        contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
        
        # Look for a four-sided contour (the document)
        for c in contours:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            
            if len(approx) == 4:
                return True # Found document boundaries
                
        return False

    def assess_quality(self, image: np.ndarray) -> dict:
        """
        Run all quality checks on the document image.
        """
        glare_check = self.detect_glare(image)
        edges_found = self.detect_document_edges(image)
        
        is_acceptable = not glare_check['has_glare'] and edges_found
        
        return {
            "is_acceptable": is_acceptable,
            "has_glare": glare_check['has_glare'],
            "edges_detected": edges_found,
            "error": "Document quality too poor for OCR" if not is_acceptable else None
        }
