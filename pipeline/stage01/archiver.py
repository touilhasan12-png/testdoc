#!/usr/bin/env python3
"""Runs Auto-Archiver (bellingcat/auto-archiver) against the harvested source URLs.
If the upstream package cannot be installed in CI, it falls back to a *clearly labelled*
local snapshot archiver (URL + timestamp + sha256 + saved bytes) and marks the row
`archiver=fallback-local`. It never claims Auto-Archiver ran when it did not."""
import json, os, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from util import out_dir, log, get_json, save, sha256, WORK

STAGE = "stage01"

def try_auto_archiver():
    rc = subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "auto-archiver"],
                        capture_output=True, text=True).returncode
    if rc != 0:
        return False, "pip install auto-archiver failed"
    rc = subprocess.run([sys.executable, "-m", "auto_archiver", "--help"], capture_output=True, text=True).returncode
    return (rc == 0), ("CLI present" if rc == 0 else "CLI missing after install")

def fallback(url, dest_dir):
    st, _ = get_json(url) if False else (None, None)
    d, h = save(url, os.path.join(dest_dir, "snapshot.bin"))
    if d:
        return {"archiver": "fallback-local", "http": 200, "sha256": h, "bytes": os.path.getsize(d)}
    return {"archiver": "fallback-local", "http": h, "sha256": None, "bytes": 0}

def main():
    out = out_dir(STAGE)
    items = json.load(open(os.path.join(out, "loc_items.json")))["items"]
    ok, detail = try_auto_archiver()
    log(STAGE, "Auto-Archiver", f"install/CLI check: ok={ok} detail={detail}")
    index = []
    for i, it in enumerate(items[:12]):
        target = it.get("page_url")
        if not target:
            continue
        rec = {"n": i + 1, "title": it["title"], "date": it["date"], "url": target}
        if ok:
            rc = subprocess.run([sys.executable, "-m", "auto_archiver", target], capture_output=True, text=True, timeout=300)
            rec.update({"archiver": "auto-archiver", "returncode": rc.returncode,
                        "stdout_tail": rc.stdout[-300:], "stderr_tail": rc.stderr[-300:]})
        else:
            rec.update(fallback(target, os.path.join(out, "snapshots", f"{i+1:02d}")))
        index.append(rec)
        log(STAGE, rec["archiver"], f"{rec['title'][:60]} -> {rec.get('sha256') or rec.get('returncode')}")
    json.dump({"auto_archiver_available": ok, "detail": detail, "archived": index},
              open(os.path.join(out, "archive_index.json"), "w"), indent=1)
    print(json.dumps({"archived": len(index), "engine": "auto-archiver" if ok else "fallback-local"}))

if __name__ == "__main__":
    main()
