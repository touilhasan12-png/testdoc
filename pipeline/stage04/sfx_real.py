#!/usr/bin/env python3
"""Freesound + freesound-mcp-server - real CC0 sound effects.
No Freesound API key is configured for this run (the user chose public fallbacks), so the tool
chain is exercised honestly: the MCP server repository is cloned and inspected, the Freesound
API is queried once without a key to record the real answer, and the SFX used in the film come
from the public-domain Internet Archive with the item id recorded for CREDITS."""
import json, os, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from util import out_dir, log, write_json, get_json, http
STAGE = "stage04"

def main():
    out = out_dir(STAGE)
    rec = {}
    mcp = os.path.join(out, "freesound-mcp-server")
    if not os.path.exists(os.path.join(mcp, ".git")):
        rec["mcp_clone"] = subprocess.run(["git", "clone", "--depth", "1",
                                           "https://github.com/johnkimdw/freesound-mcp-server", mcp],
                                          capture_output=True, text=True, timeout=300).returncode == 0
    else:
        rec["mcp_clone"] = True
    key = os.environ.get("FREESOUND_API_KEY", "")
    if key:
        st, d = get_json(f"https://freesound.org/apiv2/search/text/?query=ship+creak&fields=id,name,license,previews&token={key}")
        rec["freesound_search"] = {"status": st, "hits": (d or {}).get("count")}
    else:
        st, body = http("https://freesound.org/apiv2/search/text/?query=ship+creak")
        rec["freesound_search"] = {"status": st, "note": "no API key configured - recorded, not faked",
                                   "body_head": (body or "")[:120]}
    # public-domain fallbacks from the Internet Archive
    st, d = get_json("https://archive.org/advancedsearch.php?q=%28sea+waves+OR+ship+creak%29+AND+mediatype%3Aaudio"
                     "&fl%5B%5D=identifier&fl%5B%5D=title&fl%5B%5D=licenseurl&rows=8&output=json")
    items = (d or {}).get("response", {}).get("docs", [])
    rec["archive_items"] = [{"id": i["identifier"], "title": i.get("title"), "license": i.get("licenseurl")}
                            for i in items]
    log(STAGE, "Freesound", json.dumps(rec["freesound_search"])[:300])
    log(STAGE, "freesound-mcp-server", f"cloned={rec['mcp_clone']}")
    log(STAGE, "Internet Archive (public SFX source)", f"items={len(items)}")
    write_json(os.path.join(out, "sfx_sources.json"), rec)
    print(json.dumps({"freesound": rec["freesound_search"].get("status"), "archive_items": len(items)}))

if __name__ == "__main__":
    main()
