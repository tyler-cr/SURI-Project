#!/usr/bin/env python3

# currently commenting out tf as it makes stuff take forever to compile (We love JIT)

#import tensorflow as tf
#from tensorflow import keras
#from tensorflow.keras import layers, models
import random
import numpy as np
from pathlib import Path
from PIL import Image

binary_classes = {
                    "object_binary" : {"object": 0, "no_object": 1},
                    "noise_vs_data_binary" : {"noise": 0, "data": 1}
                  }




if __name__ == "__main__":
    
    file_path = "/Users/tylercrimando/SURI-Project/sensor/WAV_files/Distances/Spliced/augmented"

    npy_file_path = "/Users/tylercrimando/SURI-Project/ml/npy_files"

    print("creating labels np.array... please be patient!\n")
    #zero for when "noise" in wav file, one when "data" in wav file
    labels = np.array([(0 if "noise" in f.name else 1) for f in sorted(Path(file_path).iterdir()) if f.suffix.lower() == ".wav"], dtype=bool)
    
    print(labels)

    print("saving labels np.array... please be patient!\n")
    np.save(f"{npy_file_path}/labels_noise_vs_sound_labels.npy", labels)

    # spectrogram_dir = "/Users/tylercrimando/SURI-Project/sensor/WAV_files/Distances/Spliced/augmented/spectrograms"

    # all_images = [f for f in Path(spectrogram_dir).iterdir() if (f.suffix in [".png", ".jpg", ".jpeg"] and "mel" not in f.name)]
    # for image_file in all_images:
    #     a = 5
    