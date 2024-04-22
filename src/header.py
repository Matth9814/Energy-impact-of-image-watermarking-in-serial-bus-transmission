import sys
import cv2 as cv
import os
import numpy as np
import json
# JSON encoder for Numpy data types (the basic one does not support them)
from numpyencoder import NumpyEncoder
from matplotlib import pyplot as plt
from copy import deepcopy
from math import floor
import time

np.set_printoptions(threshold=sys.maxsize) # To print without ellipses

# ----------------- DATASET ----------------- #
IMGS_PATH = "../images/"    # Images root folder

# ----------------- SIMULATION ----------------- #

## WATERMARK
# NOTE: Base images are handled in the [BGR/RGB] space
# This means that if transparency has to be considered some parts of the
# code need to be adjusted to consider a 4th channel (alpha channel)
# NOTE: Watermarks are handled in GRAY scale as most libraries (i.e. BW and IW in our case)
# use them in this color space anyway

WM_BSIZE = 2025                     # Max wm size in bytes
WM_SIZE_COMP = 0                    # 1/0: compute/not compute maximum wm image size

WM_PATH = "../wm/"                  # watermarks source directory
WM_TYPES = ('img','str')            # Watermark type is either 'str' or 'img'
WM_TYPE = 'str'                     # Currently used watermark type 

# Image wm
WM_NAME = "colorful"
WM_EXTENSION = "jpeg"
WM_DIM = 45

WM_NAME_FULL = f"{WM_NAME}.{WM_EXTENSION}"                          # Name of the watermark source
WM_NAME_RESIZED = f"{WM_NAME}_{WM_DIM}x{WM_DIM}.{WM_EXTENSION}"     # Name of the resized watermark

# String wm
WM_STR_FILE  = "stringWm.txt"       # Name of the file the string is sourced from
WM_LINE = 1                         # Line the string is stored inside the file [1,2,3,...]

with open(WM_PATH+WM_STR_FILE) as fp:
    WM_STR = fp.readlines()[WM_LINE-1]  # String used as watermark
# NOTE: the string handling has to be modified if the string characters cannot be represented with 1 byte

## BIT REPLACEMENT algorithm
BRCH = 0                # Blue [BGR]: changes in the Blue channel should be less noticeable to the human eye
REPLACED_BIT = 2        # Replaced bit (0-7) inside the modified bytes 
BYTE_STRIDE = 1         # Distance of the modified bytes (1 means that bits are embedded in consecutive bytes)

## ALGORITHMS ACTIVATION macro 
# [1/0: Active/Not active]
BIT_REPLACEMENT = 1
BLIND_WM = 1
INV_WM = 1

## DEBUG macro
DEBUG_BR = 0        # Enable/Disable debug operations for bit replacement
DEBUG_BW = 0        # Enable/Disable debug operations for blind watermark (DCT+SVD)
DEBUG_IW = 0        # Enable/Disable debug operations for invisible watermark (DWT+DCT)

## Extracted data file
# DATA_FILENAME is used for generating the output file after a simulation
SIM_RES_PATH = "../simres/"
if WM_TYPE == 'img':
    DATA_FILENAME = f"energy_consumption_wm{WM_TYPE}_{WM_NAME}.json"
else:
    # First 5 char of the string identify the file
    # If they are the same for different string the previously generated file will be overwritten if present
    DATA_FILENAME = f"energy_consumption_wm{WM_TYPE}_{WM_STR[:6]}.json"
DATA_KEYS = ['BR','BW','IW','BaseImg','Img'] # Recorded structure keys (check main.py for the dictionary structure)

# ----------------- DATA ANALYSIS and PLOT ----------------- #
#SIMDATA_FILES = ["energy_consumption_wmimg_logopolito.json","energy_consumption_wmimg_colorful.json"] # List of simulation files
