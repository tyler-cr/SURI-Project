#!/usr/bin/env python3

# currently commenting out tf as it makes stuff take forever to compile (We love JIT)

#import tensorflow as tf
#from tensorflow import keras
#from tensorflow.keras import layers, models
import random
import numpy as np

binary_classes = {
                    "object_binary" : {"object": 0, "no_object": 1},
                    "noise_vs_data_binary" : {"noise": 0, "data": 1}
                  }





if __name__ == "__main__":
    a = 5
    