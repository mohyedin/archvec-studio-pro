"""
ArchVec v11: Super-Resolution & Denoising Engine.
Enhances line sharpness, removes JPEG artifacts, and scales up 2x/4x.
"""

import cv2
import numpy as np
import os
import subprocess


class SuperResEnhancer:
    def __init__(self, scale: int = 2, denoise_strength: int = 50):
        self.scale = scale
        self.denoise_strength = denoise_strength

    def enhance(self, img_bgr: np.ndarray) -> np.ndarray:
        """
        Enhances raster floor plan with high-order Lanczos interpolation,
        edge-preserving bilateral smoothing, and unsharp masking.
        """
        h, w = img_bgr.shape[:2]
        target_w = w * self.scale
        target_h = h * self.scale

        # 1. High-fidelity Lanczos4 Upscaling
        upscaled = cv2.resize(img_bgr, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4)

        # 2. Edge-Preserving Bilateral Denoising
        denoised = cv2.bilateralFilter(
            upscaled,
            d=9,
            sigmaColor=self.denoise_strength,
            sigmaSpace=self.denoise_strength
        )

        # 3. Unsharp Masking for Sharp Architectural Inks
        gaussian = cv2.GaussianBlur(denoised, (0, 0), sigmaX=2.0)
        sharpened = cv2.addWeighted(denoised, 1.5, gaussian, -0.5, 0)

        return sharpened
