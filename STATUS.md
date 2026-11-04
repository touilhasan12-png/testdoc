# STATUS — Tokyo 300 s sample
Updated: 2026-11-04 (local)

- Code complete (Remotion 4.0.540, TypeScript): 33 shots, 72 items, ~168 kickers + beats; GSI tiles/geo data/paper/photos in repo.
- Audio: `scripts/build_audio.py` (VO 01–09 verbatim, Dm–Bb–C–Am pad peak 0.066, 232 SFX events).
- Gate scripts: `scripts/make_shot_usage.py` → `SHOT-USAGE.md`; `scripts/verify_video.py` (post-render).
- Workflow `render-sample.yml`: mode `stills` (QA frames) or `full` (10 × 900-frame chunks, mux, verify).
- Next: push → stills run → fix visual issues → full render → verify → report.
- No render has been produced yet. No token is stored anywhere in this repo.
