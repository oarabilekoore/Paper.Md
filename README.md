# PaperMd

![WIP](https://img.shields.io/badge/Status-Work_in_Progress-orange)
![Architecture](https://img.shields.io/badge/Architecture-YOLO_Custom-blue)

PaperMd is a local-first document processing pipeline designed to extract structured data from handwritten technical manuscripts. It serializes image data into a JSON-based Abstract Syntax Tree (AST), mapping physical document architecture to digital components for integration with block-based web editors. This enables local compilation to formats such as PDF, DOCX, and Typst.

## Current Research Status
Recent experiments with pre-trained layout models and heuristic computer vision proved insufficient for handwritten technical notes. The project has pivoted to a custom-trained machine learning architecture to handle the specific complexities of mathematical formulas and diagrams.

Detailed documentation of these experiments and the resulting technical shift can be found in the research log:
* **[Research Findings: Layout Analysis](./research/Research_Findings_Layout_Analysis.md)**

* **[Research Findings: YOLOv11 Nano Inference Analysis and Data Normalization Protocols](./research/Research_Findings_YOLOv11_Nano_Inference_Analysis_and_Data_Normalization_Protocols.md)**
* 
## System Architecture
The pipeline executes a sequential workflow optimized for varying hardware profiles.

1. **Layout Analysis (YOLO):** A custom-trained YOLOv11 model segments the document into discrete functional blocks.
2. **Specialized Processing:** Segmented blocks are routed based on classification:
   * **Text/Headings:** Processed via Tesseract OCR following OpenCV binarization and noise reduction. OpenCV color thresholding and Hough Line Transform algorithms identify highlighted and underlined text to apply structural emphasis syntax.
   * **Mathematical Formulas:** Processed via the secondary custom model for structural mapping prior to specialized extraction.
   * **Diagrams:** Processed via the tertiary model and heuristic algorithms for conversion to vector geometry and Mermaid syntax.
3. **Data Serialization:** Extracted elements, spatial coordinates, and classifications are serialized into a strict JSON schema.

### Layout Analysis 

I have decided to start training an ML model to improve layout analysis. Which will be based on YoloV11 Nano.
Currently is setup for training on a custom dataset of handwritten technical notes.
And I plan on training it on a larger, more diverse dataset in the future, for now here is the plan to train two different models:

- Train a custom YOLOv11 Nano model on a handwritten technical notes dataset, first I am using label-studio to annotate the dataset and then use Google Colab to train the model. This initial model will be used to output the following segments:
  1. Heading
  2. Equation
  3. Diagram (This is a form of visual content, like a flowchart or mind map)
  4. Figure (This is a form of visual content, like an image or graph)
  5. Cancellation (cancelled text blocks)
  6. Table
  7. List
  8. Date
  9. Paragraph



- A second processing component targets block diagrams and flowcharts. It detects geometric nodes, directional edges and hand drawn shapes. Heuristic algorithms calculate spatial intersections to map relational text and construct Mermaid graph syntax.

## Tech Stack
* **Internal Processing:** Python (OpenCV, Ultralytics, PyTesseract).
* **Data Parsing:** TypeScript, and Bun.
* **Inference Engine:** ONNX Runtime for local CPU execution.
