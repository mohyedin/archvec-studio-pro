"""
Unit tests for ArchVec v11 Pipeline.
"""

import unittest
import numpy as np
import os
import ezdxf
import io

from ArchVec_v11.engine.super_res import SuperResEnhancer
from ArchVec_v11.engine.ink_extractor import InkExtractor
from ArchVec_v11.engine.vectorizer import Vectorizer
from ArchVec_v11.engine.scale_calibrator import ScaleCalibrator
from ArchVec_v11.engine.dxf_exporter import DXFExporter


class TestArchVecV11Pipeline(unittest.TestCase):
    def setUp(self):
        # Create a synthetic 100x100 white canvas with a black rectangle
        self.canvas = np.full((100, 100, 3), 255, dtype=np.uint8)
        self.canvas[20:80, 20:80] = 0  # Black square
        self.canvas[30:70, 30:70] = 255  # Hollow inside (wall)

    def test_super_resolution(self):
        enhancer = SuperResEnhancer(scale=2)
        enhanced = enhancer.enhance(self.canvas)
        self.assertEqual(enhanced.shape[:2], (200, 200))

    def test_ink_extraction(self):
        extractor = InkExtractor(block_size=15, c_offset=5)
        mask = extractor.extract_ink_mask(self.canvas)
        self.assertEqual(mask.shape, (100, 100))
        self.assertTrue(np.any(mask == 255))
        self.assertTrue(np.any(mask == 0))

    def test_vectorization_and_ortho(self):
        extractor = InkExtractor(block_size=15, c_offset=5)
        mask = extractor.extract_ink_mask(self.canvas)
        vectorizer = Vectorizer(epsilon_px=1.0, ortho_tol_deg=5.0)
        polys = vectorizer.vectorize_outline(mask)
        self.assertGreaterEqual(len(polys), 1)

    def test_scale_calibrator(self):
        calibrator = ScaleCalibrator()
        # 100 px = 1.0 m -> 1 px = 0.01 m
        scale = calibrator.calibrate_from_reference_line((0, 0), (100, 0), 1.0)
        self.assertAlmostEqual(scale, 0.01, places=4)
        cad_pt = calibrator.transform_point_to_cad(50, 20, 100)
        self.assertEqual(cad_pt, (0.5, 0.8))

    def test_dxf_exporter(self):
        exporter = DXFExporter()
        polys = [[(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]]
        dxf_str = exporter.export(polygons_cad=polys, reference_info="Test")
        doc = ezdxf.read(io.StringIO(dxf_str))
        self.assertIsNotNone(doc)
        msp = doc.modelspace()
        polylines = msp.query('LWPOLYLINE[layer=="A-WALL"]')
        self.assertEqual(len(polylines), 1)


if __name__ == "__main__":
    unittest.main()
