"""Keyless archival asset discovery: Wikimedia Commons, Wikipedia, Archive.org.

Feeds stages 9 (restoration), 10 (real footage) and 5 (documents). Every candidate carries its
licence and attribution so CREDITS.md can be written mechanically later.
"""
from __future__ import annotations
import json, re
from pathlib import Path
from . import net as http

COMMONS = "https://commons.wikimedia.org/w/api.php"
WIKI_EN = "https://en.wikipedia.org/w/api.php"
IA_SEARCH = "https://archive.org/advancedsearch.php"
IA_META = "https://archive.org/metadata/"
WAYBACK = "https://archive.org/wayback/available"

PD_TAGS = ("pd", "public domain", "cc0", "cc-by", "cc-by-sa", "us-gov", "no known restrictions")


def commons_files(queries: list[str], log, limit: int = 20) -> list[dict]:
    out = []
    for q in queries:
        params = {
            "action": "query", "format": "json", "generator": "search",
            "gsrsearch": f"filetype:bitmap {q}", "gsrnamespace": 6, "gsrlimit": min(limit, 50),
            "prop": "imageinfo", "iiprop": "url|size|extmetadata|mime",
            "iiextmetadatafilter": "LicenseShortName|LicenseUrl|Artist|DateTimeOriginal|ImageDescription|Credit",
        }
        st, d, err = http.api(COMMONS, params, timeout=45)
        pages = ((d or {}).get("query") or {}).get("pages") or {}
        log(f"commons q={q!r} status={st} hits={len(pages)} err={err}")
        for p in pages.values():
            ii = (p.get("imageinfo") or [{}])[0]
            em = ii.get("extmetadata") or {}
            def v(k):
                x = em.get(k) or {}
                return re.sub(r"<[^>]+>", "", str(x.get("value") or "")).strip()[:300]
            lic = v("LicenseShortName")
            out.append({
                "query": q, "title": p.get("title"), "license": lic,
                "artist": v("Artist"), "credit": v("Credit"), "date_original": v("DateTimeOriginal"),
                "description": v("ImageDescription")[:240],
                "width": ii.get("width"), "height": ii.get("height"),
                "url": ii.get("url"), "thumb": ii.get("thumburl"),
                "pageurl": ii.get("descriptionurl"),
                "commercial_safe": any(t in lic.lower() for t in PD_TAGS) if lic else False,
                "source": "wikimedia-commons",
            })
        http.polite(1.0)
    return out


def ia_items(queries: list[str], log, rows: int = 20) -> list[dict]:
    """Archive.org metadata search. The fl[] parameter only survives one field per request,
    so fields are fetched separately and zipped by index (verified behaviour in recon)."""
    fields = ["identifier", "title", "year", "mediatype", "licenseurl", "downloads", "creator"]
    out = []
    for q in queries:
        cols = {}
        for fl in fields:
            st, d, err = http.fetch_json(
                IA_SEARCH + "?" + f"q={re.sub(r'[^A-Za-z0-9 \"_-]', '', q).replace(' ', '+')}"
                + f"&fl%5B%5D={fl}&rows={rows}&page=1&output=json", timeout=45)
            docs = ((d or {}).get("response") or {}).get("docs") or []
            cols[fl] = [x.get(fl) for x in docs]
            if fl == "identifier":
                numfound = ((d or {}).get("response") or {}).get("numFound")
        n = len(cols.get("identifier") or [])
        log(f"archive.org q={q!r} numFound={numfound if 'numfound' in dir() else '?'} returned={n}")
        for i in range(n):
            rec = {fl: (cols.get(fl) or [None] * n)[i] for fl in fields}
            lic = rec.get("licenseurl") or ""
            rec.update({
                "query": q, "source": "archive-org",
                "commercial_safe": (not lic) or any(t in str(lic).lower() for t in PD_TAGS),
                "license": lic or "see item record",
                "detail_url": f"https://archive.org/details/{rec.get('identifier')}",
            })
            out.append(rec)
        http.polite(1.0)
    return out


def ia_files(identifier: str, log, limit: int = 40) -> list[dict]:
    """List the files inside one Archive.org item (for stage 10 real footage / stills)."""
    st, d, err = http.fetch_json(IA_META + identifier, timeout=60)
    if not d:
        log(f"archive.org metadata failed {identifier} status={st} err={err}")
        return []
    misc = d.get("misc") or {}
    server = misc.get("server")
    dirp = misc.get("dir")
    files = []
    for f in (d.get("files") or [])[:limit]:
        name = f.get("name")
        files.append({
            "identifier": identifier, "name": name, "format": f.get("format"),
            "size": f.get("size"), "source": f.get("source"),
            "url": f"https://archive.org/download/{identifier}/{name}" if name else None,
            "server": server, "dir": dirp,
        })
    log(f"archive.org files {identifier}: {len(files)} listed")
    return files


def wayback(url: str, log) -> dict:
    """Keyless Wayback availability check used by the archiver fallback."""
    st, d, err = http.fetch_json(WAYBACK + "?url=" + re.sub(r"[^\w:/.\-?=&%]", "", url), timeout=40)
    snap = ((d or {}).get("archived_snapshots") or {}).get("closest") or {}
    rec = {"target": url, "available": bool(snap.get("available")),
           "timestamp": snap.get("timestamp"), "url": snap.get("url"), "status": st, "error": err}
    log(f"wayback {url[:64]} -> available={rec['available']} ts={rec['timestamp']}")
    return rec


def wikipedia_sources(page: str, log) -> dict:
    """Pull the article wikitext, its citations and its coordinate template."""
    st, txt, err = http.fetch(f"https://en.wikipedia.org/w/index.php?title={page}&action=raw", timeout=60)
    if not txt:
        log(f"wikipedia raw failed {page} status={st} err={err}")
        return {"ok": False, "error": err}
    refs = []
    for i, block in enumerate(re.findall(r"<ref[^>]*>(.*?)</ref>", txt, re.S), start=1):
        flat = re.sub(r"\s+", " ", block).strip()
        def field(*names):
            for n in names:
                m = re.search(r"\|\s*" + n + r"\s*=\s*([^|}]+)", flat)
                if m:
                    return re.sub(r"\[\[|\]\]", "", m.group(1)).strip()
            return None
        refs.append({
            "ref_id": f"W{i:02d}", "index": i,
            "title": field("title"), "url": field("url"),
            "work": field("work", "website", "newspaper", "journal", "magazine"),
            "publisher": field("publisher"), "date": field("date"),
            "access_date": field("access-date", "accessdate"),
            "archive_url": field("archive-url", "archiveurl"),
            "raw": flat[:600],
        })
    coord = re.search(r"\{\{coord\|([-\d.]+)\|([-\d.]+)", txt)
    log(f"wikipedia {page}: {len(refs)} citations, coords={coord.groups() if coord else None}")
    return {
        "ok": True, "page": page, "wikitext": txt, "citations": refs,
        "coords": {"lat": float(coord.group(1)), "lon": float(coord.group(2))} if coord else None,
        "revid_url": f"https://en.wikipedia.org/w/index.php?title={page}&action=history",
    }
