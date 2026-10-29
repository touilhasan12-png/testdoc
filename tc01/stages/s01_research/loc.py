"""Mandated tools #6 Chronicling America and #7 the Library of Congress bridge.

The dedicated chroniclingamerica.loc.gov search API is retired (308 -> 404, verified in stage 0).
The live keyless paths are the LoC JSON views:
    /collections/chronicling-america/?q=...&fo=json     newspaper PAGES, full text
    /photos/?q=...&fo=json                              photographs (FSA/OWI etc.)
    /item/<id>/?fo=json                                 one item record
    tile.loc.gov/...                                    IIIF image services + OCR text
"""
from __future__ import annotations
import json, re
from pathlib import Path
from . import net as http

COLL_CA = "https://www.loc.gov/collections/chronicling-america/"
PHOTOS = "https://www.loc.gov/photos/"
SEARCH = "https://www.loc.gov/search/"


def _results(url: str, params: dict, log) -> list[dict]:
    p = {"fo": "json", "c": 40, "at": "results"}
    p.update(params)
    st, d, err = http.api(url, p)
    if not d:
        log(f"loc query failed url={url} params={params} status={st} err={err}")
        return []
    out = d.get("results") or []
    of = (d.get("pagination") or {}).get("of")
    log(f"loc query ok url={url.split('loc.gov')[1][:44]} q={params.get('q','')!r} of={of} got={len(out)}")
    return out


def search_newspaper_pages(queries: list[str], log, limit: int = 40) -> list[dict]:
    """#6 Chronicling America: full-text page search."""
    hits = []
    for q in queries:
        for r in _results(COLL_CA, {"q": q}, log)[:limit]:
            hits.append({
                "query": q,
                "title": r.get("title"),
                "date": r.get("date"),
                "url": r.get("url"),
                "id": (r.get("id") or "").rsplit("/", 2)[-1] if r.get("id") else None,
                "image_url": (r.get("image_url") or [None])[0] if isinstance(r.get("image_url"), list) else r.get("image_url"),
                "shelf": r.get("shelf_id"),
                "source": "chronicling-america",
            })
        http.polite(1.2)
    return hits


def search_photos(queries: list[str], log, limit: int = 25) -> list[dict]:
    """#7 LoC bridge: photograph search (FSA/OWI, HABS, prints & photos)."""
    hits = []
    for q in queries:
        for r in _results(PHOTOS, {"q": q}, log)[:limit]:
            iu = r.get("image_url")
            hits.append({
                "query": q,
                "title": r.get("title"),
                "date": r.get("date"),
                "url": r.get("url"),
                "image_url": (iu[0] if isinstance(iu, list) and iu else iu),
                "source": "loc-photos",
            })
        http.polite(1.2)
    return hits


def item(item_url: str, log) -> dict | None:
    """Fetch one LoC item record as JSON and normalise the fields we need."""
    u = item_url.rstrip("/")
    u = u + "/?fo=json" if "/?" not in u and not u.endswith("fo=json") else u
    if "fo=json" not in u:
        u = u.replace("/?", "/?fo=json&") if "/?" in u else u + "?fo=json"
    st, d, err = http.fetch_json(u)
    if not d:
        log(f"loc item failed {u} status={st} err={err}")
        return None
    it = d.get("item") or d
    def g(*keys):
        for k in keys:
            v = it.get(k) or d.get(k)
            if v:
                return v
        return None
    rights = g("rights", "rights_advisory")
    if isinstance(rights, list):
        rights = "; ".join(map(str, rights))
    img = g("image_url")
    if isinstance(img, list):
        img = img[-1] if img else None
    return {
        "id": g("id", "_version_"),
        "title": g("title", "display_title"),
        "date": g("date", "date_issued", "created_published"),
        "summary": (str(g("summary") or ""))[:1200],
        "rights": (str(rights or ""))[:400],
        "repository": g("repository", "source_collection"),
        "call_number": g("call_number"),
        "medium": g("medium"),
        "url": g("url"),
        "image_url": img,
        "cite_this": (str(d.get("cite_this") or ""))[:300],
        "lccn": g("lccn"),
    }


def hires(image_url: str | None, max_px: int = 2400) -> str | None:
    """Convert any LoC thumbnail/IIIF url into a bounded high-resolution download url."""
    if not image_url:
        return None
    u = image_url.split("#")[0]
    if "/iiif/" in u:
        # .../full/pct:X/0/default.jpg  ->  .../full/{max_px},/0/default.jpg
        return re.sub(r"/full/[^/]+/0/default\.jpg$", f"/full/{max_px},/0/default.jpg", u)
    m = re.search(r"(https://tile\.loc\.gov/storage-services/service/[^ ]+?)(_\d+px\.[a-z]+)$", u)
    if m:
        return m.group(1) + "r.jpg"
    return u


def ocr_for_page(page_url: str, log) -> dict:
    """Locate and fetch the OCR text of a Chronicling America page, via the item record."""
    st, d, err = http.fetch_json(page_url.rstrip("/") + "/?fo=json")
    if not d:
        return {"ok": False, "error": err or f"status {st}"}
    ft = d.get("fulltext_service") or ""
    m = re.search(r"segment=(/service/ndnp/[^\s&]+)", ft)
    out = {"ok": False, "fulltext_service": ft, "page_url": page_url}
    if not m:
        out["error"] = "no ndnp segment in fulltext_service"
        return out
    seg = m.group(1)
    base = "https://tile.loc.gov" + seg
    for suffix in ("/ocr/", ".txt"):
        st2, txt, err2 = http.fetch(base + suffix, timeout=60)
        if txt and len(txt) > 200:
            out.update({"ok": True, "ocr_url": base + suffix, "chars": len(txt), "text": txt})
            return out
    out["error"] = "ocr endpoint returned nothing usable"
    return out


# --------------------------------------------------------------------------------------
# Verified against the live service in recon (2026-10-29):
#   GET {resource_url}?fo=json  ->  resources[0] = {
#        fulltext_file  : word-coordinates-service URL returning {"<segment>": {"full_text": ...}}
#        image          : tile.loc.gov IIIF url at /full/pct:3.125/0/default.jpg
#        pdf            : page PDF
#        iiif_manifest_url, word_coordinates, segment_count, url }
# --------------------------------------------------------------------------------------

def resource_bundle(resource_url: str, log) -> dict:
    """Return the OCR text, the IIIF image url and the PDF url for one Chronicling America page."""
    u = resource_url.split("#")[0].rstrip("/")
    if "fo=json" not in u:
        u += ("&" if "?" in u else "?") + "fo=json"
    st, d, err = http.fetch_json(u, timeout=60, retries=2)
    if not d:
        log(f"loc resource failed {resource_url} status={st} err={err}")
        return {"ok": False, "url": resource_url, "status": st, "error": err}
    res = (d.get("resources") or [{}])[0]
    out = {"ok": True, "url": resource_url, "image": res.get("image"), "pdf": res.get("pdf"),
           "iiif_manifest_url": res.get("iiif_manifest_url"),
           "fulltext_service": res.get("fulltext_file"), "cite_this": str(d.get("cite_this") or "")[:300],
           "item": {k: v for k, v in (d.get("item") or {}).items()
                    if k in ("title", "date", "lccn", "url", "ndnp_loc", "batch", "shelf_id")}}
    ft = res.get("fulltext_file")
    if ft:
        st2, raw, err2 = http.fetch(ft, timeout=90, retries=2)
        if raw:
            try:
                obj = json.loads(raw)
                texts = [v.get("full_text", "") for v in obj.values() if isinstance(v, dict)]
                out["ocr_text"] = "\n".join(t for t in texts if t)
                out["ocr_chars"] = len(out["ocr_text"])
            except Exception as e:  # noqa: BLE001
                out["ocr_text"] = raw
                out["ocr_chars"] = len(raw)
                out["ocr_parse_error"] = str(e)[:140]
        else:
            out["ocr_error"] = err2
    return out


def hires_from_iiif(image_url: str | None, px: int = 2000) -> str | None:
    if not image_url:
        return None
    return re.sub(r"/full/pct:[^/]+/0/default\.jpg$", f"/full/{px},/0/default.jpg", image_url.split("#")[0])


def search_newspaper_pages_dated(queries: list[str], log, date_from: str = "1945", date_to: str = "1970",
                                 limit: int = 25) -> list[dict]:
    """#6 Chronicling America with a date window — the only honest way to look for period coverage."""
    hits = []
    for q in queries:
        params = {"q": q, "dates": f"{date_from}/{date_to}"}
        for r in _results(COLL_CA, params, log)[:limit]:
            hits.append({"query": q, "date_window": f"{date_from}-{date_to}", "title": r.get("title"),
                         "date": r.get("date"), "url": r.get("url"),
                         "image_url": (r.get("image_url") or [None])[0] if isinstance(r.get("image_url"), list) else r.get("image_url"),
                         "source": "chronicling-america"})
        http.polite(1.2)
    return hits
