"""
ArchVec v11: Vectorization Engine (Outline & Centerline with Ortho-Snapping).
Converts binary ink masks into clean geometric polylines and lines.
"""

from typing import List, Tuple, Dict, Any
import math
import cv2
import numpy as np
from skimage.morphology import skeletonize


class Vectorizer:
    def __init__(self, epsilon_px: float = 1.8, ortho_tol_deg: float = 4.0, min_area: float = 12.0):
        self.epsilon_px = epsilon_px
        self.ortho_tol_deg = ortho_tol_deg
        self.min_area = min_area

    def vectorize_outline(self, binary_mask: np.ndarray) -> List[np.ndarray]:
        """
        Extracts closed contour polygons and applies Douglas-Peucker simplification + Ortho snapping.
        """
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        polygons = []

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < self.min_area:
                continue

            approx = cv2.approxPolyDP(cnt, epsilon=self.epsilon_px, closed=True)
            if len(approx) >= 3:
                pts = approx[:, 0, :]
                rectified = self._ortho_rectify_polygon(pts)
                polygons.append(rectified)

        return polygons

    def vectorize_centerline(self, binary_mask: np.ndarray) -> List[Tuple[Tuple[float, float], Tuple[float, float]]]:
        """
        Extracts 1-pixel skeleton and detects straight centerline segments.
        """
        skel = (skeletonize(binary_mask > 0).astype(np.uint8)) * 255
        lines = cv2.HoughLinesP(
            skel,
            rho=1,
            theta=np.pi / 180.0,
            threshold=18,
            minLineLength=10,
            maxLineGap=4
        )

        segments = []
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                p1, p2 = self._ortho_rectify_line((float(x1), float(y1)), (float(x2), float(y2)))
                segments.append((p1, p2))

        return segments

    def _ortho_rectify_line(
        self,
        p1: Tuple[float, float],
        p2: Tuple[float, float]
    ) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        x1, y1 = p1
        x2, y2 = p2
        dx = x2 - x1
        dy = y2 - y1
        ang = (math.degrees(math.atan2(dy, dx)) + 360.0) % 180.0

        if ang < self.ortho_tol_deg or ang > (180.0 - self.ortho_tol_deg):
            avg_y = (y1 + y2) / 2.0
            return (x1, avg_y), (x2, avg_y)
        elif abs(ang - 90.0) < self.ortho_tol_deg:
            avg_x = (x1 + x2) / 2.0
            return (avg_x, y1), (avg_x, y2)

        return (x1, y1), (x2, y2)

    def _ortho_rectify_polygon(self, pts: np.ndarray) -> np.ndarray:
        snapped = []
        n = len(pts)
        for i in range(n):
            p1 = pts[i].astype(float)
            p2 = pts[(i + 1) % n].astype(float)
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            ang = (math.degrees(math.atan2(dy, dx)) + 360.0) % 180.0

            if ang < self.ortho_tol_deg or ang > (180.0 - self.ortho_tol_deg):
                p2[1] = p1[1]
            elif abs(ang - 90.0) < self.ortho_tol_deg:
                p2[0] = p1[0]

            snapped.append(p1)

        return np.array(snapped, dtype=float)
