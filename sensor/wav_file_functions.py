#!/usr/bin/env python3

import numpy as np
import librosa
import matplotlib.pyplot as plt
import sys
import os
from PIL import Image

from pydub import AudioSegment, effects

SPLICE_FRONT = 0
SPLICE_BACK = 1
SPLICE_MIDDLE = 2

def overlay_wavs(wav1: AudioSegment, wav2: AudioSegment, mixed_dir_and_file: str = "final_mix.wav", format: str = "wav") -> None:
    '''
    Takes AudioSegment objects and overlays them and saves them to user defined directory if specified
    '''

    #mix waves
    mixed_audio = wav1.overlay(wav2)
    mixed_audio.export(mixed_dir_and_file, format=format)

def create_AudioSegment(wav1_path: str) -> AudioSegment:
    try:
        return AudioSegment.from_file(wav1_path)
    except Exception as e:
        raise RuntimeError(f"Failed to load audio from {wav1_path}: {e}")
    
def create_stereo_AudioSegment(wav1_path: str):
    try:
        stereo = AudioSegment.from_file(wav1_path)
    
        # Split into channels
        channel_list = stereo.split_to_mono()

        left, right = channel_list[0], channel_list[1]

        return left, right
    
    except Exception as e:
        raise RuntimeError(f"Failed to load audio from {wav1_path}: {e}")

def splice_AudioSegment(audio: AudioSegment, time: float = 10, mode: int = SPLICE_MIDDLE) -> AudioSegment:

    audio_dur = audio.duration_seconds

    if audio_dur <= time:
        raise ValueError(f"duration of splice must be less then duration of audio segment. Audio segment: {audio.duration_seconds} seconds. Splice segment: {time}")
    
    time_to_cut = audio_dur - time

    time_to_cut *= 1000

    if mode == SPLICE_MIDDLE:
        half_time = time_to_cut/2
        spliced = audio[half_time:-half_time]
    elif mode == SPLICE_FRONT:
        spliced = audio[time_to_cut:]
    elif mode == SPLICE_BACK:
        spliced = audio[:-time_to_cut]
    else:
        raise ValueError(f"mode must be SPLICE_FRONT(0), SPLICE_BACK(1), or SPLICE_MIDDLE(2). Recieved {mode}")
    
    return spliced

def AudioSegment_to_wav(audio: AudioSegment, file_path: str) -> None:
    audio.export(file_path, format="wav")


def phaseinvert_AudioSegment(audio: AudioSegment) -> AudioSegment:
    return effects.invert_phase(audio)

if __name__ == "__main__":
    a = 3