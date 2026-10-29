# Stage 0 findings (runner ground truth)

Measured on a real GitHub Actions `ubuntu-latest` runner, run `40891330818`, commit `fe364a6`.

## Runner
- 4 vCPU, x86_64, Linux 7.0.0-azure, glibc 2.39, Python 3.11.17.
- More CPU than the 2-core assumption in the original plan: CPU-only neural inference is feasible for
  short clips, but still the binding constraint. Every heavy tool runs on a short segment first.

## Present after `apt-get install ffmpeg tesseract-ocr tesseract-ocr-eng imagemagick libsndfile1`
ffmpeg 6.1.1 · ffprobe · git · curl · jq · convert (ImageMagick) · tesseract · node · npm · java · xvfb-run.
Absent and not needed: sox, glxinfo. `espeak-ng` must be added explicitly where Bark/Chatterbox need it.

## FFmpeg filters confirmed available (the grade + edit stages depend on these)
`lut3d` `cas` `drawtext` `histeq` `histogram` `hqdn3d` `nlmeans` `signalstats` `unsharp` `zoompan` `ahistogram`
-> the whole Neo-Noir grading path (3D LUT + grain + halation via unsharp/blur composites) and the whole
substitute path for the removed upscaler (lanczos + unsharp + cas) are confirmed workable. No fallback needed.

## Keyless endpoints confirmed reachable from the runner
| endpoint | result |
|---|---|
| www.loc.gov (collections JSON) | 200 |
| www.loc.gov/chroniclingamerica/search/api | 200 — **the service moved** |
| chroniclingamerica.loc.gov | 308 -> www.loc.gov/chroniclingamerica (old host is a redirect only) |
| commons.wikimedia.org/w/api.php | 200 |
| archive.org/advancedsearch.php | 200 |
| basemaps.cartocdn.com dark_all tiles | 200 (keyless dark basemap for kepler.gl / geo renders) |
| pypi.org | 200 |
| api.openverse.org | slow / timed out — treated as a soft dependency, Wikimedia + Archive.org cover it |

## Bugs found in my own scaffold and fixed in this stage
1. `tc01/` was not a package, so `from lib.shared import ...` failed and `smoke.json` was never written.
   Fixed: added `tc01/__init__.py` and put `tc01/` on `sys.path`. The first run passed only because the
   step masked the failure with `|| echo`; the mask was removed so a failing stage can never look green.
2. The manifest generator stored each substitute inside `run_mode` instead of a `substitute` field, so the
   policy self-check reported all 11 removals as "removed without substitute". Fixed and re-verified:
   every removed tool now names its substitute.
3. Chronicling America URL was stale. Fixed to `www.loc.gov/chroniclingamerica/...`.

## Consequences for the remaining stages
- Stage 1 must use the www.loc.gov Chronicling America host.
- Stage 6 uses CARTO dark tiles (attribution-only, keyless) for every map render.
- Stage 9 uses IOPaint + FFmpeg lanczos/unsharp/cas instead of the removed GFPGAN/Real-ESRGAN.
- Stage 8 uses COLMAP instead of the removed Meshroom.
- Stage 12 builds the .cube LUT with the agent-authored extractor instead of the removed deep-analog.

---

# Addendum — third smoke run (commit 535969f, run 40892200170): PASS, plus one real risk found

## Chronicling America (mandated tool #6) — API status verified from the runner and locally

| path | result | verdict |
|---|---|---|
| `chroniclingamerica.loc.gov/search/api/results.json` | 308 -> `www.loc.gov/chroniclingamerica/...` | **retired** |
| `www.loc.gov/chroniclingamerica/search/api/results.json` | 404 | **retired** |
| `chroniclingamerica.loc.gov/search/titles/results.json` | 404 | **retired** |
| `www.loc.gov/newspapers/?fo=json&c=1` | **200, `pagination.of = 3,224,499`** | **LIVE — this is the working path** |
| `www.loc.gov/search/?q=...&fo=json&c=N` | 200 | LIVE universal search |
| `www.loc.gov/collections/chronicling-america/?fo=json` | 200 | LIVE collection view |

Consequence: the dedicated Chronicling America search API is gone. Stage 1 must reach the same holdings
through the **Library of Congress universal/collection JSON API** (`www.loc.gov/newspapers/`, `www.loc.gov/search/`,
`www.loc.gov/collections/chronicling-america/`) and follow each hit to its item page and page image.
This keeps mandated tool #6 and #7 (the LoC bridge) genuinely in use; it is a path change, not a skip.

## Risk registered for Stage 1 (must be resolved there, honestly)

Chronicling America's coverage is **state-by-state and mostly pre-1963**, and West Virginia's contribution is
patchy. It is therefore **not guaranteed** that a December-1945 Fayetteville/West Virginia page reporting the
fire exists in that collection. Stage 1 will:
1. query the LoC newspaper paths for `sodder`, `Fayetteville`, `West Virginia` titles and 1945–1968 dates;
2. record exactly what was found or not found — no invention, no substitution of a modern article for a period one;
3. if period newspaper pages are unavailable, fall back to keyless archival sources that do hold them
   (Archive.org texts/newspapers, Wikimedia Commons, state archives) and mark tool #6 as
   `used — collection reachable, no on-topic period page` or `failed` in the manifest, with the reason.

## Bug found in my own probe (fixed in this stage)

The endpoint loop used `except urllib.error.HTTPError` followed by `except Exception`, so an `HTTPError`
whose code was **not** a redirect fell out of both handlers and the endpoint was **never written to the
report**. Two of nine endpoints were missing from run 40892200170's `smoke.json`, and the run still printed
`PASS` — a report that lies by omission. Fixed: the probe now always records every endpoint, follows
redirects explicitly, and prints each result as it goes. This is exactly the failure mode rule 2 forbids,
so it is recorded here rather than quietly patched.

---

# Addendum 2 — model weight availability verified keyless (this decides stages S3/S4)

Probed from the orchestration environment against `huggingface.co`, no token, no account:

| model id | `api/models` | `resolve/main` | verdict |
|---|---|---|---|
| `suno-ai/bark` | 401 | 401 | **gated — unusable keyless** |
| `suno/bark` | **200** | **200** | **USABLE keyless — this is the id Bark must be pointed at** |
| `suno-ai/bark-small` | 401 | 401 | gated |
| `silma-ai/silma-tts` | **200** (`gated: false`, `model.pt` listed, licence tag `apache-2.0`) | — | **USABLE keyless** — mandated tool #15 is safe |
| `onnx-community/Kokoro-82M-v1.0-ONNX` | 200 | — | usable keyless, but only a fallback: per rule 8 the main narrator is the agent's own voice |
| `hexgrad/Kokoro-82M-v1.0` | 401 | — | gated |

Two conclusions that change the plan for the better:
1. Mandated tool #16 (Bark) stays in the pipeline — it only needs the correct public checkpoint id
   (`suno/bark`, set through `CHECKPOINTS_DIR` / `XDG_CACHE_HOME` + `suno/bark` in the hub config).
   If that path fails at run time, the documented fallback for whispers/sighs is Chatterbox (#14, MIT)
   driven with high exaggeration and low volume plus a Pedalboard breath chain — no third tool needed.
2. Mandated tool #15 (SILMA TTS) is confirmed downloadable with no account, so the English document and
   letter readings are not at risk.

# Addendum 3 — final S0 gate: PASS

Run `40894013547`, commit `3ea1a48`, workflow `tc01-smoke`, dispatched with `workflow_dispatch` over the API.
All 10 endpoints recorded (none dropped), zero hard failures, zero missing ffmpeg filters, manifest policy
verdict PASS with 0 removed tools lacking a substitute. `workflow_dispatch` permission on the token is
therefore confirmed working, and the whole S1..S12 execution path is proven end to end:
push -> dispatch -> runner -> apt toolchain -> stage script -> artefact -> download.
