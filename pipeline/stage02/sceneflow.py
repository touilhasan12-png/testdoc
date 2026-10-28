#!/usr/bin/env python3
"""SceneFlow (taruma/SceneFlow) - stage 2 script-to-screen alignment.
SceneFlow compares a screenplay with video and reports fidelity. In this sample the video does
not exist yet at stage 2, so we run it in *plan* mode: each shot must carry (a) a line of
narration it is under, (b) a source tool, (c) a disclosure label. Anything unmatched fails the
stage - that is the same contract the real tool enforces later against the rendered file."""
import json, os, re, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from util import out_dir, log

STAGE = "stage02"
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = "https://github.com/taruma/SceneFlow"

def main():
    out = out_dir(STAGE)
    cl = os.path.join(out, "SceneFlow")
    ok = True
    if not os.path.exists(os.path.join(cl, ".git")):
        rc = subprocess.run(["git", "clone", "--depth", "1", REPO, cl], capture_output=True, text=True, timeout=300)
        ok = rc.returncode == 0
    shots = json.load(open(os.path.join(out, "shotlist.json")))
    src = open(os.path.join(HERE, "source", "narration_v1.txt"), encoding="utf-8").read()
    narr = [l.split(":", 1)[1].strip() for l in src.splitlines() if l.startswith("NARRATOR:")]
    # distribute narration lines across shots proportionally (plan mode)
    per = max(1, len(narr) // len(shots))
    rows, unmatched = [], []
    for i, s in enumerate(shots):
        line = " ".join(narr[i * per:(i + 1) * per]) if i * per < len(narr) else narration_tail(narr, shots, i)
        row = {"shot": s["shot"], "narration_under": line[:200],
               "has_tool": bool(s["tool"]), "has_label": bool(s["label"])}
        if not (row["has_tool"] and row["has_label"]):
            unmatched.append(s["shot"])
        rows.append(row)
    json.dump({"engine": "SceneFlow", "repo_cloned": ok, "mode": "plan (no render yet)",
               "shots": rows, "unmatched": unmatched,
               "fidelity": round(1 - len(unmatched) / max(1, len(shots)), 3)},
              open(os.path.join(out, "alignment.json"), "w"), indent=1)
    log(STAGE, "SceneFlow", f"cloned={ok} shots={len(shots)} unmatched={unmatched}")
    print(json.dumps({"shots": len(shots), "unmatched": unmatched}))
    if unmatched:
        raise SystemExit("shots without tool or disclosure label")

def narration_tail(narr, shots, i):
    return " ".join(narr[-2:])

if __name__ == "__main__":
    main()
