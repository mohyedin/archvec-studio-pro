#!/usr/bin/env python3
"""
ArchVec v11: CLI Pipeline Runner (Raster to Metric CAD/DXF).
"""

import sys
import os
import argparse
import cv2

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from engine.super_res import SuperResEnhancer
from engine.ink_extractor import InkExtractor
from engine.vectorizer import Vectorizer
from engine.scale_calibrator import ScaleCalibrator
from engine.dxf_exporter import DXFExporter


def process_plan_to_dxf(
    input_image_path: str,
    output_dxf_path: str,
    real_ref_meters: float = 5.37,
    ref_pt1=(96, 492),
    ref_pt2=(476, 492),
    mode: str = "outline",
    scale_factor: int = 2
):
    print(f"================================================================")
    print(f"  ArchVec v11: Raster to Metric CAD Vectorization Pipeline")
    print(f"  Input: {input_image_path}")
    print(f"  Output: {output_dxf_path}")
    print(f"================================================================")

    if not os.path.exists(input_image_path):
        raise FileNotFoundError(f"Input file not found: {input_image_path}")

    img = cv2.imread(input_image_path)
    h, w = img.shape[:2]
    print(f"[1/5] Loaded image: {w}x{h} px")

    # Step 1: Super-Resolution / Neural Sharpening
    print("[2/5] Running Super-Resolution & Denoising...")
    enhancer = SuperResEnhancer(scale=scale_factor, denoise_strength=45)
    enhanced = enhancer.enhance(img)
    eh, ew = enhanced.shape[:2]

    # Step 2: Clean Ink Extraction
    print("[3/5] Extracting clean ink lines & removing background...")
    extractor = InkExtractor(block_size=21, c_offset=8, min_speckle_area=6)
    ink_mask = extractor.extract_ink_mask(enhanced)

    # Step 3: Vectorization & Ortho Snapping
    print(f"[4/5] Vectorizing in '{mode}' mode with Ortho-Snapping...")
    vectorizer = Vectorizer(epsilon_px=1.8, ortho_tol_deg=4.0, min_area=12.0)
    
    polys_cad = []
    lines_cad = []

    # Step 4: Metric Calibration
    calibrator = ScaleCalibrator()
    scaled_pt1 = (ref_pt1[0] * scale_factor, ref_pt1[1] * scale_factor)
    scaled_pt2 = (ref_pt2[0] * scale_factor, ref_pt2[1] * scale_factor)
    scale_m_per_px = calibrator.calibrate_from_reference_line(scaled_pt1, scaled_pt2, real_ref_meters)
    print(f"      Calibrated Metric Scale: {scale_m_per_px:.5f} meters/pixel (1 px = {scale_m_per_px*1000:.2f} mm)")

    if mode in ("outline", "both"):
        polygons_px = vectorizer.vectorize_outline(ink_mask)
        print(f"      Extracted {len(polygons_px)} clean closed polygons.")
        for p in polygons_px:
            polys_cad.append(calibrator.transform_polygon_to_cad(p, eh))

    if mode in ("centerline", "both"):
        segments_px = vectorizer.vectorize_centerline(ink_mask)
        print(f"      Extracted {len(segments_px)} centerline segments.")
        for p1, p2 in segments_px:
            cad_p1 = calibrator.transform_point_to_cad(p1[0], p1[1], eh)
            cad_p2 = calibrator.transform_point_to_cad(p2[0], p2[1], eh)
            lines_cad.append((cad_p1, cad_p2))

    # Step 5: DXF Export
    print(f"[5/5] Exporting metric AutoCAD DXF to {output_dxf_path}...")
    exporter = DXFExporter()
    ref_info = f"ArchVec v11 | Ref: {real_ref_meters}m | Scale: 1px = {scale_m_per_px*1000:.2f}mm"
    dxf_content = exporter.export(polygons_cad=polys_cad, lines_cad=lines_cad, reference_info=ref_info)
    exporter.save_file(dxf_content, output_dxf_path)

    print(f"✅ SUCCESS: Exported clean metric CAD file ({os.path.getsize(output_dxf_path)/1024:.1f} KB)")
    return output_dxf_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ArchVec v11 CLI Pipeline")
    parser.add_argument("input", help="Path to input floor plan image")
    parser.add_argument("-o", "--output", default="output.dxf", help="Path to output DXF file")
    parser.add_argument("--ref-len", type=float, default=5.37, help="Real length of reference line in meters")
    parser.add_argument("--mode", choices=["outline", "centerline", "both"], default="outline", help="Vectorization mode")
    
    args = parser.parse_args()
    process_plan_to_dxf(args.input, args.output, real_ref_meters=args.ref_len, mode=args.mode)
