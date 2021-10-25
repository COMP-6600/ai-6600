# -*- coding: utf-8 -*-
"""
Created on Sat Oct 23 00:18:51 2021

@author: Ali Yildirim
"""

import os


# Initially used pytorch, switched to keras since it worked better
#import torch
#from torch import optim
#from torch import nn

import tensorflow as tf
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.layers import Reshape, Dense, Dropout, Input, Flatten
from tensorflow.keras.models import Sequential, Model, load_model
from tensorflow.keras.layers import Flatten, BatchNormalization, UpSampling2D
from tensorflow.keras.layers import Conv2D, ZeroPadding2D, LeakyReLU
from tensorflow.keras import layers, losses
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.models import Model
import math
import matplotlib.pyplot as plt
from __future__ import print_function
import numpy as np
from PIL import Image
from tqdm import tqdm
import time
import pandas as pd
import sklearn
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from utils import *

print(f"TF version: {tf.__version__}")
gpus = tf.config.experimental.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(gpus[0], True)
print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))

# Resolution for generation
# Higher this is, more memory is used
# Resolution is RES * 32
RES = 3 # I use 3 for 64 * 64

# Images need to be square, or about same size.
# Couldn't get good results otherwise.
# When they're loaded, they're resized to be square.
SQUARE_RES = 448 # Rows/Columns
# Channels for the image (3 since RGB)
CHNL = 3

# Seed scale factor for generation
SEED = 100

# Config
# Location for all data
DATA = "./dataset/train/"
EPOCHS = 100
BATCH_SIZE = 2
BUFFER_SIZE = 50000

# Preprocessing step.
# This may take some time.
print("Images are being loaded.")

# Array of training data
train_data = []
# Original images location
img_origin = os.path.join(DATA, "no-watermark")
# Watermarked images location
img_wm = os.path.join(DATA, "watermark")
i = 0

# Get all files as watermarked and unwatermarked pairs
# Add them to a list
for file in tqdm(os.listdir(img_origin)):
    train_data.append([])
    orig = os.path.join(img_origin, file)
    wm = os.path.join(img_wm, file)
    
    # Resize the images
    # Convert(RGB) is needed
    # Because if the image isn't rgb
    # It gets messed up in processing.
    wm_img = Image.open(wm).convert('RGB').resize((SQUARE_RES, SQUARE_RES), Image.ANTIALIAS)
    orig_img = Image.open(orig).convert('RGB').resize((SQUARE_RES, SQUARE_RES), Image.ANTIALIAS)
    
    # Save image pairs converted to np arrays
    train_data[i].append(np.asarray(orig_img))
    train_data[i].append(np.asarray(wm_img))
    
    # Iterate the training data array
    i = i+1
    
    # Comment out this section if you have high ram or v. memory
    # There's about 15k+ pics, so the preprocessing -
    # -allocates about 70gb of memory if we load all.
    # More images there are, exponentially more space is needed.
    # 1K should be enough for now.
    # Also causes issues with tensorflow as it overloads the GPU memory
    if(i>999):
        break

print("Loading successful.")
print("Only 1k images are loaded.")
print("Comment out the if statement if you want all of them.")
print("Preparing data...")

# Convert data to np array for processing
# Divide data further due to large size
train_data = np.array(train_data)
train_data = train_data.astype(np.float32)
train_data = train_data / 255
print("Done!")
print("Saving training data in binary format.")
# Save the preprocessed array
np.save(DATA, train_data)

# Create a new dataframe.
# Batch the data
# Shuffle the data
# Uses TF's own functions
df = tf.data.Dataset.from_tensor_slices(train_data).batch(BATCH_SIZE).shuffle(BUFFER_SIZE)
#print(df)

################### GAN ######################

# Denoising function
# This serves as the generator.
# The idea here is similar to image de-noising 
# Where it uses the watermarked images
# As the "noisy" image with WM, and the discriminator
# Will have the real versions of the images.
# It'll try to remove watermarks with each iteration.
# Takes in the square size of the current model
class Denoise(Model):
    def __init__(self, in_shp):
        super(Denoise, self).__init__()
        # Encodes data for denoising using relu
        # Uses a convolutional network
        # Layers are from 32 to 256 representing bits.
        self.encoder = tf.keras.Sequential([
          layers.Input(shape=(in_shp, in_shp, 3)),
          layers.Conv2D(256, (3,3), activation='relu', padding='same', strides=2),
          layers.Conv2D(128, (3,3), activation='relu', padding='same', strides=2),
          layers.Conv2D(64, (3,3), activation='relu', padding='same', strides=2),
          layers.Conv2D(32, (3,3), activation='relu', padding='same', strides=2),
          ])
        # Decodes relu encoding
        # Similar to above segment
        self.decoder = tf.keras.Sequential([

          layers.Conv2DTranspose(32, kernel_size=3, strides=2, activation='relu', padding='same'),
          layers.Conv2DTranspose(64, kernel_size=3, strides=2, activation='relu', padding='same'),
          layers.Conv2DTranspose(128, kernel_size=3, strides=2, activation='relu', padding='same'),
          layers.Conv2DTranspose(256, kernel_size=3, strides=2, activation='relu', padding='same'),
          layers.Conv2D(3, kernel_size=(3,3), activation='sigmoid', padding='same')
          ])
    
    def call(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded

# Discriminator for the GAN.
# GAN requires a discriminator and a generator
# Discriminator takes an image data
# Shaped to nparray
def train_discriminator(np_image):
    # Use sequential model
    model = Sequential()
    # Uses settings described on above step
    # Uses Conv2D, and multiple convolutions are added
    # Ranging from 32 bits to 512 bits for this step.
    # Sigmoid function is used for dense layer
    # Returns the model resulting from training
    model.add(Conv2D(32, kernel_size = 3, strides = 2, input_shape = np_image, 
                     padding = "same"))
    model.add(LeakyReLU(alpha = 0.2))
    model.add(Dropout(0.2))
    model.add(Conv2D(64, kernel_size = 3, strides = 2, padding = "same"))
    model.add(ZeroPadding2D(padding = ((0,1),(0,1))))
    model.add(BatchNormalization(momentum = 0.8))
    model.add(LeakyReLU(alpha = 0.2))
    model.add(Dropout(0.2))
    model.add(Conv2D(128, kernel_size = 3, strides = 2, padding = "same"))
    model.add(BatchNormalization(momentum = 0.8))
    model.add(LeakyReLU(alpha = 0.2))
    model.add(Dropout(0.2))
    model.add(Conv2D(256, kernel_size = 3, strides = 1, padding = "same"))
    model.add(BatchNormalization(momentum = 0.8))
    model.add(LeakyReLU(alpha = 0.2))
    model.add(Dropout(0.2))
    model.add(Conv2D(512, kernel_size = 3, strides = 1, padding = "same"))
    model.add(BatchNormalization(momentum = 0.8))
    model.add(LeakyReLU(alpha = 0.2))
    model.add(Dropout(0.2))
    model.add(Flatten())
    model.add(Dense(1, activation = 'sigmoid'))
    return model


# Generates layers for the model
# Returns the activations when a prediction is made
def generate_layer_out(model, data, n_layers):
    layer_out = [layer.output for layer in model.layers[:n_layers]]
    activation_model = Model(inputs = model.input, outputs = layer_out)
    activations = activation_model.predict(data)
    
    return activations

# Displays activations
# It's for viewing the training progress in real time
def display_act(activations, col_size, row_size, act_index):
    activation = activations[act_index]
    activation_index = 0
    fig, ax = plt.subplots(row_size, col_size, figsize = (row_size*12, col_size * 10))
    
    for row in range(0, row_size):
        for col in range(0, col_size):
            ax[row][col].imshow(activation[0, :, :, activation_index])
            activation_index += 1

################## Utility functions ###########################
# Error calculation, mean squared error root
# Root of the mean square of the error margin is returned.
def mse(y_real, y_pred):
    return tf.keras.backend.sqrt(tf.keras.backend.mean(tf.keras.backend.square(y_real - y_true)))
# Random string generator, 
# Used for generating names for out files.
def random_str(length):
    letters = string.ascii_lowercase
    result = ''.join(rnd.choice(letters) for i in range(length))
    return result

#print(len(df))

# Generate training data
data_gen = tf.keras.preprocessing.image.ImageDataGenerator(rescale = 1.0/255)
# Generate testing data

######### WARNING
# flow_from_directory needs the images to be in a subfolder
# Copy-paste watermarked images equal to the amount of images loaded
# Into a subfolder in the directory called "images".
# Adjust as needed.
# TODO: Handle that part in code.
test_gen = data_gen.flow_from_directory(
    directory = "./dataset/train/watermark/",
    target_size = (SQUARE_RES, SQUARE_RES),
    color_mode = "rgb",
    batch_size = BATCH_SIZE,
    class_mode = "input",
    shuffle = True )

# Establish a generator with SQUARE_RES
generator = Denoise(SQUARE_RES)
generator.compile(optimizer = "adam", loss = mse)
generator.build((1, SQUARE_RES, SQUARE_RES, 3))

## TODO : TRAIN AND EVALUATE
# I COULDNT FINISH THIS PART AS THIS THING FUCKS UP THE MEMORY AND GPU
# FOUND A WORKAROUND, SHOULD BE DONE ASAP