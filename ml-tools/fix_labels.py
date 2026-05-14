import json
import os
from pathlib import Path

from PIL import Image

# Final Paths
SOURCE_DATA = Path("data")
IMAGE_DIR = Path("/home/vaseline/mnt/gdrive/images/train")
OUTPUT_DIR = Path("data_final")
OUTPUT_DIR.mkdir(exist_ok=True)

print("Indexing images...")
image_map = {}
for img_path in IMAGE_DIR.glob("*.jpg"):
    try:
        with Image.open(img_path) as img:
            w, h = img.size
            image_map.setdefault((w, h), []).append(img_path.name)
    except Exception:
        continue

print("Running deep recovery...")
for file_path in SOURCE_DATA.glob("*.json"):
    try:
        with open(file_path, "r") as f:
            content = json.load(f)

        results = []
        # Structure 1: Root is a list (Label Studio Export)
        if isinstance(content, list) and len(content) > 0:
            results = content[0].get("annotations", [{}])[0].get("result", [])
        # Structure 2: Root is a dict with 'annotations'
        elif isinstance(content, dict):
            if "annotations" in content and content["annotations"]:
                results = content["annotations"][0].get("result", [])
            elif "result" in content:
                results = content["result"]

        if not results:
            print(f"No results found in {file_path.name}. Check structure.")
            continue

        orig_w = results[0].get("original_width")
        orig_h = results[0].get("original_height")
        matches = image_map.get((orig_w, orig_h), [])

        if matches:
            # Use relative path from DOCUMENT_ROOT
            image_rel_path = f"images/train/{matches[0]}"

            formatted_task = {
                "data": {"image": f"/data/local-files/?d={image_rel_path}"},
                "annotations": [{"result": results}],
            }

            with open(OUTPUT_DIR / file_path.name, "w") as f:
                json.dump(formatted_task, f, indent=2)
            print(f"Recovered {file_path.name} -> {matches[0]}")
        else:
            print(f"No image match for {file_path.name} ({orig_w}x{orig_h})")

    except Exception as e:
        print(f"Error in {file_path.name}: {e}")

print(f"Import files from {OUTPUT_DIR}")
