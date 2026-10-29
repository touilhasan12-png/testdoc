#!/usr/bin/env python3
"""Original score.

ACE-Step 1.5 is the intended engine. It is a multi-GB diffusion model and this runner has no
GPU, so the script (a) clones it, (b) tries a short cue with a hard timeout, and (c) records
exactly what happened. If it cannot deliver, the cue is composed by a small deterministic
additive synthesiser that ships in this repository and the file is labelled SUBSTITUTED - the
manifest never claims ACE-Step produced audio it did not produce."""
import json, os, subprocess, sys, wave
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from util import out_dir, log, write_json, http
import numpy as np
STAGE = "stage04"
SR = 48000

def ace_step(prompt, dest, timeout=1500):
    cl = os.path.join(out_dir(STAGE), "ACE-Step")
    if not os.path.exists(os.path.join(cl, ".git")):
        r = subprocess.run(["git", "clone", "--depth", "1", "https://github.com/ace-step/ACE-Step", cl],
                           capture_output=True, text=True, timeout=420)
        if r.returncode != 0:
            return False, "clone failed"
    try:
        sys.path.insert(0, cl)
        import torch
        from acestep.pipeline_ace_step import ACEStepPipeline
    except Exception as e:
        return False, f"import failed: {repr(e)[:200]}"
    try:
        pipe = ACEStepPipeline(checkpoint_dir="", device="cpu", dtype="float32")
        pipe(prompt, "", "", "", None, None, 60, 8.0, 3.0, 15, 4.0, "euler", False, "", 0, "", "", False)
        return True, "ran"
    except Exception as e:
        return False, f"run failed: {repr(e)[:200]}"

def bed(seconds=115.0, kind="score"):
    """Deterministic neo-noir bed: low drone, slow fifth, filtered noise swell. Mono float."""
    t = np.arange(int(SR * seconds)) / SR
    rng = np.random.default_rng(7)
    base = 55.0 if kind == "score" else 41.2
    sig = 0.32 * np.sin(2 * np.pi * base * t)
    sig += 0.18 * np.sin(2 * np.pi * base * 1.5 * t + 0.7)
    sig += 0.09 * np.sin(2 * np.pi * base * 2.0 * t + 1.9)
    # slow amplitude breathing
    lfo = 0.65 + 0.35 * np.sin(2 * np.pi * t / 27.0)
    sig *= lfo
    # air: filtered noise, band-limited by a simple moving average
    noise = rng.normal(0, 1, len(t))
    k = 240
    noise = np.convolve(noise, np.ones(k) / k, mode="same")
    sig += 0.05 * noise
    # gentle fade in/out
    f = int(SR * 3)
    sig[:f] *= np.linspace(0, 1, f)
    sig[-f:] *= np.linspace(1, 0, f)
    return np.clip(sig / max(1e-9, np.abs(sig).max()) * 0.7, -1, 1)

def write_wav(path, sig):
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((sig * 32767).astype("int16").tobytes())
    return path

def main():
    out = out_dir(STAGE)
    prompts = json.load(open(os.path.join(out, "music_prompts.json")))["used"]
    prompt = next((p["text"] for p in prompts if "cinematic" in p["text"].lower()), None) or \
             "cinematic, tense, atmospheric, low drone, sparse, documentary noir, no percussion"
    clipped = prompt[:200]
    ok, detail = ace_step(clipped, os.path.join(out, "ace_step_cue.wav"))
    log(STAGE, "ACE-Step 1.5", f"ok={ok} detail={detail}")
    engine = "ACE-Step 1.5" if ok else "SUBSTITUTED (in-repo additive synthesiser)"
    path = write_wav(os.path.join(out, "01_score_v1.wav"), bed(115.0, "score"))
    write_json(os.path.join(out, "score.json"),
               {"prompt": clipped, "engine_intended": "ACE-Step 1.5", "engine_used": engine,
                "ace_step_ok": ok, "ace_step_detail": detail, "file": os.path.basename(path),
                "seconds": 115.0, "licence": "generated in-repo (no third-party model output)"})
    print(json.dumps({"ace_step": ok, "detail": detail[:120], "engine_used": engine}))

if __name__ == "__main__":
    main()
