# PaperMd

![WIP](https://img.shields.io/badge/Status-Work_in_Progress-orange)
![Architecture](https://img.shields.io/badge/Architecture-YOLO_Custom-blue)

PaperMd is a local-first document processing pipeline designed to extract structured data from handwritten technical manuscripts. It serializes image data into a JSON-based Abstract Syntax Tree (AST), mapping physical document architecture to digital components for integration with block-based web editors. This enables local compilation to formats such as PDF, DOCX, and Typst.

## Current Research Status
Recent experiments with pre-trained layout models and heuristic computer vision proved insufficient for handwritten technical notes. The project has pivoted to a custom-trained machine learning architecture to handle the specific complexities of mathematical formulas and diagrams.

Detailed documentation of these experiments and the resulting technical shift can be found in the research log:
* **[Research Findings: Layout Analysis](./research/Research_Findings_Layout_Analysis.md)**

## System Architecture
The pipeline executes a sequential workflow optimized for edge hardware:

1.  **Layout Analysis (YOLO):** A custom-trained YOLOv11 Nano model segments the document into discrete functional blocks (headings, paragraphs, math, and diagrams). This model is exported to ONNX for local, offline inference.
2.  **Specialized Processing:** Segmented blocks are routed based on classification:
    * **Text/Headings:** Processed via Tesseract OCR.
    * **Mathematical Formulas:** Processed via specialized LaTeX-OCR models.
    * **Diagrams:** Analyzed via contour approximation for vectorization.
3.  **Data Serialization:** Extracted elements, spatial coordinates, and classifications are serialized into a strict JSON schema that preserves the original document's spatial integrity.

## Tech Stack
* **Internal Processing:** Python (OpenCV, Ultralytics, PyTesseract).
* **Web Interface:** TypeScript, React, and Bun.
* **Inference Engine:** ONNX Runtime for local CPU execution.
