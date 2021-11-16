# -*- coding: utf-8 -*-
"""
Created on Tue Nov 16 04:48:32 2021

@author: Ali Yildirim
"""
import sys
import numpy as np 
from tensorflow import keras
import cv2
from pathlib import Path

# PARSER
n = len(sys.argv)

currentRoot = Path(".")
inFile = currentRoot / str(sys.argv[1])
modelName = str(sys.argv[2])

image = cv2.imread(str(inFile), cv2.IMREAD_COLOR)
container = np.array([cv2.resize(image, (196, 196))]) / 255

reconstructed_model = keras.models.load_model(modelName)
result = reconstructed_model.predict(container)

cv2.imwrite(f"{inFile}_out", (result[0])*255)
