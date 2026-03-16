import torch
import torch.nn as nn
from torchvision import transforms, models
import numpy as np
import cv2
from PIL import Image

from .texture_analyzer import TextureAnalyzer

class LivenessNet(nn.Module):
    """
    A lightweight CNN for binary classification (Live vs Spoof).
    Uses MobileNetV2 as a feature extractor.
    """
    def __init__(self):
        super(LivenessNet, self).__init__()
        # Load pre-trained MobileNetV2
        self.backbone = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.IMAGENET1K_V1)
        
        # Replace the final classification layer for Binary output
        num_features = self.backbone.classifier[1].in_features
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(0.2),
            nn.Linear(num_features, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 1),
            nn.Sigmoid() # Output: probability of being "Live" (1.0)
        )
        
    def forward(self, x):
        return self.backbone(x)

class LivenessDetector:
    """
    End-to-end liveness detector combining CNN and Texture Analysis.
    """
    def __init__(self, device=None, model_path=None):
        if device is None:
            self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = device
            
        self.texture_analyzer = TextureAnalyzer()
        self.model = LivenessNet().to(self.device).eval()
        
        # Load weights if provided (in a real scenario, you'd train this first)
        if model_path is not None:
            try:
                self.model.load_state_dict(torch.load(model_path, map_location=self.device))
                print(f"Loaded liveness model from {model_path}")
            except Exception as e:
                print(f"Warning: Could not load weights from {model_path}: {e}. Using untrained head.")
        else:
            print("Warning: Initializing Liveness CNN with untrained classification head.")

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
    @torch.no_grad()
    def predict_liveness(self, face_image: np.ndarray) -> dict:
        """
        Takes a face crop and predicts if it's a live person or a spoof.
        Returns a probability score and a boolean decision.
        """
        if face_image is None or face_image.size == 0:
            return {"is_live": False, "score": 0.0, "error": "Invalid face crop"}
            
        # 1. Texture Analysis (Fast heuristic check)
        texture_result = self.texture_analyzer.analyze_texture(face_image)
        
        # Convert BGR to RGB PIL Image
        face_rgb = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(face_rgb)
        
        # 2. CNN Prediction
        tensor = self.transform(pil_img).unsqueeze(0).to(self.device)
        score = self.model(tensor).item() # scalar 0.0 to 1.0
        
        # Final decision logic (ensemble)
        # In a real app, if it's too blurry, automatic fail.
        # Otherwise, trust the CNN mostly (score > 0.6)
        is_live = score > 0.6 and texture_result['is_clear']
        
        return {
            "is_live": is_live,
            "liveness_score": float(score),
            "blur_score": texture_result['blur_score'],
            "passed_texture_check": texture_result['is_clear']
        }
