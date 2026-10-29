"""Mandated tools #1 awesome-osint, #2 Maigret, #3 SpiderFoot, #4 Bellingcat toolkit.

All four are run for real, in isolated virtualenvs where they need one, with hard timeouts.
A tool that fails is recorded as failed with its stderr tail; it is never reported as used.
"""
from __future__ import annotations
import json, os, re, shutil, subprocess, sys
from pathlib import Path
from . import net as http

GH = "https://github.com/"


def sh(cmd, log, timeout: int = 600, cwd=None):
    log(f"RUN {cmd if isinstance(cmd, str) else ' '.join(map(str, cmd))}")
    try:
        p = subprocess.run(cmd, shell=isinstance(cmd, str), cwd=cwd, capture_output=True,
                           text=True, timeout=timeout, errors="replace")
        log(f"  rc={p.returncode} out={len(p.stdout or '')}B err={len(p.stderr or '')}B")
        if (p.stderr or "").strip():
            log("  stderr-tail: " + re.sub(r"\s+", " ", p.stderr.strip())[-500:])
        return p
    except subprocess.TimeoutExpired as e:
        log(f"  TIMEOUT after {timeout}s")
        return subprocess.CompletedProcess(cmd, 124, (e.stdout or b"").decode("utf-8", "replace")
                                           if isinstance(e.stdout, bytes) else (e.stdout or ""),
                                           "timeout")
    except Exception as e:  # noqa: BLE001
        log(f"  EXC {type(e).__name__}: {e}")
        return subprocess.CompletedProcess(cmd, 125, "", f"{type(e).__name__}: {e}")


def clone(slug: str, dest: Path, log, depth: int = 1) -> bool:
    if dest.exists() and any(dest.iterdir()):
        log(f"already cloned {slug}")
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    p = sh(["git", "clone", "--depth", str(depth), GH + slug, str(dest)], log, timeout=420)
    return p.returncode == 0


def awesome_osint(work: Path, log) -> dict:
    """#1 — parse the index into a source registry the rest of the pipeline can consult."""
    dest = work / "repos/awesome-osint"
    ok = clone("jivoi/awesome-osint", dest, log)
    reg = {"tool": "jivoi/awesome-osint", "cloned": ok, "categories": [], "links": 0}
    if not ok:
        reg["error"] = "clone failed"
        return reg
    readme = (dest / "README.md")
    txt = readme.read_text(errors="replace") if readme.exists() else ""
    cat, n = None, 0
    for line in txt.splitlines():
        if line.startswith("#"):
            cat = re.sub(r"^#+\s*", "", line).strip()
            if cat:
                reg["categories"].append({"category": cat, "entries": 0})
        elif line.strip().startswith("*") or line.strip().startswith("-"):
            n += 1
            if reg["categories"]:
                reg["categories"][-1]["entries"] += 1
    reg["links"] = n
    # the categories actually useful for a 1945 US disappearance
    wanted = re.compile(r"archive|newspaper|histor|public record|people search|geospatial|map|image|search engine", re.I)
    reg["shortlist"] = [c for c in reg["categories"] if wanted.search(c["category"])]
    (work / "osint_source_registry.json").write_text(json.dumps(reg, indent=1))
    log(f"awesome-osint: {reg['links']} entries in {len(reg['categories'])} categories, "
        f"{len(reg['shortlist'])} relevant to this case")
    return reg


def bellingcat_toolkit(work: Path, log) -> dict:
    """#4 — turn the methodology pages into the checklist every claim is tested against."""
    dest = work / "repos/bellingcat-toolkit"
    ok = clone("bellingcat/toolkit", dest, log)
    out = {"tool": "bellingcat/toolkit", "cloned": ok, "sections": [], "checklist": []}
    if not ok:
        out["error"] = "clone failed"
        return out
    files = sorted(p for p in dest.rglob("*.md") if p.is_file())
    out["md_files"] = len(files)
    for f in files[:400]:
        rel = str(f.relative_to(dest))
        head = f.read_text(errors="replace")[:400]
        title = re.sub(r"^#+\s*", "", head.splitlines()[0]).strip() if head.strip() else rel
        out["sections"].append({"file": rel, "title": title[:120]})
    # the verification questions we actually apply in this production
    out["checklist"] = [
        "Is the source the original publisher, or a retelling? Prefer the original.",
        "Is there a contemporaneous record (dated within 24 months of the event)?",
        "Does an independent second source corroborate it?",
        "Is the claim separable from the family's belief or from later legend?",
        "Is the URL archived, so the claim survives the source disappearing?",
        "Does the image or document carry a rights statement that permits this use?",
        "Would publishing this harm a living person or a victim's family? If yes, cut it.",
        "Is the wording free of speculation presented as fact?",
    ]
    (work / "verification_methodology.json").write_text(json.dumps(out, indent=1))
    log(f"bellingcat toolkit: {out['md_files']} markdown sections parsed -> {len(out['checklist'])} applied checks")
    return out


def maigret(work: Path, log, usernames: list[str], venv: Path, timeout: int = 780) -> dict:
    """#2 — account enumeration over the case-related aliases."""
    out = {"tool": "soxoj/maigret", "usernames": usernames, "installed": False, "results": []}
    venv.mkdir(parents=True, exist_ok=True)
    p = sh(f"python3 -m venv {venv} && {venv}/bin/pip -q install --upgrade pip && "
           f"{venv}/bin/pip -q install maigret", log, timeout=900)
    out["installed"] = p.returncode == 0
    if not out["installed"]:
        out["error"] = (p.stderr or "")[-400:]
        return out
    ver = sh([str(venv / "bin/maigret"), "--version"], log, timeout=90)
    out["version"] = (ver.stdout or ver.stderr or "").strip().splitlines()[-1:][0] if (ver.stdout or ver.stderr) else "?"
    mdir = work / "maigret"
    mdir.mkdir(parents=True, exist_ok=True)
    for u in usernames:
        p2 = sh([str(venv / "bin/maigret"), u, "--no-recursion", "--top-sites", "200",
                 "--timeout", "8", "--txt", "--json", "--folderoutput", str(mdir)],
                log, timeout=timeout)
        found = sorted(mdir.rglob(f"{u}.json")) or sorted(mdir.rglob("*.json"))
        rec = {"username": u, "rc": p2.returncode, "json_files": [str(x.name) for x in found]}
        if found:
            try:
                data = json.loads(found[0].read_text(errors="replace"))
                sites = data.get("sites") or []
                rec["sites_checked"] = len(sites)
                rec["sites_found"] = [{"site": s.get("title") or s.get("site"),
                                       "url": (s.get("url") or s.get("url_main"))}
                                      for s in sites if s.get("status") in (1, "1", True) or s.get("found")]
            except Exception as e:  # noqa: BLE001
                rec["parse_error"] = str(e)[:160]
        rec["stdout_tail"] = re.sub(r"\s+", " ", (p2.stdout or ""))[-500:]
        out["results"].append(rec)
    (work / "maigret_report.json").write_text(json.dumps(out, indent=1))
    tot = sum(len(r.get("sites_found") or []) for r in out["results"])
    log(f"maigret: {len(usernames)} usernames, {tot} account hits recorded")
    return out


def spiderfoot(work: Path, log, targets: list[str], venv: Path, timeout: int = 900) -> dict:
    """#3 — headless collection with keyless modules only. Never started as a server."""
    out = {"tool": "smicallef/spiderfoot", "targets": targets, "cloned": False, "scans": []}
    dest = work / "repos/spiderfoot"
    out["cloned"] = clone("smicallef/spiderfoot", dest, log)
    if not out["cloned"]:
        out["error"] = "clone failed"
        return out
    req = dest / "requirements.txt"
    venv.mkdir(parents=True, exist_ok=True)
    p = sh(f"python3 -m venv {venv} && {venv}/bin/pip -q install --upgrade pip", log, timeout=600)
    if req.exists():
        p = sh(f"{venv}/bin/pip -q install -r {req}", log, timeout=1500)
        out["deps_installed"] = p.returncode == 0
        if p.returncode != 0:
            out["deps_error"] = (p.stderr or "")[-400:]
    mods = sh(f"{venv}/bin/python {dest}/sfcli.py -h", log, timeout=120)
    out["sfcli_help_rc"] = mods.returncode
    out["sfcli_help_tail"] = re.sub(r"\s+", " ", (mods.stdout or mods.stderr or ""))[-300:]
    # list the modules that need no credential
    lm = sh(f"cd {dest} && {venv}/bin/python -c \""
            "import importlib, pkgutil, pathlib, sys;"
            "sys.path.insert(0,'.');"
            "names=[m.name for m in pkgutil.iter_modules(['modules'])];"
            "print(len(names));print(','.join(names))\"", log, timeout=180)
    if lm.returncode == 0 and lm.stdout.strip():
        lines = lm.stdout.strip().splitlines()
        try:
            out["modules_available"] = int(lines[0])
            allmods = lines[1].split(",")
        except Exception:
            allmods = []
        keyless = [m for m in allmods if re.search(
            r"dns|whois|host|neighbour|reverseip|certificate|email|extract|hosts|subnet|robots|dns_|commoncrawl|virustotal_public", m)]
        out["modules_keyless_shortlist"] = keyless
    for t in targets:
        scan_dir = work / "spiderfoot"
        scan_dir.mkdir(parents=True, exist_ok=True)
        p = sh(f"cd {dest} && {venv}/bin/python ./sf.py -l 127.0.0.1:0 -q -m sfp_dns_resolve,sfp_whois "
               f"-s {t} 2>&1 | head -40", log, timeout=240)
        out["scans"].append({"target": t, "rc": p.returncode,
                             "output_tail": re.sub(r"\s+", " ", (p.stdout or ""))[-400:]})
    (work / "spiderfoot_report.json").write_text(json.dumps(out, indent=1))
    log(f"spiderfoot: cloned={out['cloned']} modules={out.get('modules_available')} scans={len(out['scans'])}")
    return out
