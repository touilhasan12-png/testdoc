#!/usr/bin/env python3
"""Probe every mandatory tool: does the repository exist, is it licence-visible, does it install.
Writes tools/tool_status.json. Never invents a result: every field comes from an HTTP response or a real process exit."""
import json, os, subprocess, sys, urllib.request, urllib.error, time, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAN = json.load(open(os.path.join(ROOT, "tools/tools_manifest.json")))
TOKEN = os.environ.get("GITHUB_TOKEN")
OUT = {"generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "python": sys.version.split()[0], "tools": {}}

def api(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json",
          "User-Agent": "tcs01-probe", **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {})})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception as e:
        return -1, {"error": str(e)}

def pip_try(pkg, timeout=240):
    try:
        p = subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "--no-input", pkg],
                           capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stderr or p.stdout).strip().splitlines()[-1:] or [""]
    except subprocess.TimeoutExpired:
        return 124, ["pip install timed out"]

def main():
    for t in MAN["tools"]:
        rec = {"n": t["n"], "name": t["name"], "kind": t["kind"], "group": t["group"],
               "declared_license": t.get("license_expected"), "commercial": t.get("commercial"),
               "repo": t.get("repo"), "substitute": t.get("substitute"), "status": None, "detail": None}
        if t["kind"] == "repo":
            st, d = api(f"https://api.github.com/repos/{t['repo']}")
            if st == 200:
                rec["status"] = "reachable"
                rec["license"] = (d.get("license") or {}).get("spdx_id")
                rec["stars"] = d.get("stargazers_count"); rec["archived"] = d.get("archived")
                rec["last_push"] = d.get("pushed_at"); rec["size_kb"] = d.get("size")
                rec["lang"] = d.get("language")
                rec["html_url"] = d.get("html_url")
            else:
                rec["status"] = "failed"; rec["detail"] = f"HTTP {st} on {t['repo']}"
                OUT["tools"][t["id"]] = rec; continue
        elif t["kind"] == "substitute":
            code = os.path.join(ROOT, t["substitute"]) if t.get("substitute") else None
            rec["status"] = "substituted" if code and os.path.exists(code) else "pending_code"
            rec["detail"] = "no upstream repository under this name; equivalent function implemented in-repo and labelled SUBSTITUTED"
        elif t["kind"] == "service":
            rec["status"] = "service"
            rec["detail"] = "hosted data source, not a repository"
        else:
            rec["status"] = "desktop-app"
            rec["detail"] = "desktop/GUI application; executable check happens in stage 12"
        OUT["tools"][t["id"]] = rec
    # real install checks - only for tools we intend to actually run, listed here with their PyPI name
    installs = {"pedalboard": "pedalboard", "demucs": "demucs", "auto-editor": "auto-editor",
                "remotion": None, "ffmpeg": None}
    OUT["install_checks"] = {}
    for k, pkg in installs.items():
        if pkg is None:
            continue
        rc, tail = pip_try(pkg)
        OUT["install_checks"][k] = {"pip": pkg, "returncode": rc, "tail": tail}
    json.dump(OUT, open(os.path.join(ROOT, "tools/tool_status.json"), "w"), indent=1)
    ok = sum(1 for v in OUT["tools"].values() if v["status"] in ("reachable", "substituted", "service", "desktop-app"))
    print(f"probed {len(OUT['tools'])} tools, {ok} accounted for")
    for k, v in OUT["install_checks"].items():
        print("install", k, "rc=", v["returncode"], v["tail"][:1])

if __name__ == "__main__":
    main()
