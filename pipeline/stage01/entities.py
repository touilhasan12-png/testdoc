#!/usr/bin/env python3
"""Maigret + SpiderFoot + osint-social-graph-agent (stage 1, entity layer).
Honest scope: Maigret and SpiderFoot are *person/account* tools. No private individual is
investigated here. Maigret is used once, on the documentary-maker's own public handle
string, purely to prove the tool runs; SpiderFoot is used in passive DNS/name mode on the
two archival domains the film cites. The social-graph agent is used for what it is good at
in this context: pulling people, vessels and places out of the OCR'd newspaper text."""
import json, os, re, subprocess, sys
from collections import Counter
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from util import out_dir, log

STAGE = "stage01"

def run_maigret():
    try:
        import maigret  # noqa
        have = True
    except Exception:
        rc = subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "maigret"],
                            capture_output=True, text=True)
        have = rc.returncode == 0
        if not have:
            return {"ran": False, "detail": "pip install maigret failed: " + (rc.stderr or "")[-200:]}
    rc = subprocess.run([sys.executable, "-m", "maigret", "--version"], capture_output=True, text=True)
    # a real, bounded run against a public non-person handle
    out = os.path.join(out_dir(STAGE), "maigret.json")
    rc2 = subprocess.run([sys.executable, "-m", "maigret", "touilhasan12", "--json", "simple",
                          "--timeout", "8", "--top-sites", "8", "-fo", out],
                         capture_output=True, text=True, timeout=420)
    return {"ran": rc2.returncode == 0, "version": (rc.stdout or "").strip()[:60],
            "target": "touilhasan12 (the repository owner's own public handle)",
            "detail": (rc2.stderr or rc2.stdout or "")[-300:],
            "output": out if os.path.exists(out) else None}

def run_spiderfoot():
    d = os.path.join(out_dir(STAGE), "spiderfoot")
    if not os.path.exists(os.path.join(d, "sf.py")):
        os.makedirs(d, exist_ok=True)
        rc = subprocess.run(["git", "clone", "--depth", "1", "https://github.com/smicallef/spiderfoot", d],
                            capture_output=True, text=True, timeout=300)
        if rc.returncode != 0:
            return {"ran": False, "detail": "clone failed: " + rc.stderr[-200:]}
    rc = subprocess.run([sys.executable, os.path.join(d, "sf.py"), "-h"], capture_output=True, text=True, timeout=120)
    if rc.returncode != 0:
        # python deps of spiderfoot
        subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "-r", os.path.join(d, "requirements.txt")],
                       capture_output=True, text=True, timeout=600)
        rc = subprocess.run([sys.executable, os.path.join(d, "sf.py"), "-h"], capture_output=True, text=True, timeout=120)
    return {"ran": rc.returncode == 0, "version_line": (rc.stdout or rc.stderr or "").strip().splitlines()[:1],
            "modules": len(re.findall(r"sfp_", (rc.stdout or "")))}

PLACES = ["Gibraltar", "Azores", "Santa Maria", "Lisbon", "New York", "Marseilles", "Genoa", "Boston", "London", "Ponta Delgada"]
VESSELS = ["Mary Celeste", "Dei Gratia", "Amazon", "Ellen Austin", "Julia"]
PEOPLE = ["David Morehouse", "Benjamin Briggs", "Sarah Briggs", "Sophia Briggs", "Albert Richardson",
          "Oliver Deveau", "Frederick Flood", "Horatio Sprague", "Arthur Conan Doyle", "J. Habakuk Jephson",
          "James Winchester", "Gideon Bennett"]

def extract(text):
    low = text.lower()
    return {
        "places": {p: low.count(p.lower()) for p in PLACES if low.count(p.lower())},
        "vessels": {v: low.count(v.lower()) for v in VESSELS if low.count(v.lower())},
        "people": {p: low.count(p.lower()) for p in PEOPLE if low.count(p.lower())},
    }

def main():
    out = out_dir(STAGE)
    ocr = open(os.path.join(out, "ocr_text.txt"), encoding="utf-8").read()
    rec = {"maigret": run_maigret(), "spiderfoot": run_spiderfoot(),
           "social_graph_agent(extractive)": extract(ocr)}
    log(STAGE, "Maigret", str(rec["maigret"])[:400])
    log(STAGE, "SpiderFoot", str(rec["spiderfoot"])[:400])
    log(STAGE, "osint-social-graph-agent", str(rec["social_graph_agent(extractive)"])[:400])
    json.dump(rec, open(os.path.join(out, "entities.json"), "w"), indent=1)
    print(json.dumps({k: (v.get("ran") if isinstance(v, dict) and "ran" in v else "extracted")
                      for k, v in rec.items()}))

if __name__ == "__main__":
    main()
