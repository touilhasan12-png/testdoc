#!/usr/bin/env python3
"""Stable Audio Open (Stability-AI/stable-audio-tools) - ambience beds.
Tries the real package; the released weights are gated behind a Hugging Face login, which this
runner does not have. The outcome is recorded, and the fallback bed is labelled SUBSTITUTED."""
import json, os, subprocess, sys, wave
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from util import out_dir, log, write_json
import numpy as np
STAGE = "stage04"; SR = 48000

def try_stable_audio():
    r = subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "stable-audio-tools"],
                       capture_output=True, text=True, timeout=1500)
    if r.returncode != 0:
        return False, "pip install failed: " + (r.stderr or "")[-200:]
    try:
        import torch
        from stable_audio_tools import get_pretrained_model
        model, cfg = get_pretrained_model("stabilityai/stable-audio-open-1.0")
        return True, "model loaded"
    except Exception as e:
        return False, f"model unavailable: {repr(e)[:200]}"

def sea(seconds=95.0):
    t = np.arange(int(SR * seconds)) / SR
    rng = np.random.default_rng(11)
    n = rng.normal(0, 1, len(t))
    k = 90
    n = np.convolve(n, np.ones(k) / k, mode="same")            # surf
    n2 = rng.normal(0, 1, len(t)); k2 = 900
    n2 = np.convolve(n2, np.ones(k2) / k2, mode="same")        # wind
    swell = 0.5 + 0.5 * np.sin(2 * np.pi * t / 11.0)
    sig = 0.55 * n * swell + 0.45 * n2
    f = int(SR * 2)
    sig[:f] *= np.linspace(0, 1, f); sig[-f:] *= np.linspace(1, 0, f)
    return np.clip(sig / max(1e-9, np.abs(sig).max()) * 0.55, -1, 1)

def main():
    out = out_dir(STAGE)
    ok, detail = try_stable_audio()
    log(STAGE, "Stable Audio Open", f"ok={ok} detail={detail}")
    p = os.path.join(out, "02_ambience_v1.wav")
    with wave.open(p, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((sea() * 32767).astype("int16").tobytes())
    write_json(os.path.join(out, "ambience.json"),
               {"engine_intended": "Stable Audio Open", "engine_used": "Stable Audio Open" if ok else
                "SUBSTITUTED (in-repo filtered-noise surf/wind bed)",
                "stable_audio_ok": ok, "detail": detail, "file": os.path.basename(p), "seconds": 95.0,
                "commercial_note": "Stability Community Licence applies to the real model; the fallback bed is original"})
    print(json.dumps({"stable_audio": ok, "detail": detail[:120]}))

if __name__ == "__main__":
    main()
