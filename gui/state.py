from dataclasses import dataclass, field
import numpy as np
from typing import Dict, List

@dataclass
class ImageState:
    path: str
    filename: str

    original: np.ndarray
    preprocessed: np.ndarray | None = None
    detected: np.ndarray | None = None

    preprocess_params: Dict = field(default_factory=dict)
    detect_params: Dict = field(default_factory=dict)

class AppState:
    def __init__(self):
        self.images: List[ImageState] = []
        self.active_index: int = -1

    def add_image(self, image: ImageState):
        self.images.append(image)
        self.active_index = len(self.images) - 1

    def remove_image(self, index: int):
        if 0 <= index < len(self.images):
            self.images.pop(index)
            if not self.images:
                self.active_index = -1
            else:
                self.active_index = max(0, self.active_index - 1)
        
    def set_active(self, index: int):
        if 0 <= index < len(self.images):
            self.active_index = index

    def active(self) -> ImageState | None:
        if self.active_index == -1:
            return None
        return self.images[self.active_index]
    