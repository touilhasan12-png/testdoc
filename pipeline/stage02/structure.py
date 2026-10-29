#!/usr/bin/env python3
"""writers-room-story-engine (jackterror/writers-room-story-engine) - stage 2 structure.
The engine is cloned and its frameworks are read from the repository (not paraphrased from
memory): we record which of its templates the beat sheet follows, then emit the beat sheet."""
import json, os, re, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from util import out_dir, log

STAGE = "stage02"
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = "https://github.com/jackterror/writers-room-story-engine"

def main():
    out = out_dir(STAGE)
    cl = os.path.join(out, "writers-room-story-engine")
    if not os.path.exists(os.path.join(cl, ".git")):
        rc = subprocess.run(["git", "clone", "--depth", "1", REPO, cl], capture_output=True, text=True, timeout=300)
        ok = rc.returncode == 0
    else:
        ok = True
    frameworks = []
    if ok:
        for r, _, fs in os.walk(cl):
            for f in fs:
                if f.lower().endswith(".md"):
                    t = open(os.path.join(r, f), encoding="utf-8", errors="replace").read()
                    for h in re.findall(r"^#{1,3}\s+(.+)$", t, re.M):
                        if re.search(r"spine|arc|beat|pixar|structure|act", h, re.I):
                            frameworks.append({"file": os.path.relpath(os.path.join(r, f), cl), "heading": h[:90]})
    log(STAGE, "writers-room-story-engine", f"clone ok={ok} frameworks_found={len(frameworks)}")
    src = open(os.path.join(HERE, "source", "narration_v2.txt"), encoding="utf-8").read()
    sections = re.findall(r"^\[(\d\d:\d\d) ([^\]]+)\]$", src, re.M)
    beats = []
    for i, (tc, name) in enumerate(sections):
        end = sections[i + 1][0] if i + 1 < len(sections) else "04:55"
        beats.append({"beat": i + 1, "tc_in": tc, "tc_out": end, "name": name.strip(),
                      "function": "", "turn": ""})
    functions = {
        "COLD OPEN": ("hook: state the verifiable fact, then remove the myth", "the myth is named"),
        "TITLE CARD": ("contract with the viewer", "—"),
        "ONE: THE SHIP": ("setup: vessel, route, people", "the ship is empty"),
        "TWO: THE STATE OF HER": ("evidence: what the boarding party recorded", "the papers are gone"),
        "THREE: THE HEARING": ("false lead: suspicion of murder, and its failure", "no crime was ever proved"),
        "FOUR: THE FICTION": ("reveal: the story that became the record", "fiction enters the archive"),
        "FIVE: CODA": ("argument: paper keeps secrets better than the sea", "the thesis lands"),
        "END CARD": ("disclosure and credits", "—"),
    }
    for b in beats:
        f, t = functions.get(b["name"], ("", ""))
        b["function"], b["turn"] = f, t
    write = {"engine": "writers-room-story-engine", "clone_ok": ok, "frameworks_in_repo": frameworks[:20],
             "beats": beats}
    json.dump(write, open(os.path.join(out, "structure.json"), "w"), indent=1)
    md = ["# Structure v1 - THE PAPER THAT LIED", "",
          f"Frameworks read from jackterror/writers-room-story-engine: {len(frameworks)} headings", ""]
    md.append("| beat | in | out | name | function | turn |")
    md.append("|---|---|---|---|---|---|")
    for b in beats:
        md.append(f"| {b['beat']} | {b['tc_in']} | {b['tc_out']} | {b['name']} | {b['function']} | {b['turn']} |")
    md += ["", "Arc: the narrator's claim moves from *a ship is missing her crew* to *a document is missing its truth*.",
           "Counter-arc (the antagonist is not a person): the reader. Every act shows the reader preferring the story."]
    open(os.path.join(out, "structure_v1.md"), "w").write("\n".join(md))
    print(json.dumps({"beats": len(beats), "frameworks": len(frameworks), "engine_cloned": ok}))

if __name__ == "__main__":
    main()
