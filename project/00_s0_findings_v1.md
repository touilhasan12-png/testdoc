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
