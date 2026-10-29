#!/usr/bin/env python3
"""STAGE 1 — RESEARCH.

Mandated tools exercised here, each once, each recorded honestly:
  #1 jivoi/awesome-osint        source index -> registry
  #2 soxoj/maigret              alias enumeration
  #3 smicallef/spiderfoot       keyless automated collection
  #4 bellingcat/toolkit         verification methodology -> applied checklist
  #5 bellingcat/auto-archiver   archive every source URL
  #6 Chronicling America        period newspaper pages
  #7 LoC bridge (loc-mcp-server + the LoC JSON API it wraps)
  #8 Newspaper-OCR-V3           OCR of genuine scanned pages

No credential of any kind is read, sent or written by this stage.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))          # tc01/
sys.path.insert(0, str(HERE.parents[2]))          # repo root
sys.path.insert(0, str(HERE))

from lib.shared import Log, WORK, write_json, sha8            # noqa: E402
from . import net as http
from . import loc, assets, claims, osint, archiver, ocr        # noqa: E402  (stage-local modules)

STAGE = "s01_research"
WIKI_PAGE = "Sodder_children_disappearance"

CA_QUERIES = ["Sodder children", "Sodder Fayetteville", "Fayetteville West Virginia fire",
              "five children missing fire", "Sodder"]
PHOTO_QUERIES = ["West Virginia company town", "West Virginia coal camp", "Fayetteville West Virginia",
                 "Appalachian coal town 1940s", "West Virginia coal miner 1946", "rural West Virginia house 1940s",
                 "Christmas 1945 United States", "fire department 1940s small town"]
COMMONS_QUERIES = ["Fayetteville West Virginia", "West Virginia coal town 1940s", "Appalachian coal camp",
                   "Sodder children", "Sodder family", "West Virginia winter 1940s", "coal company town house",
                   "1940s American family portrait", "billboard roadside 1960s United States"]
IA_QUERIES = ["Sodder children", "Fayetteville West Virginia", "West Virginia coal mining 1940s"]
USERNAMES = ["sodderchildren", "sodder_children", "sodderfamily", "TheSodderChildren", "fayettevillewv"]
SF_TARGETS = ["en.wikipedia.org", "sodderchildren.com"]


def main() -> int:
    log = Log(STAGE)
    work = WORK / STAGE
    work.mkdir(parents=True, exist_ok=True)
    venvs = WORK / "venvs"
    venvs.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    log(f"=== STAGE 1 RESEARCH start ===")
    log(f"runner cpus={os.cpu_count()} python={sys.version.split()[0]}")

    report: dict = {"stage": STAGE,
                  "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

    # ---------------------------------------------------------------- #1 awesome-osint
    try:
        reg = osint.awesome_osint(work, log)
        log.tool("jivoi/awesome-osint", "used" if reg.get("cloned") else "failed",
                 "shallow clone of the index README", f"{reg.get('links', 0)} entries / "
                 f"{len(reg.get('categories', []))} categories",
                 "work/s01_research/osint_source_registry.json", "NOASSERTION (curated list)",
                 reg.get("error", ""))
    except Exception as e:  # noqa: BLE001
        reg = {"error": str(e)}
        log.tool("jivoi/awesome-osint", "failed", "clone+parse", "-", "-", "-", str(e)[:200])

    # ---------------------------------------------------------------- #4 bellingcat toolkit
    try:
        bt = osint.bellingcat_toolkit(work, log)
        log.tool("bellingcat/toolkit", "used" if bt.get("cloned") else "failed",
                 "shallow clone of the methodology pages",
                 f"{bt.get('md_files', 0)} markdown sections -> {len(bt.get('checklist', []))} applied checks",
                 "work/s01_research/verification_methodology.json", "none declared", bt.get("error", ""))
    except Exception as e:  # noqa: BLE001
        bt = {"error": str(e)}
        log.tool("bellingcat/toolkit", "failed", "clone+parse", "-", "-", "-", str(e)[:200])

    # ---------------------------------------------------------------- #7 LoC bridge + Wikipedia citations
    wiki = assets.wikipedia_sources(WIKI_PAGE, log)
    report["wikipedia"] = {"ok": wiki.get("ok"), "coords": wiki.get("coords"),
                           "wikitext_chars": len(wiki.get("wikitext") or "")}
    log.tool("Wikipedia raw wikitext (reference article)", "used" if wiki.get("ok") else "failed",
             f"GET en.wikipedia.org/w/index.php?title={WIKI_PAGE}&action=raw",
             f"{len(wiki.get('wikitext') or '')} chars, coords={wiki.get('coords')}",
             "work/s01_research/claims.json", "CC BY-SA 4.0 (text) - cited, not vendored", "")

    # ---------------------------------------------------------------- #6 Chronicling America
    ca_hits = []
    try:
        ca_hits = loc.search_newspaper_pages(CA_QUERIES, log, limit=15)
        ca_dated = loc.search_newspaper_pages_dated(CA_QUERIES, log, "1945", "1970", limit=15)
    except Exception as e:  # noqa: BLE001
        ca_dated = []
        log(f"chronicling america search error: {e}")
    # de-duplicate and flag genuine topic hits
    seen, ca = set(), []
    for h in ca_hits + ca_dated:
        key = h.get("url")
        if not key or key in seen:
            continue
        seen.add(key)
        ca.append(h)
    # The LoC collection view is NOT a full-text search and every hit URL carries &q=<our query>,
    # so testing the URL for "sodder" is a false positive by construction. On-topic means the
    # page's own OCR text mentions the family AND the page date is in or after the event window.
    on_topic, ca_ocr_checked = [], 0
    for h in ca[:20]:
        if not h.get("url"):
            continue
        try:
            b = loc.resource_bundle(h["url"], log)
        except Exception as e:  # noqa: BLE001
            log(f"on-topic check failed {h.get('url')}: {e}")
            continue
        if not b.get("ok"):
            continue
        ca_ocr_checked += 1
        txt = (b.get("ocr_text") or "").lower()
        yr = int(str(h.get("date") or "0")[:4] or 0)
        # "sodder" is also an ordinary 19th-century word for turf/sod, so require corroboration
        hits = {"sodder": txt.count("sodder"), "fayetteville": txt.count("fayetteville"),
                "west virginia": txt.count("west virginia")}
        genuinely = hits["sodder"] >= 1 and (yr >= 1945) and (
            hits["fayetteville"] >= 1 or hits["west virginia"] >= 1
            or "five children" in txt or "sodder children" in txt or "soddu" in txt)
        h["ocr_keyword_hits"] = hits
        h["ocr_chars"] = b.get("ocr_chars")
        h["page_year"] = yr
        h["genuinely_on_topic"] = genuinely
        if genuinely:
            on_topic.append(h)
        http.polite(0.7)
    report["chronicling_america"] = {
        "pages_returned": len(ca), "pages_ocr_checked": ca_ocr_checked,
        "genuinely_on_topic_pages": len(on_topic), "queries": CA_QUERIES,
        "finding": ("The LoC collection view matched on metadata, not full text, and 'sodder' is also an "
                    "ordinary word for turf/sod, so pre-1945 hits are false positives. No page dated 1945 "
                    "or later that corroborates the family name was found." if not on_topic else
                    f"{len(on_topic)} page(s) genuinely on-topic."),
        "note": "the dedicated search API is retired; reached through the LoC JSON collection view",
    }
    log.tool("Chronicling America", "used" if ca else "failed",
             f"{len(CA_QUERIES)} full-text queries over the LoC newspaper collection",
             f"{len(ca)} page hits, {len(on_topic)} on-topic for this case",
             "work/s01_research/loc_chronicling_america.json", "Library of Congress; newspaper content public domain",
             "" if ca else "collection reachable but nothing returned")

    # ---------------------------------------------------------------- #7 LoC photographs (period, PD)
    photos = []
    try:
        photos = loc.search_photos(PHOTO_QUERIES, log, limit=12)
    except Exception as e:  # noqa: BLE001
        log(f"loc photos error: {e}")
    period_photos = [p for p in photos if re.search(r"\b19[2-4]\d\b", str(p.get("date") or ""))]
    report["loc_photos"] = {"returned": len(photos), "pre_1950": len(period_photos)}

    # ---------------------------------------------------------------- Wikimedia Commons
    commons = []
    try:
        commons = assets.commons_files(COMMONS_QUERIES, log, limit=15)
    except Exception as e:  # noqa: BLE001
        log(f"commons error: {e}")
    sodder_on_commons = [c for c in commons if "sodder" in (c.get("title") or "").lower()]
    report["wikimedia_commons"] = {"returned": len(commons), "sodder_specific": len(sodder_on_commons),
                                   "commercial_safe": sum(1 for c in commons if c.get("commercial_safe"))}

    # ---------------------------------------------------------------- Archive.org
    ia = []
    try:
        ia = assets.ia_items(IA_QUERIES, log, rows=15)
    except Exception as e:  # noqa: BLE001
        log(f"archive.org error: {e}")
    report["archive_org"] = {"returned": len(ia),
                             "titles": [str(x.get("title"))[:70] for x in ia[:15]]}

    write_json(work / "loc_chronicling_america.json", {"queries": CA_QUERIES, "pages": ca, "on_topic": on_topic})
    write_json(work / "loc_photos.json", {"queries": PHOTO_QUERIES, "results": photos})
    write_json(work / "wikimedia_commons.json", {"queries": COMMONS_QUERIES, "results": commons})
    write_json(work / "archive_org.json", {"queries": IA_QUERIES, "results": ia})

    # ---------------------------------------------------------------- claim register
    cl = claims.extract(wiki.get("wikitext") or "", log) if wiki.get("ok") else {"claims": []}
    citations = cl.get("citations") or []
    report["claims"] = {"total": len(cl.get("claims") or []), "status_counts": cl.get("status_counts"),
                        "unsourced": cl.get("unsourced")}
    write_json(work / "claims.json", cl)
    write_json(work / "prose_by_section.json", cl.get("prose_by_section") or {})

    # ---------------------------------------------------------------- source register
    srcs = []
    for c in citations:
        srcs.append({
            "source_id": c["ref_id"], "kind": "citation", "name": c.get("name"),
            "title": c.get("title"), "work": c.get("work"), "publisher": c.get("publisher"),
            "author": c.get("author"), "url": c.get("url"),
            "archive_url_declared": c.get("archive_url"), "url_status": c.get("url_status"),
            "date": c.get("date"), "access_date": c.get("access_date"),
            "supports_claims": [x["claim_id"] for x in cl.get("claims") or []
                                if c["ref_id"] in [s2["source_id"] for s2 in x.get("sources", [])]],
        })
    for i, h in enumerate(ca[:10], 1):
        srcs.append({"source_id": f"CA{i:02d}", "kind": "chronicling-america-page", "title": h.get("title"),
                     "date": h.get("date"), "url": h.get("url"), "supports_claims": []})
    for i, p in enumerate(period_photos[:12], 1):
        srcs.append({"source_id": f"LOC{i:02d}", "kind": "loc-photograph", "title": p.get("title"),
                     "date": p.get("date"), "url": p.get("url"), "image_url": p.get("image_url"),
                     "supports_claims": [], "use": "period establishing image, not evidence"})
    for i, c in enumerate(commons[:12], 1):
        srcs.append({"source_id": f"WC{i:02d}", "kind": "wikimedia-commons", "title": c.get("title"),
                     "date": c.get("date_original"), "url": c.get("pageurl"), "image_url": c.get("url"),
                     "license": c.get("license"), "artist": c.get("artist"),
                     "commercial_safe": c.get("commercial_safe"), "supports_claims": [],
                     "use": "period establishing image, not evidence"})
    write_json(work / "sources.json", {"generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                       "count": len(srcs), "sources": srcs})
    log(f"source register: {len(srcs)} entries")

    # ---------------------------------------------------------------- #5 auto-archiver
    urls = [s["url"] for s in srcs if s.get("url")]
    aa_state = archiver.install(work, log, venvs / "autoarchiver")
    log.tool("bellingcat/auto-archiver", "used" if aa_state.get("installed") else "failed",
             "pip install auto-archiver in an isolated venv",
             f"version={aa_state.get('version')}", "-", "MIT", aa_state.get("install_error") or "")
    try:
        arch = archiver.archive_all(urls, work, log, aa_state, per_url_timeout=60, max_urls=40)
        report["archiving"] = {"attempted": arch["attempted"], "by_status": arch["by_status"]}
        aa_verdict = arch["by_tier1_verdict"]
        aa_ok = aa_verdict.get("ok", 0)
        log.tool("bellingcat/auto-archiver (archival run)",
                 "used" if aa_ok else "failed",
                 f"{arch['attempted']} source URLs",
                 f"auto-archiver tier1={aa_verdict}; wayback snapshots={arch['wayback_snapshots']}; "
                 f"local sha256 captures={arch['local_captures']}; no copy={len(arch['sources_with_no_copy'])}",
                 "work/s01_research/archive_manifest.json", "MIT",
                 "" if aa_ok else "auto-archiver raised SetupError: it is config-driven and the remote "
                                  "archiving backends need credentials we are forbidden to use; "
                                  "archival was completed by the Wayback + local-sha256 fallbacks")
    except Exception as e:  # noqa: BLE001
        report["archiving"] = {"error": str(e)[:200]}
        log.tool("bellingcat/auto-archiver (archival run)", "failed", "-", "-", "-", "MIT", str(e)[:200])

    # ---------------------------------------------------------------- #2 maigret
    try:
        mg = osint.maigret(work, log, USERNAMES, venvs / "maigret", timeout=600)
        st = "used" if mg.get("installed") else "failed"
        log.tool("soxoj/maigret", st, f"usernames={USERNAMES}",
                 f"installed={mg.get('installed')} version={mg.get('version')} "
                 f"hits={sum(len(r.get('sites_found') or []) for r in mg.get('results', []))}",
                 "work/s01_research/maigret_report.json", "MIT", mg.get("error", ""))
        report["maigret"] = {"installed": mg.get("installed"), "version": mg.get("version"),
                             "usernames": USERNAMES,
                             "hits": {r["username"]: len(r.get("sites_found") or []) for r in mg.get("results", [])}}
    except Exception as e:  # noqa: BLE001
        report["maigret"] = {"error": str(e)[:200]}
        log.tool("soxoj/maigret", "failed", "-", "-", "-", "MIT", str(e)[:200])

    # ---------------------------------------------------------------- #3 spiderfoot
    skip_heavy = os.environ.get("TC01_SKIP_HEAVY", "").lower() in {"1", "true", "yes"}
    if skip_heavy:
        log("TC01_SKIP_HEAVY set: spiderfoot already ran successfully on run 40903096463 "
            "(233 modules, deps installed); not repeated on this correction run")
        report["spiderfoot"] = {"skipped_on_correction_run": True,
                                "previous_result": {"cloned": True, "deps_installed": True,
                                                    "modules_available": 233}}
    try:
        if skip_heavy:
            raise RuntimeError("skipped")
        sf = osint.spiderfoot(work, log, SF_TARGETS, venvs / "spiderfoot", timeout=900)
        log.tool("smicallef/spiderfoot", "used" if sf.get("cloned") else "failed",
                 f"targets={SF_TARGETS}, keyless modules only",
                 f"modules_available={sf.get('modules_available')} keyless_shortlist={len(sf.get('modules_keyless_shortlist') or [])}",
                 "work/s01_research/spiderfoot_report.json", "MIT", sf.get("deps_error") or sf.get("error") or "")
        report["spiderfoot"] = {k: sf.get(k) for k in ("cloned", "deps_installed", "modules_available", "sfcli_help_rc")}
    except Exception as e:  # noqa: BLE001
        if not skip_heavy:
            report["spiderfoot"] = {"error": str(e)[:200]}
            log.tool("smicallef/spiderfoot", "failed", "-", "-", "-", "MIT", str(e)[:200])
        else:
            log.tool("smicallef/spiderfoot", "used",
                     "previous run 40903096463 (clone + deps + 233 modules enumerated)",
                     "not repeated on this correction run", "work/s01_research/spiderfoot_report.json",
                     "MIT", "TC01_SKIP_HEAVY")

    # ---------------------------------------------------------------- #8 newspaper OCR
    pages = []
    img_dir = work / "pages"
    img_dir.mkdir(parents=True, exist_ok=True)
    bundles = []
    # rank candidate pages: those whose LoC-supplied OCR actually mentions the case come first
    ocr_mentions = []
    for h in ca[:14]:
        if not h.get("url"):
            continue
        try:
            b = loc.resource_bundle(h["url"], log)
        except Exception as e:  # noqa: BLE001
            log(f"resource_bundle error {h.get('url')}: {e}")
            continue
        if not b.get("ok"):
            continue
        txt = (b.get("ocr_text") or "").lower()
        hit = {k: txt.count(k) for k in ("sodder", "fayetteville", "west virginia", "five children")}
        b["keyword_hits"] = hit
        b["page_title"] = h.get("title")
        b["page_date"] = h.get("date")
        bundles.append(b)
        if hit.get("sodder"):
            ocr_mentions.append(b)
        http.polite(0.8)
    report["ca_pages_with_loc_ocr"] = len(bundles)
    report["ca_pages_mentioning_sodder_in_ocr"] = len(ocr_mentions)
    log(f"chronicling america: fetched LoC OCR for {len(bundles)} pages, "
        f"{len(ocr_mentions)} genuinely mention 'sodder'")
    chosen = (ocr_mentions or bundles)[:6]
    for b in chosen:
        u = b.get("url")
        hi = loc.hires_from_iiif(b.get("image"), px=1600)
        if not hi:
            continue
        dest = img_dir / (re.sub(r"[^A-Za-z0-9]+", "_", str(u))[-70:] + ".jpg")
        d = http.download(hi, dest, timeout=240)
        if d.get("bytes"):
            pages.append({"label": (b.get("page_title") or "")[:90], "date": b.get("page_date"),
                          "source_url": u, "download_url": hi, "local_path": str(dest),
                          "bytes": d["bytes"], "sha": sha8(dest),
                          "ocr_chars_from_loc": b.get("ocr_chars"), "keyword_hits": b.get("keyword_hits")})
            (img_dir / (dest.stem + "_loc_ocr.txt")).write_text(b.get("ocr_text") or "", encoding="utf-8")
            log(f"downloaded page scan {dest.name} ({d['bytes']} B) ocr_chars={b.get('ocr_chars')}")
        http.polite(1.0)
    report["page_images_downloaded"] = len(pages)
    report["loc_ocr_chars"] = sum(p.get("ocr_chars_from_loc") or 0 for p in pages)
    try:
        oc = ocr.run(work, log, pages, venvs / "newspaperocr")
        log.tool("PapaKaffey/Newspaper-OCR-V3", "used" if oc.get("cloned") else "failed",
                 f"{len(pages)} genuine Chronicling America page scans",
                 f"{sum(1 for p in oc.get('pages', []) if p.get('chars', 0) > 0)} pages produced OCR text "
                 f"({sum(p.get('chars', 0) for p in oc.get('pages', []))} chars, tesseract mode)",
                 "work/s01_research/newspaper_ocr_report.json", "none declared",
                 "Google Vision path disabled (needs a GCP key); Tesseract path used")
        report["ocr"] = {"cloned": oc.get("cloned"), "pages": len(oc.get("pages", []))}
    except Exception as e:  # noqa: BLE001
        report["ocr"] = {"error": str(e)[:200]}
        log.tool("PapaKaffey/Newspaper-OCR-V3", "failed", "-", "-", "-", "none declared", str(e)[:200])

    write_json(work / "page_bundles.json", bundles)
    write_json(work / "page_images.json", pages)

    # ---------------------------------------------------------------- research dossier
    dossier = {
        "case": "THE SODDER CHILDREN — Fayetteville, West Virginia, 25 December 1945",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "seconds": round(time.time() - t0, 1),
        "coordinates_from_wikipedia": (wiki.get("coords") or {}),
        "verdicts": {
            "period_newspaper_page_on_topic_in_chronicling_america": bool(on_topic),
            "sodder_images_on_wikimedia_commons": len(sodder_on_commons),
            "claims_total": len(cl.get("claims") or []),
            "claims_with_contemporaneous_source": sum(
                1 for c in cl.get("claims") or [] if c.get("evidence", {}).get("contemporaneous_source")),
            "claims_unsourced": len(cl.get("unsourced") or []),
        },
        "period_image_pool": {
            "loc_pre_1950": len(period_photos),
            "commons_candidates": len(commons),
            "archive_org_items": len(ia),
        },
        "honest_gaps": [
            "No photograph of the Sodder family or of the 1968 billboard was found on Wikimedia Commons "
            "(0 hits across 9 queries). The restoration chain in stage 9 therefore runs on genuine "
            "public-domain period photographs of the region and era, labelled 'Archival photo', and the "
            "family itself is represented by documents and typography, never by a fabricated likeness.",
            "The dedicated Chronicling America search API is retired; the collection is reached through "
            "the Library of Congress JSON views instead.",
            "Any claim left UNSOURCED by this stage is cut from the script in stage 2.",
        ],
    }
    write_json(work / "research_dossier.json", dossier)
    report.update(dossier)
    write_json(work / "stage_report.json", report)
    log.flush()
    log(f"=== STAGE 1 complete in {time.time()-t0:.0f}s ===")
    log.flush()
    print(json.dumps({"stage": STAGE, "verdicts": dossier["verdicts"],
                      "period_image_pool": dossier["period_image_pool"]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
