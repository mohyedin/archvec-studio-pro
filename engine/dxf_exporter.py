"""
ArchVec v11: Professional AIA Layered DXF Exporter.
Exports metric AutoCAD DXF files (R2010) with clean layers.
"""

from typing import List, Tuple, Optional
import io
import math
import numpy as np
import ezdxf
from ezdxf.enums import TextEntityAlignment


class DXFExporter:
    def __init__(self):
        pass

    def export(
        self,
        polygons_cad: Optional[List[List[Tuple[float, float]]]] = None,
        lines_cad: Optional[List[Tuple[Tuple[float, float], Tuple[float, float]]]] = None,
        reference_info: Optional[str] = None
    ) -> str:
        """
        Generates standard AutoCAD R2010 DXF document string.
        """
        doc = ezdxf.new("R2010")
        msp = doc.modelspace()

        # Setup standard AIA CAD layers
        layers = [
            ("A-WALL", 7, "Continuous"),        # White/Black
            ("A-CENTERLINE", 3, "Continuous"),  # Green
            ("A-DIMS", 1, "Continuous"),        # Red
            ("A-ANNO", 6, "Continuous")         # Magenta
        ]

        for name, color, linetype in layers:
            if name not in doc.layers:
                doc.layers.add(name=name, color=color, linetype=linetype)

        # 1. Export Outline Polygons (A-WALL)
        if polygons_cad:
            for poly in polygons_cad:
                if len(poly) >= 3:
                    msp.add_lwpolyline(poly, close=True, dxfattribs={"layer": "A-WALL"})

        # 2. Export Centerline Segments (A-CENTERLINE)
        if lines_cad:
            for p1, p2 in lines_cad:
                msp.add_line(p1, p2, dxfattribs={"layer": "A-CENTERLINE"})

        # 3. Reference Annotation
        if reference_info:
            msp.add_text(
                reference_info,
                dxfattribs={"layer": "A-ANNO", "height": 0.30}
            ).set_placement((0, -1.0), align=TextEntityAlignment.LEFT)

        stream = io.StringIO()
        doc.write(stream)
        return stream.getvalue()

    def save_file(self, dxf_string: str, filepath: str) -> str:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(dxf_string)
        return filepath
