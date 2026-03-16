import cv2
import numpy as np

class TextureAnalyzer:
    """
    Analyzes image texture for anti-spoofing (detecting printed photos or screens).
    Uses Laplacian variance (blur/focus detection) and frequency analysis.
    """
    def __init__(self):
        # Blur threshold (less than this is considered blurry/spoofed)
        self.blur_threshold = 100.0
        
    def get_blur_score(self, image: np.ndarray) -> float:
        """
        Compute the variance of the Laplacian.
        Low variance = blurry (often a printed photo).
        """
        if image is None or image.size == 0:
            return 0.0
            
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
            
        return cv2.Laplacian(gray, cv2.CV_64F).var()
        
    def analyze_texture(self, face_crop: np.ndarray) -> dict:
        """
        Perform multiple texture analyses on a face crop.
        """
        blur_score = self.get_blur_score(face_crop)
        
        # Simple heuristic: photos/screens are often blurrier than live faces
        # due to the capturing process
        is_clear = blur_score > self.blur_threshold
        
        return {
            "blur_score": float(blur_score),
            "is_clear": bool(is_clear)
        }
