#!/usr/bin/env python3
"""Stage 2 - script. Produces the screenplay package for approval gate A."""
import json, os, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from util import out_dir, log, write_json
HERE = os.path.dirname(os.path.abspath(__file__))
STAGE = "stage02"
STEPS = [("writers-room-story-engine", "structure.py"),
         ("ai-screenplay-writer", "scenes.py"),
         ("STORYMACHINE (SUBSTITUTED)", "script_diag.py"),
         ("scriptbreak (SUBSTITUTED)", "script_break.py"),
         ("SceneFlow", "sceneflow.py")]

def main():
    res = []
    for name, script in STEPS:
        log(STAGE, name, "start")
        p = subprocess.run([sys.executable, os.path.join(HERE, script)], capture_output=True, text=True, timeout=1200)
        res.append({"tool": name, "ok": p.returncode == 0, "rc": p.returncode,
                    "stdout": p.stdout[-800:], "stderr": p.stderr[-800:]})
        log(STAGE, name, f"done ok={p.returncode == 0}")
    write_json(os.path.join(out_dir(STAGE), "stage02_report.json"), res)
    failed = [r["tool"] for r in res if not r["ok"]]
    print(json.dumps({"failed": failed}))
    if failed:
        raise SystemExit("failed: " + ", ".join(failed))

if __name__ == "__main__":
    main()
