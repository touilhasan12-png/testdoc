"""Mandated tool #5 — bellingcat/auto-archiver, plus the archival fallbacks.

Auto-Archiver is config-driven. Invoked with only --feed it raises
`auto_archiver.core.consts.SetupError` inside check_steps and the shell pipeline still exits 0,
which is exactly how a failed tool can be mis-reported as a success. This module therefore
classifies on the tool's own output text, never on the return code, and reports three separate
tiers so nothing is conflated:

  tier1_auto_archiver  the tool itself: ok | setup_error | other_error | not_installed
  tier2_wayback        an existing Internet Archive snapshot (keyless)
  tier3_local          the bytes we fetched, with sha256 (our own capture, not the tool's)
"""
from __future__ import annotations
import hashlib, json, re, subprocess, time
from pathlib import Path
from . import net as http, assets

_probe_budget = [3]          # bare-invocation probes, so we do not pay the timeout 40 times

ERROR_MARKERS = ("SetupError", "ExitError", "Traceback", "MissingConfig", "No such option",
                 "usage:", "error:", "ConfigurationError")
SUCCESS_MARKERS = ("archived successfully", "success=True", "Saved to", "archive_url",
                   "https://web.archive.org/web/", "https://archive.ph/")


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


def classify(text: str) -> str:
    t = text or ""
    if any(m in t for m in ("SetupError", "MissingConfig", "ConfigurationError")):
        return "setup_error"
    if "No such option" in t or "usage:" in t and "error" in t.lower():
        return "cli_error"
    if any(m in t for m in ("Traceback", "error:")):
        return "other_error"
    if any(m in t for m in SUCCESS_MARKERS):
        return "ok"
    return "inconclusive"


def install(work: Path, log, venv: Path) -> dict:
    venv.mkdir(parents=True, exist_ok=True)
    sh(f"python3 -m venv {venv} && {venv}/bin/pip -q install --upgrade pip", log, timeout=600)
    p2 = sh(f"{venv}/bin/pip -q install auto-archiver", log, timeout=1500)
    ok = p2.returncode == 0
    binp = venv / "bin/auto-archiver"
    state = {"tool": "bellingcat/auto-archiver", "installed": ok, "binary": str(binp),
             "binary_exists": binp.exists(),
             "install_error": None if ok else (p2.stderr or "")[-400:]}
    if ok:
        v = sh(f"{binp} --version 2>&1 | head -3", log, timeout=120)
        m = re.search(r"(\d+\.\d+\.\d+)", (v.stdout or "") + (v.stderr or ""))
        state["version"] = m.group(1) if m else re.sub(r"\s+", " ", (v.stdout or ""))[:60]
        h = sh(f"{binp} --help 2>&1 | head -60", log, timeout=120)
        state["help"] = re.sub(r"\n{2,}", "\n", (h.stdout or "") + (h.stderr or ""))[:2500]
        state["help_flags"] = sorted(set(re.findall(r"(--[\w-]+)", state["help"])))
        state["has_example_config_cmd"] = any("example" in f or "config" in f for f in state["help_flags"])
    return state


def _try_auto_archiver(aa: dict, url: str, work: Path, log, timeout: int) -> dict:
    if not aa.get("installed") or not aa.get("binary_exists"):
        return {"verdict": "not_installed"}
    binp = aa["binary"]
    cfg = work / "autoarchiver.yaml"
    if not cfg.exists():
        # minimal config guessed from the project documentation; the tool's own error text
        # tells us what is missing and that text is preserved verbatim in the report.
        cfg.write_text(
            "database:\n  name: local_csv_db\n  config:\n    filename: work/s01_research/aa_report.csv\n"
            "steps:\n  - general_extractor\n  - wayback_machine_availability\n  - local_archive\n"
            "  - console_db\n", encoding="utf-8")
    attempts = []
    cmds = [f"cd {work} && {binp} --config {cfg} --feed '{url}' 2>&1 | tail -25"]
    if _probe_budget[0] > 0:
        _probe_budget[0] -= 1
        cmds.append(f"cd {work} && {binp} --feed '{url}' 2>&1 | tail -25")
    for cmd in cmds:
        p = sh(cmd, log, timeout=timeout)
        blob = ((p.stdout or "") + "\n" + (p.stderr or ""))[-1500:]
        verdict = classify(blob)
        attempts.append({"cmd_index": len(attempts), "rc": p.returncode, "verdict": verdict,
                         "output_tail": re.sub(r"\s+", " ", blob)[-700:]})
        if verdict == "ok":
            break
    best = "ok" if any(a["verdict"] == "ok" for a in attempts) else attempts[-1]["verdict"]
    return {"verdict": best, "attempts": attempts}


def archive_all(urls: list[str], work: Path, log, aa: dict,
                per_url_timeout: int = 120, max_urls: int = 40) -> dict:
    cap_dir = work / "captures"
    cap_dir.mkdir(parents=True, exist_ok=True)
    jsonl = cap_dir / "local_captures.jsonl"
    records = []
    todo = [u for u in dict.fromkeys(urls) if u][:max_urls]
    log(f"archiving {len(todo)} unique source URLs")

    for i, u in enumerate(todo, 1):
        rec = {"url": u, "status": "pending"}
        rec["tier1_auto_archiver"] = _try_auto_archiver(aa, u, work, log, per_url_timeout * 2)
        wb = assets.wayback(u, log)
        rec["tier2_wayback"] = wb
        if wb.get("available"):
            rec["archived_url"] = wb["url"]
            rec["status"] = "archived:wayback-snapshot"
        st, body, err = http.fetch(u, timeout=per_url_timeout)
        if body is not None:
            safe = re.sub(r"[^A-Za-z0-9._-]+", "_", u)[:88]
            ext = ".html" if "<html" in body[:4000].lower() else (".json" if body[:1] in "{[" else ".txt")
            dest = cap_dir / f"cap{i:03d}_{safe}{ext}"
            dest.write_text(body, encoding="utf-8")
            raw = body.encode("utf-8", "replace")
            rec["tier3_local"] = {"path": f"work/s01_research/captures/{dest.name}",
                                  "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                                  "http_status": st}
            rec.setdefault("archived_url", f"local:{dest.name}")
            if rec["status"] == "pending":
                rec["status"] = "captured:local-only"
        else:
            rec["tier3_local"] = {"error": err, "http_status": st}
        if rec["status"] == "pending":
            rec["status"] = "FAILED-no-copy"
        rec["tier1_verdict"] = rec["tier1_auto_archiver"]["verdict"]
        records.append(rec)
        with jsonl.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), **rec}) + "\n")
        http.polite(0.8)

    from collections import Counter
    out = {
        "auto_archiver": aa,
        "attempted": len(records),
        "by_status": dict(Counter(r["status"] for r in records)),
        "by_tier1_verdict": dict(Counter(r["tier1_verdict"] for r in records)),
        "wayback_snapshots": sum(1 for r in records if (r.get("tier2_wayback") or {}).get("available")),
        "local_captures": sum(1 for r in records if (r.get("tier3_local") or {}).get("bytes")),
        "sources_with_no_copy": [r["url"] for r in records if r["status"] == "FAILED-no-copy"],
        "records": records,
        "local_capture_log": str(jsonl),
    }
    (work / "archive_manifest.json").write_text(json.dumps(out, indent=1))
    log(f"archiving: status={out['by_status']} tier1={out['by_tier1_verdict']} "
        f"wayback={out['wayback_snapshots']} local={out['local_captures']}")
    return out
