# -*- coding: utf-8 -*-
"""
Created on Tue Nov 16 04:48:32 2021

@author: Ali Yildirim
"""
import pathlib
import sys
import numpy as np 
from tensorflow import keras
import cv2
from io import BytesIO
from pathlib import Path
import os

# Root model path for future versioning
MODEL_PATH = Path(os.path.dirname(os.path.realpath(__file__))) / "models"


class WatermarkRemover:
    def __init__(self, original_image, model_name):
        self.original_image = np.frombuffer(original_image, np.uint8)
        self.model = MODEL_PATH / model_name
        self.container_old = None
        self.container = self.parse_image()

        self.processed = self.process_image()

    def parse_image(self):
        # image = cv2.imread(self.original_image, cv2.IMREAD_COLOR)
        image = cv2.imdecode(self.original_image, cv2.IMREAD_COLOR)
        image_old = cv2.imread(str(Path(os.path.dirname(os.path.realpath(__file__))) / "upload" / "input" / "input.jpg"), cv2.IMREAD_COLOR)

        self.container_old = np.array([cv2.resize(image_old, (196, 196))]) / 255
        # cv2.imshow('image', image)
        return np.array([cv2.resize(image, (196, 196))]) / 255

    def process_image(self):
        reconstructed_model = keras.models.load_model(str(self.model))
        return reconstructed_model.predict(self.container)

    def get_processed_image(self):
        # cv2.imshow("image", ((self.processed[0])*255))
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        cv2.imwrite("output.jpg", ((self.processed[0]) * 255))
        return self.dirty_workaround()
        # return cv2.imencode(self.processed[0] * 255)

    def dirty_workaround(self):
        image_data = None
        with open(str(Path(os.path.dirname(os.path.realpath(__file__))) / "output.jpg"), "rb") as f:
            image_data = f.read()
        return image_data


# # filedata = None
# with open("./upload/input/input.jpg", "rb") as f:
#     filedata = f.read()
#
# wr = WatermarkRemover(filedata, "test_model")
# wrg = wr.get_processed_image()



