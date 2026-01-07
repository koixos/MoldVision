from dataclasses import dataclass
import numpy as np

EXTS = (".png", ".jpg", ".jpeg")

PREPROCESS_METHODS = [
    "weighted",
    "average",
    "max",
    "min",
    "luminosity",
]

DETECT_METHODS = [
    "variance",
    "adaptive",
    "edge",
    "saturation",
    "var_lbp",
]

@dataclass
class PreprocessedImage:
    img: np.ndarray | None = None
    texture: str = "low_txt"

@dataclass
class PreprocessParams:
    custom: bool = False
    gray_method: str = PREPROCESS_METHODS[0]

@dataclass
class DetectParams:
    custom: bool = False
    ksize: int = 9
    elemsize: int = 5
    th: int = 75
    method: str = DETECT_METHODS[0]
    opacity: float = 0.6
