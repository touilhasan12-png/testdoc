#!/usr/bin/env python3
"""Stage 3 - voice. Order matters: measure the main narrator, fall back only on recorded
failure, then the second voice, the texture layer, and the cleanup chain."""
import json, os, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from util import out_dir, log, write_json
HERE = os.path.dirname(os.path.abspath(__file__))
STAGE = "stage03"

def sh(script, env=None):
    e = {**os.environ, **(env or {})}
    p = subprocess.run([sys.executable, os.path.join(HERE, script)], capture_output=True, text=True,
                       timeout=7200, env=e)
    return {"script": script, "rc": p.returncode, "stdout": p.stdout[-1200:], "stderr": p.stderr[-1200:]}

def main():
    res = {}
    res["chatterbox"] = sh("chatterbox_narrate.py")
    log(STAGE, "Chatterbox", f"rc={res['chatterbox']['rc']}")
    if res["chatterbox"]["rc"] != 0:
        res["kokoro"] = sh("kokoro_narrate.py")
        log(STAGE, "kokoro-onnx (fallback)", f"rc={res['kokoro']['rc']}")
    res["silma"] = sh("silma_read.py")
    log(STAGE, "SILMA TTS", f"rc={res['silma']['rc']}")
    res["bark"] = sh("bark_texture.py")
    log(STAGE, "Bark", f"rc={res['bark']['rc']}")
    res["build"] = sh("build_track.py")
    log(STAGE, "build_track", f"rc={res['build']['rc']}")
    write_json(os.path.join(out_dir(STAGE), "stage03_report.json"), res)
    print(json.dumps({k: v["rc"] for k, v in res.items()}))
    # the track is the deliverable of this stage; the optional voices are reported, not required
    if res["build"]["rc"] != 0:
        raise SystemExit("narration track could not be assembled")

if __name__ == "__main__":
    main()
