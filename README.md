# PaperMd

![Status](https://img.shields.io/badge/Status-Active_Development-green)
![Stage](https://img.shields.io/badge/Stage-Dataset_Annotation-blue)
![Architecture](https://img.shields.io/badge/Model-YOLOv11_Nano-orange)

PaperMd is a local-first, offline pipeline that converts photographs of handwritten notes into structured digital documents. A photo of a notebook page goes in — a clean, formatted, editable document comes out.

The core thesis is that layout understanding and handwriting recognition are two separate problems that must be solved independently before they can be composed. PaperMd solves them in sequence.

---

## The Problem

Existing document AI is trained on digital PDFs and typed text. It fails on handwriting because handwriting has no implicit grid — ascenders and descenders from adjacent lines overlap in pixel space, ink color varies, ruled lines interfere, and no two people's spatial conventions are the same. Generic tools like LayoutParser and DocLayout-YOLO misclassify entire handwritten pages as a single figure. Tesseract fragments paragraphs into individual lines. There is no production-grade open tool that handles this correctly.

PaperMd is being built to solve this specifically and locally, with no external API dependencies.

---

## Current Status

**Phase: Dataset Annotation — Batch 1 (50 images)**

The first training batch is being annotated in Label Studio using the class schema below. A proof-of-concept model trained on 61 images (earlier label schema) already detects figures at 0.88 confidence and equations at 0.41–0.66 confidence. Equation fragmentation is the primary known issue and is being addressed through annotation consistency rules in this batch.

Target for v1 release: 300+ annotated images across diverse handwriting styles, subjects, and capture conditions.

---

## Label Schema

The following classes are used for layout annotation in Label Studio:

| ID | Class | Description |
|---|---|---|
| 1 | `Abandon` | Crossed-out or cancelled content. Box tightly around the strikethrough only. |
| 2 | `Title` | Page or section title. Typically larger, centred, or isolated at the top. |
| 3 | `Heading` | Sub-section heading. Bolded, underlined, or spatially separated from body text. |
| 4 | `Plain_Text` | Body paragraph. One box per contiguous paragraph block regardless of line count. |
| 5 | `Formula` | Any mathematical expression, equation, or symbolic notation. One box per contiguous equation block — never one box per line. |
| 6 | `Figure` | Any visual content: diagrams, graphs, sketches, free body diagrams, circuit drawings. |
| 7 | `Caption` | Label or description associated with a Figure. Always annotated separately from the Figure. |
| 8 | `Table` | Tabular data with visible or implied grid structure. |
| 9 | `List` | Bulleted or numbered list. One box around the full list including all items. |
| 0 | `Date` | Date field, typically top-right corner of a notebook page. |

### Annotation Rules

- **Formula boxes span the full block** — if three lines form one equation, one box covers all three. Fragmentation into per-line boxes is the single most common annotation error and directly causes fragmented inference.
- **Plain_Text containing inline math is still Plain_Text** — a sentence like "where n is the number of values" is `Plain_Text`. The formula `Mean(x̄) = Σx/n` on its own line is `Formula`.
- **Lists are not Plain_Text** — any content with bullet points (`•`, `-`, `*`) or numbered items (`①`, `1.`, `(a)`) is `List`.
- **Code blocks are Plain_Text** — handwritten code (Python, pseudocode) is annotated as `Plain_Text` unless a separate `Code` class is added in a future iteration.
- **Boxes are consistently loose** — due to ascender/descender overlap between handwritten lines, boxes will clip adjacent ruled lines. This is acceptable. Consistent loose boxes across all images are better than inconsistently tight ones.
- **Minimum annotation size** — do not annotate content smaller than approximately 20×20px at normalized resolution. Stray marks, marginalia, and partial characters at page edges are ignored.

---

## System Architecture

PaperMd executes a two-stage pipeline.

### Stage 1 — Layout Detection (Model 1)

A custom YOLOv11 Nano model segments the page into discrete content blocks and classifies each into the schema above. YOLO Nano is chosen specifically for its edge-computing profile — it runs entirely offline via ONNX export on low-end hardware including Intel Celeron.

**Training pipeline:**
1. Images annotated in Label Studio (YOLO format export)
2. Model trained on Google Colab (GPU)
3. Weights exported to `.onnx` for local inference

**Known challenges:**
- Handwriting has no implicit grid — interleaved ascenders/descenders make bounding boxes inherently imprecise for text regions
- Dataset diversity across handwriting styles is critical for generalization and requires contributions beyond the author's own notes (see Contributing below)
- Minimum viable dataset: 300 annotated images. Target for generalization: 1000+

### Stage 2 — Content Extraction

Each detected region is cropped and routed to a specialist extractor based on its class:

| Class | Extractor |
|---|---|
| `Plain_Text`, `Heading`, `Title`, `List`, `Caption` | TrOCR (`microsoft/trocr-base-handwritten`) |
| `Formula` | LaTeX-OCR (Pix2Tex) |
| `Figure` | Preserved as image crop in output (v1). Subclassification model in v2. |
| `Table` | TrOCR per cell (v2) |
| `Date` | TrOCR |
| `Abandon` | Discarded |

### Output

Extracted content and spatial coordinates are serialized into a JSON AST preserving reading order. This is compiled to Markdown for v1, with Typst and DOCX targets planned for later versions.

---

## Roadmap

### v1 — Core Pipeline (Current)
- [x] Research phase: pre-trained model evaluation
- [x] Architecture decision: custom YOLOv11 Nano
- [x] Proof of concept: 61-image model, figure detection working
- [ ] Annotation Batch 1: 50 images
- [ ] Annotation Batch 2: 100 images (targeting diverse handwriting)
- [ ] First full training run with stable annotation schema
- [ ] TrOCR integration for Plain_Text crops
- [ ] LaTeX-OCR integration for Formula crops
- [ ] JSON AST schema and Markdown export
- [ ] TypeScript inference pipeline via `onnxruntime-node`

### v2 — Extended Content
- [ ] Figure subclassification model (circuit, graph, flowchart, diagram)
- [ ] Table cell extraction
- [ ] Inline annotation model (underlines, highlights, strikethroughs, inline math)
- [ ] Typst and DOCX export targets
- [ ] Editor integration (block-based web editor)

### v3 — Generalization
- [ ] Multi-language handwriting support
- [ ] Scan input support (flatbed scanner pipeline)
- [ ] Public dataset release

---

## Research Log

Detailed findings from the investigative phase are documented here:

- **[Research Findings: Layout Analysis](./research/Research_Findings_Layout_Analysis.md)** — Why LayoutParser, OpenCV heuristics, and Tesseract segmentation all failed on handwritten notes, and the decision to train a custom model.
- **[Research Findings: YOLOv11 Nano Inference Analysis and Data Normalization Protocols](./research/Research_Findings_YOLOv11_Nano_Inference_Analysis_and_Data_Normalization_Protocols.md)** — Analysis of the first 24-image inference run, failure modes, confidence score distribution, and data normalization requirements.

---

## Contributing

PaperMd's model quality is directly limited by dataset diversity. A model trained only on one person's handwriting will fail on everyone else's.

**We are actively collecting handwritten note images.**

What we need:
- Photos of handwritten notes in any subject — math, science, engineering, humanities, anything
- Any pen, pencil, or writing instrument
- Any notebook type — ruled, blank, grid, dotted
- Neat or messy — messy notes are actually more valuable for robustness

What we do with them:
- Images are used exclusively to train and evaluate the layout detection model
- Nothing will be published, shared, or used outside this project
- Contributors who want credit will be listed in this repository

To contribute, open an issue tagged `dataset-contribution` or contact the maintainer directly.

---

## Development Setup

**Training (Google Colab):**
[Colab Training Script](https://colab.research.google.com/drive/1dAh-BjzS0RTTE1kF7Bv_9cwfVaie_BeL?usp=sharing)

**Local inference (TypeScript):**
```bash
npm install onnxruntime-node
```

```typescript
import * as ort from 'onnxruntime-node';
const session = await ort.InferenceSession.create('./weights/papermd-layout.onnx');
```

---

## Hardware Target

PaperMd is designed to run on consumer hardware without a GPU. The reference development machine is an Intel Celeron N4020 with 8GB RAM running CachyOS Linux. If it runs well there, it runs well everywhere.