#!/usr/bin/env python3

import csv

from pathlib import Path

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

if __name__ == "__main__":
    print("TESTING DICT_WAV_FROM_CSV\n")
    print_me = dict_wav_from_csv("docs/6-3-26_Recording_Notes.csv")
    print(print_me)