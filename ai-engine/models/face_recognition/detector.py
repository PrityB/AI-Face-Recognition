import numpy as np
import cv2
import torch
from facenet_pytorch import MTCNN
from PIL import Image

class FaceDetector:
    """
    Face detector and aligner using PyTorch MTCNN.
    Provides bounding boxes, probabilities, and facial landmarks.
    """
    def __init__(self, device=None):
        if device is None:
            self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = device
            
        # Initialize MTCNN for face detection
        self.mtcnn = MTCNN(
            keep_all=True,        # Return all detected faces
            device=self.device,   # Use GPU if available
            thresholds=[0.6, 0.7, 0.7],
            min_face_size=40      # Ignore very small faces
        )
        
    def detect_faces(self, image: np.ndarray):
        """
        Detect faces in a numpy image (OpenCV format: BGR).
        Returns list of (box, prob, landmarks).
        """
        # Convert BGR (OpenCV) to RGB (PIL)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(image_rgb)
        
        # Detect faces
        boxes, probs, landmarks = self.mtcnn.detect(pil_img, landmarks=True)
        
        results = []
        if boxes is not None:
            for i, box in enumerate(boxes):
                if probs[i] > 0.90:  # High confidence threshold
                    results.append({
                        "box": [int(b) for b in box],
                        "confidence": float(probs[i]),
                        "landmarks": landmarks[i].tolist() if landmarks is not None else []
                    })
        return results
        
    def extract_face_crops(self, image: np.ndarray, margin=20):
        """
        Extract aligned face crops from the image.
        Returns list of cropped numpy images (BGR).
        """
        faces = self.detect_faces(image)
        crops = []
        
        h, w = image.shape[:2]
        
        for face in faces:
            x1, y1, x2, y2 = face['box']
            
            # Add margin
            x1 = max(0, x1 - margin)
            y1 = max(0, y1 - margin)
            x2 = min(w, x2 + margin)
            y2 = min(h, y2 + margin)
            
            crop = image[y1:y2, x1:x2]
            if crop.size > 0:
                crops.append(crop)
                
        return crops

if __name__ == "__main__":
    # Test block
    print("Initializing MTCNN Face Detector...")
    detector = FaceDetector()
    print(f"Device being used: {detector.device}")
