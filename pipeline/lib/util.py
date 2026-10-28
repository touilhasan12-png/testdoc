"""Shared helpers: deterministic paths, http with retries, provenance logging."""
import json, os, hashlib, time, urllib.request, urllib.error, urllib.parse, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
WORK = os.path.join(ROOT, "work")
UA = "TrueCrimeSample01/1.0 (documentary research pipeline; contact: repo owner)"

def log_path(stage):
    p = os.path.join(WORK, "logs", f"{stage}.log")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p

def log(stage, tool, msg):
    line = f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} | {stage} | {tool} | {msg}\n"
    with open(log_path(stage), "a") as f:
        f.write(line)
    sys.stdout.write(line)

def out_dir(stage):
    p = os.path.join(WORK, stage)
    os.makedirs(p, exist_ok=True)
    return p

def sha256(path, n=16):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(65536), b""):
            h.update(b)
    return h.hexdigest()[:n]

def http(url, tries=4, timeout=60, headers=None, binary=False):
    last = None
    h = {"User-Agent": UA}
    if headers:
        h.update(headers)
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=h)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                data = r.read()
                return r.status, data if binary else data.decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}"
            if e.code in (403, 404, 410):
                break
        except Exception as e:
            last = f"{type(e).__name__}: {e}"
        time.sleep(1.5 * (i + 1))
    return -1, last

def get_json(url, **kw):
    st, body = http(url, **kw)
    if st != 200:
        return st, None
    try:
        return st, json.loads(body)
    except Exception as e:
        return -1, {"_parse_error": str(e)}

def save(url, dest):
    st, body = http(url, binary=True, timeout=180)
    if st == 200:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as f:
            f.write(body)
        return dest, sha256(dest)
    return None, st

def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(obj, open(path, "w"), indent=1, ensure_ascii=False)
    return path
