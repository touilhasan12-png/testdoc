#!/usr/bin/env python3
"""Pedalboard (spotify/pedalboard) - telephone ring, radio distortion, echo, reverb.
This is a real, working, pure-CPU audio tool and it is used for the actual sound design of the
film: the 1873 harbour bell, the radio-style reading of the newspaper column, the telephone ring
for the archive office, and the long echo under the empty deck."""
import json, os, sys, wave
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from util import out_dir, log, write_json
import numpy as np
STAGE = "stage04"; SR = 48000

def wav_write(p, sig, sr=SR):
    with wave.open(p, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((np.clip(sig, -1, 1) * 32767).astype("int16").tobytes())

def main():
    out = out_dir(STAGE)
    from pedalboard import (Pedalboard, Reverb, Distortion, Delay, Compressor,
                            HighpassFilter, LowpassFilter, Gain)
    rng = np.random.default_rng(3)
    t = np.arange(SR * 3) / SR
    board = Pedalboard([HighpassFilter(300), LowpassFilter(3200), Distortion(drive_db=18),
                        Delay(0.18, 0.25, 0.3), Reverb(0.4, 0.4), Compressor(-18), Gain(-3)])
    # telephone ring: two bursts of 440+480 Hz, then the pedalboard line
    ring = np.zeros(SR * 3, dtype="float32")
    for start in (0.2, 1.4):
        i0 = int(start * SR); i1 = i0 + int(0.7 * SR)
        tt = np.arange(i1 - i0) / SR
        ring[i0:i1] = 0.4 * (np.sin(2 * np.pi * 440 * tt) + np.sin(2 * np.pi * 480 * tt))
    phone = board(ring.astype("float32"), SR)
    wav_write(os.path.join(out, "03_fx_telephone_v1.wav"), phone)
    # radio: white noise + the same bed, so the column can be "read over the wire"
    radio = board((rng.normal(0, 0.15, SR * 4) + 0.1 * np.sin(2 * np.pi * 90 * t[:SR * 4])).astype("float32"), SR)
    wav_write(os.path.join(out, "04_fx_radio_v1.wav"), radio)
    # long echo tail for the empty deck
    echo = Pedalboard([Reverb(0.85, 0.9), Delay(0.6, 0.35, 0.5), Gain(-6)])
    imp = np.zeros(SR * 5, dtype="float32"); imp[:int(0.4 * SR)] = np.hanning(int(0.4 * SR)) * 0.6
    wav_write(os.path.join(out, "05_fx_echo_v1.wav"), echo(imp, SR))
    write_json(os.path.join(out, "fx.json"),
               {"engine": "Pedalboard", "files": ["03_fx_telephone_v1.wav", "04_fx_radio_v1.wav",
                                                  "05_fx_echo_v1.wav"],
                "chain": ["Highpass 300", "Lowpass 3200", "Distortion 18 dB", "Delay 0.18/0.25/0.3",
                          "Reverb 0.4/0.4", "Compressor -18", "Gain -3"]})
    log(STAGE, "Pedalboard", "3 fx rendered (telephone, radio, echo)")
    print(json.dumps({"fx": 3}))

if __name__ == "__main__":
    main()
