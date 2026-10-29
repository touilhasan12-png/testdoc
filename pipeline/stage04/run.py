#!/usr/bin/env python3
"""Stage 4 - music and sound design, ending in one mix file for approval gate B."""
import json, os, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from util import out_dir, log, write_json
HERE = os.path.dirname(os.path.abspath(__file__)); STAGE = "stage04"
STEPS = ["music_prompts.py", "score.py", "ambience.py", "sfx_real.py", "mm_audio.py",
         "fx_pedalboard.py", "mix.py"]

def main():
    res = []
    for s in STEPS:
        p = subprocess.run([sys.executable, os.path.join(HERE, s)], capture_output=True, text=True, timeout=5400)
        res.append({"script": s, "rc": p.returncode, "stdout": p.stdout[-800:], "stderr": p.stderr[-800:]})
        log(STAGE, s, f"rc={p.returncode}")
    write_json(os.path.join(out_dir(STAGE), "stage04_report.json"), res)
    print(json.dumps({r["script"]: r["rc"] for r in res}))
    if res[-1]["rc"] != 0:
        raise SystemExit("mix failed")

if __name__ == "__main__":
    main()
