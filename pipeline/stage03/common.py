"""Stage 3 helpers: parse the narration source and keep per-line bookkeeping."""
import json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from util import out_dir, log  # noqa

STAGE = "stage03"
HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "..", "stage02", "source", "narration_v2.txt")

def lines():
    """[(index, cue, text)] from the narration source - one entry per spoken line."""
    src = open(SOURCE, encoding="utf-8").read()
    cue = "00:00"
    out = []
    for raw in src.splitlines():
        m = re.match(r"^\[(\d\d:\d\d)", raw)
        if m:
            cue = m.group(1)
        if raw.startswith("NARRATOR:"):
            out.append({"i": len(out) + 1, "cue": cue, "text": raw.split(":", 1)[1].strip()})
    return out

def doc_quotes():
    """Public-domain newspaper sentences that SILMA reads as the second voice."""
    return [
        {"id": "Q1", "source": "Alexandria Gazette, 14 March 1873 (Library of Congress)",
         "text": "The cargo consisting of barrels of spirits is untouched, with the exception of one cask which had started."},
        {"id": "Q2", "source": "Alexandria Gazette, 14 March 1873 (Library of Congress)",
         "text": "Every document which could have thrown any light upon the history of the derelict had been removed."},
        {"id": "Q3", "source": "The Sun, New York, 25 March 1873 (Library of Congress)",
         "text": "From the log of the abandoned vessel she is supposed to be the American brigantine Mary Celeste, bound from New York to Genoa."},
    ]
