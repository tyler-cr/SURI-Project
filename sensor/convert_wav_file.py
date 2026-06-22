#!/usr/bin/env python3

import numpy as np
import librosa
import matplotlib.pyplot as plt
import sys
import os
import json
from PIL import Image
from pathlib import Path


LOG  = 0
MEL  = 1
BOTH = 2

def dict_from_amplitudes():
    Full = {
        "5Amp" :{
            "noise":{
                "10Hz" :{
                    "30cm":[],
                    "45cm":[],
                    "60cm":[],
                    "75cm":[],
                    "90cm":[],
                },
                "100Hz":{
                    "30cm":[],
                    "45cm":[],
                    "60cm":[],
                    "75cm":[],
                    "90cm":[],
                },
                "200Hz":{
                    "30cm":[],
                    "45cm":[],
                    "60cm":[],
                    "75cm":[],
                    "90cm":[],
                }
            },
            "data":{
                "10Hz" :{
                    "30cm":[],
                    "45cm":[],
                    "60cm":[],
                    "75cm":[],
                    "90cm":[],
                },
                "100Hz":{
                    "30cm":[],
                    "45cm":[],
                    "60cm":[],
                    "75cm":[],
                    "90cm":[],
                },
                "200Hz":{
                    "30cm":[],
                    "45cm":[],
                    "60cm":[],
                    "75cm":[],
                    "90cm":[],
                }
            }
        },
        "10Amp":{
            "noise":{
                "10Hz" :{
                    "30cm":[],
                    "45cm":[],
                    "60cm":[],
                    "75cm":[],
                    "90cm":[],
                },
                "100Hz":{
                    "30cm":[],
                    "45cm":[],
                    "60cm":[],
                    "75cm":[],
                    "90cm":[],
                },
                "200Hz":{
                    "30cm":[],
                    "45cm":[],
                    "60cm":[],
                    "75cm":[],
                    "90cm":[],
                }
            },
            "data":{
                "10Hz" :{
                    "30cm":[],
                    "45cm":[],
                    "60cm":[],
                    "75cm":[],
                    "90cm":[],
                },
                "100Hz":{
                    "30cm":[],
                    "45cm":[],
                    "60cm":[],
                    "75cm":[],
                    "90cm":[],
                },
                "200Hz":{
                    "30cm":[],
                    "45cm":[],
                    "60cm":[],
                    "75cm":[],
                    "90cm":[],
                }
            }
        },
        "20Amp":{
            "noise":{
                "10Hz" :{
                    "30cm":[],
                    "45cm":[],
                    "60cm":[],
                    "75cm":[],
                    "90cm":[],
                },
                "100Hz":{
                    "30cm":[],
                    "45cm":[],
                    "60cm":[],
                    "75cm":[],
                    "90cm":[],
                },
                "200Hz":{
                    "30cm":[],
                    "45cm":[],
                    "60cm":[],
                    "75cm":[],
                    "90cm":[],
                }
            },
            "data":{
                "10Hz" :{
                    "30cm":[],
                    "45cm":[],
                    "60cm":[],
                    "75cm":[],
                    "90cm":[],
                },
                "100Hz":{
                    "30cm":[],
                    "45cm":[],
                    "60cm":[],
                    "75cm":[],
                    "90cm":[],
                },
                "200Hz":{
                    "30cm":[],
                    "45cm":[],
                    "60cm":[],
                    "75cm":[],
                    "90cm":[],
                }
            }
        },
    }

    return Full


def create_waveform_graph(wav_file_dir: str, graph_title: str, graph_file_path: str = None):
    y, sr = librosa.load(wav_file_dir)

    fig, ax = plt.subplots(figsize=(11, 8.5))
    fig.patch.set_facecolor("black")
    ax.set_facecolor("black")

    librosa.display.waveshow(y, sr=sr, axis="s", color="red", ax=ax)

    ax.set_title(graph_title, color="white")
    ax.set_xlabel("Time (Seconds)", color="white")
    ax.set_ylabel("Normalized Amplitude", color="white")

    ax.tick_params(colors="white")

    for spine in ax.spines.values():
        spine.set_color("orange")

    if graph_file_path is not None:
        plt.savefig(graph_file_path, facecolor=fig.get_facecolor(), bbox_inches="tight")
    else:
        plt.show()

    plt.close()


def get_raw_spectro(wav_file: str):
    """
    Extracts a raw STFT spectrogram from a WAV file as decibel-scaled data.

    Loads audio without resampling, computes the linear STFT spectrogram,
    converts to dB scale, and returns as float32 NumPy array.

    Args:
        wav_file (str): Path to input WAV file.

    Returns:
        np.ndarray: Raw spectrogram in dB with shape (freq_bins, time_frames).
    """
    print(f"Grabbing {wav_file}")
    # Load audio without resampling
    y, sr = librosa.load(wav_file)

    # Compute Short-Time Fourier Transform (STFT)
    # This gives the linear frequency domain representation
    print(f"Computing STFT...")
    frequency_domain = librosa.stft(y)

    # Convert magnitude to decibels
    # amplitude_to_db expects the magnitude (absolute value) of the STFT
    print("Converting magnitude to decibels...")
    S_db = librosa.amplitude_to_db(np.abs(frequency_domain), ref=np.max)
    print()
    return S_db.astype(np.float32)
        


def create_spectrogram_from_wav_borderless(
    wav_file_dir: str,
    spectrogram_title: str,
    spectrogram_filepath: str,
    type: int = LOG
) -> str:
    
    """
    Generates borderless spectrogram image(s) from a WAV file without axes or colorbar.
    
    Creates either log-STFT, mel-spectrogram, or both as transparent PNGs with 
    no figure frame. Uses internal helper for saving. Output saved to specified directory.
    
    Args:
        wav_file_dir (str): Path to input WAV file.
        spectrogram_title (str): Base name for output filename(s).
        spectrogram_filepath (str): Directory path for output images.
        type (int): Spectrogram type—LOG(0), MEL(1), or BOTH(2). Default is LOG.
        
    Returns:
        str: Absolute path to the last saved image file.
        
    Raises:
        ValueError: If type parameter is not 0, 1, or 2.
        FileNotFoundError: If input WAV file does not exist.
    """

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
        • Resolution: standard figure size (10x4 inches)
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

    clipped_dir = "C:/Users/Tyler/Desktop/SURI-Project/sensor/WAV_files/Distances/Spliced"

    # waveform_dir = f"{clipped_dir}/waveforms"
    # print(create_amplitude_features(clipped_dir))

    data = dict_from_amplitudes()

    for f in (file for file in Path(clipped_dir).iterdir() if file.suffix.lower() == ".wav"):
        split_string = f.name.split("_")
        geo_type = split_string[0]
        distance = split_string[1]
        freq     = split_string[2]
        amp      = split_string[3]
        sample   = split_string[4]

        data[amp][geo_type][freq][distance].append(create_amplitude_features(f))

    print("testing json formatting...")
    with open("data.json", "w") as f:

        json.dump(data, f, indent=4)  # indent=4 makes it pretty-printed

    



    # TODO: make into own function
    # for f in (file for file in Path(clipped_dir).iterdir() if file.suffix.lower() == ".wav"):
    #     split_string = f.name.split("_")
    #     geo_type = split_string[0]
    #     distance = split_string[1]
    #     freq     = split_string[2]
    #     amp      = split_string[3]

    #     graph_title = f"{geo_type} waveform for {freq} at {amp}, {distance} from geophone".upper()
        
    #     file_title = f"{f.name}_waveform.png"

    #     new_file_dir = f"{waveform_dir}/{file_title}"

    #     #create waveform
    #     print(f"creating waveform for {f.name}")
    #     create_waveform_graph(f, graph_title=graph_title, graph_file_path=new_file_dir)  


    exit()
    file_path = "/Users/tylercrimando/SURI-Project"