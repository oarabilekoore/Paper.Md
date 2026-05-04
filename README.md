# PaperMd

## Purpose
PaperMd converts handwritten notes into structured Markdown or Typst documents. The system operates entirely locally. It is optimized for low-resource hardware, specifically dual-core processors like the Intel Celeron N4020 with 8GB of RAM.

## Architecture
The application is written in Go. It operates as a sequential pipeline to strictly control memory allocation. Go uses CGO to bind directly to system-level C++ libraries, preventing the memory overhead of spawning separate child processes. 

The pipeline modules include:

* Vision (internal/vision): Uses GoCV (OpenCV bindings) to apply adaptive thresholding and contour detection. This isolates text blocks, equations, and diagrams without requiring a neural network layout model.
* Text OCR (internal/ocr): Uses Gosseract (Tesseract C++ API bindings) to process standard text regions.
* Math OCR (internal/math): Uses the ONNX Runtime Go library to execute an INT8 quantized Pix2Tex model. This isolates heavy inference strictly to equation bounding boxes.
* Document Generation (internal/markdown, internal/typst): Reconstructs the spatial layout of the parsed elements. It injects the strings and SVG data into native Markdown syntax or Typst markup.
