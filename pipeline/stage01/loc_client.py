#!/usr/bin/env python3
"""SUBSTITUTE for libofcongress-mcp-server (no upstream repo exists under that name).
Function: query the Library of Congress JSON API and return normalised item records
with the full OCR text of each newspaper page, so the agent can cite and archive them."""
import json, os, sys, urllib.parse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from util import get_json, out_dir, log, write_json

STAGE = "stage01"

def search(q, date_from, date_to, limit=25):
    url = ("https://www.loc.gov/collections/chronicling-america/?"
           + urllib.parse.urlencode({"q": q, "dates": f"{date_from}/{date_to}",
                                     "fo": "json", "c": limit, "sb": "date"}))
    st, d = get_json(url)
    if d is None:
        return [], f"HTTP {st}"
    items = []
    for r in d.get("results", []):
        items.append({
            "title": r.get("title"),
            "date": r.get("date"),
            "page_url": r.get("id"),
            "item_url": r.get("url"),
            "ocr": (r.get("description") or [""])[0] if r.get("description") else "",
            "image": (r.get("image_url") or [None])[-1],
            "source": "Library of Congress, Chronicling America",
        })
    return items, None

def main():
    out = out_dir(STAGE)
    # The LoC full-text index is noisy (it matches the words separately). We keep the
    # broad harvest for the record, then tighten with a quoted phrase search, and we keep
    # only pages whose own OCR actually contains the phrase - no inferred hits.
    plan = [
        ("broad", "Mary Celeste", "1872-11-01", "1885-12-31", 40),
        ("phrase", '"Mary Celeste"', "1872-11-01", "1885-12-31", 40),
        ("wreck", '"Mary Celeste" wreck', "1872-12-01", "1874-12-31", 25),
        ("doyle", '"J. Habakuk Jephson"', "1884-01-01", "1886-12-31", 25),
    ]
    all_items, errors, per_query = [], [], {}
    for tag, q, a, b, lim in plan:
        items, err = search(q, a, b, lim)
        per_query[tag] = {"q": q, "from": a, "to": b, "returned": len(items), "error": err}
        log(STAGE, "libofcongress-mcp(SUBSTITUTED)", f"[{tag}] q='{q}' {a}..{b} -> {len(items)} items {err or ''}")
        if err:
            errors.append(f"{tag}: {err}")
        for it in items:
            it["query_tag"] = tag
        all_items += items
    seen, uniq = set(), []
    for it in all_items:
        k = it["page_url"]
        if k and k not in seen:
            seen.add(k); uniq.append(it)
    verified = [it for it in uniq if "mary celeste" in (it.get("ocr") or "").lower()]
    write_json(os.path.join(out, "loc_items.json"),
               {"query_errors": errors, "per_query": per_query, "count_raw": len(uniq),
                "count_phrase_verified": len(verified), "items": verified or uniq})
    print(json.dumps({"raw": len(uniq), "phrase_verified": len(verified), "errors": errors}))
    if not uniq:
        raise SystemExit("no LoC items retrieved - stopping rather than inventing sources")

if __name__ == "__main__":
    main()
