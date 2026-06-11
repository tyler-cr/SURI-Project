# This is where I figured out I can't use shebangs reliably across os systems... ughhhhhhhh

# MAKE SURE SIGLeNT IS PLUGGED IN    MAKE SURE IT'S IN   MAKE SURE SIGLENT IS PLUGGED IN! 

import pyvisa
import numpy as np
import time

rm = pyvisa.ResourceManager()

#Note: this may change
RESOURCE = "USB0::0xF4EC::0x1102::SDG2XFBX7R1477::INSTR"

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

    ch = 1
    freq = 200
    amp = 20

    sdg = connect()
    
    configure_regular(sdg=sdg, freq=freq, amp=amp)
    trigger_basic(sdg)
    
    time.sleep(1)

    output(sdg, False)

