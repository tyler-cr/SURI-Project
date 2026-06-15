#!/usr/bin/env python3

import numpy as np
from scipy.io.wavfile import read, write

def create_sine(freq: int = None, amp: float = None, sample_rate: int = None, time: int = 1):
    """
    Generates a sine wave audio signal at specified parameters.
    
    Produces a single-frequency sinusoidal waveform with configurable amplitude,
    frequency, sampling rate, and duration. Outputs as 16-bit signed integer 
    PCM data suitable for WAV file export. Applies default values if parameters
    are omitted.
    
    Args:
        freq (int): Sine wave frequency in Hz. Default: 100.
        amp (float): Amplitude normalized to [-1.0, 1.0]. Default: 0.5.
        sample_rate (int): Samples per second. Default: 2.1 × freq.
        time (int): Duration in seconds. Default: 1.
        
    Returns:
        tuple: (sample_rate, wav_array) where wav_array is np.ndarray 
               with dtype=np.int16 ready for scipy.io.wavfile.write().
        
    Raises:
        UserWarning: Printed if amp exceeds ±1.0 (automatically corrected to 0.5).
    """
    
    if freq is None: 
        print("create_wav: freq variable not specified... Defaulting to 100Hz")
        freq = 100
    if amp is None:
        print("create_wav: amp variable not specified... Defaulting to .5")
        amp = .5
    elif abs(amp) > 1:
        print(f"create_wav: amplitude must be between -1 and 1. Recieved: {amp}. Defaulting to .5")
        amp = 0.5
    if sample_rate is None:
        print("create_wav: sample_rate variable not specified... Defaulting to 2.1000 * freq")
        sample_rate = (int)(2.1*freq)
    
    wav_array = np.arange(0, time, 1 / (sample_rate))
    wav_array = 32767 * amp * np.sin(2 * np.pi * freq * wav_array)
    wav_array = wav_array.astype(np.int16)

    return sample_rate, wav_array

def concat_wav_arrays(wav_array_list: list):
    """
    Concatenates multiple WAV audio arrays into a single continuous stream.
    
    Expects a list of tuples containing (sample_rate, wav_array) pairs returned 
    by create_sine(). Extracts only the audio arrays and concatenates them 
    sequentially along the sample axis. Sample rate validation is not performed—
    caller must ensure uniform rates across inputs.
    
    Args:
        wav_array_list (list): List of tuples [(sample_rate, wav_array), ...].
        
    Returns:
        np.ndarray: Single concatenated array of dtype=np.int16.
        
    Note:
        Discards individual sample_rates; caller responsible for ensuring 
        all input arrays share compatible rates before concatenation.
    """
    
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