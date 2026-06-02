#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageChops

import convert_wav_to_spectro as c
import wav_file_functions as w

trials_per = 3

#Hertz
Hz = ["10","100","200"]

#Voltage peak to peak (don't ask me to explain)
Vpp = ["5", "10", "20"]

file_number = 2
file_prefix = "WAV_files/InvertPhase_vs_Stereo/260601_"
file_type   = ".WAV"

new_dir = "WAV_files/InvertPhase_vs_Stereo/Spectrograms"

if __name__ == "__main__":

    #Need to handle creating Spectrograms folder / checking if it already exists
    check_for_path = Path(new_dir)
    if check_for_path.is_dir():
        print("Destination directort already exists!")
    else:
        Path(new_dir).mkdir(parents=True, exist_ok=True)

    all_wavs = [f.name for f in Path("WAV_files/InvertPhase_vs_Stereo").iterdir() if f.is_file()]
    all_wavs.sort()


    #would love if this wasn't hardcoded, but for now it'll do. Maybe down the line so this is reusable, I'll have some regex
    # to comprehend what's going on
    mono_with_pi = all_wavs[:54]
    stereo_wo_pi = all_wavs[54:]

    print("Iterating over mono audio\n")

    file_num = 2
    sample = 1
    currentHz = 0
    currentVpp = 0

    for file in range(len(mono_with_pi)//2):
        file_num_str = f"{file_num:03d}"

        data_file  = f"{file_prefix}{file_num_str}_Tr1{file_type}"
        noise_file = f"{file_prefix}{file_num_str}_Tr2{file_type}"

        print(f"attempting to grab {data_file} and {noise_file} as AudioSegments!\n")
        data_AS  = w.create_AudioSegment(data_file)
        noise_AS = w.create_AudioSegment(noise_file)
        file_num += 1

        data_AS  = w.splice_AudioSegment(data_AS)
        noise_AS = w.splice_AudioSegment(noise_AS)

        print("Taking spliced audio and exporting into new wavs for spectrograms\n")
        data_file_spliced  = f"{file_prefix}{file_num_str}_spliced_Tr1{file_type}"
        w.AudioSegment_to_wav(data_AS, data_file_spliced)
        noise_file_spliced = f"{file_prefix}{file_num_str}_spliced_Tr2{file_type}"
        w.AudioSegment_to_wav(noise_AS, noise_file_spliced)

        hertz = Hz[currentHz]
        vol = Vpp[currentVpp]
        print(f"current hertz: {hertz}, current vol: {vol}, current sample: {sample}\n")

        spectro_title_data = f"{hertz}Hz{vol}Vpp_data_PI_sample{sample}"
        spectro_title_noise = f"{hertz}Hz{vol}Vpp_noise_PI_sample{sample}"

        spectro_file_path_data  = new_dir+"/"+spectro_title_data
        spectro_file_path_noise = new_dir+"/"+spectro_title_noise

        data_image  = c.create_spectrogram_from_wav(data_file_spliced, spectro_title_data, new_dir)
        noise_image = c.create_spectrogram_from_wav(noise_file_spliced, spectro_title_noise, new_dir)

        #Mix
        print("Mixing spliced data and noise AudioSegments")
        
        spectro_title_mixed = f"{hertz}Hz{vol}Vpp_mixed_PI_sample{sample}"
        spectro_file_path_mixed = new_dir+"/"+spectro_title_mixed

        mixed_file = f"{file_prefix}{file_num_str}_Mixed{file_type}"
        w.overlay_wavs(data_AS, noise_AS, mixed_file)

        mixed_image = c.create_spectrogram_from_wav(mixed_file, spectro_title_mixed, new_dir)

        # there is a much more elegant way to do this but lets get it working before we optimize
        sample += 1
        if sample > 3:
            sample = 1
            currentVpp += 1
            if currentVpp > 2:
                currentVpp = 0
                currentHz +=1
                if currentHz > 2:
                    currentHz = 0
                    print("We SHOULD be done with PI now...")
    print("confirmed done w/ PI. Nice :D\n")

    sample = 1
    currentHz = 0
    currentVpp = 0

    print("Beginning iterating over stereo\n")
    for file in range(len(stereo_wo_pi)):
        file_num_str = f"{file_num:03d}"
        stereo_file  = f"{file_prefix}{file_num_str}{file_type}"

        print(f"Attempting to grab stero of {stereo_file}")
        data_AS, noise_AS = w.create_stereo_AudioSegment(stereo_file)
        file_num += 1

        data_AS  = w.splice_AudioSegment(data_AS)
        noise_AS = w.splice_AudioSegment(noise_AS)

        print("Taking spliced audio and exporting into new wavs for spectrograms\n")
        data_file_spliced  = f"{file_prefix}{file_num_str}_spliced_data{file_type}"
        w.AudioSegment_to_wav(data_AS, data_file_spliced)
        noise_file_spliced = f"{file_prefix}{file_num_str}_spliced_noise{file_type}"
        w.AudioSegment_to_wav(noise_AS, noise_file_spliced)

        hertz = Hz[currentHz]
        vol = Vpp[currentVpp]
        print(f"current hertz: {hertz}, current vol: {vol}, current sample: {sample}\n")

        spectro_title_data = f"{hertz}Hz{vol}Vpp_data_PI_sample{sample}"
        spectro_title_noise = f"{hertz}Hz{vol}Vpp_noise_PI_sample{sample}"

        spectro_file_path_data  = new_dir+"/"+spectro_title_data
        spectro_file_path_noise = new_dir+"/"+spectro_title_noise

        data_image  = c.create_spectrogram_from_wav(data_file_spliced, spectro_title_data, new_dir)
        noise_image = c.create_spectrogram_from_wav(noise_file_spliced, spectro_title_noise, new_dir)


        #Phase Invert
        print("Phase Inverting the noise image")
        noise_AS = w.phaseinvert_AudioSegment(noise_AS)

        #Mix
        print("Mixing spliced data and noise AudioSegments")

        spectro_title_mixed = f"{hertz}Hz{vol}Vpp_mixed_Stereo_sample{sample}"
        spectro_file_path_mixed = new_dir+"/"+spectro_title_mixed

        mixed_file = f"{file_prefix}{file_num_str}_Mixed{file_type}"
        w.overlay_wavs(data_AS, noise_AS, mixed_file)

        mixed_image = c.create_spectrogram_from_wav(mixed_file, spectro_title_mixed, new_dir)

        # there is a much more elegant way to do this but lets get it working before we optimize
        sample += 1
        if sample > 3:
            sample = 1
            currentVpp += 1
            if currentVpp > 2:
                currentVpp = 0
                currentHz +=1
                if currentHz > 2:
                    currentHz = 0
                    print("We SHOULD be done with PI now...")
                    break
    print("confirmed done w/ STEREO. Nice :D\n")















