#!/usr/bin/env python3
"""Stage 1 - research. Runs the eight research tools in order and writes one stage report.
Every step is recorded; a failed mandatory step is reported as failed (never as passed)."""
import json, os, subprocess, sys, traceback
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from util import out_dir, log, write_json

HERE = os.path.dirname(os.path.abspath(__file__))
STAGE = "stage01"
STEPS = [
    ("jivoi/awesome-osint + Bellingcat toolkit", "osint_index.py"),
    ("Chronicling America / libofcongress-mcp (SUBSTITUTED)", "loc_client.py"),
    ("Auto-Archiver", "archiver.py"),
    ("Newspaper-OCR-V3 (Tesseract path)", "newspaper_ocr.py"),
    ("Maigret + SpiderFoot + osint-social-graph-agent", "entities.py"),
]

def main():
    results = []
    for name, script in STEPS:
        log(STAGE, name, "start")
        try:
            p = subprocess.run([sys.executable, os.path.join(HERE, script)],
                               capture_output=True, text=True, timeout=1800)
            ok = p.returncode == 0
            results.append({"tool": name, "script": script, "ok": ok, "rc": p.returncode,
                            "stdout": p.stdout[-1500:], "stderr": p.stderr[-1500:]})
            log(STAGE, name, f"done ok={ok}")
        except Exception as e:
            results.append({"tool": name, "script": script, "ok": False, "error": str(e)})
            log(STAGE, name, f"EXCEPTION {e}")
    out = out_dir(STAGE)
    write_json(os.path.join(out, "stage01_report.json"), results)
    failed = [r["tool"] for r in results if not r["ok"]]
    print(json.dumps({"steps": len(results), "failed": failed}, indent=1))
    if failed:
        print("FAILED STEPS: " + "; ".join(failed))
        raise SystemExit(1)

if __name__ == "__main__":
    main()
