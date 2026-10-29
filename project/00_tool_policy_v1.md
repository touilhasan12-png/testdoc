# TOOL POLICY v1 — TrueCrime_Sample_01 (THE SODDER CHILDREN)

Owner instruction received 2026-10-29, applied immediately and permanently for this project:

1. The repository `touilhasan12-png/testdoc` stays PUBLIC. No token, key, secret or credential is ever
   committed, printed, logged or uploaded. `.gitignore` and `.secrets/` enforce this.
2. REMOVE every tool whose licence is non-commercial, all-rights-reserved, source-available-with-a-paid-tier,
   or whose models/weights carry non-commercial terms.
3. REMOVE every tool that needs an API key / token / account to function.
4. Where a removed tool has a keyless, commercially-clean substitute, the agent (or a clean tool) becomes
   the substitute. Where no clean substitute exists, the tool is dropped and recorded as SKIPPED.
5. No output of a skipped or removed tool is ever faked or claimed.

---

## A. REMOVED — non-commercial / all-rights-reserved / paid-tier licences

| # | Tool | Why removed | Substitute (commercial-clean, keyless) |
|---|---|---|---|
| 18 | Stable Audio Open (`Stability-AI/stable-audio-tools`) | model weights gated on HuggingFace and require licence acceptance; effectively an account/key gate | `tc01/lib/synth_bed.py` — deterministic numpy score bed (drone, pulse, string pad) rendered to WAV, plus `Pedalboard` for space. Fully owned, fully clean |
| 35 | Meshroom (`alicevision/Meshroom`) | pretrained models are non-commercial | **COLMAP** (`colmap/colmap`, BSD-3-Clause) — fully open, CPU-capable CLI (`feature_extractor`, `exhaustive_matcher`, `mapper`, `model_converter`) |
| 37 | GFPGAN (`TencentARC/GFPGAN`) | model weights restricted to non-commercial use | `IOPaint` (#40, Apache-2.0, kept) face/defect cleanup + FFmpeg `hqdn3d`/`unsharp`/`cas` detail recovery. Order becomes: IOPaint -> upscale -> colourise |
| 38 | Real-ESRGAN (`xinntao/Real-ESRGAN`) | README restricts the pretrained models to non-commercial use | FFmpeg `scale=...:flags=lanczos` two-step upscale + `unsharp` + `cas` (zero licence risk, zero download) |
| 45 | Remotion (`remotion-dev/remotion`) | source-available; a paid licence is required for companies with 4+ staff | **Motion Canvas** (`motion-canvas/motion-canvas`, MIT) if a Node render is needed, otherwise FFmpeg `drawtext`/`overlay`/`fade` title builds. Default: FFmpeg titles |
| 49 | deep-analog (`EtonMu/deep-analog`) | "All Rights Reserved", patent pending | `tc01/lib/lut_from_reference.py` — extracts the look of a reference still (per-channel tone curves + hue/sat map + grain + halation) and writes a `.cube` 3D LUT applied with FFmpeg `lut3d`. Agent-authored, fully owned |

## B. REMOVED — requires an API key / token / account

| # | Tool | Key it needed | Substitute (keyless) |
|---|---|---|---|
| 20 | Freesound + `MTG/freesound-python` | Freesound `client_id` + `client_secret` | Wikimedia Commons audio (CC0/PD, keyless API) + Archive.org audio + `tc01/lib/synth_sfx.py` procedural SFX (fire crackle, wind, rain, phone ring, radio static, footsteps, door, clock) |
| 21 | `johnkimdw/freesound-mcp-server` | same Freesound key | dropped with #20; the same procedural + Commons path covers it |
| 30 | Mapillary (`mapillary/mapillary_tools`) | Mapillary API token | Wikimedia Commons geolocated photographs (`generator=search` + `prop=coordinates`, keyless) and Archive.org stills; labelled "Archival photo" |
| 50 | CinegradeAI (`Mohit485/CinegradeAI`) | Google Gemini API key | `tc01/stages/s12/grade_report.py` — per-scene analysis from FFmpeg `signalstats`/`histogram` (YMIN/YAVG/YMAX, saturation, contrast) emitted as a grading-suggestions report the agent applies |
| 11 | STORYMACHINE | n/a — repository does not exist | Already recorded as NOT FOUND. Substitute: `tc01/stages/s02/diagnose.py` — agent-authored screenplay diagnostic (structure, causality, pacing, continuity, claim-to-source coverage) |

## C. KEPT BUT RUN IN KEYLESS MODE (no removal needed)

| # | Tool | Keyless mode |
|---|---|---|
| 3 | SpiderFoot | only keyless modules enabled (DNS, WHOIS, hosts, neighbours); key modules disabled and reported |
| 8 | Newspaper-OCR-V3 | Tesseract path only; the Google Vision path is disabled |
| 9 | ai-screenplay-writer | its multi-agent graph is followed as a methodology; the agent itself is the LLM, so no external LLM key |
| 28 | kepler.gl | no Mapbox token: dark keyless basemap (CARTO dark_matter tiles, attribution-only) or a token-free custom style; if headless render fails -> `tc01/lib/geo_render.py` draws animated paths over the same dark tiles with Pillow/ffmpeg |
| 42 | broll-fetcher | Pexels/Pixabay disabled; Wikimedia Commons + Openverse + Archive.org paths only (all keyless) |

## D. KEPT AS FOUND — commercially clean and keyless (39 tools)

1 awesome-osint · 2 Maigret · 3 SpiderFoot* · 4 bellingcat/toolkit · 5 Auto-Archiver · 6 Chronicling America ·
7 loc-mcp-server · 8 Newspaper-OCR-V3* · 9 ai-screenplay-writer* · 10 writers-room-story-engine ·
12 scriptbreak · 13 SceneFlow · 14 Chatterbox · 15 SILMA TTS · 16 Bark · 17 ACE-Step 1.5 · 19 MMAudio ·
22 Demucs · 23 Pedalboard (GPL — run as a separate process) · 24 awesome-music-prompts · 25 ScanOld ·
26 text-to-handwriting · 27 synthetic-manuscript-generator · 28 kepler.gl* · 29 QGIS (GPL — run as a
separate process) · 31 TimelineJS3 · 32 RAWGraphs · 33 caseboard · 34 osint-social-graph-agent ·
36 AI-Forensics-3D-Reconstruction · 39 DeOldify · 40 IOPaint · 41 OpenMontage (AGPL — separate process) ·
42 broll-fetcher* · 43 FFmpeg · 44 kburns-slideshow · 46 auto-editor · 47 pyCapCut · 48 ChromaShift

`*` = keyless mode as described in section C.

## E. Copyleft notes that survive this policy

GPL/LGPL/AGPL/MPL are commercial-safe but viral. `Pedalboard`, `QGIS`, `OpenMontage` and `FFmpeg` are run as
**separate processes over files**, never linked into anything delivered, so the delivered video and the
CapCut draft carry no copyleft obligation. Recorded in `manifest.md` and `CREDITS.md`.

## F. Net effect on the mandate

- 50 mandated tools: **39 kept as found**, **5 kept in keyless mode**, **11 removed** (6 licence + 4 key + 1 non-existent), **11 agent/clean substitutes** supplied.
- Every removal and every substitute is logged in `manifest.md` with its reason, and reported in Arabic at the end of each stage.
