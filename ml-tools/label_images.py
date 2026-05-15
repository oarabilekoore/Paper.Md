import os
import shutil
from pathlib import Path

import torch
from ultralytics import YOLO

model_path = "../models/0515_0106_n14.pt"
test_image_dir = "../../PaperMd Training Images/Batch 1/"
model_name = Path(model_path).stem
output_base_dir = os.path.join("../models", model_name)

if not os.path.exists(model_path):
    print(f"Error: Model weights not found at {model_path}")
    exit(1)

# Load model
model = YOLO(model_path)


def custom_forward(x, *args, **kwargs):
    out = model.model._original_forward(x, *args, **kwargs)
    if isinstance(out, dict):
        return out.get("one2one", list(out.values())[0])
    return out


if not hasattr(model.model, "_original_forward"):
    model.model._original_forward = model.model.forward
    model.model.forward = custom_forward

# Run inference
results = model.predict(
    source=test_image_dir,
    conf=0.25,  # Lower threshold to capture "low accuracy" samples
    save=True,
    project="research",
    name=model_name,
    exist_ok=True,
)

# --- POST-PROCESSING: SORT BY ACCURACY ---
# Calculate average confidence per image
image_perf = []
for res in results:
    if len(res.boxes.conf) > 0:
        avg_conf = res.boxes.conf.mean().item()
    else:
        avg_conf = 0.0

    image_perf.append(
        {
            "path": res.path,
            "conf": avg_conf,
            "saved_path": os.path.join(res.save_dir, os.path.basename(res.path)),
        }
    )

# Sort: Highest confidence first
image_perf.sort(key=lambda x: x["conf"], reverse=True)

high_acc = image_perf[:5]
low_acc = [img for img in image_perf if img["conf"] > 0][-5:]

# --- DIRECTORY MANAGEMENT ---
eval_dir = os.path.join(output_base_dir, "eval_samples")
os.makedirs(eval_dir, exist_ok=True)


def copy_samples(samples, folder_name):
    target = os.path.join(eval_dir, folder_name)
    os.makedirs(target, exist_ok=True)
    for img in samples:
        if os.path.exists(img["saved_path"]):
            shutil.copy(img["saved_path"], target)


copy_samples(high_acc, "high_accuracy")
copy_samples(low_acc, "low_accuracy")

# --- GENERATE README ---
readme_path = os.path.join(output_base_dir, "README.md")
all_confs = [img["conf"] for img in image_perf if img["conf"] > 0]
avg_total_conf = sum(all_confs) / len(all_confs) if all_confs else 0

readme_content = f"""# Model Performance Report: {model_name}

## Metadata
- **Model Path:** `{model_path}`
- **Source Images:** `{test_image_dir}`
- **Total Images Tested:** {len(results)}
- **Images with Detections:** {len(all_confs)}

## Performance Metrics
- **Mean Confidence (mConf):** {avg_total_conf:.4f}
- **Highest Confidence Image:** {high_acc[0]["conf"]:.4f} if high_acc else "N/A"
- **Lowest Confidence Image (non-zero):** {low_acc[-1]["conf"]:.4f} if low_acc else "N/A"

## Observations
- High accuracy samples are located in `./eval_samples/high_accuracy/`
- Low accuracy samples are located in `./eval_samples/low_accuracy/`
- Results generated on hardware: Intel Celeron N4020 (NNPACK Disabled)
"""

with open(readme_path, "w") as f:
    f.write(readme_content)

print(f"Evaluation complete. Files moved to {output_base_dir}")
print(f"README created at {readme_path}")
