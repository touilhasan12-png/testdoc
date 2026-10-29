#!/usr/bin/env python3
"""SILMA TTS (silma-ai/SILMA-TTS) - second voice, reads the archive quotations.
Same principle as Chatterbox: it is a reader, not a witness. Bounded test first; if the
model cannot run inside the budget the outcome is written down, not covered up."""
import json, os, sys, time, wave
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from util import out_dir, log, write_json
from common import doc_quotes, STAGE

TEST_ONLY = os.environ.get("SILMA_TEST_ONLY", "1") == "1"
BUDGET_S = float(os.environ.get("SILMA_BUDGET", "600"))

def main():
    out = os.path.join(out_dir(STAGE), "silma")
    os.makedirs(out, exist_ok=True)
    quotes = doc_quotes()
    t0 = time.time()
    try:
        from silma_tts.api import SilmaTTS
    except Exception as e:
        write_json(os.path.join(out, "status.json"), {"ok": False, "stage": "import", "error": repr(e)[:500]})
        log(STAGE, "SILMA TTS", f"import failed: {e!r}")
        raise SystemExit(2)
    api = SilmaTTS()
    # SILMA is a zero-shot reader: it needs a reference clip + its transcript. We use the
    # reference clip shipped in the repository, never a recording of any real participant.
    ref = None
    for root, _, files in os.walk("/tmp/silma"):
        for f in files:
            if f.endswith(".wav") and "ref" in f:
                ref = os.path.join(root, f); break
        if ref: break
    if not ref:
        write_json(os.path.join(out, "status.json"),
                   {"ok": False, "stage": "reference_audio", "error": "no reference clip in the repo checkout"})
        log(STAGE, "SILMA TTS", "no reference clip found - stopping")
        raise SystemExit(4)
    log(STAGE, "SILMA TTS", f"loaded, reference clip {os.path.basename(ref)}")
    metas = []
    for q in (quotes[:1] if TEST_ONLY else quotes):
        p = os.path.join(out, f"quote_{q['id']}.wav")
        s = time.time()
        res = api.infer(ref_file=ref, ref_text=None, gen_text=q["text"],
                        file_wave=p, seed=None, speed=1)
        wav, srate = (res[0], res[1]) if isinstance(res, tuple) else (None, 24000)
        dur = time.time() - s
        import numpy as np
        if wav is None:                      # the api already wrote the file
            with wave.open(p) as f:
                n, srate = f.getnframes(), f.getframerate()
            arr = np.zeros(n, dtype="float32"); dur_len = n / srate
        else:
            arr = np.asarray(wav).squeeze()
            dur_len = len(arr) / srate
        metas.append({**q, "wav": os.path.basename(p), "synth_seconds": round(dur, 1),
                      "audio_seconds": round(dur_len, 2)})
        log(STAGE, "SILMA TTS", f"{q['id']} {dur_len:.1f}s audio in {dur:.1f}s")
        if time.time() - t0 > BUDGET_S:
            log(STAGE, "SILMA TTS", "budget reached, stopping")
            break
    ok = len(metas) == (1 if TEST_ONLY else len(quotes))
    write_json(os.path.join(out, "lines.json"), {"reader": "SILMA TTS (document reader, synthetic)",
                                                 "test_only": TEST_ONLY, "quotes": metas})
    write_json(os.path.join(out, "status.json"), {"ok": ok, "rendered": len(metas),
                                                  "requested": 1 if TEST_ONLY else len(quotes)})

if __name__ == "__main__":
    main()
