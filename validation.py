import numpy as np

def iou(mask_pred, mask_gt):
    # make sure masks are binary
    p = (mask_pred > 0).astype(np.uint8)
    g = (mask_gt > 0).astype(np.uint8)

    # Intersection: both predicted and ground truth masks are 1
    intersection = np.logical_and(p, g).sum()

    # Union: either predicted or ground truth or both are 1
    union = np.logical_or(p, g).sum()

    if union == 0:
        # if theres no mold in the image and no mold predicted IoU is 1
        if intersection == 0:
            return 1.0
        # if theres no mold in the image but mold is predicted IoU is 0
        else:
            return 0.0
        
    return intersection / union
    union = np.logical_or(p, g).sum()