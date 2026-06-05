#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageChops
import sys

import convert_wav_to_spectro as c
import wav_file_functions as w
import interpret_images as interpret

sys.path.insert(1, "/Users/tylercrimando/SURI-Project/utils")

import tutils

trials_per = 3

#Hertz
Hz = ["10","100","200"]

#Voltage peak to peak (don't ask me to explain)
Vpp = ["5", "10", "20"]

MONO = 0
STEREO = 1

file_number = 2
FILE_PREFIX = "WAV_files/InvertPhase_vs_Stereo/260601_"
FILE_TYPE   = ".WAV"

new_dir = "WAV_files/InvertPhase_vs_Stereo/Spectrograms"

#TODO: stop the hardcoding
def split_spectograms(list1_split: str = "mixed_PI", list2_split: str = "mixed_Stereo"):
    """
    Split spectrogram filenames into two lists based on substring matching.
    
    Scans the default spectrograms directory, sorts the files alphabetically, 
    and categorizes them into two lists depending on whether their filenames 
    contain 'list1_split' or 'list2_split'. 
    
    Ensures that both lists have an equal number of items to guarantee 
    one-to-one pairing for comparison later.
    
    Args:
        list1_split: Substring to filter the first list (e.g., 'mixed_PI').
        list2_split: Substring to filter the second list (e.g., 'mixed_Stereo').
        
    Returns:
        tuple[list, list]: Two lists of sorted filenames corresponding to the 
        provided substrings.
        
    Raises:
        ValueError: If the number of files matching each substring does not match.
    """
    all_spectrograms = [f.name for f in Path("WAV_files/InvertPhase_vs_Stereo/Spectrograms").iterdir() if f.is_file()]
    all_spectrograms.sort()

    list1 = []
    list2 = []

    for spectro in all_spectrograms:
        if list1_split in spectro:
            list1.append(spectro)
        elif list2_split in spectro:
            list2.append(spectro)

    if len(list1) != len(list2):
        raise ValueError(f"ERROR: List sizes are not equal! {list1_split} size: {len(list1)}. {list2_split} size {len(list2)}")

    return list1, list2

def create_large_compare_directory( list1_split: str = "mixed_PI", 
                                    list2_split: str = "mixed_Stereo", 
                                    img_path: str = "WAV_files/InvertPhase_vs_Stereo/Spectrograms/",
                                    samples_per: int = 3,
                                    new_dir: str = "Compare"
                                    ):
    """
    Generate a directory of side-by-side comparison images from matched spectrogram pairs.
    
    Retrieves two sets of spectrograms based on filename substrings, validates they are 
    equal in count, and then generates composite images placing each pair next to its 
    difference map. 
    
    Files are grouped into batches (determined by 'samples_per') and organized by the 
    base name of the first file, creating a structured set of comparison results.
    
    Args:
        list1_split: Substring filter for the first set of images (e.g., 'mixed_PI').
        list2_split: Substring filter for the second set of images (e.g., 'mixed_Stereo').
        img_path: Directory containing the source spectrogram files.
        samples_per: Number of unique samples to generate per condition (cycling index).
        new_dir: Name of the subdirectory to create for saving output images.
        
    Returns:
        None. Creates the output directory and saves the comparison images.
        
    Note:
        The output filenames are derived from the first part of the source filename 
        (split by '_') followed by a sample number suffix.
    """    

    list1, list2 = split_spectograms(list1_split=list1_split, list2_split=list2_split)

    new_dir_rel = f"{img_path}/{new_dir}"
    tutils.create_directory(new_dir_rel)


    for i in range(len(list1)):
        img1 = list1[i]
        img2 = list2[i]

        img1_path = f"{img_path}{img1}"
        img2_path = f"{img_path}{img2}"

        sample_num = (i%3)+1 

        new_name = img1.split("_")[0]
        new_image_path = f"{new_dir_rel}/{new_name}_{sample_num}.png"

        interpret.large_image_compare(image1_path=img1_path, image2_path=img2_path, new_image_path=new_image_path)

#function currently assumes that audio_file_list is all mono or all stereo. Maybe change?
#once again, try to stop the hard coding
def splice_and_spectro( file_num_start: int = 2,
                        samples_count:  int = 3,
                        audio_file_list: list = None,
                        type: int = STEREO,
                        splice_time: int = 10,
                        splice_type: int = w.SPLICE_MIDDLE,
                        mix: bool = False,
                        file_prefix: str = "WAV_files/InvertPhase_vs_Stereo/260601_",
                        file_type: str = FILE_TYPE
                        ):
    """
    Process a list of audio files by splicing segments and generating spectrograms.
    
    Iterates through a sequence of numbered files (handling both Mono and Stereo formats),
    extracts a central segment of specified duration, and exports separate WAV files 
    for data and noise channels. It then generates corresponding spectrograms with 
    labels indicating frequency (Hz), voltage (Vpp), sample number, and channel type.
    
    If 'mix' is enabled, it also overlays the data and noise channels to create 
    mixed audio files and their respective spectrograms.
    
    Note:
        This function assumes all files in 'audio_file_list' are either exclusively 
        Mono or exclusively Stereo. The Hz and Vpp labels cycle through predefined 
        global lists ('Hz' and 'Vpp') based on the sample count.
    
    Args:
        file_num_start: Starting index number for the file sequence (zero-padded to 3 digits).
        samples_count: Number of unique samples to generate before cycling Hz/Vpp values.
        audio_file_list: List of filenames to process (used for iteration length only; 
                         actual paths are constructed via 'file_prefix').
        type: Audio format mode (MONO=0 or STEREO=1).
        splice_time: Duration in seconds of the segment to extract from each file.
        splice_type: Splicing strategy (e.g., SPLICE_MIDDLE).
        mix: If True, generate mixed (overlayed) audio and spectrograms as well.
        file_prefix: Base path and prefix for constructing input file paths.
        file_type: File extension (e.g., '.WAV').
        
    Returns:
        None. Writes spliced WAV files and spectrogram images to disk.
        
    Raises:
        TypeError: If audio_file_list is None.
        ValueError: If 'type' is not MONO(0) or STEREO(1).
    """
    
    file_num = file_num_start

    if audio_file_list is None:
        raise TypeError("ERROR: audio_file_list cannot be None")
    if type != 0 and type != 1:
        print(type)
        raise ValueError(f"ERROR: type must be MONO(0) or STEREO(1). Recieved: {type}")

    sample = 1
    currentHz = 0
    currentVpp = 0

    spliced_directory = f"WAV_files/InvertPhase_vs_Stereo/Spliced/"
    tutils.create_directory(spliced_directory)

    if mix:
        mixed_directory = f"WAV_files/InvertPhase_vs_Stereo/Mixed/Spectrograms"
        tutils.create_directory(mixed_directory)

    for _ in range(len(audio_file_list)):
        file_num_str = f"{file_num:03d}"

        if type == MONO:
            
            data_file  = f"{file_prefix}{file_num_str}_Tr1{file_type}"
            noise_file = f"{file_prefix}{file_num_str}_Tr2{file_type}"
            
            print(f"attempting to grab {data_file} and {noise_file} as AudioSegments!\n")
            
            data_AS  = w.create_AudioSegment(data_file)
            noise_AS = w.create_AudioSegment(noise_file)

        else:
            stereo_file  = f"{file_prefix}{file_num_str}{file_type}"

            print(f"attempting to grab {stereo_file} as AudioSegments!\n")

            data_AS, noise_AS = w.create_stereo_AudioSegment(stereo_file)
        
        file_num += 1

        data_AS  = w.splice_AudioSegment(data_AS, splice_time, splice_type)
        noise_AS = w.splice_AudioSegment(noise_AS, splice_time, splice_type)

        spliced_directory = f"WAV_files/InvertPhase_vs_Stereo/Spliced/260601_"

        print("Taking spliced audio and exporting into new wavs for spectrograms\n")
        data_file_spliced  = f"{spliced_directory}{file_num_str}_spliced_data{file_type}"
        w.AudioSegment_to_wav(data_AS, data_file_spliced)
        noise_file_spliced = f"{spliced_directory}{file_num_str}_spliced_noise{file_type}"
        w.AudioSegment_to_wav(noise_AS, noise_file_spliced)

        hertz = Hz[currentHz]
        vol = Vpp[currentVpp]
        print(f"current hertz: {hertz}, current vol: {vol}, current sample: {sample}\n")

        type_str = "MONO" if type == MONO else "STEREO"

        spectro_title_data = f"{hertz}Hz{vol}Vpp_data_{type_str}_sample{sample}"
        spectro_title_noise = f"{hertz}Hz{vol}Vpp_noise_{type_str}_sample{sample}"

        spectro_file_path_data  = new_dir+"/"+spectro_title_data
        spectro_file_path_noise = new_dir+"/"+spectro_title_noise

        data_image  = c.create_spectrogram_from_wav(data_file_spliced, spectro_title_data, new_dir)
        noise_image = c.create_spectrogram_from_wav(noise_file_spliced, spectro_title_noise, new_dir)

        if mix:

            spectro_title_mixed = f"{hertz}Hz{vol}Vpp_mixed_{type_str}_sample{sample}"
            #spectro_file_path_mixed = new_dir+"/"+spectro_title_mixed


            mixed_file = f"260601_{file_num_str}_Mixed{file_type}"
            mixed_directory = f"WAV_files/InvertPhase_vs_Stereo/Mixed"

            
            w.overlay_wavs(data_AS, noise_AS, f"{mixed_directory}/{mixed_file}")

            c.create_spectrogram_from_wav(f"{mixed_directory}/{mixed_file}", spectro_title_mixed, f"{mixed_directory}/Spectrograms")

        # there is a much more elegant way to do this but lets get it working before we optimize
        sample += 1
        if sample > samples_count:
            sample = 1
            currentVpp += 1
            if currentVpp > 2:
                currentVpp = 0
                currentHz +=1
                if currentHz > 2:
                    currentHz = 0
                    break

# this currently only works for Stereo
def splice_and_spectro_with_dict(
                        wav_dict: dict, 
                        splice_time: int = 10,
                        splice_type: int = w.SPLICE_MIDDLE,
                        mix: bool = False,
                        wav_directory: str = None
                        ):

    """
    Process stereo audio files from a dictionary mapping filenames to labels.
    
    Iterates through the provided WAV files, splits each into separate data and 
    noise channel AudioSegments, extracts a central segment of specified duration, 
    and exports them as individual WAV files. It then generates labeled spectrograms 
    for both channels using the 'detail' values from the dictionary.
    
    If 'mix' is enabled, it overlays the data and noise channels and creates an 
    additional mixed audio file with its corresponding spectrogram.
    
    Note:
        This function currently only supports Stereo audio files (monophonic files 
        will fail when attempting to split channels). The wav_directory path handling 
        requires care with trailing slashes—empty strings may cause errors.
    
    Args:
        wav_dict: Dictionary mapping source filenames (keys) to output labels (values).
        splice_time: Duration in seconds of the segment to extract from each file.
        splice_type: Splicing strategy (e.g., SPLICE_MIDDLE, SPLICE_FRONT, SPLICE_BACK).
        mix: If True, generate overlayed (mixed) audio and spectrograms in addition 
             to the separated channel outputs.
        wav_directory: Base directory containing the source WAV files.
        
    Returns:
        None. Writes spliced WAV files and spectrogram images to subdirectories 
        under 'wav_directory' (Spliced/, Spectrograms/, Mixed/).
        
    Raises:
        TypeError: If wav_dict or wav_directory is None.
        RuntimeError: If any file fails to load or process (from underlying functions).
    """

    if wav_dict is None:
        raise TypeError("ERROR: wav_dict cannot be None")
    if wav_directory is None:
        raise TypeError("ERROR: wav_directory cannot be None")
    
    spliced_directory = f"{wav_directory}/Spliced/"
    tutils.create_directory(spliced_directory)

    spectrogram_directory = f"{wav_directory}/Spectrograms/"
    tutils.create_directory(spectrogram_directory)

    if mix:
        mixed_directory = f"{wav_directory}/Mixed/Spectrograms"
        tutils.create_directory(mixed_directory)

    if wav_directory[-1] == '/':
        wav_directory = wav_directory[:-1]

    #key, value
    for wav_file, detail in wav_dict.items():
        stereo_file  = f"{wav_directory}/{wav_file}" # maybe make the function handle if user already pet the slash instead of hard coding it?

        print(f"attempting to grab {stereo_file} as AudioSegments!\n")

        data_AS, noise_AS = w.create_stereo_AudioSegment(stereo_file)

        data_AS  = w.splice_AudioSegment(data_AS, splice_time, splice_type)
        noise_AS = w.splice_AudioSegment(noise_AS, splice_time, splice_type)

        print("Taking spliced audio and exporting into new wavs for spectrograms\n")

        data_file_spliced  = f"{spliced_directory}data_{wav_file}"
        noise_file_spliced = f"{spliced_directory}noise_{wav_file}"


        w.AudioSegment_to_wav(data_AS, data_file_spliced)
        w.AudioSegment_to_wav(noise_AS, noise_file_spliced)

        data_image = c.create_spectrogram_from_wav(data_file_spliced, f"{detail}_data", spectrogram_directory)
        noise_image = c.create_spectrogram_from_wav(noise_file_spliced, f"{detail}_noise", spectrogram_directory)

        if mix:
            spectro_title_mixed = f"{detail}_mixed"
            mixed_file = f"mixed_{wav_file}"
            mixed_directory = f"{wav_directory}/Mixed"
            w.overlay_wavs(data_AS, noise_AS, f"{mixed_directory}/{mixed_file}")
            c.create_spectrogram_from_wav(f"{mixed_directory}/{mixed_file}", spectro_title_mixed, f"{mixed_directory}/Spectrograms")

def rename_and_splice_and_spectro(wav_dict: dict, 
                        splice_time: int = 10,
                        splice_type: int = w.SPLICE_MIDDLE,
                        wav_directory: str = None,
                        rename_or_copy: int = tutils.RENAME
                        ):
    """
    Rename (or copy) stereo audio files based on a dictionary, then process them 
    by splicing and generating spectrograms.
    
    First, applies a batch rename or copy operation to the source files using the 
    mapping in 'wav_dict'. Then, it scans the target directory for files containing 
    "Hz" in their names, sorts them, and processes each as a stereo pair. Each file 
    is spliced into data and noise channels, saved as new WAVs, and converted into 
    labeled spectrograms derived from the filename stem.
    
    Note:
        This function currently assumes all processed files are Stereo. It also 
        relies on the presence of "Hz" in filenames to identify valid targets for 
        processing. The output labels are generated by stripping the last 4 characters 
        (assumed extension) from the filename.
    
    Args:
        wav_dict: Dictionary mapping original filenames (keys) to new labels/values (values).
        splice_time: Duration in seconds of the segment to extract from each file.
        splice_type: Splicing strategy (e.g., SPLICE_MIDDLE).
        wav_directory: Base directory containing the source WAV files.
        rename_or_copy: Action to perform first—'tutils.RENAME' to rename files in place, 
                        or 'tutils.COPY' to duplicate them into a 'COPY/' subdirectory.
        
    Returns:
        None. Writes renamed/copied files, spliced WAVs, and spectrograms to disk.
        
    Raises:
        TypeError: If wav_dict or wav_directory is None.
        ValueError/IndexError: If path handling fails or filenames don't meet assumptions.
    """

    spliced_directory = f"{wav_directory}/Spliced/"
    tutils.create_directory(spliced_directory)

    spectrogram_directory = f"{wav_directory}/Spectrograms/"
    tutils.create_directory(spectrogram_directory)

    if wav_directory[-1] == '/':
        wav_directory = wav_directory[:-1]

    tutils.batch_rename_and_copy(directory_of_files = wav_directory, wav_dict=wav_dict, action=rename_or_copy)

    #tremendously hacky way to deal with this right now that works only with the assumption of Hz
    if rename_or_copy == tutils.RENAME:
        all_wavs = [f.name for f in Path(f"{wav_directory}").iterdir() if (f.is_file() and "Hz" in f.name)]
    else:
        #Copying currently doesn't work. Will attempt to fix
        all_wavs = [f.name for f in Path(f"{wav_directory}/COPY").iterdir() if (f.is_file() and "Hz" in f.name)]

    all_wavs.sort()

    for wav_file in all_wavs:
        stereo_file  = f"{wav_directory}/{wav_file}"

        print(f"attempting to grab {stereo_file} as AudioSegments!\n")

        data_AS, noise_AS = w.create_stereo_AudioSegment(stereo_file)

        data_AS  = w.splice_AudioSegment(data_AS, splice_time, splice_type)
        noise_AS = w.splice_AudioSegment(noise_AS, splice_time, splice_type)

        print("Taking spliced audio and exporting into new wavs for spectrograms\n")

        data_file_spliced  = f"{spliced_directory}data_{wav_file}"
        noise_file_spliced = f"{spliced_directory}noise_{wav_file}"


        w.AudioSegment_to_wav(data_AS, data_file_spliced)
        w.AudioSegment_to_wav(noise_AS, noise_file_spliced)

        data_image = c.create_spectrogram_from_wav(data_file_spliced, f"{wav_file[:-4]}_data", spectrogram_directory)
        noise_image = c.create_spectrogram_from_wav(noise_file_spliced, f"{wav_file[:-4]}_noise", spectrogram_directory)

def spectrograms_from_dir(wav_directory: str = None):
    """
    Generate spectrograms for all audio files in a directory.
    
    Scans the provided directory for all files, sorts them alphabetically, 
    and creates a spectrogram for each one. The output images are saved in 
    a 'spectrograms' subdirectory with filenames derived from the source 
    audio files (extension stripped).
    
    Note:
        This function assumes files have a 4-character extension (e.g., '.WAV'). 
        It processes all files found in the directory regardless of format—ensure 
        only valid audio files are present to avoid errors.
    
    Args:
        wav_directory: Path to the directory containing audio files to process.
        
    Returns:
        None. Creates a 'spectrograms' subdirectory and saves the generated images.
        
    Raises:
        TypeError: If wav_directory is None.
        RuntimeError: If any file fails to load or process (from underlying spectrogram function).
    """

    all_wavs = [f.name for f in Path(wav_directory).iterdir() if f.is_file()]
    all_wavs.sort()

    tutils.create_directory(f"{wav_directory}/spectrograms")

    spectrogram_directory = f"{wav_directory}/spectrograms"

    for wav in all_wavs:
        print(f"Creating spectrogram for {wav}")
        wav_file = f"{wav_directory}/{wav}"
        c.create_spectrogram_from_wav(wav_file_dir=wav_file, spectrogram_title=wav[:-4], spectrogram_filepath=spectrogram_directory)

    



    
    




if __name__ == "__main__":

    spectrograms_from_dir("/Users/tylercrimando/SURI-Project/sensor/WAV_files/Distances/Spliced/averaged", )

    # wav_dict = tutils.dict_wav_from_csv("../docs/6-3-26_Recording_Notes.csv")

    # rename_and_splice_and_spectro(rename_or_copy=tutils.RENAME, wav_dict=wav_dict, splice_time=30, wav_directory="WAV_files/Distances")



    # NOTE: THIS IS OLD CODE BEFORE ME USING CSVS FOR GRABBING WAVS. KEEPING FOR NOW

    # tutils.create_directory(new_dir)

    # all_wavs = [f.name for f in Path("WAV_files/InvertPhase_vs_Stereo").iterdir() if f.is_file()]
    # all_wavs.sort()

    # print(len(all_wavs))


    # #would love if this wasn't hardcoded, but for now it'll do. Maybe down the line so this is reusable, I'll have some regex
    # # to comprehend what's going on
    # mono_with_pi = all_wavs[:54]
    # stereo_wo_pi = all_wavs[54:]

    # print("Iterating over mono audio\n")

    # splice_and_spectro(audio_file_list=mono_with_pi, type = MONO, mix=True)
    
    # print("Iterating over stereo audio\n")
    
    # splice_and_spectro(audio_file_list=stereo_wo_pi, file_num_start=29, mix=True)

    # create_large_compare_directory(list1_split="mixed_PI", list2_split="mixed_Stereo", new_dir="Stereo_vs_Mono_Comparisons")

    # create_large_compare_directory(list1_split="data", list2_split="noise", new_dir="Data_vs_Noise_Comparisons")















