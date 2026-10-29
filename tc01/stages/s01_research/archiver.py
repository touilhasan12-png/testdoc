"""Mandated tool #5 — Auto-Archiver.

Every source URL that a claim depends on is archived before it is used. Three tiers, tried in
order and each recorded honestly:
  1. bellingcat/auto-archiver, installed in its own venv and run for real;
  2. Wayback Machine availability (keyless) -> cite the existing snapshot;
  3. local capture: the bytes we fetched, sha256, status and content-type, stored under work/.
"""
from __future__ import annotations
import hashlib, json, re, subprocess, time
from pathlib import Path
from . import net as http, assets


def sh(cmd, log, timeout=600):
    log(f"RUN {cmd if isinstance(cmd,str) else ' '.join(map(str,cmd))}")
    try:
        p = subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True, text=True,
                           timeout=timeout, errors="replace")
        log(f"  rc={p.returncode}")
        if (p.stderr or '').strip():
            log("  stderr-tail: " + re.sub(r"\s+", " ", p.stderr.strip())[-400:])
        return p
    except subprocess.TimeoutExpired:
        log(f"  TIMEOUT after {timeout}s")
        return subprocess.CompletedProcess(cmd, 124, "", "timeout")
    except Exception as e:  # noqa: BLE001
        log(f"  EXC {type(e).__name__}: {e}")
        return subprocess.CompletedProcess(cmd, 125, "", str(e))


def install(work: Path, log, venv: Path) -> dict:
    venv.mkdir(parents=True, exist_ok=True)
    p = sh(f"python3 -m venv {venv} && {venv}/bin/pip -q install --upgrade pip", log, timeout=600)
    p2 = sh(f"{venv}/bin/pip -q install auto-archiver", log, timeout=1500)
    ok = p2.returncode == 0
    ver = sh(f"{venv}/bin/auto-archiver --version", log, timeout=120) if ok else None
    return {"tool": "bellingcat/auto-archiver", "installed": ok,
            "install_error": None if ok else (p2.stderr or "")[-400:],
            "version": ((ver.stdout or ver.stderr).strip().splitlines() or ["?"])[-1] if ver else None}


def archive_all(urls: list[str], work: Path, log, aa_state: dict,
                per_url_timeout: int = 90, max_urls: int = 60) -> dict:
    cap_dir = work / "captures"
    cap_dir.mkdir(parents=True, exist_ok=True)
    jsonl = cap_dir / "local_captures.jsonl"
    records = []
    todo = [u for u in dict.fromkeys(urls) if u][:max_urls]
    log(f"archiving {len(todo)} unique source URLs")

    for i, u in enumerate(todo, 1):
        rec = {"url": u, "tier1_auto_archiver": None, "tier2_wayback": None,
               "tier3_local": None, "status": "pending"}
        # tier 1 — real auto-archiver invocation (only if it installed cleanly)
        if aa_state.get("installed"):
            aa_bin = str(Path(work).parent / "venvs" / "autoarchiver" / "bin" / "auto-archiver")
            p = sh(f"cd {work} && {aa_bin} --feed '{u}' 2>&1 | head -25", log,
                   timeout=per_url_timeout * 2)
            rec["tier1_auto_archiver"] = {"rc": p.returncode,
                                          "output_tail": re.sub(r"\s+", " ", (p.stdout or ""))[-300:]}
            if p.returncode == 0 and "archive" in (p.stdout or "").lower():
                rec["status"] = "archived:auto-archiver"
        # tier 2 — wayback
        wb = assets.wayback(u, log)
        rec["tier2_wayback"] = wb
        if wb.get("available"):
            rec["archived_url"] = wb["url"]
            if rec["status"] == "pending":
                rec["status"] = "archived:wayback-existing"
        # tier 3 — local capture
        st, body, err = http.fetch(u, timeout=per_url_timeout)
        loc = None
        if body is not None:
            safe = re.sub(r"[^A-Za-z0-9._-]+", "_", u)[:90]
            ext = ".html" if "<html" in body[:4000].lower() else (".json" if body[:1] in "{[" else ".txt")
            dest = cap_dir / f"cap{i:03d}_{safe}{ext}"
            dest.write_text(body, encoding="utf-8")
            loc = {"path": str(dest), "bytes": len(body.encode("utf-8", "replace")),
                   "sha256": hashlib.sha256(body.encode("utf-8", "replace")).hexdigest(),
                   "status": st}
            rec["archived_url"] = rec.get("archived_url") or f"file://{dest}"
            if rec["status"] == "pending":
                rec["status"] = "archived:local-capture"
        rec["tier3_local"] = loc or {"error": err}
        if rec["status"] == "pending":
            rec["status"] = "FAILED"
        records.append(rec)
        with jsonl.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), **rec}) + "\n")
        http.polite(1.0)

    from collections import Counter
    summary = Counter(r["status"] for r in records)
    out = {"auto_archiver": aa_state, "attempted": len(records), "by_status": dict(summary),
           "records": records, "local_capture_log": str(jsonl)}
    (work / "archive_manifest.json").write_text(json.dumps(out, indent=1))
    log(f"archiving done: {dict(summary)}")
    return out
