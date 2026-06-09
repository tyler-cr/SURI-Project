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

def get_raw_spectro(wav_file: str):
    y, sr = librosa.load(wav_file, sr=None)

    S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
    S_db = librosa.power_to_db(S, ref=np.max).astype(np.float32)

    return S_db

def get_raw_spectro_list(wav_dir: str):
    all_wavs = np.array([get_raw_spectro(f) for f in sorted(Path(wav_dir).iterdir()) if f.suffix.lower() == ".wav"], dtype=np.float32)

    all_wavs = all_wavs[..., np.newaxis]
    
    all_wavs = np.clip((all_wavs + 80) / 80, 0, 1).astype(np.float32)
    return all_wavs
        


def create_spectrogram_from_wav_borderless(
    wav_file_dir: str,
    spectrogram_title: str,
    spectrogram_filepath: str,
    type: int = LOG
) -> str:
    y, sr = librosa.load(wav_file_dir)

    if type > 2 or type < 0:
        raise ValueError(f"type must be LOG(0), MEL(1), or BOTH(2). Received: {type}")

    os.makedirs(spectrogram_filepath, exist_ok=True)

    output_path = None

    def save_spec(data, filename, y_axis):
        fig = plt.figure(figsize=(10, 4), dpi=100, frameon=False)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_axis_off()

        librosa.display.specshow(
            data,
            sr=sr,
            x_axis="time",
            y_axis=y_axis,
            ax=ax
        )

        path = os.path.join(spectrogram_filepath, filename)
        fig.savefig(path, dpi=100, bbox_inches=None, pad_inches=0)
        plt.close(fig)

        print(f"Saved {path} to disk!")
        return path

    if type != MEL:
        frequency_domain = librosa.stft(y)
        spectrogram_in_db = librosa.amplitude_to_db(np.abs(frequency_domain), ref=np.max)
        output_path = save_spec(spectrogram_in_db, f"{spectrogram_title}_log.png", "log")

    if type != LOG:
        S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
        power_in_db = librosa.power_to_db(S, ref=np.max)
        output_path = save_spec(power_in_db, f"{spectrogram_title}_mel.png", "mel")

    return output_path

def create_spectrogram_from_wav(wav_file_dir: str, spectrogram_title: str, spectrogram_filepath: str, type: int = LOG) -> str:
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
    create_spectrogram_from_wav_borderless(wav_file_dir="/Users/tylercrimando/SURI-Project/sensor/WAV_files/Distances/45cm_200Hz_20Amp_3.wav", spectrogram_title="test1", spectrogram_filepath=file_path)
    create_spectrogram_from_wav(wav_file_dir="/Users/tylercrimando/SURI-Project/sensor/WAV_files/Distances/45cm_200Hz_20Amp_3.wav", spectrogram_title="test2", spectrogram_filepath=file_path)
