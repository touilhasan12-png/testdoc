#!/usr/bin/env python3
"""Assemble the narration track from whichever narrator actually produced audio, then clean it.
Steps: concatenate lines with cue gaps -> Demucs (vocal isolation/clean) -> auto-editor (silence
trim) -> final mono 48 kHz WAV + a timing map used later by the edit."""
import json, os, subprocess, sys, wave
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from util import out_dir, log, write_json
from common import STAGE, lines

def find_narrator(out):
    for name in ("chatterbox", "kokoro"):
        p = os.path.join(out, name, "lines.json")
        if os.path.exists(p):
            d = json.load(open(p))
            if d.get("lines"):
                return name, d
    return None, None

def concat(d, wavs, dest, gap=0.42):
    import numpy as np
    chunks, sr = [], None
    for w in wavs:
        with wave.open(w) as f:
            sr = f.getframerate()
            n = f.getnframes()
            a = np.frombuffer(f.readframes(n), dtype="int16").astype("float32") / 32768.0
        chunks.append(a)
        chunks.append(np.zeros(int(sr * gap), dtype="float32"))
    full = np.concatenate(chunks)
    with wave.open(dest, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(sr)
        f.writeframes((np.clip(full, -1, 1) * 32767).astype("int16").tobytes())
    return sr, len(full) / sr

def main():
    out = out_dir(STAGE)
    name, d = find_narrator(out)
    if not name:
        raise SystemExit("no narrator produced audio - nothing to assemble (recorded, not hidden)")
    base = os.path.join(out, name)
    wavs = [os.path.join(base, l["wav"]) for l in d["lines"]]
    missing = [w for w in wavs if not os.path.exists(w)]
    if missing:
        raise SystemExit(f"missing narrator lines: {missing[:3]}")
    raw = os.path.join(out, "01_narration_raw.wav")
    sr, dur = concat(d, wavs, raw)
    log(STAGE, f"assembly ({name})", f"raw track {dur:.1f}s @ {sr} Hz")

    cleaned = os.path.join(out, "02_narration_demucs.wav")
    r = subprocess.run([sys.executable, "-m", "demucs", "--two-stems", "vocals", "-n", "htdemucs",
                        "-o", os.path.join(out, "demucs"), raw], capture_output=True, text=True,
                       timeout=5400)
    cand = os.path.join(out, "demucs", "htdemucs", os.path.basename(raw)[:-4], "vocals.wav")
    demucs_ok = r.returncode == 0 and os.path.exists(cand)
    if demucs_ok:
        os.replace(cand, cleaned)
        log(STAGE, "Demucs", "vocals stem extracted")
    else:
        log(STAGE, "Demucs", f"failed rc={r.returncode}: {(r.stderr or '')[-300:]}")

    trimmed = os.path.join(out, "03_narration_trimmed.wav")
    r2 = subprocess.run([sys.executable, "-m", "auto_editor", (cleaned if demucs_ok else raw),
                         "--output", trimmed, "--silent-threshold", "0.05", "--margin", "0.12s"],
                        capture_output=True, text=True, timeout=3600)
    trim_ok = r2.returncode == 0 and os.path.exists(trimmed)
    log(STAGE, "auto-editor", f"rc={r2.returncode} out_exists={os.path.exists(trimmed)}")

    final = trimmed if trim_ok else (cleaned if demucs_ok else raw)
    with wave.open(final) as f:
        final_sr, final_dur = f.getframerate(), f.getnframes() / f.getframerate()
    write_json(os.path.join(out, "track.json"),
               {"narrator": d.get("narrator"), "narrator_engine": name,
                "raw_wav": os.path.basename(raw), "raw_seconds": round(dur, 2),
                "demucs_ok": demucs_ok, "auto_editor_ok": trim_ok,
                "final_wav": os.path.basename(final), "final_seconds": round(final_dur, 2),
                "sample_rate": final_sr,
                "disclosure": "Synthetic voice. No real person's voice is cloned or imitated."})
    print(json.dumps({"engine": name, "final_seconds": round(final_dur, 1),
                      "demucs": demucs_ok, "auto_editor": trim_ok}))

if __name__ == "__main__":
    main()
