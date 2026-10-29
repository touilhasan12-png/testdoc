#!/usr/bin/env python3
"""ai-screenplay-writer (E-Asrar-Haghighi/ai-screenplay-writer) - stage 2 scene pass.
The upstream project is a multi-agent LLM system; there is no API key in CI and we will not
fake an LLM call. What we *can* run is its output contract: a scene list in a fixed schema.
So we (a) clone the repo and read its schema, (b) write the scenes against that schema from
the approved narration with a continuity checker - and label the result honestly."""
import json, os, re, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from util import out_dir, log

STAGE = "stage02"
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = "https://github.com/E-Asrar-Haghighi/ai-screenplay-writer"

SCENES = [
 ("COLD", "Exterior. Open Atlantic, dawn. Extreme wide.",
  "An empty horizon. No ship. A slow push in.", "Cold open", "ARCHIVE PLATE: none. 100% generated atmosphere"),
 ("SHIP-1", "Exterior. Deck of a brigantine. Day.", "Empty deck, sail filled, wheel untended, slow pan.",
  "The ship sails herself", "REENACTMENT"),
 ("SHIP-2", "Interior. Cabin. Day.", "A child's toy on the floor. An unmade bunk. No people.",
  "Ten people, no bodies", "REENACTMENT"),
 ("EVID-1", "Archive insert. Newspaper column.", "Slow drift across a photographed column, ink on paper.",
  "The Liverpool correspondent's account", "ARCHIVAL PHOTO (Library of Congress)"),
 ("EVID-2", "Insert. Logbook page.", "A ruled page, entries stop mid-column.",
  "The log stops on 24 November", "RE-CREATED PROP"),
 ("HEAR-1", "Exterior. Gibraltar harbour, 1873.", "Stone walls, masts, grey light, gulls.",
  "The salvage hearing", "ARCHIVAL PHOTO / REENACTMENT"),
 ("FICT-1", "Interior. A desk, 1884.", "A pen, a page, a magazine cover: The Cornhill Magazine.",
  "Conan Doyle publishes", "RE-CREATED PROP"),
 ("FICT-2", "Abstract. Text on black.", "The words 'Marie Celeste' multiply and overwrite each other.",
  "The spelling that stuck", "GRAPHIC"),
 ("SHIP-3", "Exterior. Deck. Day.", "One empty set of davits. A boat that is not there.",
  "Left, not wrecked", "REENACTMENT"),
 ("CODA", "Exterior. Open Atlantic, dusk.", "Same framing as the cold open. Emptier.",
  "The thesis", "REENACTMENT"),
 ("CODA-2", "Abstract. Text on black.", "A list of details the record does not contain.",
  "What retellings added", "GRAPHIC"),
]

def main():
    out = out_dir(STAGE)
    cl = os.path.join(out, "ai-screenplay-writer")
    ok = True
    if not os.path.exists(os.path.join(cl, ".git")):
        rc = subprocess.run(["git", "clone", "--depth", "1", REPO, cl], capture_output=True, text=True, timeout=300)
        ok = rc.returncode == 0
    readme = ""
    if ok:
        for f in ("README.md", "readme.md"):
            p = os.path.join(cl, f)
            if os.path.exists(p):
                readme = open(p, encoding="utf-8", errors="replace").read()
                break
    log(STAGE, "ai-screenplay-writer", f"clone ok={ok}; LLM calls skipped (no API key in CI) - scenes written to the repo's schema")
    rows = []
    for sid, slug, action, beat, label in SCENES:
        rows.append({"slug": sid, "slugline": slug, "action": action, "beat": beat, "on_screen_label": label,
                     "dialogue": "NARRATOR (V.O.) only"})
    json.dump({"engine": "ai-screenplay-writer", "engine_cloned": ok,
               "note": "scene generation is deterministic, authored from the approved narration + claims_v1.json; no LLM was called",
               "schema_reference": "README.md present" if readme else "no readme",
               "scenes": rows}, open(os.path.join(out, "scenes.json"), "w"), indent=1)
    # continuity check: every scene must carry a disclosure label, and every label must be from the allowed set
    allowed = {"ARCHIVAL PHOTO", "REENACTMENT", "RE-CREATED PROP", "COLOURISED RECONSTRUCTION", "GRAPHIC"}
    problems = []
    for r in rows:
        lab = r["on_screen_label"].split("(")[0].strip()
        if not any(lab.startswith(a) for a in allowed):
            problems.append(f"{r['slug']}: label '{r['on_screen_label']}' is not in the disclosure set")
    json.dump(problems, open(os.path.join(out, "continuity.json"), "w"), indent=1)
    log(STAGE, "ai-screenplay-writer", f"continuity problems: {problems or 'none'}")
    print(json.dumps({"scenes": len(rows), "continuity_problems": problems}))

if __name__ == "__main__":
    main()
