#!/usr/bin/env python3
"""Final mix for the voice gate: narration + score + ambience + fx, ducked and limited.
Everything is rendered here so the approval gate B has a single 4:55 file to listen to."""
import json, os, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from util import out_dir, log, write_json
STAGE = "stage04"

def dur(path):
    import wave
    with wave.open(path) as w:
        return w.getnframes() / w.getframerate()

def main():
    out = out_dir(STAGE)
    voice = None
    for cand in ("04_narration_paced.wav", "03_narration_trimmed.wav", "02_narration_demucs.wav",
                 "01_narration_raw.wav"):
        p = os.path.join(os.path.dirname(out), "stage03", cand)
        if os.path.exists(p):
            voice = p; break
    if not voice:
        raise SystemExit("no narration file to mix")
    total = dur(voice)
    score = os.path.join(out, "01_score_v1.wav")
    amb = os.path.join(out, "02_ambience_v1.wav")
    mix = os.path.join(out, "06_mix_v1.wav")
    # narration at unity, score ducked under it, ambience low, gentle limiter
    fc = (
        f"[1:a]aloop=loop=-1:size=2e9,atrim=0:{total},volume=0.16,afade=t=in:st=0:d=3,"
        f"afade=t=out:st={total-4}:d=4[sc];"
        f"[2:a]aloop=loop=-1:size=2e9,atrim=0:{total},volume=0.10[am];"
        f"[0:a]volume=1.0[v];"
        f"[v][sc][am]amix=inputs=3:duration=first:weights='1 1 1'[mix];"
        f"[mix]alimiter=limit=0.92,aresample=48000[m]"
    )
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", voice, "-i", score, "-i", amb,
                        "-filter_complex", fc, "-map", "[m]", "-ac", "2", mix],
                       capture_output=True, text=True, timeout=1800)
    ok = r.returncode == 0 and os.path.exists(mix)
    log(STAGE, "FFmpeg (mix)", f"rc={r.returncode} ok={ok} {(r.stderr or '')[-200:]}")
    mp3 = os.path.join(out, "06_mix_v1_preview.mp3")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mix, "-b:a", "160k", mp3],
                   capture_output=True, text=True, timeout=1200)
    write_json(os.path.join(out, "mix.json"),
               {"voice": os.path.basename(voice), "seconds": round(total, 2), "mix_ok": ok,
                "levels": {"narration": 1.0, "score": 0.16, "ambience": 0.10, "limiter": 0.92},
                "preview_mp3": os.path.basename(mp3) if os.path.exists(mp3) else None})
    print(json.dumps({"mixed_seconds": round(total, 1), "ok": ok}))

if __name__ == "__main__":
    main()
