# PaperMd

![WIP](https://img.shields.io/badge/Status-Work_in_Progress-orange)
![Architecture](https://img.shields.io/badge/Architecture-Experimental-red)

PaperMd is a document processing pipeline designed to extract structured data from 
hand-written notes. It converts scanned manuscript images into a JSON-based Abstract Syntax Tree (AST) -- it is to be implemented and discussed. This format maps physical document architecture to digital components for integration with block-based web editors and allows for compilation to other document formats like pdf,docx and typst.

# System Architecture
The pipeline executes sequential computer vision and machine learning operations:

Image Preprocessing: Heuristic contour detection isolates document boundaries from the background.

Layout Analysis: Object detection models (e.g., LayoutParser, YOLOv8) segment the document image into discrete functional blocks. These blocks are classified into types such as headings, standard text, mathematical formulas, and diagrams.

Optical Character Recognition (OCR): Tesseract processes the segmented bounding boxes to extract textual data.

Data Serialization: The extracted elements and their associated classifications, spatial coordinates, and confidence scores are serialized into a strict JSON schema.

## Languages 

I will be using python for all internal processing. Typescript, React on Bun will be used for the web interface.
