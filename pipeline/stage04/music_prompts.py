#!/usr/bin/env python3
"""awesome-music-prompts (yzfly/awesome-music-prompts) - the prompt library behind the score.
Cloned for real; the cinematic/tense/atmospheric entries are extracted and used verbatim as the
seed text for ACE-Step and Stable Audio."""
import json, os, re, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from util import out_dir, log, write_json
STAGE = "stage04"

def main():
    out = out_dir(STAGE)
    cl = os.path.join(out, "awesome-music-prompts")
    ok = True
    if not os.path.exists(os.path.join(cl, ".git")):
        ok = subprocess.run(["git", "clone", "--depth", "1",
                             "https://github.com/yzfly/awesome-music-prompts", cl],
                            capture_output=True, text=True, timeout=300).returncode == 0
    found = []
    if ok:
        for r, _, fs in os.walk(cl):
            for f in fs:
                if f.endswith((".md", ".txt", ".json")):
                    t = open(os.path.join(r, f), encoding="utf-8", errors="replace").read()
                    for line in t.splitlines():
                        if re.search(r"cinematic|tense|atmospheric|noir|drone", line, re.I) and len(line) > 25:
                            found.append({"file": os.path.relpath(os.path.join(r, f), cl),
                                          "text": line.strip()[:220]})
    picked = found[:8]
    write_json(os.path.join(out, "music_prompts.json"),
               {"engine": "awesome-music-prompts", "cloned": ok, "candidates": len(found), "used": picked})
    log(STAGE, "awesome-music-prompts", f"cloned={ok} candidates={len(found)} used={len(picked)}")
    print(json.dumps({"cloned": ok, "candidates": len(found)}))

if __name__ == "__main__":
    main()
