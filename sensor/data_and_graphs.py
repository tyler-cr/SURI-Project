import numpy as np
import librosa
import matplotlib.pyplot as plt
import sys
import os
import json
from PIL import Image
from pathlib import Path
import csv
from matplotlib.lines import Line2D



def json_to_dict(json_path:str):
    with open(json_path, 'r') as f:
        return json.load(f)

#TODO: impliment
def create_amp_csv(json_path:str, table_img_path:None):
    for freq in [10, 100, 200]:
        a = 5

#TODO: impliment
def list_to_csv(input_list: list):
    a = 5


#TODO: Remove hard coded vals and make scalable
def dir_to_csvs():
    test_json_path = "C:/Users/Tyler/Desktop/SURI-Project/sensor/WAV_files/Distances/Spliced/amplitude/amplitude_data.json"
    clipped_dir = "C:/Users/Tyler/Desktop/SURI-Project/sensor/WAV_files/Distances/Spliced"

    Table10Hz  = []
    Table100Hz = []
    Table200Hz = []

    for f in (file for file in Path(clipped_dir).iterdir() if file.suffix.lower() == ".wav"):
        split_string = f.name.split("_")
        geo_type = split_string[0]
        distance = split_string[1]
        freq     = split_string[2]
        amp      = split_string[3]
        sample   = split_string[4]

        peak_amp, RMS_amp = create_amplitude_features(f)

        row = [f.name, distance, amp, peak_amp, RMS_amp]

        if   freq == "10Hz"  : Table10Hz.append(row)
        elif freq == "100Hz" : Table100Hz.append(row)
        else:                  Table200Hz.append(row)

    with open("10Hz_Amplitude_Table.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["file name", "distance", "amp", "peak", "RMS"])
        writer.writerows(Table10Hz)

    with open("100Hz_Amplitude_Table.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["file name", "distance", "amp", "peak", "RMS"])
        writer.writerows(Table100Hz)

    with open("200Hz_Amplitude_Table.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["file name", "distance", "amp", "peak", "RMS"])
        writer.writerows(Table200Hz)

def create_amplitude_features(wav_file_dir:str):
    y, sr = librosa.load(wav_file_dir)
    peak_amp = float(np.max(y))
    RMS_amp = float(np.sqrt(np.mean(y**2)))

    return peak_amp, RMS_amp

#TODO: Impliment better. Right now it's v bad
def create_amp_dot_plots(clipped_dir: str = "C:/Users/Tyler/Desktop/SURI-Project/sensor/WAV_files/Distances/Spliced"):
    Table10Hz  = []
    Table100Hz = []
    Table200Hz = []

    for f in (file for file in Path(clipped_dir).iterdir() if file.suffix.lower() == ".wav"):
        split_string = f.name.split("_")
        geo_type = split_string[0]
        distance = split_string[1]
        freq     = split_string[2]
        amp      = split_string[3]
        sample   = split_string[4]

        peak_amp, RMS_amp = create_amplitude_features(f)

        row = [f.name, distance, amp, peak_amp, RMS_amp, geo_type]

        if   freq == "10Hz"  : Table10Hz.append(row)
        elif freq == "100Hz" : Table100Hz.append(row)
        else:                  Table200Hz.append(row)
    

    color_map = {
        "5Amp":  "blue",
        "10Amp": "green",
        "20Amp": "red"
    }

    #10,100,200
    i=0
    for freq_table in [Table10Hz, Table100Hz, Table200Hz]:
        if i == 0: freq_str = "10Hz"
        elif i==1: freq_str = "100Hz"
        else:      freq_str = "200Hz"

        print("working on next table")
        #Peak vs RMS
        x_vals = [val[1] for val in freq_table if val[-1] != "noise"]
        colors = [color_map[val[2]] for val in freq_table if val[-1] != "noise"]
        for amp_type in ["peak", "RMS"]:
            print(f"working on {amp_type} graph")

            if amp_type == "peak":
                y_vals = [val[3] for val in Table10Hz if val[-1] != "noise"]
            else:
                y_vals = [val[4] for val in Table10Hz if val[-1] != "noise"]

    

            fig, ax = plt.subplots(figsize=(11, 8.5))
            fig.patch.set_facecolor("black")
            ax.set_facecolor("black")
    
            scatter = plt.scatter(x_vals, y_vals, c=colors)

            legend_handles = [
                Line2D([0], [0], marker="o", linestyle="", color=color, label=amp)
                for amp, color in color_map.items()
            ]

            ax.legend(handles=legend_handles, title="Vpp")

            ax.set_xlabel("distance from wave generator", color="white")
            ax.set_ylabel("peak amplitude", color="white")
            ax.tick_params(colors="white")

            for spine in ax.spines.values():
                spine.set_color("orange")

            ax.set_title(f"{freq_str}: {amp_type} amplitude vs distance from wave generator", color="white")
            plt.savefig(f"{freq_str}_{amp_type}_amp_vs_distance.png", facecolor=fig.get_facecolor(), bbox_inches="tight")
            
        i += 1


if __name__ == "__main__":
    create_amp_dot_plots()

