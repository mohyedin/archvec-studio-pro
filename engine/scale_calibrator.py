"""
ArchVec v11: Single-Reference Metric Scale Calibrator.
Transforms pixel vectors into real-world 1:1 metric CAD coordinates.
"""

from typing import Tuple, List
import math
import numpy as np


class ScaleCalibrator:
    def __init__(self, scale_m_per_px: float = 0.015):
        self.scale_m_per_px = scale_m_per_px

    def calibrate_from_reference_line(
        self,
        pt1_px: Tuple[float, float],
        pt2_px: Tuple[float, float],
        real_length_m: float
    ) -> float:
        """
        Calculates scale factor (meters per pixel) from two points and known real-world length.
        """
        dx = pt2_px[0] - pt1_px[0]
        dy = pt2_px[1] - pt1_px[1]
        dist_px = math.hypot(dx, dy)

        if dist_px < 1e-4:
            raise ValueError("Reference points are too close to compute valid scale.")

        self.scale_m_per_px = real_length_m / dist_px
        return self.scale_m_per_px

    def transform_point_to_cad(self, x_px: float, y_px: float, img_height_px: float) -> Tuple[float, float]:
        """
        Converts raster pixel (origin top-left, Y downwards)
        to CAD metric coordinates (origin bottom-left, Y upwards, in meters).
        """
        cad_x = x_px * self.scale_m_per_px
        cad_y = (img_height_px - y_px) * self.scale_m_per_px
        return (cad_x, cad_y)

    def transform_polygon_to_cad(self, polygon_px: np.ndarray, img_height_px: float) -> List[Tuple[float, float]]:
        return [
            self.transform_point_to_cad(pt[0], pt[1], img_height_px)
            for pt in polygon_px
        ]
