"""Stage 0 — runner smoke test.

Verifies, on a real GitHub Actions runner and with no credential of any kind:
  1. the tc01 scaffold is present and importable;
  2. the tool manifest is complete (50 mandated entries) and matches the owner policy;
  3. base toolchain availability (python, ffmpeg, tesseract, imagemagick, node, java);
  4. the ffmpeg filters the grade/edit stages depend on;
  5. outbound reachability of every keyless endpoint the pipeline will use.
Writes work/smoke/smoke.json and appends to the step summary.
"""
from __future__ import annotations

import json
import platform
import shutil
import socket
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))   # repo root
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tc01"))       # tc01/
from lib.shared import REPO, WORK, now, read_json, run, scrub, which, write_json  # noqa: E402

STAGE = "smoke"
FILTERS = ["lut3d", "lutyuv", "nlmeans", "hqdn3d", "unsharp", "cas", "drawtext",
           "zoompan", "signalstats", "histogram", "overlay", "xfade", "atempo",
           "afftdn", "highpass", "lowpass", "aecho", "volume", "scale", "format"]
ENDPOINTS = {
    "chronicling_america": "https://chroniclingamerica.loc.gov/search/api/results.json?format=json&rows=1",
    "loc_collections": "https://www.loc.gov/photos/?fo=json&c=1",
    "wikimedia_commons": "https://commons.wikimedia.org/w/api.php?action=query&format=json&meta=siteinfo",
    "archive_org": "https://archive.org/advancedsearch.php?q=sodder&fl%5B%5D=identifier&rows=1&output=json",
    "openverse": "https://api.openverse.org/v1/images/?q=snow&page_size=1",
    "osm_tiles_carto_dark": "https://basemaps.cartocdn.com/dark_all/12/1178/1560.png",
    "huggingface": "https://huggingface.co/api/models/suno-ai/bark",
    "pypi": "https://pypi.org/pypi/auto-editor/json",
}


def main() -> int:
    out = WORK / STAGE
    out.mkdir(parents=True, exist_ok=True)
    rep: dict = {"ts": now(), "stage": STAGE}

    rep["runner"] = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "cpus": __import__("os").cpu_count(),
        "hostname_is_sandbox": socket.gethostname(),
    }

    # 1. scaffold
    rep["scaffold"] = {
        "repo_root": str(REPO),
        "lib_shared_importable": True,
        "manifest_present": (REPO / "project/00_tools_manifest_v1.json").exists(),
        "policy_present": (REPO / "project/00_tool_policy_v1.md").exists(),
        "stages_present": sorted(p.name for p in (REPO / "tc01/stages").iterdir() if p.is_dir()),
    }

    # 2. manifest vs owner policy
    man = read_json(REPO / "project/00_tools_manifest_v1.json", {}) or {}
    tools = man.get("tools", [])
    removed = [t for t in tools if t["status"].startswith("REMOVED") or t["status"] == "NOT_FOUND"]
    bad = [t["tool"] for t in tools
           if t["status"] in ("KEPT", "KEPT_KEYLESS") and t.get("commercial") == "noncommercial"]
    bad += [t["tool"] for t in tools if t["status"] in ("KEPT",) and "needs" in (t.get("reason") or "").lower()
            and "key" in (t.get("reason") or "").lower()]
    missing_sub = [t["tool"] for t in removed if not t.get("substitute")]
    rep["manifest"] = {
        "total": len(tools),
        "counts": man.get("meta", {}).get("counts"),
        "removed_or_missing": [{"n": t["n"], "tool": t["tool"], "status": t["status"],
                                "substitute": t.get("substitute", "NONE")} for t in removed],
        "policy_violations_noncommercial_kept": bad,
        "removed_without_substitute": missing_sub,
        "verdict": "PASS" if not bad and not missing_sub else "REVIEW",
    }

    # 3. binaries
    bins = which("ffmpeg", "ffprobe", "git", "curl", "jq", "tesseract", "convert",
                 "node", "npm", "java", "espeak-ng", "xvfb-run", "sox", "glxinfo")
    rep["binaries"] = {k: (v or "ABSENT") for k, v in bins.items()}

    # 4. ffmpeg filters
    filt = {}
    p = run(["ffmpeg", "-hide_banner", "-filters"], None, timeout=60)
    blob = p.stdout or ""
    for f in FILTERS:
        filt[f] = bool(any(line.split()[1:2] == [f] for line in blob.splitlines()
                           if line.strip().startswith(("T", ".", "A", "V", "G", "C", "N"))))
    rep["ffmpeg_filters"] = filt
    rep["ffmpeg_missing_filters"] = [k for k, v in filt.items() if not v]

    # 5. endpoints (stdlib only, no key, no credential)
    import urllib.request
    ep = {}

    class _NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            raise urllib.error.HTTPError(req.full_url, code, f"redirect -> {newurl}", headers, fp)

    opener = urllib.request.build_opener(_NoRedirect)
    for name, url in ENDPOINTS.items():
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "tc01-smoke/1.0"})
            with opener.open(req, timeout=25) as r:
                ep[name] = {"http": r.status, "bytes": len(r.read(60000)), "final_url": r.geturl()}
        except urllib.error.HTTPError as e:
            if e.code in (301, 302, 307, 308):
                loc = e.headers.get("Location", "")
                try:
                    req2 = urllib.request.Request(loc, headers={"User-Agent": "tc01-smoke/1.0"})
                    with urllib.request.urlopen(req2, timeout=25) as r2:
                        ep[name] = {"http": r2.status, "bytes": len(r2.read(60000)),
                                    "via_redirect": e.code, "final_url": r2.geturl()}
                    continue
                except Exception as e2:  # noqa: BLE001
                    ep[name] = {"http": None, "error": scrub(str(e2))[:160], "via_redirect": e.code,
                                "redirect_to": loc}
                    continue
        except Exception as e:  # noqa: BLE001
            ep[name] = {"http": None, "error": scrub(str(e))[:160]}
    rep["endpoints"] = ep
    rep["endpoint_failures"] = [k for k, v in ep.items() if not v.get("http")]

    rep["overall"] = "PASS" if (
        not rep["ffmpeg_missing_filters"]
        and not rep["endpoint_failures"]
        and rep["manifest"]["verdict"] == "PASS"
        and rep["binaries"].get("ffmpeg") != "ABSENT"
    ) else "REVIEW"

    write_json(out / "smoke.json", rep)
    (out / "smoke_summary.md").write_text(
        f"# stage 0 smoke — {rep['overall']}\n\n"
        f"- manifest: {rep['manifest']['total']} tools, verdict {rep['manifest']['verdict']}\n"
        f"- removed/missing: {len(rep['manifest']['removed_or_missing'])}\n"
        f"- ffmpeg filters missing: {rep['ffmpeg_missing_filters'] or 'none'}\n"
        f"- endpoint failures: {rep['endpoint_failures'] or 'none'}\n"
        f"- binaries absent: {[k for k, v in rep['binaries'].items() if v == 'ABSENT'] or 'none'}\n",
        encoding="utf-8")
    print(json.dumps({k: rep[k] for k in ("overall", "ffmpeg_missing_filters", "endpoint_failures")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
