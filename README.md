# PaperMd

![Status](https://img.shields.io/badge/Status-Active_Development-green)
![Stage](https://img.shields.io/badge/Stage-Dataset_Annotation-blue)
![Architecture](https://img.shields.io/badge/Model-YOLOv11_Nano-orange)
![License: Model](https://img.shields.io/badge/Model_License-GPL--3.0-blue)
![License: App](https://img.shields.io/badge/App_License-BSL--1.1-orange)

PaperMd is a local-first, offline pipeline that converts photographs of handwritten notes into structured digital documents. A photo of a notebook page goes in — a clean, formatted, editable document comes out.

The core thesis is that layout understanding and handwriting recognition are two separate problems that must be solved independently before they can be composed. PaperMd solves them in sequence.

---

## The Problem

Existing document AI is trained on digital PDFs and typed text. It fails on handwriting because handwriting has no implicit grid — ascenders and descenders from adjacent lines overlap in pixel space, ink color varies, ruled lines interfere, and no two people's spatial conventions are the same. Generic tools like LayoutParser and DocLayout-YOLO misclassify entire handwritten pages as a single figure. Tesseract fragments paragraphs into individual lines. There is no production-grade open tool that handles this correctly.

PaperMd is being built to solve this specifically and locally, with no external API dependencies.

---

## Current Status

**Phase: Dataset Annotation — Batch 1 (50 images)**

The first training batch is being annotated in Label Studio using the class schema below. A proof-of-concept model trained on 61 images (earlier label schema) already detects figures at 0.88 confidence and equations at 0.41–0.66 confidence. Equation fragmentation is the primary known issue and is being addressed through annotation consistency rules in this batch. An active learning loop is in place — the current model pre-labels new images in Label Studio, which are then reviewed and corrected rather than annotated from scratch.

Target for v1 release: 300+ annotated images across diverse handwriting styles, subjects, and capture conditions.

---

## Label Schema

The following classes are used for layout annotation in Label Studio:

| ID | Class | Description |
|:---:|---|---|
| `1` | `Abandon` | Crossed-out or cancelled content |
| `2` | `Plain_Text` | Body paragraph, heading, title, or caption |
| `3` | `Formula` | Mathematical expression or equation |
| `4` | `Figure` | Diagram, graph, sketch, or any visual content |
| `5` | `List_Identifier` | Bullet point or list number marker only |
| `6` | `Table` | Tabular data with visible or implied grid structure |

### Annotation Rules

- **Formula boxes span the full block** — if three lines form one equation, one box covers all three. Fragmentation into per-line boxes is the single most common annotation error and directly causes fragmented inference.
- **Plain_Text containing inline math is still Plain_Text** — a sentence like "where n is the number of values" is `Plain_Text`. The formula `Mean(x̄) = Σx/n` on its own line is `Formula`.
- **List_Identifier marks the symbol only** — box tightly around the `•`, `-`, `①` etc. The text body of the list item is `Plain_Text`.
- **Code blocks are Plain_Text** — handwritten code or pseudocode is annotated as `Plain_Text`.
- **Boxes are consistently loose** — due to ascender/descender overlap between handwritten lines, boxes will clip adjacent ruled lines. This is acceptable. Consistent loose boxes across all images are better than inconsistently tight ones.
- **Minimum annotation size** — do not annotate content smaller than approximately 20×20px at normalized resolution. Stray marks and marginalia are ignored.

---

## System Architecture

PaperMd executes a three-stage pipeline.

### Stage 1 — Layout Detection (Model 1)

A custom YOLOv11 Nano model segments the page into discrete content blocks and classifies each into the schema above. YOLO Nano is chosen specifically for its edge-computing profile — it runs entirely offline via ONNX export on low-end hardware including Intel Celeron.

**Training pipeline:**
1. Images annotated in Label Studio (YOLO format export)
2. Active learning loop — current model pre-labels; human reviews and corrects
3. Model trained on Google Colab (GPU)
4. Weights exported to `.onnx` for local inference

**Known challenges:**
- Handwriting has no implicit grid — interleaved ascenders/descenders make bounding boxes inherently imprecise for text regions
- Dataset diversity across handwriting styles is critical for generalization and requires contributions beyond the author's own notes
- Minimum viable dataset: 300 annotated images. Target for generalization: 1000+

### Stage 2 — Content Extraction

Each detected region is cropped and routed to a specialist extractor based on its class:

| Class | Extractor |
|---|---|
| `Plain_Text` | TrOCR (`microsoft/trocr-base-handwritten`) |
| `Formula` | LaTeX-OCR (Pix2Tex) |
| `Figure` | Preserved as image crop in output (v1) |
| `Table` | TrOCR per cell (v2) |
| `List_Identifier` | Used for structural parsing only |
| `Abandon` | Discarded |

### Stage 3 — Document Reconstruction

Extracted content and spatial coordinates are mapped to an Excalidraw element schema, preserving the original spatial layout of the page. Text is rendered in Caveat — an open-source handwriting-style font — at the original bounding box coordinates, producing a document that looks like the original notes but is fully digital, searchable, and editable.

The reconstruction output is serialized to a JSON AST and rendered in the PaperMd editor, with PDF and DOCX export targets planned.

### Application Stack

- **Frontend:** React + React Router v7 (framework mode) + shadcn/ui + Tailwind CSS
- **Editor:** Excalidraw (`@excalidraw/excalidraw`) embedded as a React component, A4-constrained canvas
- **Formula rendering:** KaTeX
- **Inference:** `onnxruntime-web` (browser WASM) / `onnxruntime-node` (server)
- **State:** Zustand
- **Runtime:** Bun

---

## Roadmap

### v1 — Core Pipeline (Current)
- [x] Research phase: pre-trained model evaluation
- [x] Architecture decision: custom YOLOv11 Nano
- [x] Proof of concept: 61-image model, figure detection working
- [x] Active learning loop: model-assisted annotation in Label Studio
- [x] rclone backup sync for Label Studio data
- [ ] Annotation Batch 1: 50 images
- [ ] Annotation Batch 2: 100+ images (targeting diverse handwriting)
- [ ] First full training run with stable annotation schema
- [ ] TrOCR integration for Plain_Text crops
- [ ] LaTeX-OCR integration for Formula crops
- [ ] JSON AST schema
- [ ] Excalidraw-based document reconstruction with spatial awareness
- [ ] TypeScript inference pipeline via `onnxruntime-web`
- [ ] PDF export

### v2 — Extended Content
- [ ] Figure subclassification model (circuit, graph, flowchart, diagram)
- [ ] Table cell extraction
- [ ] Inline annotation model (underlines, highlights, strikethroughs, inline math)
- [ ] DOCX and Typst export targets
- [ ] Circuit emulation and editing

### v3 — Generalization
- [ ] Multi-language handwriting support
- [ ] Scan input support (flatbed scanner pipeline)
- [ ] Public dataset release

---

## Research Log

- **[Research Findings: Layout Analysis](./research/Research_Findings_Layout_Analysis.md)** — Why LayoutParser, OpenCV heuristics, and Tesseract segmentation all failed on handwritten notes, and the decision to train a custom model.
- **[Research Findings: YOLOv11 Nano Inference Analysis and Data Normalization Protocols](./research/Research_Findings_YOLOv11_Nano_Inference_Analysis_and_Data_Normalization_Protocols.md)** — Analysis of the first 24-image inference run, failure modes, confidence score distribution, and data normalization requirements.

---

## Contributing

PaperMd's model quality is directly limited by dataset diversity. A model trained only on one person's handwriting will fail on everyone else's. We are actively collecting handwritten note images from anyone willing to contribute.

**What we need:**
- Photos of handwritten notes in any subject — math, science, engineering, humanities, anything
- Any pen, pencil, or writing instrument
- Any notebook type — ruled, blank, grid, dotted
- Neat or messy — messy notes are more valuable for robustness

**What we do with them:**
- Images are used exclusively to train and evaluate the layout detection model
- Nothing will be published, shared, or used outside this project
- Contributors are credited by name in this repository
- **Contributors receive a permanent free license to the PaperMd application**

[Submit your notes here →](https://forms.google.com)

To contribute code, open an issue or pull request. The model training code, dataset tooling, and annotation guidelines are all open under GPL-3.

---

## Licensing

PaperMd uses a split licensing model.

**Model, training code, and dataset tooling — GPL-3.0**

The machine learning components are fully open source. Anyone can use, study, modify, and redistribute them under the terms of GPL-3. Derivative works must also be GPL-3.

**Application — Business Source License 1.1 (BSL-1.1)**

The PaperMd application is source-available. The code is publicly readable on GitHub. Use is free for personal, non-commercial, and research purposes. Commercial use requires a paid license. Each release automatically converts to GPL-3 four years after its release date.

**Free licenses are granted to:**

| Who | License | Verification |
|---|---|---|
| Note contributors | Permanent free commercial license | Automatic on submission |
| BIUST students and staff | 4-year free commercial license, renewable | Student email (`@studentmail.biust.ac.bw`) |

BIUST students and staff can claim their free license at `papermd.app/license` using their university email. No payment or card required.

---

## Development Setup

**Training (Google Colab):**
[Colab Training Script](https://colab.research.google.com/drive/1dAh-BjzS0RTTE1kF7Bv_9cwfVaie_BeL?usp=sharing)

**Application:**
```bash
bun install
bun dev
```

**Local inference:**
```typescript
import * as ort from 'onnxruntime-node';
const session = await ort.InferenceSession.create('./weights/papermd-layout.onnx');
```

**Python annotation preprocessing (optional):**
```bash
pip install opencv-python pytesseract pillow
python internal/processing.py
```

---

## Hardware Target

PaperMd is designed to run on consumer hardware without a GPU. The reference development machine is an Intel Celeron N4020 with 8GB RAM running CachyOS Linux. If it runs well there, it runs well everywhere.
