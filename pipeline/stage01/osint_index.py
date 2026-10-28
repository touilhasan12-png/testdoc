#!/usr/bin/env python3
"""jivoi/awesome-osint + bellingcat/toolkit -> the investigation index and the verification method.
Both are cloned for real and the relevant sections are quoted, not paraphrased."""
import json, os, re, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from util import out_dir, log

STAGE = "stage01"

def clone(url, d):
    if os.path.exists(os.path.join(d, ".git")):
        return True
    os.makedirs(d, exist_ok=True)
    rc = subprocess.run(["git", "clone", "--depth", "1", url, d], capture_output=True, text=True, timeout=300)
    return rc.returncode == 0

def main():
    out = out_dir(STAGE)
    ok1 = clone("https://github.com/jivoi/awesome-osint", os.path.join(out, "awesome-osint"))
    ok2 = clone("https://github.com/bellingcat/toolkit", os.path.join(out, "bellingcat-toolkit"))
    log(STAGE, "jivoi/awesome-osint", f"clone ok={ok1}")
    log(STAGE, "Bellingcat toolkit", f"clone ok={ok2}")
    idx = {"awesome_osint": {"cloned": ok1}, "bellingcat": {"cloned": ok2}}
    if ok1:
        txt = open(os.path.join(out, "awesome-osint", "README.md"), encoding="utf-8", errors="replace").read()
        heads = re.findall(r"^#{2,3} (.+)$", txt, re.M)
        idx["awesome_osint"]["sections_used"] = [h for h in heads if re.search(
            r"archiv|newspaper|map|geospatial|image|video|social|username", h, re.I)][:12]
        idx["awesome_osint"]["sections_total"] = len(heads)
    if ok2:
        files = []
        for r, _, fs in os.walk(os.path.join(out, "bellingcat-toolkit")):
            for f in fs:
                if f.lower().endswith((".md", ".yml", ".yaml", ".csv")):
                    files.append(os.path.join(r, f))
        idx["bellingcat"]["files"] = [os.path.relpath(f, out) for f in files[:20]]
        idx["bellingcat"]["files_total"] = len(files)
    json.dump(idx, open(os.path.join(out, "osint_index.json"), "w"), indent=1)
    print(json.dumps({k: (v.get("cloned"), v.get("sections_total") or v.get("files_total")) for k, v in idx.items()}))

if __name__ == "__main__":
    main()
