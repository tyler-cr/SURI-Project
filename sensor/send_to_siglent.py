# This is where I figured out I can't use shebangs reliably across os systems... ughhhhhhhh

# MAKE SURE SIGLeNT IS PLUGGED IN    MAKE SURE IT'S IN   MAKE SURE SIGLENT IS PLUGGED IN! 

import pyvisa
import numpy as np
import time
import csv
import winsound


rm = pyvisa.ResourceManager()

WAV_TYPES = ["SINE","SQUARE","RAMP","NOISE"]

#Note: this may change
RESOURCE = "USB0::0xF4EC::0x1102::SDG2XFBX7R1477::INSTR"


def csv_to_str_list(csv_file_path: str = None) -> list:
    """
    Reads a CSV file and returns rows as concatenated strings in a list.
    
    Each row's columns are joined with underscores to form single string entries.
    Useful for extracting flat lists of waveform type identifiers or simple parameters.
    
    Args:
        csv_file_path (str): Path to input CSV file. Must not be None.
        
    Returns:
        list: List of strings, where each string represents one CSV row joined by '_'.
        
    Raises:
        TypeError: If csv_file_path is None.
        FileNotFoundError: If the specified CSV file does not exist.
    """
    wav_list = []
    
    if csv_file_path is None:
        raise TypeError(f"ERROR: csv_file_path cannot be none! Recieved csv_file_path: {csv_file_path}")

    with open(csv_file_path, mode='r') as file:
        reader = csv.reader(file)

        for row in reader:
            wav_type = "_".join(row)
            wav_list.append(wav_type)

    return wav_list

def csv_to_dict_list(csv_file_path: str = None) -> list:
    """
    Reads a CSV file and returns rows as dictionaries keyed by header names.
    
    Parses the CSV using DictReader, preserving column names from the first row 
    as dictionary keys. Enables instruction-based sequencing for hardware control.
    
    Args:
        csv_file_path (str): Path to input CSV file with headers.
        
    Returns:
        list: List of dicts, one per row, with keys from CSV header row.
        
    Example:
        [{'FREQ': '100', 'AMP': '5', 'SAMPLES': '1'}, ...]
    """
    with open(csv_file_path, mode = 'r') as file:
        csv_reader = csv.DictReader(file)
        dict_list = list(csv_reader)
    return dict_list

def batch_siglent_run(sdg, dict_list: dict, buffer: int = 4):
    """
    Executes a sequence of signal generator commands based on CSV-loaded instructions.
    
    Orchestrates automated waveform generation while pausing for manual confirmation
    when geographic location, wave generator position, or cavity settings change.
    Supports synchronized field recording with human-in-the-loop checkpoints.
    
    Args:
        sdg: PyVISA resource object connected to Siglent SDG device.
        dict_list (list): List of instruction dicts from csv_to_dict_list().
        buffer (int): Wait time (seconds) between iterations within a sample batch. Default: 4.
        
    Note:
        Requires manual user input (ENTER keypress) to confirm physical setup changes.
        Calls dict_to_siglent_instruction() for each instruction cycle.
        
    Side Effects:
        Sends SCPI commands to SDG device; generates audible signals at configured freq/amp.
    """

    input("WAIT: Please press ENTER on your keyboard and start the recording at the same time")
    
    prev_geo_loc = "NEAR"
    prev_wav_loc = "MID"
    prev_cav = "NO"

    print(f"Reminder of dict_list order: {dict_list}")
    
    for instruction in dict_list:

        samples = instruction["SAMPLES"]
        time_per = instruction["TIME"]
        
        cur_geo_loc = instruction["GEO_LOC"]
        cur_wav_loc = instruction["WAVE_LOC"]
        cur_cav     = instruction["CAVITY"]

        if prev_geo_loc != cur_geo_loc:
            winsound.Beep(400, 1000)
            input(f"WAIT: GEOPHONE LOCATION INSTRUCTION CHANGED. PREV:{prev_geo_loc}. CUR:{cur_geo_loc}\n PLEASE SWITCH TO DESIGNATED LOCATION AND PRESS 'ENTER' TO CONTINUE")
            input("please press 'ENTER' again to continue")
            prev_geo_loc = cur_geo_loc

        if prev_wav_loc != cur_wav_loc:
            winsound.Beep(400, 1000)
            input(f"WAIT: WAVE GENERATOR LOCATION INSTRUCTION CHANGED. PREV:{prev_wav_loc}. CUR:{cur_wav_loc}\n PLEASE SWITCH TO DESIGNATED LOCATION AND PRESS 'ENTER' TO CONTINUE")
            input("please press 'ENTER' again to continue")
            prev_wav_loc = cur_wav_loc

        if prev_cav != cur_cav:
            winsound.Beep(400, 1000)
            input(f"WAIT: CAVITY INSTRUCTION CHANGED. PREV:{prev_cav}. CUR:{cur_cav}\n PLEASE SWITCH TO DESIGNATED LOCATION AND PRESS 'ENTER' TO CONTINUE")
            input("please press 'ENTER' again to continue")
            prev_cav = cur_cav

        
        print(f"Beginning {cur_cav} cavity {cur_wav_loc} wav loc {cur_geo_loc} geo loc {instruction['FREQ']}Hz Freq {instruction['AMP']}Vpp Amp")
        for i in range(int(samples)):
            time.sleep(buffer)
            dict_to_siglent_instruction(sdg, instruction)
            output(sdg, True)
            time.sleep(int(time_per)*1.05) # 1.05 is for a buffer. Python continues before the machine actually begins running, but we don't need to be absurdly accurate
            output(sdg, False)

    input("Please end recording on field recorder and then press any button to continue")
    print("Hopefully this should have worked!")


        

def dict_to_siglent_instruction(sdg, instruction_dict: dict)->None:
    """
    Translates an instruction dictionary into Siglent SDG configuration commands.
    
    Extracts frequency and amplitude values from the provided dict and applies 
    them via configure_regular(). Currently configures continuous sine wave output.
    
    Args:
        sdg: PyVISA resource object for the Siglent SDG.
        instruction_dict (dict): Instruction containing FREQ, AMP, and other fields.
        
    Returns:
        None
    """

    configure_regular(sdg,
                      freq=instruction_dict["FREQ"],
                      amp=instruction_dict["AMP"]
                      )

def connect(resource=RESOURCE):
    """
    Establishes VISA connection to Siglent SDG function generator.
    
    Opens USB-TMC resource with extended timeout and large chunk size for reliable
    communication. Verifies connection by querying device identification string.
    
    Args:
        resource (str): VISA resource string identifying the SDG device. 
                        Default: "USB0::0xF4EC::0x1102::SDG2XFBX7R1477::INSTR".
        
    Returns:
        pyvisa.Resource: Open resource object for subsequent SCPI command transmission.
        
    Raises:
        VisaError: If device cannot be found or connection fails.
    """

    rm = pyvisa.ResourceManager()
    sdg = rm.open_resource(resource, timeout=50000, chunk_size=24 * 1024 * 1024)
    sdg.write_termination = "\n"
    sdg.read_termination = "\n"
    print(sdg.query("*IDN?"))
    return sdg

def set_load(sdg, load=50, ch=1):
    """
    Configures output load impedance on specified channel.
    
    Sets the SDG's assumed output termination value, affecting amplitude calibration.
    Typical values are 50Ω for RF equipment or HIGH-Z for high-impedance inputs.
    
    Args:
        sdg: PyVISA resource object for the Siglent SDG.
        load (int): Load impedance in ohms. Default: 50.
        ch (int): Channel number (1 or 2). Default: 1.
    """
    sdg.write(f"C{ch}:OUTP LOAD,{load}")

def configure_regular(sdg, freq=100, amp=10.0, offset=0.0, phase=0.0, ch=1):
    """
    Configures continuous single-waveform output (e.g., sine wave) on specified channel.
    
    Sends BSWV (basic sequence wave) SCPI command to set waveform type, frequency,
    amplitude, DC offset, and phase. Primarily used for sustained tone generation.
    
    Args:
        sdg: PyVISA resource object for the Siglent SDG.
        freq (float): Frequency in Hz. Default: 100.
        amp (float): Peak-to-peak voltage in Vpp. Default: 10.0.
        offset (float): DC offset in volts. Default: 0.0.
        phase (float): Initial phase in degrees. Default: 0.0.
        ch (int): Channel number (1 or 2). Default: 1.
        
    Note:
        Does not enable output—call output(sdg, True) separately to activate.
    """
    sdg.write(f"C{ch}:BSWV WVTP,SINE,FRQ,{freq},AMP,{amp},OFST,{offset},PHSE,{phase}")

def output(sdg, state, ch=1):
    """
    Toggles RF output on or off for specified channel.
    
    Enables or disables the actual signal transmission from the function generator.
    Used to start/stop waveform generation after configuration.
    
    Args:
        sdg: PyVISA resource object for the Siglent SDG.
        state (bool): True to turn ON, False to turn OFF.
        ch (int): Channel number (1 or 2). Default: 1.
    """
    sdg.write(f"C{ch}:OUTP {'ON' if state else 'OFF'}")

def configure_burst(sdg, ch=1, freq=200, amp=20, seconds=1.0):
    """
    Configures burst-mode sine wave output with gated triggering.
    
    Sets up gated burst waveform using BTWV commands to emit a fixed number of cycles
    when manually triggered. Uses NCYC (number of cycles) gating method.
    
    Args:
        sdg: PyVISA resource object for the Siglent SDG.
        ch (int): Channel number (1 or 2). Default: 1.
        freq (int): Carrier frequency in Hz. Default: 200.
        amp (int): Amplitude in Vpp. Default: 20.
        seconds (float): Burst duration in seconds. Default: 1.0.
        
    Note:
        Requires trigger_burst() call to actually emit the waveform.
        Waits for *OPC? completion queries before enabling output.
    """

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
    """
    Manually triggers a pre-configured burst waveform output.
    
    Sends MTRIG (manual trigger) command to initiate gated burst emission.
    Only active after configure_burst() has been called successfully.
    
    Args:
        sdg: PyVISA resource object for the Siglent SDG.
        ch (int): Channel number (1 or 2). Default: 1.
    """

    sdg.write(f"C{ch}:BTWV MTRIG")

def trigger_basic(sdg, ch=1):
    """
    Basic output trigger—turns channel output ON immediately.
    
    Alternative to burst triggering; simply enables continuous output mode.
    Equivalent to calling output(sdg, True, ch).
    
    Args:
        sdg: PyVISA resource object for the Siglent SDG.
        
        ch (int): Channel number (1 or 2). Default: 1.
    """
    sdg.write(f"C{ch}:OUTP ON")

if __name__ == "__main__":

    #print(csv_to_list("C:/Users/Tyler/Desktop/SURI-Project/CSV_To_Wav-Sheet1.csv"))

    test_file_path = "C:/Users/Tyler/Desktop/SURI-Project/sensor/siglent_send_wave_csvs/[Wave@A1]CSV_to_SIGLENT_DICT.csv"

    sdg = connect()

    instruction_list = csv_to_dict_list(test_file_path)

    batch_siglent_run(sdg, instruction_list, buffer=5)