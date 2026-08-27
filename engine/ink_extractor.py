"""
ArchVec v11: Clean Ink Extraction & Background Removal Engine.
Extracts pure black/gray architectural lines and discards paper textures.
"""

import cv2
import numpy as np


class InkExtractor:
    def __init__(self, block_size: int = 21, c_offset: int = 8, min_speckle_area: int = 6):
        self.block_size = block_size if block_size % 2 == 1 else block_size + 1
        self.c_offset = c_offset
        self.min_speckle_area = min_speckle_area

    def extract_ink_mask(self, img_bgr: np.ndarray) -> np.ndarray:
        """
        Converts image to grayscale, applies adaptive thresholding,
        and filters out tiny dust/speckles.
        Returns uint8 binary mask (ink=255, background=0).
        """
        if len(img_bgr.shape) == 3:
            gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        else:
            gray = img_bgr.copy()

        # 1. Adaptive Gaussian Thresholding
        binary = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            self.block_size,
            self.c_offset
        )

        # 2. Filter floating dust / tiny specs
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
        clean_mask = np.zeros_like(binary)
        for i in range(1, num_labels):
            if stats[i, cv2.CC_STAT_AREA] >= self.min_speckle_area:
                clean_mask[labels == i] = 255

        return clean_mask
