# This is where I figured out I can't use shebangs reliably across os systems... ughhhhhhhh

# MAKE SURE SIGLeNT IS PLUGGED IN    MAKE SURE IT'S IN   MAKE SURE SIGLENT IS PLUGGED IN! 

import pyvisa
import numpy as np
import time
import csv

rm = pyvisa.ResourceManager()

WAV_TYPES = ["SINE","SQUARE","RAMP","NOISE"]

#Note: this may change
RESOURCE = "USB0::0xF4EC::0x1102::SDG2XFBX7R1477::INSTR"


def csv_to_list(csv_file_path: str = None) -> list:
    wav_list = []
    
    if csv_file_path is None:
        raise TypeError(f"ERROR: csv_file_path cannot be none! Recieved csv_file_path: {csv_file_path}")

    with open(csv_file_path, mode='r') as file:
        reader = csv.reader(file)

        for row in reader:
            wav_type = "_".join(row)
            wav_list.append(wav_type)

    return wav_list



    

#TODO: honestly non sine waves might be out of the scope for this project...
def create_wav(wav_type: str="SINE", freq: int = None, amp: float = None):
    if wav_type not in WAV_TYPES:
        raise ValueError(f"ERROR: wav type must be SINE, SQUARE, RAMP, or NOISE. Recieved: {wav_type}")

    if freq is None: 
        print("create_wav: freq variable not specified... Defaulting to 100Hz")
        freq = 100
    if amp is None:
        print("create_wav: amp variable not specified... Defaulting to 20Vpp")
        amp = 20

    



def connect(resource=RESOURCE):
    rm = pyvisa.ResourceManager()
    sdg = rm.open_resource(resource, timeout=50000, chunk_size=24 * 1024 * 1024)
    sdg.write_termination = "\n"
    sdg.read_termination = "\n"
    print(sdg.query("*IDN?"))
    return sdg

def set_load(sdg, load=50, ch=1):
    sdg.write(f"C{ch}:OUTP LOAD,{load}")

def configure_regular(sdg, freq=100, amp=10.0, offset=0.0, phase=0.0, ch=1):
    sdg.write(f"C{ch}:BSWV WVTP,SINE,FRQ,{freq},AMP,{amp},OFST,{offset},PHSE,{phase}")

def output(sdg, state, ch=1):
    sdg.write(f"C{ch}:OUTP {'ON' if state else 'OFF'}")

def configure_burst(sdg, ch=1, freq=200, amp=20, seconds=1.0):
    cycles = round(freq * seconds)

    sdg.write(f"C{ch}:OUTP OFF")
    sdg.write(f"C{ch}:BTWV STATE,ON")
    sdg.write(f"C{ch}:BTWV GATE_NCYC,NCYC")
    sdg.write(f"C{ch}:BTWV TRSR,MAN")
    sdg.write(f"C{ch}:BTWV TIME,{cycles}")
    sdg.write(f"C{ch}:BTWV CARR,WVTP,SINE")
    sdg.write(f"C{ch}:BTWV CARR,FRQ,{freq}")
    sdg.write(f"C{ch}:BTWV CARR,AMP,{amp}")
    sdg.query("*OPC?")
    sdg.write(f"C{ch}:OUTP ON")
    sdg.query("*OPC?")


def trigger_burst(sdg, ch=1):
    sdg.write(f"C{ch}:BTWV MTRIG")

def trigger_basic(sdq, ch=1):
    sdg.write(f"C{ch}:OUTP ON")

if __name__ == "__main__":

    #print(csv_to_list("C:/Users/Tyler/Desktop/SURI-Project/CSV_To_Wav-Sheet1.csv"))

    test = create_sine(freq = 500, amp = 20)

    print(test)