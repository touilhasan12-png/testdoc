#!/usr/bin/env python3
"""Chatterbox (resemble-ai/chatterbox) - MAIN English narrator. Synthetic voice, no cloning.

CPU reality check: the script synthesises ONE line first, measures seconds-per-character, and
only commits to the full 4:55 if the projection fits the job budget. If it does not fit, it
exits non-zero with the measurement so the pipeline can fall back - it never ships a partial
take pretending to be complete."""
import json, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from util import out_dir, log, write_json
from common import lines, STAGE

BUDGET_S = float(os.environ.get("CHATTERBOX_BUDGET", "2400"))   # 40 min of synthesis
TEST_ONLY = os.environ.get("CHATTERBOX_TEST_ONLY") == "1"

def main():
    out = os.path.join(out_dir(STAGE), "chatterbox")
    os.makedirs(out, exist_ok=True)
    L = lines()
    t0 = time.time()
    try:
        import torch
        from chatterbox.tts import ChatterboxTTS
    except Exception as e:
        write_json(os.path.join(out, "status.json"), {"ok": False, "stage": "import", "error": repr(e)[:400]})
        log(STAGE, "Chatterbox", f"import failed: {e!r}")
        raise SystemExit(2)
    log(STAGE, "Chatterbox", f"torch {torch.__version__}, cuda={torch.cuda.is_available()}")
    model = ChatterboxTTS.from_pretrained(device="cpu")
    log(STAGE, "Chatterbox", "model loaded on cpu")

    def synth(text, path):
        wav = model.generate(text)
        import torchaudio as ta
        ta.save(path, wav, model.sr)
        return os.path.getsize(path)

    # ---- measurement on the first line
    p0 = os.path.join(out, "test_01.wav")
    s0 = time.time()
    synth(L[0]["text"], p0)
    dt, chars = time.time() - s0, len(L[0]["text"])
    rate = dt / max(1, chars)
    total_chars = sum(len(x["text"]) for x in L)
    projected = rate * total_chars + 20
    write_json(os.path.join(out, "measurement.json"),
               {"first_line_seconds": round(dt, 1), "chars": chars, "sec_per_char": round(rate, 3),
                "total_chars": total_chars, "projected_seconds": round(projected, 1),
                "budget_seconds": BUDGET_S, "fits": projected < BUDGET_S})
    log(STAGE, "Chatterbox", f"first line {dt:.1f}s for {chars} chars -> projected full read {projected/60:.1f} min (budget {BUDGET_S/60:.0f})")
    if TEST_ONLY or projected >= BUDGET_S:
        write_json(os.path.join(out, "status.json"),
                   {"ok": False, "stage": "budget", "projected_seconds": round(projected),
                    "reason": "CPU synthesis would exceed the job budget; stopped after the measured line",
                    "test_wav": "test_01.wav"})
        log(STAGE, "Chatterbox", "stopping before the full take: budget exceeded (this is recorded, not hidden)")
        raise SystemExit(3)

    # ---- full take
    metas = []
    for line in L:
        p = os.path.join(out, f"line_{line['i']:02d}.wav")
        if os.path.exists(p) and os.path.getsize(p) > 2000:
            metas.append({**line, "wav": os.path.basename(p), "bytes": os.path.getsize(p), "cached": True})
            continue
        synth(line["text"], p)
        import wave
        with wave.open(p) as w:
            dur = w.getnframes() / w.getframerate()
        metas.append({**line, "wav": os.path.basename(p), "bytes": os.path.getsize(p),
                      "seconds": round(dur, 2), "cached": False})
        log(STAGE, "Chatterbox", f"line {line['i']:02d}/{len(L)} {dur:.1f}s")
    write_json(os.path.join(out, "lines.json"), {"narrator": "Chatterbox (synthetic)", "lines": metas})
    write_json(os.path.join(out, "status.json"),
               {"ok": True, "lines": len(metas), "total_seconds": round(sum(m.get("seconds", 0) for m in metas), 1)})
    log(STAGE, "Chatterbox", f"full take done: {len(metas)} lines")

if __name__ == "__main__":
    main()
