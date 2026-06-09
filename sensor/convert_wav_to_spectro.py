#!/usr/bin/env python3

import numpy as np
import librosa
import matplotlib.pyplot as plt
import sys
import os
from PIL import Image
from pathlib import Path

LOG  = 0
MEL  = 1
BOTH = 2

def create_spectrogram_from_wav(wav_file_dir: str, spectrogram_title: str, spectrogram_filepath: str, type: int = BOTH) -> str:
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

    if type > 2 or type < 0:
        raise ValueError(f"type must be LOG(0), MEL(1), or BOTH(2). Recieved: {type}")
    
    if type != MEL:
        #stft is short-time fourier transform
        frequency_domain = librosa.stft(frequency)
        spectrogram_in_db = librosa.amplitude_to_db(np.abs(frequency_domain), ref = np.max)

    if type != LOG:
        S = librosa.feature.melspectrogram(y = frequency, sr=sample_rate, n_mels=128, fmax=8000)
        power_in_db = librosa.power_to_db(S, ref = np.max)


    plt.figure(figsize=(10,4))

    
    os.makedirs(spectrogram_filepath, exist_ok=True)
    
    if type != MEL:
        librosa.display.specshow(spectrogram_in_db, sr=sample_rate, x_axis="time", y_axis="log")

        plt.colorbar(format='%+2.0f dB')
        plt.title(spectrogram_title)
        plt.tight_layout()

        plt.gca().set_facecolor('white') 
        plt.gcf().set_facecolor('white')


        output_path = os.path.join(spectrogram_filepath, f"{spectrogram_title}_log.png")
        plt.savefig(output_path, facecolor='white', edgecolor='none')
        print(f"Saved {output_path} to disk!")

    if type != LOG:
        librosa.display.specshow(power_in_db, sr=sample_rate, x_axis="time", y_axis="mel")
        if type != BOTH:
            plt.colorbar(format='%+2.0f dB')
        plt.title(spectrogram_title)
        plt.tight_layout()

        plt.gca().set_facecolor('white') 
        plt.gcf().set_facecolor('white')


        output_path = os.path.join(spectrogram_filepath, f"{spectrogram_title}_mel.png")
        plt.savefig(output_path, facecolor='white', edgecolor='none')
        print(f"Saved {output_path} to disk!")


    plt.close()

    return output_path

#Testing mel spectrograms to maybe use these instead?
#UPDATE: because of what will likely be predominately low frequency agitation on our end, this will likey go unused.
def create_mel_spectrogram_from_wav(wav_file_dir: str, spectrogram_title: str, spectrogram_filepath: str):
    """
    Generates a mel-spectrogram visualization from an audio WAV file.

    Args:
        wav_file_dir: Path to input .wav file
        spectrogram_title: Title text displayed on the plot
        spectrogram_filepath: Directory path where output PNG will be saved

    Returns:
        str: Full filepath of saved .png image

    Notes:
        • Mel scale: 128 frequency bins, max frequency 8000 Hz
        • Power converted to dB scale for visualization
        • Output image has white background
        • Resolution: standard figure size (10×4 inches)
        • File format: PNG
    
    Raises:
        FileNotFoundError: If wav_file_dir doesn't exist
        ValueError: If audio file format invalid or corrupted
        OSError: If spectrogram_filepath cannot be created
    """
          
    frequency, sample_rate = librosa.load(wav_file_dir)
    
    S = librosa.feature.melspectrogram(y = frequency, sr=sample_rate, n_mels=128, fmax=8000)

    spectrogram_in_db = librosa.power_to_db(S, ref = np.max)



    plt.figure(figsize=(10,4))
    librosa.display.specshow(spectrogram_in_db, sr=sample_rate, x_axis="time", y_axis="mel")
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
    file_path = "/Users/tylercrimando/SURI-Project"
    create_spectrogram_from_wav(wav_file_dir="/Users/tylercrimando/SURI-Project/sensor/WAV_files/Distances/45cm_200Hz_20Amp_3.wav", spectrogram_title="test", spectrogram_filepath=file_path)
