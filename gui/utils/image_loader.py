import cv2
import os

EXTS = (".png", ".jpg", ".jpeg")

def load_image(path: str):
    ext = os.path.splitext(path)[1].lower()
    if ext not in EXTS:
        raise ValueError(f"Unsupported image format: {ext}")
    
    img = cv2.imread(path)
    if img is None:
        raise ValueError(f"Failed to load image: {path}")
    
    return img
