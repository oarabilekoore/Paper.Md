from trand=sformers import TcOCRProcessor, VisionEncoderDecoderModel
from PIL  import Image

processor = TcOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten")

def extract_text(image_crop): 

