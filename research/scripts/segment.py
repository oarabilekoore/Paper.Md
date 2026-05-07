import cv2
import pytesseract
from pytesseract import Output

image_path = "test_image2.jpg"
img = cv2.imread(image_path)

# 1. Convert to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 2. Light adaptive thresholding
thresh = cv2.adaptiveThreshold(
    gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 10
)

print("Running Tesseract Block Analysis...")
d = pytesseract.image_to_data(thresh, config="--psm 3", output_type=Output.DICT)

n_boxes = len(d["level"])
valid_blocks = 0

print("\n--- Detected Structural Blocks ---")

for i in range(n_boxes):
    # CHANGED: We now look for Level 2 (Blocks) instead of Level 3 (Paragraphs)
    if d["level"][i] == 2:
        x, y, w, h = d["left"][i], d["top"][i], d["width"][i], d["height"][i]

        # Filter out tiny noise blocks and the giant page-wrapping block
        img_h, img_w = img.shape[:2]
        if (w > 50 and h > 20) and (w < img_w * 0.95 and h < img_h * 0.95):
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 3)
            valid_blocks += 1
            print(f"Block {valid_blocks}: X:{x} Y:{y} W:{w} H:{h}")

cv2.imwrite("output_tesseract_blocks.jpg", img)
print(
    f"\nSaved output with {valid_blocks} structural blocks to 'output_tesseract_blocks.jpg'"
)
