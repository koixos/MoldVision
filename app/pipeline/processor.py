from ..defs import PreprocessedImage, PreprocessParams, DetectParams

import cv2
import numpy as np
import matplotlib.pyplot as plt

class Processor:
    def __init__(self):
        self.preprocess_params = PreprocessParams()
        self.detect_params = DetectParams()

    def scale_img(self, img, max_dim=1024):
        """
        1) IMAGE SCALING
            eğer görselin h veya w boyutlarından en az biri
            max_dim ile belirtilen pixel boyutundan büyükse en büyük olan boyutu
            max_dim'e eşitleyecek şekilde iki boyutu da resize ediyor ve son
            görseli dönüyor
        """
        h,w = img.shape[:2]
        scale = min(max_dim / max(h, w), 1.0)
        if scale < 1.0:
            img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
        return img    

    def detect_background_brightness(self, img, sample_center=False):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        v = hsv[:, :, 2]

        region = v

        if sample_center:
            h, w = v.shape
            ch, cw = h // 2, w // 2
            region = v[ch - h // 6 : ch + h // 6,
                    cw - w // 6 : cw + w // 6]

        mean_val = np.mean(region)

        if mean_val < 85:   
            return "dark"
        if mean_val < 170:
            return "medium"
        return "light"
    
    def to_grayscale(self, img, method="weighted"):  
        b, g, r = cv2.split(img)
        if method == "weighted":
            return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if method == "average":
            return ((r + g + b) / 3).astype(np.uint8)
        if method == "max":
            return np.maximum(np.maximum(r, g), b)
        if method == "min":
            return np.minimum(np.minimum(r, g), b)
        if method == "luminosity":
            return (0.21 * r + 0.72 * g + 0.07 * b).astype(np.uint8)
        raise ValueError(f"Unknown method: {method}")

    def preprocess(self, img, params: PreprocessParams): 
        img = self.scale_img(img)

        detected_brightness = self.detect_background_brightness(img)

        method = params.gray_method

        if not params.custom:
            if detected_brightness == "light":
                method = "average"
            elif detected_brightness == "medium":
                method = "max"
            else:
                pass
        
        gray = self.to_grayscale(img, method)

        return gray, detected_brightness
    
    def local_variance(self, gray, ksize=9):
        mean = cv2.blur(gray.astype(np.float32), (ksize, ksize))
        sq_mean = cv2.blur((gray.astype(np.float32) ** 2), (ksize, ksize))
        return sq_mean - mean ** 2

    def detect(self, preprocessed: PreprocessedImage, params: DetectParams):
        img = preprocessed.img

        method = params.method
        ksize = params.ksize
        elemsize = params.elemsize
        th = params.th
        opac = params.opacity

        var_map = self.local_variance(img, ksize)
        var_norm = cv2.normalize(var_map, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        
        self.plot_histogram(var_norm)

        mask = None
        if not params.custom:
            brightness = preprocessed.img
            if brightness == "dark":
                pass
            if brightness == "medium":
                th = np.percentile(var_norm, 80) # en yüksek %20'yi al
                _, mask = cv2.threshold(var_norm, th, 255, cv2.THRESH_BINARY)

                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (elemsize, elemsize))
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)
            if brightness == "light":
                pass
        else:
            pass

        #visualize(original_img, mask)

    def visualize(self, img, mask=None, title="Mold Candidates Overlay"):
        display = img.copy()

        if mask is not None:
            _red = np.zeros_like(display)
            _red[:, :, 2] = 255
            display = cv2.addWeighted(display, 0.7, _red, 0.3, 0)
            display[mask==0] = img[mask==0]

        plt.figure(figsize=(10, 6))
        plt.axis('off')
        plt.title(title)
        plt.imshow(cv2.cvtColor(display, cv2.COLOR_BGR2RGB))
        plt.show()

    def plot_histogram(self, var_map):
        plt.figure(figsize=(6, 4))
        plt.hist(var_map.ravel(), bins=256, range=(0, 256))
        plt.title("Local Variance Histogram")
        plt.xlabel("Variance Value")
        plt.ylabel("Frequency")
        plt.show()
