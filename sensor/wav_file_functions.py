#!/usr/bin/env python3

from pathlib import Path

import numpy as np
from scipy.io import wavfile
import librosa
import matplotlib.pyplot as plt
import sys
import os
import random
from scipy.io.wavfile import read, write
from PIL import Image

sys.path.insert(1, "/Users/tylercrimando/SURI-Project/utils")

import tutils

from pydub import AudioSegment, effects

SPLICE_FRONT = 0
SPLICE_BACK = 1
SPLICE_MIDDLE = 2

def overlay_wavs(wav1: AudioSegment, wav2: AudioSegment, mixed_dir_and_file: str = "final_mix.wav", format: str = "wav") -> None:
    """
    Overlays two AudioSegments and exports the result.

    Args:
        wav1: The base audio segment.
        wav2: The audio segment to overlay on top of wav1.
        mixed_dir_and_file: Output file path (default: 'final_mix.wav').
        format: Export format (default: 'wav').

    Returns:
        None. Writes the mixed audio directly to the specified file.
    """

    #mix waves
    mixed_audio = wav1.overlay(wav2)
    mixed_audio.export(mixed_dir_and_file, format=format)

def create_AudioSegment(wav1_path: str) -> AudioSegment:
    """
    Loads an audio file into an AudioSegment object.

    Args:
        wav1_path: Path to the audio file to load.

    Returns:
        An AudioSegment object representing the loaded audio.

    Raises:
        RuntimeError: If the file cannot be found, is corrupted, or fails to load.
    """

    try:
        return AudioSegment.from_file(wav1_path)
    except Exception as e:
        raise RuntimeError(f"Failed to load audio from {wav1_path}: {e}")
    
def create_stereo_AudioSegment(wav1_path: str):
    """
    Loads a stereo audio file and splits it into separate left and right channels.

    Args:
        wav1_path: Path to the stereo audio file.

    Returns:
        A tuple containing two AudioSegment objects: (left_channel, right_channel).

    Raises:
        RuntimeError: If the file cannot be loaded or does not contain exactly two channels.
    """
    try:
        stereo = AudioSegment.from_file(wav1_path)
    
        # Split into channels
        channel_list = stereo.split_to_mono()

        left, right = channel_list[0], channel_list[1]

        return left, right
    
    except Exception as e:
        raise RuntimeError(f"Failed to load audio from {wav1_path}: {e}")

def splice_AudioSegment(audio: AudioSegment, time: float = 10, mode: int = SPLICE_MIDDLE) -> AudioSegment:
    """
    Extracts a central, leading, or trailing segment of a specified duration from an AudioSegment.

    The function removes audio from the start, end, or both sides to leave exactly 'time' seconds.

    Args:
        audio: The source AudioSegment to splice.
        time: The desired duration (in seconds) of the resulting segment.
        mode: The splicing strategy:
              - SPLICE_MIDDLE: Keeps the center portion (removes equal time from start/end).
              - SPLICE_FRONT: Keeps the beginning portion (removes time from the end).
              - SPLICE_BACK: Keeps the ending portion (removes time from the start).

    Returns:
        A new AudioSegment of length 'time'.

    Raises:
        ValueError: If 'time' is greater than or equal to the audio duration, or if 'mode' is invalid.
    """

    audio_dur = audio.duration_seconds

    if audio_dur <= time:
        raise ValueError(f"duration of splice must be less then duration of audio segment. Audio segment: {audio.duration_seconds} seconds. Splice segment: {time}")
    
    time_to_cut = audio_dur - time

    time_to_cut *= 1000
    time_to_cut = int(time_to_cut)

    if mode == SPLICE_MIDDLE:
        half_time = int(time_to_cut/2)
        spliced = audio[half_time:-half_time]
    elif mode == SPLICE_FRONT:
        spliced = audio[time_to_cut:]
    elif mode == SPLICE_BACK:
        spliced = audio[:-time_to_cut]
    else:
        raise ValueError(f"mode must be SPLICE_FRONT(0), SPLICE_BACK(1), or SPLICE_MIDDLE(2). Recieved {mode}")
    
    return spliced

def AudioSegment_to_wav(audio: AudioSegment, file_path: str) -> None:
    """
    Exports an AudioSegment object to a WAV file.

    Args:
        audio: The AudioSegment object to export.
        file_path: The destination path (including filename) for the WAV file.

    Returns:
        None. Writes the file directly to disk.
    """

    audio.export(file_path, format="wav")

# assumes that wav files are already of the same length
def wav_average(wav_list: list = None, output_file: str = "averaged_wav.wav"):
    """
    Generate an averaged WAV file from multiple input audio tracks.
    
    Reads all WAV files in the provided list, verifies they share the same 
    sample rate, computes the arithmetic mean of their audio data at each 
    sample point, and exports the result as a single averaged WAV file.
    
    The output preserves the original audio data type and sample rate for 
    compatibility with downstream processing.
    
    Note:
        All input files must have matching sample rates, otherwise a ValueError 
        is raised. Files must also be the same length (handled by NumPy's mean).
    
    Args:
        wav_list: List of paths to WAV files to average.
        output_file: Destination path for the averaged WAV file. Defaults to 'averaged_wav.wav'.
        
    Returns:
        None. Writes the averaged audio file to disk.
        
    Raises:
        TypeError: If wav_list is not a list.
        ValueError: If sample rates between files do not match.
        RuntimeError: If any file fails to load (from underlying wavfile.read).
    """

    if type(wav_list) is not list:
        raise TypeError(f"ERROR: wav_list must be of type list. Recieved: {type(wav_list)}")

    sample_rate, baseline_data = wavfile.read(wav_list[0])

    audio_tracks = [baseline_data]

    for wav_file in wav_list[1:]:
        sr, data = wavfile.read(wav_file)

        if sr != sample_rate:
            raise ValueError(f"ERROR: Sample rates must all match. Expected rate: {sample_rate}, Recieved {sr} from {wav_file}")
        
        audio_tracks.append(data)
    
    averaged_audio = np.mean(audio_tracks, axis=0)
    final_audio = averaged_audio.astype(baseline_data.dtype)

    wavfile.write(output_file, sample_rate, final_audio)

def phaseinvert_AudioSegment(audio: AudioSegment) -> AudioSegment:
    """
    Inverts the phase of an AudioSegment by multiplying sample values by -1.

    Args:
        audio: The AudioSegment to invert.

    Returns:
        A new AudioSegment with inverted phase.

    Note:
        Phase-inverted audio is often used for noise cancellation when mixed
        with the original signal.
    """

    return effects.invert_phase(audio)

def augment_wav(wav_file: str):
    sample_rate, wav_array = wavfile.read(wav_file)
    original_dtype = wav_array.dtype
    original_length = len(wav_array)
    
    if np.issubdtype(original_dtype, np.integer):
        max_int = np.iinfo(original_dtype).max
        wav_array_float = wav_array.astype(np.float32) / max_int
    else:
        wav_array_float = wav_array.astype(np.float32)
        max_int = 1.0
    
    if random.random() < 0.67:
        percent = random.uniform(-30, 30) / 100.0
        shift_samples = int(percent * original_length)
        wav_array_float = np.roll(wav_array_float, shift=shift_samples)

    if random.random() < 0.40:
        amplitude = 0.1 * (wav_array_float.max() - wav_array_float.min())
        noise = amplitude * (np.random.random(len(wav_array_float)) - 0.5)
        wav_array_float += noise

    if random.random() < 0.40:
        rate = 0.5 + random.random()
        stretched = librosa.effects.time_stretch(wav_array_float, rate=rate)
        
        if len(stretched) > original_length:
            wav_array_float = stretched[:original_length]
        else:
            padded = np.zeros(original_length, dtype=np.float32)
            padded[:len(stretched)] = stretched
            wav_array_float = padded
    
    wav_array_float = np.clip(wav_array_float, -1.0, 1.0)
    
    if np.issubdtype(original_dtype, np.integer):
        wav_array_final = (wav_array_float * max_int).astype(original_dtype)
    else:
        wav_array_final = wav_array_float
    
    return sample_rate, wav_array_final, wav_array_final.dtype


def batch_augment_wav(wav_dir: str = None, count_per: int = 10):

    if wav_dir is None:
        raise TypeError(f"ERROR: wav_dir must be filled!")
    
    if wav_dir[-1] == "/": wav_dir = wav_dir[:-1]

    wav_list = [f.name for f in Path(wav_dir).iterdir() if (f.is_file()) and f.name[0] != '.']
    tutils.create_directory(f"{wav_dir}/augmented")

    for wav_file in wav_list:

        for i in range(count_per):
            augmented_file_path = f"{wav_dir}/augmented/{wav_file[:-4]}_{i:03d}.wav"

            sr, augmented_audio, dtype = augment_wav(f"{wav_dir}/{wav_file}")
            final_audio = augmented_audio.astype(dtype)

            write(augmented_file_path, sr, final_audio)

            print(f"Saved augmented file: {augmented_file_path}")


    



if __name__ == "__main__":
    wav_dir = "/Users/tylercrimando/Downloads/ESC-50-master/audio/5-263831-A-6.wav"
    
    batch_augment_wav("/Users/tylercrimando/Desktop/demo")

    #TODO: make this into a function
    # cur_dir = "WAV_files/Distances/Spliced"
    
    # test_path = "/Users/tylercrimando/SURI-Project/sensor/WAV_files/Distances/Spliced"

    # # Get list of filenames only
    # test_list = [f.name for f in Path(test_path).iterdir() if (f.is_file() and "Hz" in f.name)]
    # test_list.sort()

    # # Create destination directory safely
    # dest_dir = f"{test_path}/averaged"
    # tutils.create_directory(dest_dir)

    # num_batches = len(test_list) // 3
    
    # for i in range(num_batches):
    #     # Get the 3 filenames for this batch
    #     batch_filenames = test_list[3*i : 3*i+3]
        
    #     # Create full paths for reading ONLY (do not modify the original filenames list)
    #     batch_paths = [f"{test_path}/{fname}" for fname in batch_filenames]
        
    #     # Determine the base name for the output file using the FIRST file's name
    #     # Use .stem to remove extension cleanly, regardless of length
    #     base_name = Path(batch_filenames[0]).stem[:-2]
        
    #     output_filename = f"{base_name}_average.wav"
    #     output_full_path = f"{dest_dir}/{output_filename}"
        
    #     print(f"Averaging batch starting with: {base_name}")

    #     try:
    #         wav_average(batch_paths, output_full_path)
    #         print(f"Successfully saved to: {output_full_path}\n")
    #     except Exception as e:
    #         print(f"Error processing batch {i}: {e}\n")