import os

from label_studio_ml.model import LabelStudioMLBase
from label_studio_ml.utils import get_local_path
from ultralytics import YOLO

os.environ["USE_NNPACK"] = "0"

# Mapping based on your v2.pt output
LABEL_MAP = {
    0: "Abandon",  # cancellation -> Abandon
    1: "Figure",  # diagram -> Figure
    2: "Formula",  # equation -> Formula
    3: "Figure",  # figure -> Figure
    4: "Plain_Text",  # heading -> Plain_Text
    5: "List_Identifier",  # list -> List_Identifier
    6: "Plain_Text",  # paragraph -> Plain_Text
    8: "Table",  # table -> Table
    # 7: symbol is omitted, so it will be ignored
}


class YOLOv11Backend(LabelStudioMLBase):
    def __init__(self, **kwargs):
        super(YOLOv11Backend, self).__init__(**kwargs)

        # Look for best.pt in the same folder as this script
        self.model_path = os.path.join(os.path.dirname(__file__), "./latest-model.pt")

        if not os.path.exists(self.model_path):
            print(f"ERROR: Model weights not found at {self.model_path}")

        self.model = YOLO(self.model_path)

        if not hasattr(self.model.model, "_original_forward"):
            self.model.model._original_forward = self.model.model.forward

            def custom_forward(x, *args, **kwargs):
                out = self.model.model._original_forward(x, *args, **kwargs)
                return (
                    out.get("one2one", list(out.values())[0])
                    if isinstance(out, dict)
                    else out
                )

            self.model.model.forward = custom_forward

    def predict(self, tasks, **kwargs):
        predictions = []
        for task in tasks:
            image_url = task["data"]["image"]

            # Simplified helper call to avoid TypeError
            image_path = get_local_path(image_url)

            results = self.model.predict(image_path, conf=0.45, imgsz=320)[0]
            result_list = []
            img_width, img_height = results.orig_shape

            for box in results.boxes:
                xyxy = box.xyxy[0].tolist()
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])

                if cls_id not in LABEL_MAP:
                    continue

                x = (xyxy[0] / img_width) * 100
                y = (xyxy[1] / img_height) * 100
                w = ((xyxy[2] - xyxy[0]) / img_width) * 100
                h = ((xyxy[3] - xyxy[1]) / img_height) * 100

                result_list.append(
                    {
                        "from_name": "label",
                        "to_name": "image",
                        "type": "rectanglelabels",
                        "score": conf,
                        "value": {
                            "rectanglelabels": [LABEL_MAP[cls_id]],
                            "x": x,
                            "y": y,
                            "width": w,
                            "height": h,
                            "rotation": 0,
                        },
                    }
                )

            predictions.append({"result": result_list})
        return predictions
