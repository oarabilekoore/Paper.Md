# Research Findings: Document Layout Analysis
**Project:** PaperMd  
**Date:** May 7th 2026  

This report documents the investigative phase of **PaperMd**, focusing on the segmentation of handwritten technical notes. I utilized **Gemini** to assist in drafting, debugging, and iterating upon the Python scripts used for these experiments.

## 1. Summary of Experimental Findings
I systematically tested several automated approaches to identify paragraphs, equations, and diagrams within my notebooks. The following table summarizes why standard tools failed to meet the requirements of the project:

| Approach | Technology | Result | Core Failure Reason |
| :--- | :--- | :--- | :--- |
| **Deep Learning** | LayoutParser (EfficientDet) | **FAIL** | Model was trained on digital academic PDFs; it could not handle handwritten variance and misclassified the entire page as a table. |
| **Heuristic CV** | OpenCV (Threshold/Canny) | **FAIL** | Highly brittle to lighting and ruled lines. It either broke text into individual letters or missed light ink entirely. |
| **Engine Segmentation** | Tesseract (Leptonica) | **PARTIAL** | Most stable classical method, but inconsistent line spacing caused it to fragment single paragraphs into multiple lines. |



## 2. Experimental Artifacts
The following images from the `test_data/` directory represent the evolution of the detection logic and the specific failure modes encountered:

* **Heuristic Attempt:** `output_heuristic_tuned.jpg` - Demonstrated excessive word-level fragmentation despite kernel tuning.
* **Edge Analysis:** `output_edges_v5.jpg` - Failed to maintain block integrity across mathematical symbols and handwriting gaps.
* **Tesseract Blocks:** `output_tesseract_blocks.jpg` - The most accurate classical result, though it still lacks the robustness required for a production-grade AST.

## 3. The Technical Pivot: Custom YOLO Training
To achieve the goal of a fully **offline**, **open-access**, and **performant** tool on low-end hardware (Intel Celeron), I am shifting away from pre-trained generic models and hardcoded heuristics. 

### The Strategy
1. **Manual Labeling:** I will use **Label Studio** to annotate my own notes, teaching a model to recognize my specific style of headings, equations, and diagrams.


2. **YOLO Nano Architecture:** I am targeting the **YOLOv8/11 Nano** model. This architecture is specifically optimized for Edge computing and can run entirely offline via ONNX.

3. **Cloud-to-Local Pipeline:** Training will be conducted on a cloud GPU (Google Colab) due to local hardware limitations, with the resulting weights exported to a local `.onnx` file for production use.


4. **Structured AST:** By training a custom model, the application will accurately pipe specific regions to specialized processors—such as passing math equations to LaTeX-OCR—while maintaining global coordinates to preserve original spacing.

## 4. Conclusion
Classical computer vision and generic OCR segmentation are insufficient for the complexity of handwritten technical notes. The custom machine learning route ensures that PaperMd remains lightweight and functional without relying on external APIs or sacrificing accuracy.

***
