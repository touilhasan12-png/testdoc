#!/usr/bin/env python3
"""Fallback narrator for CPU: kokoro-onnx (Apache-2.0 model weights, MIT wrapper).
Only runs when Chatterbox could not complete inside the budget. The manifest and every
downstream file say which engine actually produced the voice. No cloning of any real person."""
import json, os, sys, wave
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from util import out_dir, log, http, write_json
from common import lines, STAGE

MODEL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
VOICES = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"
VOICE = os.environ.get("KOKORO_VOICE", "am_michael")

def fetch(url, dest):
    if os.path.exists(dest) and os.path.getsize(dest) > 1_000_000:
        return dest
    st, body = http(url, binary=True, timeout=900, tries=3)
    if st != 200:
        raise SystemExit(f"model download failed {url} -> {st}")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    open(dest, "wb").write(body)
    return dest

def main():
    out = os.path.join(out_dir(STAGE), "kokoro")
    os.makedirs(out, exist_ok=True)
    m = fetch(MODEL, os.path.join(out, "kokoro-v1.0.onnx"))
    v = fetch(VOICES, os.path.join(out, "voices-v1.0.bin"))
    from kokoro_onnx import Kokoro
    k = Kokoro(m, v)
    log(STAGE, "kokoro-onnx (fallback narrator)", f"loaded voice={VOICE}")
    metas = []
    for line in lines():
        samples, sr = k.create(line["text"], voice=VOICE, speed=0.95, lang="en-us")
        p = os.path.join(out, f"line_{line['i']:02d}.wav")
        with wave.open(p, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
            w.writeframes(samples.astype("int16").tobytes())
        metas.append({**line, "wav": os.path.basename(p), "seconds": round(len(samples) / sr, 2),
                      "bytes": os.path.getsize(p)})
        log(STAGE, "kokoro-onnx (fallback narrator)", f"line {line['i']:02d} {len(samples)/sr:.1f}s")
    write_json(os.path.join(out, "lines.json"),
               {"narrator": f"kokoro-onnx ({VOICE}) - FALLBACK, Chatterbox did not fit the CPU budget",
                "lines": metas})
    print(json.dumps({"lines": len(metas), "seconds": round(sum(m["seconds"] for m in metas), 1)}))

if __name__ == "__main__":
    main()
