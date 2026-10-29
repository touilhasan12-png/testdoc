#!/usr/bin/env python3
"""SUBSTITUTE for STORYMACHINE (no repository exists under that name).
Function: a structural diagnostic over the script - beat coverage, claim coverage, runtime,
repetition, and the two rules this film must never break (no unlabelled reconstruction, no
claim without an archived source)."""
import json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from util import out_dir, log

STAGE = "stage02"
HERE = os.path.dirname(os.path.abspath(__file__))

def main():
    out = out_dir(STAGE)
    src = open(os.path.join(HERE, "source", "narration_v2.txt"), encoding="utf-8").read()
    claims = json.load(open(os.path.join(HERE, "source", "claims_v2.json")))["claims"]
    scenes = json.load(open(os.path.join(out, "scenes.json")))["scenes"]
    narr = [l.split(":", 1)[1].strip() for l in src.splitlines() if l.startswith("NARRATOR:")]
    words = sum(len(re.findall(r"[A-Za-z']+", n)) for n in narr)
    runtime_min = words / 140.0
    findings = []
    # 1. runtime
    findings.append({"check": "runtime", "value": round(runtime_min, 2),
                     "pass": 3.5 <= runtime_min <= 5.5,
                     "note": "target 4:55 first cut; 4:55 final with title + end card"})
    # 2. every claim has at least one source
    unbacked = [c["id"] for c in claims if not c["sources"]]
    findings.append({"check": "claims_without_source", "value": unbacked, "pass": not unbacked})
    # 3. claim coverage of the narration: every claim's key noun appears in the narration
    missing = []
    for c in claims:
        key = c["text"].split()[0:4]
        if not any(k.lower().strip(",") in src.lower() for k in key[1:3]):
            missing.append(c["id"])
    findings.append({"check": "claims_not_expressed_in_narration", "value": missing, "pass": not missing})
    # 4. disclosure labels present for every visual beat
    unlabeled = [s["slug"] for s in scenes if not s.get("on_screen_label")]
    findings.append({"check": "scenes_without_disclosure", "value": unlabeled, "pass": not unlabeled})
    # 5. banned words: the film must not assert a solution, and must not gore
    banned = [w for w in ["murdered", "killed them", "blood everywhere", "corpse", "ghost did", "proved that"]
              if w in src.lower()]
    findings.append({"check": "banned_assertions", "value": banned, "pass": not banned})
    # 6. repetition: any 8-word sequence twice?
    grams = {}
    flat = " ".join(narr).lower()
    toks = re.findall(r"[a-z']+", flat)
    dup = set()
    for i in range(len(toks) - 7):
        g = " ".join(toks[i:i + 8])
        if g in grams:
            dup.add(g)
        grams[g] = i
    findings.append({"check": "repeated_8grams", "value": sorted(dup)[:5], "pass": not dup})
    ok = all(f["pass"] for f in findings)
    json.dump({"engine": "STORYMACHINE (SUBSTITUTED)", "words": words, "est_minutes": round(runtime_min, 2),
               "findings": findings, "verdict": "PASS" if ok else "FAIL"},
              open(os.path.join(out, "diagnostic.json"), "w"), indent=1)
    log(STAGE, "STORYMACHINE(SUBSTITUTED)", f"verdict={'PASS' if ok else 'FAIL'} findings={[f for f in findings if not f['pass']]}")
    print(json.dumps({"verdict": "PASS" if ok else "FAIL",
                      "failed": [f["check"] for f in findings if not f["pass"]]}))

if __name__ == "__main__":
    main()
