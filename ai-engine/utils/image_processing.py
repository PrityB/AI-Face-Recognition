import cv2
import numpy as np

def read_image_from_bytes(image_bytes: bytes) -> np.ndarray:
    """
    Convert raw bytes (from HTTP upload) into an OpenCV BGR numpy array.
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

def resize_image_if_needed(image: np.ndarray, max_dim=1920) -> np.ndarray:
    """
    Resize image to prevent OOM errors on large 4K smartphone photos.
    """
    if image is None:
        return None
        
    h, w = image.shape[:2]
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        image = cv2.resize(image, (int(w * scale), int(h * scale)))
    return image
