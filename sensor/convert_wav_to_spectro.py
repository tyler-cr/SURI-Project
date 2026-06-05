#!/usr/bin/env python3

import numpy as np
import librosa
import matplotlib.pyplot as plt
import sys
import os
from PIL import Image
from pathlib import Path

def create_spectrogram_from_wav(wav_file_dir: str, spectrogram_title: str, spectrogram_filepath: str) -> str:
    """
    Generates and saves a log-scale spectrogram image from a WAV file using STFT.

    The function loads the audio, computes the Short-Time Fourier Transform (STFT),
    converts it to decibels, and renders a white-background plot.

    Args:
        wav_file_dir: Path to the input WAV file.
        spectrogram_title: Title for the plot and the output filename.
        spectrogram_filepath: Directory path where the output PNG will be saved.

    Returns:
        str: The full absolute path to the generated PNG file.

    Raises:
        FileNotFoundError: If the input WAV file does not exist.
        ValueError: If the directory for saving the spectrogram does not exist.
    """
    
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

    os.makedirs(spectrogram_filepath, exist_ok=True)

    output_path = os.path.join(spectrogram_filepath, f"{spectrogram_title}.png")
    plt.savefig(output_path, facecolor='white', edgecolor='none')
    plt.close()

    return output_path

if __name__ == "__main__":

    a = 5

