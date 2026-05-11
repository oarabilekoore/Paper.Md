import os

import torch
from ultralytics import YOLO

# Disable NNPACK to avoid hardware warnings on Celeron
os.environ["USE_NNPACK"] = "0"

model_path = "../assets/papermd-v2-model.pt"
test_image_dir = "../../PaperMd Training Images/Batch 1/"

if not os.path.exists(model_path):
    print(f"Error: Model weights not found at {model_path}")
    exit(1)

# Load model
model = YOLO(model_path)


# PATCH: Extract the correct tensor from the dictionary output
# DocLayout-YOLO typically puts the inference tensor in the 'one2one' key
def custom_forward(x, *args, **kwargs):
    out = model.model._original_forward(x, *args, **kwargs)
    if isinstance(out, dict):
        return out.get("one2one", list(out.values())[0])
    return out


# Store original forward and apply the patch
if not hasattr(model.model, "_original_forward"):
    model.model._original_forward = model.model.forward
    model.model.forward = custom_forward

# Run inference
results = model.predict(
    source=test_image_dir,
    conf=0.25,
    save=True,
    save_txt=True,
    save_crop=True,
    project="research",
    name="inference_tests",
    # imgsz=640,  # Crucial for 8GB RAM performance
    # device="cpu",
)

print(f"Process complete.")
print(f"Full results: {results[0].save_dir}")
print(f"Equation crops saved in: {results[0].save_dir}/crops/equation/")
