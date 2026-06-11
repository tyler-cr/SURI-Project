#!/usr/bin/env python3

import numpy as np
from scipy.io.wavfile import read, write

def map_minmax(curmin, curmax, newmin, newmax):
    return 

def create_sine(freq: int = None, amp: float = None, sample_rate: int = None, time: int = 1):
    
    if freq is None: 
        print("create_wav: freq variable not specified... Defaulting to 100Hz")
        freq = 100
    if amp is None:
        print("create_wav: amp variable not specified... Defaulting to 20Vpp")
        amp = .5
    elif abs(amp) > 1:
        print(f"create_wav: amplitude must be between -1 and 1. Recieved: {amp}. Defaulting to .5")
        amp = 0.5
    if sample_rate is None:
        print("create_wav: sample_rate variable not specified... Defaulting to 2.1000 * freq")
        sample_rate = (int)(2.1*freq)
    
    #for i in (sample_rate * time):
        # y = amp x sin( freq * 2pi * x)
    
    wav_array = np.arange(0, time, 1 / (sample_rate))
    wav_array = 32767 * amp * np.sin(2 * np.pi * freq * wav_array)
    wav_array = wav_array.astype(np.int16)

    return sample_rate, wav_array

def concat_wav_arrays(wav_array_list: list):
    new_list = []

    for garbage in wav_array_list:
        new_list.append(garbage[1])

    return np.concatenate(new_list)

#waypoints = np.array( [length * ((numerator + i) /denominator) for i in range(denominator)])

if __name__ == "__main__":
    test_list = []
    for i in range(5):
        test_list.append(create_sine(100 * i, .75, 1100, i))
    
    plz_work = concat_wav_arrays(test_list)
    write("test.wav", 1100, plz_work)