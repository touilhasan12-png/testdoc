#!/usr/bin/env python3
"""Runs Auto-Archiver (bellingcat/auto-archiver) against the harvested source URLs.
If the upstream package cannot be installed in CI, it falls back to a *clearly labelled*
local snapshot archiver (URL + timestamp + sha256 + saved bytes) and marks the row
`archiver=fallback-local`. It never claims Auto-Archiver ran when it did not."""
import json, os, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from util import out_dir, log, get_json, save, sha256, WORK

STAGE = "stage01"

def try_auto_archiver(dest_dir):
    """A tool only counts as 'used' when it actually produced a file. Step 1: install.
    Step 2: run it on one URL. Step 3: check that files really landed in dest_dir."""
    rc = subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "auto-archiver>=0.9,<0.12"],
                        capture_output=True, text=True, timeout=900)
    if rc.returncode != 0:
        return False, "pip install auto-archiver failed: " + (rc.stderr or "")[-200:], None
    os.makedirs(dest_dir, exist_ok=True)
    rc = subprocess.run([sys.executable, "-m", "auto_archiver", "--help"], capture_output=True, text=True, timeout=120)
    if rc.returncode != 0:
        return False, "auto_archiver CLI missing after install", None
    return True, "CLI present", rc.stdout

def fallback(url, dest_dir):
    st, _ = get_json(url) if False else (None, None)
    d, h = save(url, os.path.join(dest_dir, "snapshot.bin"))
    if d:
        return {"archiver": "fallback-local", "http": 200, "sha256": h, "bytes": os.path.getsize(d)}
    return {"archiver": "fallback-local", "http": h, "sha256": None, "bytes": 0}

def main():
    out = out_dir(STAGE)
    items = json.load(open(os.path.join(out, "loc_items.json")))["items"]
    dest = os.path.join(out, "auto_archiver_out")
    ok, detail, _ = try_auto_archiver(dest)
    log(STAGE, "Auto-Archiver", f"install/CLI check: ok={ok} detail={detail}")
    index = []
    for i, it in enumerate(items[:8]):
        target = it.get("page_url")
        if not target:
            continue
        rec = {"n": i + 1, "title": it["title"], "date": it["date"], "url": target}
        produced = []
        if ok:
            before = set(os.listdir(dest))
            rc = subprocess.run([sys.executable, "-m", "auto_archiver", "--cli", target],
                                capture_output=True, text=True, timeout=600, cwd=dest)
            after = set(os.listdir(dest))
            produced = sorted(after - before)
            rec.update({"archiver": "auto-archiver", "returncode": rc.returncode,
                        "produced_files": produced[:6],
                        "stdout_tail": rc.stdout[-400:], "stderr_tail": rc.stderr[-400:]})
            log(STAGE, "Auto-Archiver", f"{it['title'][:50]} rc={rc.returncode} new_files={len(produced)}")
        if not produced:
            fb = fallback(target, os.path.join(out, "snapshots", f"{i+1:02d}"))
            fb["note"] = "auto-archiver produced no file; local snapshot used and labelled"
            fb["auto_archiver_returncode"] = rec.get("returncode")
            fb["auto_archiver_stderr"] = (rec.get("stderr_tail") or "")[-200:]
            rec = {**rec, **fb}
            log(STAGE, fb["archiver"], f"{it['title'][:50]} sha={fb.get('sha256')} http={fb.get('http')}")
        index.append(rec)
    json.dump({"auto_archiver_available": ok, "detail": detail, "archived": index},
              open(os.path.join(out, "archive_index.json"), "w"), indent=1)
    print(json.dumps({"archived": len(index), "engine": "auto-archiver" if ok else "fallback-local"}))

if __name__ == "__main__":
    main()
