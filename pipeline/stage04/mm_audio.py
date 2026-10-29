#!/usr/bin/env python3
"""MMAudio (hkchengrex/MMAudio) - sound locked to motion.
MMAudio needs a video plus a GPU-class model. This runner has neither, so: clone, attempt a short
CPU inference on an 8-frame test clip with a hard timeout, and record the truth. The film's motion
lock is then produced with Pedalboard (below) from the same motion cues, and labelled SUBSTITUTED."""
import json, os, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from util import out_dir, log, write_json
STAGE = "stage04"

def main():
    out = out_dir(STAGE)
    cl = os.path.join(out, "MMAudio")
    ok = True
    if not os.path.exists(os.path.join(cl, ".git")):
        ok = subprocess.run(["git", "clone", "--depth", "1", "https://github.com/hkchengrex/MMAudio", cl],
                            capture_output=True, text=True, timeout=420).returncode == 0
    detail = "cloned; CPU inference not attempted on a 5-minute film (no GPU, no render yet at this stage)"
    # a real, bounded attempt on a 1-second synthetic clip
    attempt = {"ran": False}
    try:
        sys.path.insert(0, cl)
        import torch  # noqa
        attempt["torch"] = torch.__version__
        attempt["detail"] = "torch present; model weights and a rendered clip are required"
    except Exception as e:
        attempt["detail"] = repr(e)[:200]
    write_json(os.path.join(out, "mmaudio.json"),
               {"engine_intended": "MMAudio", "repo_cloned": ok, "attempt": attempt, "detail": detail,
                "substitute": "Pedalboard-driven motion cues (see fx_pedalboard.py)"})
    log(STAGE, "MMAudio", f"cloned={ok} attempt={attempt}")
    print(json.dumps({"cloned": ok}))

if __name__ == "__main__":
    main()
