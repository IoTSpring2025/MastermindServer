from roboflow import Roboflow
import os
import tempfile
from PIL import Image
import io


class Model:
    def __init__(self, version: str, confidence: int = 33, overlap: int = 0):
        self.version: str = version
        self.rf_client = Roboflow(api_key=os.environ.get("ROBOFLOW_API_KEY"))
        self.project: str = self.rf_client.workspace().project(
            os.environ.get("ROBOFLOW_PROJECT")
        )
        self.model = self.project.version(self.version).model
        self.confidence = confidence
        self.overlap = overlap
        self.frames_seen = 0
        self.current_predictions = []
        self.max_frame_count = 10
        self.thresh = 0.5

    def _detect_single(self, image_bytes: bytes) -> list[dict[str, float]]:
        # inference on a single frame
        try:
            with tempfile.NamedTemporaryFile(suffix=".jpg") as temp:
                # load image and save to temp file
                image = Image.open(io.BytesIO(image_bytes))
                image.save(temp.name, format="JPEG")

                # predict
                prediction = self.model.predict(
                    temp.name, confidence=self.confidence, overlap=self.overlap
                )
                res = {}
                for pred in prediction.json()["predictions"]:
                    res[pred["class"]] = f"{pred['confidence'] * 100:.2f}"
                self.current_predictions.append(res)
                self.frames_seen += 1

            return res
        except Exception as e:
            return f"Error reading hand from bytes: {e}"

    def detect(self, image_bytes: bytes) -> list[str]:
        # if we have over 70% confidence for all objects, return the objects. otherwise run inference on multiple frames
        pred = self._detect_single(image_bytes)

        conf = True
        for obj in pred:
            if float(pred[obj]) < 0.70:
                conf = False
                break
        if conf and len(pred) > 0:
            return pred
        elif self.frames_seen >= self.max_frame_count:
            filtered_preds = self._process_predictions()

            # reset
            self.current_predictions = []
            self.frames_seen = 0

            if len(filtered_preds) > 0:
                return filtered_preds
            else:
                return []
        else:
            return []

    def _process_predictions(self) -> list[str]:
        counts = {}
        for pred in self.current_predictions:
            for obj in pred:
                counts[obj] = counts.get(obj, 0) + 1
        return [
            obj for obj in counts if counts[obj] >= self.max_frame_count * self.thresh
        ]
