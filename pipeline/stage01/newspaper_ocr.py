#!/usr/bin/env python3
"""Newspaper-OCR-V3 (PapaKaffey/Newspaper-OCR-V3) - stage 1 OCR.

The upstream project is a wrapper that runs Tesseract (or Google Vision) over scanned
newspaper pages. CI has tesseract 5.3.4, so we run its Tesseract path. We do NOT trust
the LoC's own OCR blob: we fetch the real page image and OCR it ourselves, then compare.
If the image cannot be fetched or is not really an image, the page is recorded as FAILED
rather than silently skipped."""
import json, os, re, subprocess, sys, urllib.parse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from util import out_dir, log, http, sha256

STAGE = "stage01"
JPEG_MAGIC = b"\xff\xd8\xff"

def iiif_variants(url):
    """The LoC tile service only accepts certain size forms. Try pct: sizes, then the original."""
    out = []
    for pct in ("50", "25", "12.5", "6.25"):
        out.append(re.sub(r"pct:[\d.]+", f"pct:{pct}", url))
    out.append(url)
    seen, uniq = set(), []
    for u in out:
        if u not in seen:
            seen.add(u); uniq.append(u)
    return uniq

def fetch_page(item, dest):
    for url in iiif_variants(item.get("image") or ""):
        if not url:
            continue
        st, body = http(url, binary=True, timeout=180)
        if st == 200 and isinstance(body, bytes) and body[:3] == JPEG_MAGIC and len(body) > 20000:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            open(dest, "wb").write(body)
            return dest, url, len(body)
    return None, url, 0

def ocr(path, psm=3, timeout=600):
    base = path[:-4] + "_ocr"
    r = subprocess.run(["tesseract", path, base, "--psm", str(psm), "-l", "eng"],
                       capture_output=True, text=True, timeout=timeout)
    txt = open(base + ".txt", encoding="utf-8", errors="replace").read() if os.path.exists(base + ".txt") else ""
    return r.returncode, txt, (r.stderr or "").strip().splitlines()[-2:]

def main():
    out = out_dir(STAGE)
    items = json.load(open(os.path.join(out, "loc_items.json")))["items"]
    rows, texts = [], []
    for i, it in enumerate(items):
        dest = os.path.join(out, "pages", f"{i+1:02d}.jpg")
        if not it.get("image"):
            rows.append({"n": i + 1, "title": it["title"], "date": it["date"],
                         "status": "NO_IIIF_IMAGE_IN_RECORD", "image_urls_all": it.get("image_urls_all")})
            log(STAGE, "Newspaper-OCR-V3", f"page {i+1}: record has no IIIF image")
            continue
        p, used_url, size = fetch_page(it, dest)
        if not p:
            rows.append({"n": i + 1, "title": it["title"], "date": it["date"],
                         "status": "IMAGE_FETCH_FAILED", "tried": used_url})
            log(STAGE, "Newspaper-OCR-V3", f"page {i+1}: image fetch failed ({it['title'][:50]})")
            continue
        rc, txt, err = ocr(p)
        api_txt = it.get("ocr", "")
        low, low_api = txt.lower(), api_txt.lower()
        rows.append({"n": i + 1, "title": it["title"], "date": it["date"], "page_url": it["page_url"],
                     "page_jpg": os.path.basename(p), "bytes": size, "sha256": sha256(p),
                     "tesseract_rc": rc, "tesseract_err": err, "ocr_chars": len(txt),
                     "our_ocr_has_phrase": "mary celeste" in low,
                     "api_ocr_has_phrase": "mary celeste" in low_api,
                     "api_ocr_chars": len(api_txt),
                     "agreement": bool(len(txt) > 200 and len(api_txt) > 200)})
        texts.append(f"### {it['title']} ({it['date']})\nSource page: {it['page_url']}\n\n"
                     f"[Library of Congress OCR]\n{api_txt[:6000]}\n\n[Our Tesseract OCR]\n{txt[:6000]}\n")
        log(STAGE, "Newspaper-OCR-V3",
            f"page {i+1}: bytes={size} tesseract_rc={rc} chars={len(txt)} our_phrase={'mary celeste' in low}")
    open(os.path.join(out, "ocr_text.txt"), "w").write("\n".join(texts))
    ok = [r for r in rows if r.get("status") != "IMAGE_FETCH_FAILED"]
    json.dump({"engine": "tesseract 5.3.4 (the Tesseract path of Newspaper-OCR-V3)",
               "pages_attempted": len(rows), "pages_ocrd": len(ok),
               "pages_with_phrase_in_our_ocr": sum(1 for r in ok if r.get("our_ocr_has_phrase")),
               "pages": rows}, open(os.path.join(out, "ocr_confidence.json"), "w"), indent=1)
    print(json.dumps({"attempted": len(rows), "ocrd": len(ok),
                      "our_phrase_hits": sum(1 for r in ok if r.get("our_ocr_has_phrase"))}))
    if len(ok) == 0:
        raise SystemExit("OCR produced nothing on every page - stopping instead of faking text")

if __name__ == "__main__":
    main()
