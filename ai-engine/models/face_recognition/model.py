import numpy as np
import cv2
import torch
from facenet_pytorch import InceptionResnetV1
from torchvision import transforms
from PIL import Image
import os

from .detector import FaceDetector

class FaceRecognizer:
    """
    Face recognizer using InceptionResnetV1 (FaceNet).
    Generates 512-dimensional embeddings and calculates cosine similarity.
    """
    def __init__(self, device=None, threshold=0.6):
        if device is None:
            self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = device
            
        self.threshold = threshold
        
        # Load pre-trained VGGFace2 model (downloads automatically on first run)
        print(f"Loading FaceNet model on {self.device}...")
        self.resnet = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)
        self.detector = FaceDetector(device=self.device)
        
        # Standard FaceNet transforms
        self.transform = transforms.Compose([
            transforms.Resize((160, 160)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
        ])

    @torch.no_grad()
    def get_embedding(self, face_image: np.ndarray) -> np.ndarray:
        """
        Generate embedding for a single cropped face.
        Expected input: OpenCV BGR image.
        """
        if face_image is None or face_image.size == 0:
            return None
            
        # Convert to PIL RGB
        if len(face_image.shape) == 3:
            face_rgb = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(face_rgb)
        else:
            return None
            
        # Transform and add batch dimension
        tensor = self.transform(pil_img).unsqueeze(0).to(self.device)
        
        # Forward pass to get embedding (shape: [1, 512])
        embedding = self.resnet(tensor)
        
        # Move to CPU and numpy
        return embedding.cpu().numpy()[0]
        
    def extract_largest_face_embedding(self, image: np.ndarray) -> np.ndarray:
        """
        Detects faces in an image, extracts the largest one, and returns its embedding.
        Useful for "enrolling" a user from an ID card or selfie.
        """
        crops = self.detector.extract_face_crops(image)
        if not crops:
            return None
            
        # Sort crops by size (largest area first)
        crops.sort(key=lambda x: x.shape[0] * x.shape[1], reverse=True)
        
        # Get embedding of the largest face
        return self.get_embedding(crops[0])

    def compare_faces(self, image1: np.ndarray, image2: np.ndarray) -> dict:
        """
        End-to-end 1:1 facial matching.
        Takes two full images, detects the largest face in each, and compares them.
        Returns match boolean and similarity score.
        """
        emb1 = self.extract_largest_face_embedding(image1)
        emb2 = self.extract_largest_face_embedding(image2)
        
        if emb1 is None or emb2 is None:
            return {
                "match": False,
                "confidence": 0.0,
                "error": "Face not detected in one or both images"
            }
            
        # Calculate Cosine Similarity
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        similarity = float(similarity)
        
        # FaceNet typical threshold for cosine is around 0.6 to 0.7 depending on dataset
        is_match = similarity >= self.threshold
        
        return {
            "match": is_match,
            "confidence": max(0.0, similarity), # Ensure no negative confidence
            "threshold": self.threshold
        }

if __name__ == "__main__":
    recognizer = FaceRecognizer()
    print("FaceNet Ready!")
