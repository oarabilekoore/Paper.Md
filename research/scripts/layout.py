import os
import urllib.request

import numpy as np
import torch
from PIL import Image

_original_load = torch.load


def _patched_load(*args, **kwargs):
    kwargs["weights_only"] = False
    return _original_load(*args, **kwargs)


torch.load = _patched_load

import layoutparser as lp

model_dir = "models/effdet_publaynet"
os.makedirs(model_dir, exist_ok=True)

weights_path = os.path.join(model_dir, "publaynet-tf_efficientdet_d1.pth.tar")

if not os.path.exists(weights_path):
    print("Downloading weights from Hugging Face...")
    url = "https://huggingface.co/layoutparser/efficientdet/resolve/main/PubLayNet/tf_efficientdet_d1/publaynet-tf_efficientdet_d1.pth.tar"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

    with urllib.request.urlopen(req) as response, open(weights_path, "wb") as out_file:
        out_file.write(response.read())

print("Loading model...")
model = lp.models.EfficientDetLayoutModel(
    config_path="tf_efficientdet_d1",
    model_path=weights_path,
    label_map={1: "Text", 2: "Title", 3: "List", 4: "Table", 5: "Figure"},
)

image_path = "Pasted image.png"

try:
    image = Image.open(image_path).convert("RGB")
    image_array = np.array(image)
except FileNotFoundError:
    print(f"Error: Could not find '{image_path}'.")
    exit(1)

print("Running inference...")
layout = model.detect(image_array)

for block in layout:
    print(
        f"Type: {block.type} | Score: {block.score:.2f} | Coordinates: {block.coordinates}"
    )

viz = lp.draw_box(image_array, layout, box_width=3)
viz.save("output_layout.jpg")
print("Output saved as 'output_layout.jpg'.")
