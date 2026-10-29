"""Keyless HTTP helpers for stage 1. No credential is ever read or sent."""
from __future__ import annotations
import json, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path

UA = "tc01-research/1.0 (documentary research pilot; non-commercial; no credential used)"
CACHE: Path | None = None


def _req(url: str, timeout: int = 45, headers: dict | None = None):
    h = {"User-Agent": UA, "Accept": "*/*"}
    if headers:
        h.update(headers)
    return urllib.request.Request(url, headers=h)


def fetch(url: str, timeout: int = 45, retries: int = 2, binary: bool = False):
    """GET with retries. Returns (status, body|None, error|None). Never raises."""
    last = None
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(_req(url, timeout), timeout=timeout) as r:
                data = r.read()
                return r.status, (data if binary else data.decode("utf-8", "replace")), None
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}"
            if e.code in (403, 404, 410):
                return e.code, None, last
        except Exception as e:  # noqa: BLE001
            last = f"{type(e).__name__}: {e}"
        time.sleep(1.5 * (attempt + 1))
    return None, None, last


def fetch_json(url: str, timeout: int = 45, retries: int = 2):
    st, body, err = fetch(url, timeout, retries)
    if body is None:
        return st, None, err
    try:
        return st, json.loads(body), None
    except Exception as e:  # noqa: BLE001
        return st, None, f"json-decode: {e}"


def api(base: str, params: dict, timeout: int = 45) -> tuple:
    return fetch_json(base + "?" + urllib.parse.urlencode(params, doseq=True), timeout)


def download(url: str, dest: Path, timeout: int = 120) -> dict:
    dest.parent.mkdir(parents=True, exist_ok=True)
    st, data, err = fetch(url, timeout, retries=1, binary=True)
    if data:
        dest.write_bytes(data)
        return {"url": url, "status": st, "bytes": len(data), "path": str(dest)}
    return {"url": url, "status": st, "bytes": 0, "path": None, "error": err}


def polite(seconds: float = 1.0) -> None:
    time.sleep(seconds)
