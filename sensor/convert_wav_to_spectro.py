#!/usr/bin/env python3

import numpy as np
import librosa
import matplotlib.pyplot as plt
import sys
import os
from PIL import Image
from pathlib import Path

def create_spectrogram_from_wav(wav_file_dir: str, spectrogram_title: str, spectrogram_filepath: str) -> str:
    frequency, sample_rate = librosa.load(wav_file_dir)
    
    #stft is short-time fourier transform
    frequency_domain = librosa.stft(frequency)

    spectrogram_in_db = librosa.amplitude_to_db(np.abs(frequency_domain), ref = np.max)

    plt.figure(figsize=(10,4))
    librosa.display.specshow(spectrogram_in_db, sr=sample_rate, x_axis="time", y_axis="log")
    plt.colorbar(format='%+2.0f dB')
    plt.title(spectrogram_title)
    plt.tight_layout()

    plt.gca().set_facecolor('white') 
    plt.gcf().set_facecolor('white')

    plt.savefig(spectrogram_filepath+"/"+spectrogram_title+".png", facecolor='white', edgecolor='none')
    plt.close()

    return spectrogram_filepath+"/"+spectrogram_title+".png"

if __name__ == "__main__":

    a = 5

