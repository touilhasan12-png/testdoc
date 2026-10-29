"""Mandated tool #8 — Newspaper-OCR-V3.

Cloned and driven for real. Its designed path uses the Google Vision API, which needs a GCP key;
per the owner policy the key is not used, so the tool runs in its Tesseract mode. Input pages are
genuine Chronicling America scans fetched from tile.loc.gov. Output text is saved verbatim and the
tool's own success or failure is recorded either way.
"""
from __future__ import annotations
import json, re, subprocess
from pathlib import Path
from . import net as http
from .osint import clone, sh


def run(work: Path, log, page_images: list[dict], venv: Path) -> dict:
    out = {"tool": "PapaKaffey/Newspaper-OCR-V3", "cloned": False, "pages": [], "mode": "tesseract"}
    dest = work / "repos/Newspaper-OCR-V3"
    out["cloned"] = clone("PapaKaffey/Newspaper-OCR-V3", dest, log)
    if out["cloned"]:
        files = sorted(p.name for p in dest.rglob("*.py"))[:40]
        out["entrypoints"] = files
        readme = dest / "README.md"
        if readme.exists():
            out["readme_head"] = readme.read_text(errors="replace")[:1200]
        # what does it need?
        for reqname in ("requirements.txt", "requirements-gpu.txt"):
            r = dest / reqname
            if r.exists():
                out[reqname] = r.read_text(errors="replace")[:800]

    ocr_dir = work / "ocr"
    ocr_dir.mkdir(parents=True, exist_ok=True)

    # make sure the system OCR engine is present
    v = sh("tesseract --version 2>&1 | head -2", log, timeout=60)
    out["tesseract"] = re.sub(r"\s+", " ", (v.stdout or ""))[:120]

    for pg in page_images:
        url = pg.get("local_path") or pg.get("download_url")
        if not url:
            continue
        img = Path(pg["local_path"]) if pg.get("local_path") else None
        if img is None or not img.exists():
            continue
        rec = {"page": pg.get("label"), "source_url": pg.get("source_url"),
               "image": str(img), "ocr_tool_rc": None, "text_file": None, "chars": 0,
               "keyword_hits": {}}
        # 1) the tool itself, if it exposes a runnable entrypoint
        if out["cloned"]:
            cand = [p for p in dest.rglob("*.py") if p.name in ("main.py", "ocr_pipeline.py", "run.py", "newspaper_ocr.py")]
            if cand:
                p = sh(f"{venv}/bin/python {cand[0]} --input {img} --engine tesseract --output {ocr_dir} 2>&1 | head -20",
                       log, timeout=240)
                rec["ocr_tool_rc"] = p.returncode
                rec["ocr_tool_output"] = re.sub(r"\s+", " ", (p.stdout or ""))[-300:]
        # 2) tesseract directly on the same scan (always recorded, never presented as the tool's output)
        base = ocr_dir / (img.stem + "_tess")
        p2 = sh(["tesseract", str(img), str(base), "-l", "eng", "--psm", "3"], log, timeout=300)
        txt_file = base.with_suffix(".txt")
        if txt_file.exists():
            text = txt_file.read_text(errors="replace")
            rec.update({"tesseract_rc": p2.returncode, "text_file": str(txt_file), "chars": len(text)})
            low = text.lower()
            for kw in ["sodder", "fayetteville", "west virginia", "five children", "fire", "missing"]:
                rec["keyword_hits"][kw] = low.count(kw)
            if re.search(r"sodder", low):
                rec["contains_sodder"] = True
                i = low.find("sodder")
                rec["context"] = re.sub(r"\s+", " ", text[max(0, i - 300):i + 600])
        out["pages"].append(rec)

    (work / "newspaper_ocr_report.json").write_text(json.dumps(out, indent=1))
    log(f"newspaper ocr: {len(out['pages'])} pages processed, "
        f"{sum(1 for p in out['pages'] if p['chars'] > 0)} produced text")
    return out
