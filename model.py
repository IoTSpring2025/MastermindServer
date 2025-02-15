from roboflow import Roboflow
import os
import tempfile
from PIL import Image
import io 

class Model():
    def __init__(self, version=4, confidence=33, overlap=15):
        self.version = version
        self.rf_client = Roboflow(api_key=os.environ.get("ROBOFLOW_API_KEY"))
        self.project = self.rf_client.workspace().project(os.environ.get("ROBOFLOW_PROJECT"))
        self.model = self.project.version(self.version).model
        self.confidence = confidence
        self.overlap = overlap
    
    def read_hand(self, image_bytes):
        try:
            with tempfile.NamedTemporaryFile(suffix=".jpg") as temp:
                image = Image.open(io.BytesIO(image_bytes))
                image.save(temp.name, format="JPEG")
                prediction = self.model.predict(temp.name, confidence=self.confidence, overlap=self.overlap)
            output = {}
            for pred in prediction.json()['predictions']:
                output[pred["class"]] = f"{pred['confidence']*100:.2f}%"
            return output
        except Exception as e:
            return f"Error reading hand from bytes: {e}"