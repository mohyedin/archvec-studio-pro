# ArchVec Studio 🏛️📐
### AI & Geometric Raster Floor Plan to Metric AutoCAD (DXF) Vectorizer

ArchVec Studio transforms low-resolution, rasterized, or scanned 2D floor plans into **clean, layered, Autodesk-compliant metric DXF files** with 1:1 real-world scaling.

---

## 🚀 Key Features

- **Waifu2x Super-Resolution & Denoising**: Upscales images 2x/4x and cleans JPEG compression artifacts.
- **100% Ink Extraction**: Isolates black architectural lines and strips paper/white backgrounds.
- **Continuous Contour Vectorization**: Extracts both outer structural boundaries and inner room cavities using Moore-Neighbor contour tracing + Douglas-Peucker simplification.
- **Automatic Semantic Layer Separation**:
  - `A-WALL` (Cyan/White): Structural walls, partitions, and openings.
  - `A-FURN` (Orange): Furniture, kitchen cabinets, stove, sink, sanitary fixtures, and beds.
  - `A-DIMS` (Red): Dimension leader lines and tick marks.
  - `A-ANNO` (Green): Native editable AutoCAD `TEXT` annotations (room labels and metric areas).
- **Ghost Text Erasure**: Automatically removes rasterized letter outlines beneath text to prevent overlapping double rendering.
- **Single-Reference Metric Scale Calibration**: Measure any known wall line (e.g. 5.37m) to scale the entire CAD drawing to 1:1 real-world metric dimensions.
- **Autodesk-Compliant DXF Export**: Compatible with AutoCAD 2000–2026, Revit, Rhino, and Autodesk Viewer (`viewer.autodesk.com`).

---

## 💻 Tech Stack
- Pure HTML5 / Canvas / WebAssembly / Vanilla JavaScript (zero server cold starts)
- Python Engine (`ezdxf`, `opencv-python`, `numpy`) for batch CLI processing
- Deployment: Vercel Static Hosting

---

## 📄 License
MIT License. Created by @mohyedin.
