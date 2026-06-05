#!/usr/bin/env python3

import os
import csv
import shutil

from pathlib import Path

RENAME = 0
COPY = 1

def create_directory(new_dir: str = "WAV_files/InvertPhase_vs_Stereo/Spectrograms"):
    check_for_path = Path(new_dir)
    if check_for_path.is_dir():
        print("Destination directory already exists!")
    else:
        Path(new_dir).mkdir(parents=True, exist_ok=True)

#currently has to be formatted csv with Distance,Freq,Amplitude,Sample,Notes,,File Name
def dict_wav_from_csv(csv_file_path: str = None) -> dict:
    """
    Given a csv file in a specific form,
    returns a dictionary that maps wav file names to detailed string
    """

    dict_wav = {}
    
    if csv_file_path is None:
        raise TypeError(f"ERROR: csv_file_path cannot be none! Recieved csv_file_path: {csv_file_path}")

    with open(csv_file_path, mode='r') as file:
        reader = csv.DictReader(file)

        for row in reader:
            dict_wav[f"{row['File Name']}.wav"] = f"{row['Distance']}_{row['Freq']}_{row['Amplitude']}Amp_{row['Sample']}"


    return dict_wav

# currently assumes we're working with wav files
def batch_rename_and_copy(csv_file_path: str = None, directory_of_files: str = None, action: int = COPY, wav_dict: dict = None) -> None:

    if (action != COPY and action != RENAME):
        raise ValueError(f"ERROR: action must either be RENAME(0) or COPY(1). Recieved {action}")

    if type(directory_of_files) is not str:
        raise TypeError(f"ERROR: Directory of files must be given as string. Recieved {type(directory_of_files)}")
    
    if wav_dict is None and csv_file_path is not None:
        wav_dict = dict_wav_from_csv(csv_file_path)
    elif wav_dict is None:
        raise ValueError("ERROR: Either 'wav_dict' must be provided or 'csv_file_path'.")

    if action == COPY: create_directory(f"{directory_of_files}/COPY")

    if directory_of_files[-1] == '/': directory_of_files = directory_of_files[:-1]

    action_str = "copied" if action == COPY else "renamed"

    for wav_file, detail in wav_dict.items():
        
        if action == COPY:
            try: shutil.copy(f"{directory_of_files}/{wav_file}", f"{directory_of_files}/COPY/{detail}.wav")
            except: print(f"unable to copy {wav_file}")
        else:
            try: os.rename(f"{directory_of_files}/{wav_file}", f"{directory_of_files}/{detail}.wav")
            except: print(f"unable to rename {wav_file}")
        
        
        print(f"{action_str} {wav_file} to {detail}.wav")

if __name__ == "__main__":
    print("TESTING batch_rename_csv\n")
    batch_rename_and_copy(action= tutils.COPY, csv_file_path= "docs/6-3-26_Recording_Notes.csv", directory_of_files="/Users/tylercrimando/SURI-Project/sensor/WAV_files/Distances")