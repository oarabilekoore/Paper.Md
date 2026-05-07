import os

from ultralytics import YOLO

model_path = "./best.pt"
test_image_dir = "../testing_data/"

if not os.path.exists(model_path):
    print(f"Error: Model weights not found at {model_path}")
    exit(1)

model = YOLO(model_path)

results = model.predict(
    source=test_image_dir,
    conf=0.25,
    save=True,
    save_txt=True,
    project="research",
    name="inference_tests",
)

print(f"Inference complete. Results saved to: {results[0].save_dir}")
