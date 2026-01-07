from ..defs import PreprocessParams, DetectParams
from ..state import ImageState

import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage.feature import local_binary_pattern


class Processor:
    def __init__(self):
        self.preprocess_params = PreprocessParams()
        self.detect_params = DetectParams()
    

    def preprocess(self, img_st: ImageState): 
        img = img_st.original
        if img is None: return
        img = self._scale_img(img)
        gray = self._to_grayscale(img, img_st.preprocess_params.gray_method)
        texture = self._detect_background_texture(gray)
        return gray, texture
        

    def detect(self, img_st: ImageState):
        method = img_st.detect_params.method

        if not img_st.detect_params.custom:
            return self._detect_auto(img_st)
        
        if method == "variance":
            return self._detect_var(img_st)
        if method == "adaptive":
            return self._detect_adap(img_st)
        if method == "edge":
            return self._detect_edge(img_st)
        if method == "saturation":
            return self._detect_satur(img_st)
        if method == "var_lbp":
            return self._detect_var_lbp(img_st)
        
        raise ValueError("Unknown detection method")
    

    def show_variance_histogram(self, img_st: ImageState):
        var_map = self._calc_variance_map(img_st.preprocessed.img, img_st.detect_params.ksize)
        if var_map is not None:
            self._plot_histogram(var_map, img_st.detect_params.th)
    

    def _analyze_img(self, img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        v = hsv[:, :, 2]
        s = hsv[:, :, 1]

        return {
            "mean_v": float(np.mean(v)),
            "std_v": float(np.std(v)),
            "mean_s": float(np.mean(s))
        }
    

    def _detect_auto(self, img_st: ImageState):
        # Default strategy: Variance based
        # We can expand this to pick strategies based on texture/brightness
        img_st.auto_info = "Auto: Variance Method"
        return self._detect_var(img_st)


    def _detect_var(self, img_st: ImageState):
        ksize = img_st.detect_params.ksize
        elemsize = img_st.detect_params.elemsize
        #th = img_st.detect_params.th
        #opac = img_st.detect_params.opacity

        gray = img_st.preprocessed.img
        txt = img_st.preprocessed.texture

        # decide kernel size
        if txt == "low_txt":    ksize = 7
        elif txt == "mid_txt":  ksize = 11
        else:                   ksize = 15

        var_norm = self._calc_variance_map(gray, ksize)     

        # stage 1: lenient candid detection
        th1 = np.percentile(var_norm, 80)
        mask1 = (var_norm > th1).astype(np.uint8) * 255

        # connected comp.s
        num, labels, stats, _ = cv2.connectedComponentsWithStats(mask1, connectivity=8)

        h, w = mask1.shape
        img_area = h * w
        final_mask = np.zeros_like(mask1)

        for i in range(1, num):
            area = stats[i, cv2.CC_STAT_AREA]

            if area < 0.0005 * img_area: continue
            if area > 0.25 * img_area: continue

            comp_mask = (labels == i).astype(np.uint8) * 255

            if txt in ("low_txt", "mid_txt"):
                lbp_ratio = self._lbp_uniform_ratio(gray, comp_mask)       
                # mold -> low uniformity
                if lbp_ratio > 0.8: continue

            final_mask[labels == i] = 255            

        # morphology
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (elemsize, elemsize))
        final_mask = cv2.morphologyEx(final_mask, cv2.MORPH_CLOSE, kernel, iterations=1)
        final_mask = cv2.morphologyEx(final_mask, cv2.MORPH_OPEN, kernel, iterations=1)

        # resize and overlay
        oh, ow = img_st.original.shape[:2]
        final_mask = cv2.resize(final_mask, (ow, oh), interpolation=cv2.INTER_NEAREST)

        detected_mold = self._apply_mask(img_st.original, final_mask)
        return detected_mold
    

    def _detect_adap(self, img_st: ImageState):
        pass


    def _detect_edge(self, img_st: ImageState):
        pass


    def _detect_var_lbp(self, img_st: ImageState):
        pass


    def _detect_satur(self, img_st: ImageState):
        pass

    def _scale_img(self, img, max_dim=1024):
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
    

    def _to_grayscale(self, img, method="weighted"):  
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

    
    def _detect_background_texture(self, gray, ksize=9):
        var_norm = self._calc_variance_map(gray, ksize)

        # histogram-based txt stats
        tail_ratio = np.sum(var_norm > 60) / var_norm.size

        if tail_ratio < 0.01:   
            return "low_txt"
        if tail_ratio < 0.04:
            return "mid_txt"
        return "high_txt"


    def _calc_variance_map(self, img, ksize=9):
        var_map = self._local_variance(img, ksize)     
        return cv2.normalize(var_map, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)


    def _local_variance(self, gray, ksize=9):
        mean = cv2.blur(gray.astype(np.float32), (ksize, ksize))
        sq_mean = cv2.blur((gray.astype(np.float32) ** 2), (ksize, ksize))
        return sq_mean - mean ** 2
    
    
    def _lbp_uniform_ratio(self, gray, mask, rad=2, p=16):
        lbp = local_binary_pattern(gray, p, rad, method="uniform")

        region = lbp[mask > 0]
        if region.size == 0: return 0

        uniform = np.sum(region <= p)
        return uniform / region.size
    
    
    def _apply_mask(self, img:np.ndarray, mask=None):
        if img.ndim == 2:
            base_bgr = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        else:
            base_bgr = img.copy()

        display = base_bgr.copy()

        if mask is not None:
            _red = np.zeros_like(display)
            _red[:, :, 2] = 255
            display = cv2.addWeighted(display, 0.7, _red, 0.3, 0)
            display[mask==0] = base_bgr[mask==0]

        return display
    

    def _plot_histogram(self, var_map, curr_th):
        plt.figure(figsize=(6, 4))
        plt.hist(var_map.ravel(), bins=256, range=(0, 256), color='gray', alpha=0.7)
        plt.axvline(curr_th, color='r', linestyle='--', label=f"th={curr_th}")
        plt.legend()
        plt.title("Local Variance Histogram + Threshold")
        plt.xlabel("Variance Value")
        plt.ylabel("Frequency")
        plt.tight_layout()
        plt.show()