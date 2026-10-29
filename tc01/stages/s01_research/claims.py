"""Build the claim register (rule 4: no source, no claim).

Wikipedia's citation model is name-based: one <ref name="X">FULL CITATION</ref> defines a source and
every later <ref name="X" /> reuses it. Counting only the definitions silently loses ~90% of the
attribution — the real article has 96 markers and 11 definitions. This module resolves names to
definitions, keeps the marker order, and attributes sources to a claim both at sentence level and,
where a paragraph carries the citation at its end, at paragraph level.
"""
from __future__ import annotations
import json, re
from pathlib import Path

MONTHS = r"(?:January|February|March|April|May|June|July|August|September|October|November|December)"
FACT_CUES = [
    re.compile(r"\b(?:19|20)\d{2}\b"),
    re.compile(rf"\b{MONTHS}\b"),
    re.compile(r"\b\d+\b"),
    re.compile(r"\b(?:coroner|inquest|jury|police|state|FBI|grand jury|reward|excavat|fire department)\w*", re.I),
    re.compile(r"\b(?:fire|burned|burnt|ashes|remains|bones|disappear\w*|missing)\b", re.I),
]
DROP_CUES = re.compile(r"^\s*(?:See also|References|External links|Notes|Bibliography|Further reading)\s*$", re.I)
MARK = re.compile(r"\^C(\d+)\^")


def parse_citations(wikitext: str) -> tuple[list[dict], list[str | None], dict]:
    """Return (definitions, ordered marker names, name->definition)."""
    defs: list[dict] = []
    by_name: dict[str, dict] = {}
    order: list[str | None] = []
    n = 0
    for m in re.finditer(r"<ref([^>]*?)(?:/>|>(.*?)</ref>)", wikitext, re.S):
        n += 1
        attrs, body = m.group(1) or "", m.group(2) or ""
        nm = re.search(r'name\s*=\s*"?([^"\s/>]+)', attrs)
        name = nm.group(1) if nm else None
        order.append(name)
        if body.strip():
            flat = re.sub(r"\s+", " ", body).strip()

            def field(*names):
                for f in names:
                    mm = re.search(r"\|\s*" + f + r"\s*=\s*([^|}]+)", flat)
                    if mm:
                        return re.sub(r"\[\[|\]\]", "", mm.group(1)).strip()
                return None

            rec = {
                "ref_id": f"W{len(defs) + 1:02d}", "name": name, "marker_no": n,
                "title": field("title"), "url": field("url"),
                "work": field("work", "website", "newspaper", "journal", "magazine"),
                "publisher": field("publisher"), "author": field("last", "author"),
                "date": field("date"), "access_date": field("access-date", "accessdate"),
                "archive_url": field("archive-url", "archiveurl"),
                "url_status": field("url-status"), "raw": flat[:700],
            }
            defs.append(rec)
            if name:
                by_name[name] = rec
    return defs, order, by_name


def clean_inline(wikitext: str) -> str:
    """Wikitext -> readable prose, citations preserved as sequential ^Cn^ markers."""
    t = wikitext
    t = re.sub(r"<!--.*?-->", " ", t, flags=re.S)
    t = re.sub(r"\{\{Notelist\}\}|\{\{Reflist[^}]*\}\}|\{\{reflist[^}]*\}\}", " ", t)

    counter = {"n": 0}

    def _mark(m):
        counter["n"] += 1
        return f" ^C{counter['n']}^ "

    t = re.sub(r"<ref[^>]*?/>", _mark, t)                      # reuse markers
    t = t if False else re.sub(r"<ref[^>]*?>.*?</ref>", _mark, t, flags=re.S)   # full definitions

    t = re.sub(r"\{\{(?:cite|Cite)[^{}]*\}\}", " ", t)
    t = re.sub(r"\{\{efn\|([^}]*)\}\}", r" \1 ", t)
    t = re.sub(r"\{\{convert\|([\d.]+)\|(\w+)\|([\d.]+)\|(\w+)[^}]*\}\}", r"\1 \2 (\3 \4)", t)
    t = re.sub(r"\{\{[^{}]*\}\}", " ", t)
    t = re.sub(r"\{\{[^{}]*\}\}", " ", t)
    t = re.sub(r"\[\[(?:File|Image|Category):[^\]]*\]\]", " ", t, flags=re.I)
    t = re.sub(r"<\s*/?\s*(?:ref|nowiki|gallery|table|tr|td|th|br|small|sup)[^>]*>", " ", t, flags=re.I)
    t = re.sub(r"\[\[[^|\]]*\|([^\]]*)\]\]", r"\1", t)
    t = re.sub(r"\[\[([^\]]*)\]\]", r"\1", t)
    t = re.sub(r"'''?|''", "", t)
    t = re.sub(r"https?://\S+", " ", t)
    t = re.sub(r"&nbsp;|&amp;|&ndash;|&mdash;", lambda m: {"&nbsp;": " ", "&amp;": "&",
                                                           "&ndash;": "-", "&mdash;": "-"}[m.group(0)], t)
    t = re.sub(r"[ \t]+", " ", t)
    return t


def sections(wikitext: str) -> list[tuple[str, str]]:
    parts = re.split(r"\n(={2,6})\s*(.+?)\s*\1\s*\n", wikitext)
    out = [("LEAD", parts[0])]
    i = 1
    while i + 2 <= len(parts) - 1:
        out.append((parts[i + 1].strip(), parts[i + 2]))
        i += 3
    return out


def extract(wikitext: str, log) -> dict:
    defs, order, by_name = parse_citations(wikitext)
    log(f"citations: {len(defs)} definitions, {len(order)} markers in the article body")

    claims, cid = [], 0
    prose_by_sec = {}
    for sec_name, sec_raw in sections(wikitext):
        if DROP_CUES.match(sec_name):
            continue
        prose = clean_inline(sec_raw)
        prose_by_sec[sec_name] = prose.strip()
        for para in [p for p in re.split(r"\n\s*\n", prose) if p.strip()]:
            para_markers = set(int(x) for x in MARK.findall(para))
            for sent in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'])", para):
                s = re.sub(r"\s+", " ", sent).strip()
                if len(s) < 40 or len(s) > 480:
                    continue
                if not any(p.search(s) for p in FACT_CUES):
                    continue
                sent_markers = set(int(x) for x in MARK.findall(s))
                text = MARK.sub("", s).strip()
                text = re.sub(r"\s{2,}", " ", text)
                used = sent_markers or para_markers       # paragraph-level fallback
                resolved = []
                for mn in sorted(used):
                    if 1 <= mn <= len(order):
                        nm = order[mn - 1]
                        rec = by_name.get(nm) if nm else None
                        if rec and rec["ref_id"] not in [r["ref_id"] for r in resolved]:
                            resolved.append(rec)
                        elif not rec and nm is None and mn <= len(defs):
                            if defs[mn - 1]["ref_id"] not in [r["ref_id"] for r in resolved]:
                                resolved.append(defs[mn - 1])
                cid += 1
                claims.append({
                    "claim_id": f"C{cid:03d}", "section": sec_name, "text": text,
                    "attribution": "sentence" if sent_markers else ("paragraph" if para_markers else "none"),
                    "sources": [{
                        "source_id": r["ref_id"], "title": r.get("title"), "work": r.get("work"),
                        "publisher": r.get("publisher"), "author": r.get("author"),
                        "url": r.get("url"), "date": r.get("date"),
                        "archive_url": r.get("archive_url"), "url_status": r.get("url_status"),
                    } for r in resolved],
                    "has_year": bool(re.search(r"\b(?:19|20)\d{2}\b", text)),
                })

    for c in claims:
        srcs = c["sources"]
        contemporaneous = [s for s in srcs if re.search(r"\b(?:194[5-9]|195\d|196\d)\b", str(s.get("date") or ""))]
        c["evidence"] = {
            "n_sources": len(srcs),
            "contemporaneous_source": bool(contemporaneous),
            "has_archived_copy": any(s.get("archive_url") for s in srcs),
        }
        c["status"] = ("SOURCED_PERIOD" if contemporaneous
                       else "SOURCED_SECONDARY" if srcs else "UNSOURCED")

    counts: dict[str, int] = {}
    for c in claims:
        counts[c["status"]] = counts.get(c["status"], 0) + 1
    used_sources = sorted({s["source_id"] for c in claims for s in c["sources"]})
    log(f"claims extracted: {len(claims)} | {counts} | sources used: {used_sources}")
    return {
        "claims": claims, "citations": defs, "marker_order": order,
        "prose_by_section": prose_by_sec, "status_counts": counts,
        "unsourced": [c["claim_id"] for c in claims if c["status"] == "UNSOURCED"],
        "sources_used": used_sources,
    }
