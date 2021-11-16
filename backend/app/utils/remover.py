"""
Created on Tue Nov 16 04:48:32 2021
@author: Ali Yildirim
"""
import numpy as np
from tensorflow import keras
from cv2 import cv2
from io import BytesIO
from pathlib import Path
import os

# Root model path for future versioning
ROOT_PATH = Path(os.path.dirname(os.path.realpath(__file__)))
MODEL_PATH = ROOT_PATH / "models"
OUTPUT_PATH = str(ROOT_PATH / "output.jpg")


class WatermarkRemover:
    def __init__(self, original_image, model_name):
        # Clear out any lingering output files
        try:
            Path(OUTPUT_PATH).unlink(missing_ok=True)
        except Exception as e:
            print(e)
            pass

        # Process
        self._original_image = np.frombuffer(original_image, np.uint8)
        self._model = MODEL_PATH / model_name
        self._container = self.parse_image()
        self._processed = self.process_image()

    def parse_image(self):
        image = cv2.imdecode(self._original_image, cv2.IMREAD_COLOR)
        return np.array([cv2.resize(image, (196, 196))]) / 255

    def process_image(self):
        reconstructed_model = keras.models.load_model(str(self._model))
        return reconstructed_model.predict(self._container)

    def get_processed_image(self):
        cv2.imwrite(OUTPUT_PATH, ((self._processed[0]) * 255))
        return self.dirty_workaround()

    @staticmethod
    def dirty_workaround():
        with open(OUTPUT_PATH, "rb") as f_img:
            image_data = f_img.read()
        return image_data


# DEBUG
# with open("./upload/input/input.jpg", "rb") as f:
#     filedata = f.read()
#
# wr = WatermarkRemover(filedata, "test_model")
# wrg = wr.get_processed_image()
