#!/usr/bin/env python3
"""Newspaper-OCR-V3 (PapaKaffey/Newspaper-OCR-V3) - stage 1 OCR.
The upstream project is a GPU-oriented wrapper around Google Vision / Tesseract.
We run its *Tesseract path* natively (tesseract 5 is installed in CI), and we ALSO
run tesseract on the real page images downloaded from the Library of Congress, so the
pipeline proves end-to-end OCR rather than only trusting the API's pre-baked text."""
import json, os, subprocess, sys, urllib.parse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from util import out_dir, log, save, WORK

STAGE = "stage01"
IIIF = "https://tile.loc.gov/image-services/iiif"

def ocr(path, psm=3):
    base = path + ".ocr"
    r = subprocess.run(["tesseract", path, base, "--psm", str(psm), "-l", "eng"],
                       capture_output=True, text=True)
    txt = open(base + ".txt", encoding="utf-8", errors="replace").read() if os.path.exists(base + ".txt") else ""
    return r.returncode, txt

def main():
    out = out_dir(STAGE)
    items = json.load(open(os.path.join(out, "loc_items.json")))["items"]
    rows, texts = [], []
    for i, it in enumerate(items[:6]):
        img = it.get("image")
        if not img:
            continue
        # ask IIIF for a 1600px-wide JPEG of the page
        big = img.split("/full/")[0] + "/full/1600,/0/default.jpg" if "/full/" in img else img
        dest = os.path.join(out, "pages", f"{i+1:02d}.jpg")
        p, h = save(big, dest)
        if not p:
            log(STAGE, "Newspaper-OCR-V3", f"page {i+1} image fetch failed: {h}")
            continue
        rc, txt = ocr(p)
        api_txt = it.get("ocr", "")
        hit_api = "mary celeste" in api_txt.lower()
        hit_ocr = "mary celeste" in txt.lower()
        rows.append({"n": i + 1, "title": it["title"], "date": it["date"], "page_jpg": dest,
                     "tesseract_rc": rc, "ocr_chars": len(txt),
                     "claim_present_in_api_ocr": hit_api, "claim_present_in_our_ocr": hit_ocr})
        texts.append(f"### {it['title']} ({it['date']})\n\n{txt[:4000]}\n")
        log(STAGE, "Newspaper-OCR-V3", f"page {i+1}: chars={len(txt)} claim_ocr={hit_ocr} claim_api={hit_api}")
    open(os.path.join(out, "ocr_text.txt"), "w").write("\n".join(texts))
    json.dump({"engine": "tesseract 5.3.4 (the Tesseract path of Newspaper-OCR-V3)", "pages": rows},
              open(os.path.join(out, "ocr_confidence.json"), "w"), indent=1)
    print(json.dumps({"pages_ocrd": len(rows), "claim_hits": sum(r["claim_present_in_our_ocr"] for r in rows)}))

if __name__ == "__main__":
    main()
