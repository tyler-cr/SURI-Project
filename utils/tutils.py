#!/usr/bin/env python3

import os
import csv
import shutil

from pathlib import Path

RENAME = 0
COPY = 1

def create_directory(new_dir: str = "WAV_files/InvertPhase_vs_Stereo/Spectrograms"):
    """
    Ensure a directory exists, creating it if necessary.
    
    Checks if the specified path already exists as a directory. If it does, 
    prints a notification message and exits without changes. If it doesn't 
    exist, creates the directory (including any required parent directories).
    
    This function acts as a safe wrapper around standard directory creation, 
    preventing errors if the target already exists while ensuring all nested 
    folders are built automatically.
    
    Args:
        new_dir: The path of the directory to check or create. 
                 Defaults to 'WAV_files/InvertPhase_vs_Stereo/Spectrograms'.
        
    Returns:
        None.
        
    Note:
        Does not raise an error if the directory already exists; simply logs 
        a message and continues.
    """

    check_for_path = Path(new_dir)
    if check_for_path.is_dir():
        print("Destination directory already exists!\n")
    else:
        Path(new_dir).mkdir(parents=True, exist_ok=True)

#currently has to be formatted csv with Distance,Freq,Amplitude,Sample,Notes,,File Name
def dict_wav_from_csv(csv_file_path: str = None) -> dict:
    """
    Parse a CSV file and return a dictionary mapping WAV filenames to metadata labels.
    
    Reads a CSV file with specific required columns ('File Name', 'Distance', 'Freq', 
    'Amplitude', 'Sample') and constructs a dictionary where keys are WAV filenames 
    (with .wav extension appended) and values are formatted metadata strings.
    
    The output value format follows: '{Distance}_{Freq}_{Amplitude}Amp_{Sample}'
    
    Note:
        The CSV must be properly formatted with the exact column headers mentioned 
        above. Missing columns or malformed data will cause errors during parsing.
    
    Args:
        csv_file_path: Path to the input CSV file containing recording metadata.
        
    Returns:
        dict: Mapping of 'filename.wav' → 'Distance_Freq_AmpAmplitude_Sample' string.
        
    Raises:
        TypeError: If csv_file_path is None.
        KeyError: If any required column is missing from the CSV.
        FileNotFoundError: If the CSV file path does not exist.
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
    """
    Batch rename or copy WAV files based on metadata from a CSV or provided dictionary.
    
    Iterates through a mapping of original filenames to new labels (either loaded from 
    a CSV via 'dict_wav_from_csv' or passed directly). Depending on the 'action' setting, 
    it either renames files in place or copies them into a 'COPY/' subdirectory with 
    their new names.
    
    Includes basic error handling: if a specific file operation fails, it prints a warning 
    but continues processing the rest of the list to prevent total batch failure.
    
    Note:
        - If both 'csv_file_path' and 'wav_dict' are provided, 'wav_dict' takes precedence 
          (CSV is ignored).
        - Requires 'directory_of_files' to be a non-empty string.
        - The trailing slash on the directory path is automatically handled.
    
    Args:
        csv_file_path: Path to a CSV file containing filename-to-metadata mappings.
        directory_of_files: Base directory containing the source WAV files.
        action: Operation mode—'RENAME' (0) to rename in place, or 'COPY' (1) to duplicate 
                into a subdirectory.
        wav_dict: Optional pre-loaded dictionary mapping filenames to new names. 
                  If provided, 'csv_file_path' is ignored.
        
    Returns:
        None. Performs file system operations directly.
        
    Raises:
        ValueError: If 'action' is invalid or if neither 'wav_dict' nor 'csv_file_path' is provided.
        TypeError: If 'directory_of_files' is not a string or is empty.
    """


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


    #batch_rename_and_copy(action= COPY, csv_file_path= "docs/6-3-26_Recording_Notes.csv", directory_of_files="/Users/tylercrimando/SURI-Project/sensor/WAV_files/Distances")