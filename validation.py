import argparse
import os

import cv2
import numpy as np
import matplotlib.pyplot as plt

import Processor


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


def load_mask(path, target_shape=None):
    mask = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if mask is None:
        raise FileNotFoundError(path)

    if target_shape is not None and (mask.shape[0], mask.shape[1]) != target_shape:
        mask = cv2.resize(mask, (target_shape[1], target_shape[0]), interpolation=cv2.INTER_NEAREST)

    return mask


def overlay_mask(image, mask, color=(0, 0, 255), alpha=0.3):
    base = image.copy()
    color_layer = np.zeros_like(base)
    color_layer[:] = color
    blended = cv2.addWeighted(base, 1 - alpha, color_layer, alpha, 0)
    output = base.copy()
    output[mask > 0] = blended[mask > 0]
    return output


def visualize_triplet(image, gt_mask, pred_mask, title=None):
    gt_overlay = overlay_mask(image, gt_mask, color=(0, 0, 255))
    pred_overlay = overlay_mask(image, pred_mask, color=(0, 255, 0))

    plt.figure(figsize=(14, 6))
    if title:
        plt.suptitle(title)

    plt.subplot(1, 3, 1)
    plt.title("Image")
    plt.axis("off")
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    plt.subplot(1, 3, 2)
    plt.title("Ground Truth")
    plt.axis("off")
    plt.imshow(cv2.cvtColor(gt_overlay, cv2.COLOR_BGR2RGB))

    plt.subplot(1, 3, 3)
    plt.title("Prediction")
    plt.axis("off")
    plt.imshow(cv2.cvtColor(pred_overlay, cv2.COLOR_BGR2RGB))

    plt.tight_layout()
    plt.show()


def evaluate_dataset(image_dir, mask_dir, start_idx, end_idx, img_ext, mask_ext, visualize=False, index=None):
    results = []

    for i in range(start_idx, end_idx + 1):
        img_path = os.path.join(image_dir, f"{i}{img_ext}")
        mask_path = os.path.join(mask_dir, f"{i}{mask_ext}")

        pred_mask = Processor.predict_mask(img_path)
        gt_mask = load_mask(mask_path, target_shape=pred_mask.shape[:2])

        score_iou = iou(pred_mask, gt_mask)
        results.append((i, score_iou))

        if visualize and (index is None or i == index):
            image = Processor.load_imgs(img_path)
            visualize_triplet(image, gt_mask, pred_mask, title=f"{i}: IoU={score_iou:.3f}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Validate mold detection against GT masks.")
    parser.add_argument("--visualize", action="store_true", help="Show overlays for each sample")
    parser.add_argument("--index", type=int, default=None, help="Only visualize a single index")

    args = parser.parse_args()

    results = evaluate_dataset(
        "./data",
        "./gt_masks",
        1,
        15,
        ".png",
        ".png",
        visualize=args.visualize,
        index=args.index,
    )

    ious = [r[1] for r in results]

    for idx, s_iou in results:
        print(f"{idx}: IoU={s_iou:.3f}")

    print(f"Mean IoU: {np.mean(ious):.3f}")
    if not args.visualize:
        print("(Execute command \"python3 validation.py --visualize\" to see overlay masks)")


if __name__ == "__main__":
    main()
