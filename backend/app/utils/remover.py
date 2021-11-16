# -*- coding: utf-8 -*-
"""
Created on Tue Nov 16 04:48:32 2021

@author: Ali Yildirim
"""
import sys
import numpy as np 
#import matplotlib.pyplot as plt 
import tensorflow as tf 
from tensorflow import keras
from keras.models import Model
#from keras.layers import Conv2D, MaxPooling2D, Dense, Input, Conv2D, UpSampling2D, BatchNormalization
#from tensorflow.keras.optimizers import Adam
#from keras.callbacks import EarlyStopping
import cv2
import os 


## PARSER
n = len(sys.argv)
#print("DEBUG: Argument number = " + str(n))
inPath = str(sys.argv[1])
outPath = str(sys.argv[2])
inFile = str(sys.argv[3])
filename = inPath + inFile
modelName = str(sys.argv[4])

#print(inPath)
#print(outPath)
#print(inFile)
#print(filename)
image = cv2.imread(filename, cv2.IMREAD_COLOR)
container = []
container.append(cv2.resize(image, (196, 196)))
container = np.array(container)
container = container/255
container.shape

reconstructed_model = keras.models.load_model(modelName)
result = reconstructed_model.predict(container)


cv2.imwrite(outPath + inFile, (cv2.cvtColor(result[0], cv2.COLOR_BGR2RGB))*255)
print(cv2.imwrite(outPath + inFile, (cv2.cvtColor(result[0], cv2.COLOR_BGR2RGB))*255))