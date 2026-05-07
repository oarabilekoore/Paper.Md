import layoutparser as lp
import numpy as np
from PIL import Image

# 1. Initialize the model
# Using tf_efficientdet_d1 trained on the PubLayNet dataset
model = lp.AutoLayoutModel("lp://effdet/PubLayNet/tf_efficientdet_d1")

# 2. Load the image
# Ensure you have a sample image named 'paper_sample.jpg' in the same folder
image_path = "paper_sample.jpg"

try:
    # Convert PIL image to RGB and then to a NumPy array for LayoutParser
    image = Image.open(image_path).convert("RGB")
    image_array = np.array(image)
except FileNotFoundError:
    print(f"Error: Could not find '{image_path}'. Please add an image to test.")
    exit(1)

# 3. Detect the layout
print("Running inference... (This will download model weights on the first run)")
layout = model.detect(image_array)

# 4. Output the raw data to the console
print("\n--- Detected Blocks ---")
for block in layout:
    # Each block contains coordinates, a type (e.g., Text, Title, Figure), and a confidence score
    print(
        f"Type: {block.type} | Score: {block.score:.2f} | Coordinates: {block.coordinates}"
    )

# 5. Generate a visual representation
# Draws bounding boxes over the original image and saves it
viz = lp.draw_box(image_array, layout, box_width=3)
viz.save("output_layout.jpg")
print("\nSuccess: Output image with bounding boxes saved as 'output_layout.jpg'.")
