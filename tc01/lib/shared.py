"""Shared helpers for the TrueCrime_Sample_01 pipeline (tc01).

Rules enforced here:
  * no credential is ever read, written, printed or logged;
  * every artefact is written under work/<stage>/ and listed in work/<stage>/MANIFEST.txt;
  * every tool invocation records (tool, input, output, path, license) so the orchestration
    agent can append it to Google Drive 07_logs and to project/00_tools_manifest_v1.json.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
WORK = REPO / "work"
PROJECT = REPO / "project"

SECRET_PATTERNS = [
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9]{36}"),
    re.compile(r"gho_[A-Za-z0-9]{36}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
]


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def scrub(text: str) -> str:
    """Redact anything that looks like a credential before it can reach a log."""
    out = str(text)
    for pat in SECRET_PATTERNS:
        out = pat.sub("[REDACTED-CREDENTIAL]", out)
    return out


def stage_dir(stage: str) -> Path:
    d = WORK / stage
    d.mkdir(parents=True, exist_ok=True)
    (WORK / "logs").mkdir(parents=True, exist_ok=True)
    return d


class Log:
    """Line logger that writes to stdout, a stage log file and the step manifest."""

    def __init__(self, stage: str):
        self.stage = stage
        self.dir = stage_dir(stage)
        self.path = WORK / "logs" / f"{stage}.log"
        self.records: list[dict] = []

    def __call__(self, msg: str, **kw) -> None:
        line = f"[{now()}] {msg}"
        if kw:
            line += " " + json.dumps(kw, ensure_ascii=False, sort_keys=True)
        print(scrub(line), flush=True)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(scrub(line) + "\n")

    def tool(self, tool: str, status: str, inp: str, out: str, path: str = "",
             license: str = "", note: str = "") -> dict:
        """Record one mandated-tool invocation. status: used | failed | skipped | substitute."""
        rec = {
            "ts": now(), "stage": self.stage, "tool": tool, "status": status,
            "input": inp, "output": out, "path": path, "license": license, "note": note,
        }
        self.records.append(rec)
        self(f"TOOL {tool} -> {status}" + (f" ({note})" if note else ""))
        return rec

    def flush(self) -> Path:
        man = self.dir / "MANIFEST.txt"
        with man.open("w", encoding="utf-8") as fh:
            fh.write(f"# {self.stage} — {now()}\n")
            fh.write("# tool | status | input | output | path | license | note\n")
            for r in self.records:
                fh.write(" | ".join(scrub(str(r.get(k, ""))) for k in
                                   ("tool", "status", "input", "output", "path", "license", "note")) + "\n")
            fh.write("\n# files\n")
            for p in sorted(self.dir.rglob("*")):
                if p.is_file():
                    fh.write(f"{p.relative_to(REPO)}\t{p.stat().st_size}\n")
        (self.dir / "tool_log.json").write_text(
            json.dumps(self.records, indent=1, ensure_ascii=False), encoding="utf-8")
        return man


def sha8(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:12]


def run(cmd: list[str] | str, log: Log | None = None, timeout: int = 1800,
        cwd: str | None = None, check: bool = False) -> subprocess.CompletedProcess:
    """Run a subprocess with a hard timeout; never raises on non-zero unless check=True."""
    shell = isinstance(cmd, str)
    if log:
        log(f"RUN {cmd if shell else ' '.join(map(str, cmd))}")
    t0 = time.time()
    try:
        p = subprocess.run(cmd, shell=shell, cwd=cwd, capture_output=True, text=True,
                           timeout=timeout, errors="replace")
        if log:
            tail = (p.stdout or "")[-1200:]
            err = (p.stderr or "")[-800:]
            log(f"DONE rc={p.returncode} in {time.time()-t0:.1f}s")
            if tail.strip():
                log("stdout-tail: " + tail.strip().replace("\n", " | ")[:1000])
            if err.strip():
                log("stderr-tail: " + err.strip().replace("\n", " | ")[:700])
        if check and p.returncode != 0:
            raise RuntimeError(f"command failed rc={p.returncode}")
        return p
    except subprocess.TimeoutExpired as e:
        if log:
            log(f"TIMEOUT after {timeout}s: {cmd}")
        return subprocess.CompletedProcess(cmd, 124, stdout=(e.stdout or b"").decode("utf-8", "replace")
                                           if isinstance(e.stdout, bytes) else (e.stdout or ""),
                                           stderr=f"timeout after {timeout}s")


def which(*names: str) -> dict[str, str | None]:
    from shutil import which as _w
    return {n: _w(n) for n in names}


def read_json(path: str | Path, default=None):
    p = Path(path)
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8"))


def write_json(path: str | Path, obj) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=1, ensure_ascii=False), encoding="utf-8")
    return p


def env_flag(name: str, default: bool = False) -> bool:
    v = os.environ.get(name)
    if v is None:
        return default
    return v.strip().lower() in {"1", "true", "yes", "on"}
