#!/usr/bin/env python3

# currently commenting out tf as it makes stuff take forever

#import tensorflow as tf
#from tensorflow import keras
#from tensorflow.keras import layers, models
import random
import numpy as np

binary_classes = {"object": 0, "no_object": 1}

# I totally chose these percentes randomly
def augment_wav(wav_file: str):
    wav = read(wav_file) # 0 is sample rate, 1 is array of audio
    wav_array = wav[1]

    #time_shift (wrap around) from 5 to 30 percent of audio
    if random.random() < 0.67:
        percent = random.randrange(-30,30, step=.25)
        
        int_to_shift = (int) (percent * wav[0])
        np.roll(wav[1], shift=int_to_shift)

    #noise_inject
    if random.random() < 0.40:
        noise = 0.1*(wav_array.max() - wav_array.min()) * np.random.random(wav_array.shape[0])
        noise -= noise.mean()
        wav_array += noise

    #time_stretch



if __name__ == "__main__":
    wav = read("/Users/tylercrimando/Downloads/ESC-50-master/audio/5-263831-A-6.wav") # (sample rate, data, type)
    print(len(wav[1]))

    arr = np.array([0,1,2,3,4,5,6,7,8,9])
    
    print(arr)

    for i in range(10):
        print()
        arr =  np.roll(arr, shift=1)
        print(arr)
    