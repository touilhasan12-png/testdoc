#!/usr/bin/env python3
"""Bark (suno-ai/bark) - breath / sigh texture only. Bark is heavy; we ask it for very short
non-verbal cues (music/sfx tokens) and keep them as texture layers, never as speech."""
import json, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from util import out_dir, log, write_json
STAGE = "stage03"

CUES = [
    {"id": "breath_a", "prompt": "[breath]"},
    {"id": "sigh_a", "prompt": "[sigh]"},
]

def main():
    out = os.path.join(out_dir(STAGE), "bark")
    os.makedirs(out, exist_ok=True)
    try:
        import numpy as np, torch, wave
        _orig = torch.load
        def _load(*a, **kw):
            kw.setdefault("weights_only", False)
            return _orig(*a, **kw)
        torch.load = _load
        from bark import SAMPLE_RATE, generate_audio, preload_models
    except Exception as e:
        write_json(os.path.join(out, "status.json"), {"ok": False, "stage": "import", "error": repr(e)[:400]})
        log(STAGE, "Bark", f"import failed: {e!r}")
        raise SystemExit(2)
    t = time.time()
    try:
        preload_models(text_use_small=True, coarse_use_small=True, fine_use_small=True)
    except Exception as e:
        write_json(os.path.join(out, "status.json"),
                   {"ok": False, "stage": "model_download", "error": repr(e)[:400]})
        log(STAGE, "Bark", f"model download/load failed: {e!r}")
        raise SystemExit(3)
    log(STAGE, "Bark", f"models loaded in {time.time()-t:.1f}s")
    made = []
    for c in CUES:
        a = generate_audio(c["prompt"], history_prompt="en_speaker_6")
        p = os.path.join(out, c["id"] + ".wav")
        with wave.open(p, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SAMPLE_RATE)
            w.writeframes((np.clip(a, -1, 1) * 32767).astype("int16").tobytes())
        made.append({"id": c["id"], "prompt": c["prompt"], "wav": os.path.basename(p),
                     "seconds": round(len(a) / SAMPLE_RATE, 2)})
        log(STAGE, "Bark", f"{c['id']} {len(a)/SAMPLE_RATE:.1f}s")
    write_json(os.path.join(out, "cues.json"), {"engine": "Bark", "cues": made})
    write_json(os.path.join(out, "status.json"), {"ok": True, "cues": len(made)})

if __name__ == "__main__":
    main()
