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
    print(sdg.query(f"C{ch}:OUTP?"))

def upload_normalized(sdg, name, samples, freq, amp=2.0, offset=0.0, phase=0.0, ch=1):
    samples = np.asarray(samples, dtype=np.float64)
    samples = np.clip(samples, -1.0, 1.0)
    data = np.round(samples * 32767).astype("<i2").tobytes()
    cmd = f"C{ch}:WVDT WVNM,{name},FREQ,{freq},AMPL,{amp},OFST,{offset},PHASE,{phase},WAVEDATA,".encode("ascii")
    sdg.write_raw(cmd + data)
    sdg.write(f"C{ch}:ARWV NAME,{name}")
    sdg.write(f"C{ch}:BSWV WVTP,ARB,FRQ,{freq},AMP,{amp},OFST,{offset},PHSE,{phase}")

def output(sdg, state, ch=1):
    sdg.write(f"C{ch}:OUTP {'ON' if state else 'OFF'}")

sdg = connect()

t = np.linspace(0, 1, 16384, endpoint=False)
samples = np.sin(2 * np.pi * 5 * t)

#still fenangling with a fair bit
set_load(sdg)
upload_normalized(sdg, "wave1", samples, freq=100, amp=10)
output(sdg, True)
time.sleep(5)
output(sdg, False)
