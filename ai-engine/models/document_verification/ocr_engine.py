import cv2
import pytesseract
import numpy as np
import re

class OCREngine:
    """
    OCR Engine using OpenCV for preprocessing and Tesseract for text extraction.
    Designed to extract details from ID cards and Passports.
    """
    def __init__(self):
        # Regular expressions for common fields
        self.date_pattern = re.compile(r'\b\d{2}[/-]\d{2}[/-]\d{4}\b')
        self.mrz_pattern = re.compile(r'P<[A-Z0-9<]+') # Simplified Passport MRZ line 1

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Grayscale, denoise, and threshold the image to improve OCR accuracy.
        """
        if image is None or image.size == 0:
            return None
            
        # 1. Grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 2. Resize to 300 DPI equivalent for better Tesseract reading
        gray = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
        
        # 3. Apply Gaussian blur to remove noise
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # 4. Adaptive Thresholding
        thresh = cv2.adaptiveThreshold(
            blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 31, 2
        )
        return thresh

    def extract_text(self, image: np.ndarray) -> str:
        """
        Extract raw text from a preprocessed image using Tesseract.
        """
        processed = self.preprocess_image(image)
        if processed is None:
            return ""
            
        # PSM 6: Assume a single uniform block of text.
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(processed, config=custom_config)
        return text

    def parse_document(self, image: np.ndarray) -> dict:
        """
        Extract structured data from the document.
        """
        raw_text = self.extract_text(image)
        
        # Basic parsing logic (Heuristic based)
        dates = self.date_pattern.findall(raw_text)
        dob = dates[0] if len(dates) > 0 else "Unknown"
        expiry = dates[1] if len(dates) > 1 else "Unknown"
        
        # Identify document type basically by checking for MRZ
        is_passport = bool(self.mrz_pattern.search(raw_text))
        
        return {
            "raw_text": raw_text.strip(),
            "dob": dob,
            "expiry": expiry,
            "doc_type": "PASSPORT" if is_passport else "ID_CARD"
        }
