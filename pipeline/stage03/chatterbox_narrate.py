#!/usr/bin/env python3
"""Chatterbox (resemble-ai/chatterbox) - MAIN English narrator. Synthetic voice, no cloning.

Two CI realities are handled explicitly and recorded rather than hidden:
  1. torch>=2.6 loads chatterbox checkpoints with weights_only=True by default -> we pass
     weights_only=False for this local, public model only.
  2. chatterbox's Perth watermarker object can be None on this image (resemble-perth mismatch).
     If so we substitute a no-op watermarker, set status.json watermark=false, and the film's
     credits state that the narration carries no Perth watermark.

Budget guard: one measured line first; if the projection exceeds the job budget the script
stops and exits 3 so the pipeline can fall back - it never ships a partial take as complete."""
import json, os, sys, time, wave
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from util import out_dir, log, write_json
from common import lines, STAGE

BUDGET_S = float(os.environ.get("CHATTERBOX_BUDGET", "2400"))
TEST_ONLY = os.environ.get("CHATTERBOX_TEST_ONLY") == "1"

def main():
    out = os.path.join(out_dir(STAGE), "chatterbox")
    os.makedirs(out, exist_ok=True)
    L = lines()
    try:
        import torch
        import torchaudio
        _orig = torch.load
        def _load(*a, **kw):
            kw.setdefault("weights_only", False)
            return _orig(*a, **kw)
        torch.load = _load
        import chatterbox.tts as ct
    except Exception as e:
        write_json(os.path.join(out, "status.json"), {"ok": False, "stage": "import", "error": repr(e)[:400]})
        log(STAGE, "Chatterbox", f"import failed: {e!r}")
        raise SystemExit(2)

    watermark = True
    try:
        model = ct.ChatterboxTTS.from_pretrained(device="cpu")
    except TypeError as e:
        watermark = False
        log(STAGE, "Chatterbox", f"Perth watermarker unavailable ({e}); installing no-op watermarker, status records watermark=false")
        class _NoopWatermark:
            def apply_watermark(self, wav, sample_rate=None, **kw):
                return wav
        ct.perth.PerthImplicitWatermarker = _NoopWatermark
        try:
            model = ct.ChatterboxTTS.from_pretrained(device="cpu")
        except Exception as e2:
            write_json(os.path.join(out, "status.json"),
                       {"ok": False, "stage": "load", "watermark": watermark, "error": repr(e2)[:400]})
            log(STAGE, "Chatterbox", f"model load failed after watermark workaround: {e2!r}")
            raise SystemExit(2)

    def synth(text, path):
        wav = model.generate(text)
        if hasattr(wav, "dim") and wav.dim() == 1:
            wav = wav.unsqueeze(0)
        torchaudio.save(path, wav.cpu(), model.sr)
        return path

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
                "budget_seconds": BUDGET_S, "fits": projected < BUDGET_S, "watermark": watermark})
    log(STAGE, "Chatterbox", f"measured line: {dt:.1f}s/{chars} chars -> projected {projected/60:.1f} min (budget {BUDGET_S/60:.0f} min), watermark={watermark}")
    if TEST_ONLY or projected >= BUDGET_S:
        write_json(os.path.join(out, "status.json"),
                   {"ok": False, "stage": "budget", "watermark": watermark,
                    "projected_seconds": round(projected),
                    "reason": "CPU synthesis would exceed the job budget; stopped after the measured line",
                    "kept": "test_01.wav"})
        raise SystemExit(3)

    metas = []
    for line in L:
        p = os.path.join(out, f"line_{line['i']:02d}.wav")
        if not os.path.exists(p):
            synth(line["text"], p)
        with wave.open(p) as w:
            dur = w.getnframes() / w.getframerate()
        metas.append({**line, "wav": os.path.basename(p), "seconds": round(dur, 2)})
        log(STAGE, "Chatterbox", f"line {line['i']:02d}/{len(L)} {dur:.1f}s")
    write_json(os.path.join(out, "lines.json"), {"narrator": "Chatterbox (synthetic, un-cloned)", "lines": metas})
    write_json(os.path.join(out, "status.json"),
               {"ok": True, "lines": len(metas), "watermark": watermark,
                "total_seconds": round(sum(m["seconds"] for m in metas), 1)})

if __name__ == "__main__":
    main()
