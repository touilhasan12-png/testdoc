# testdoc — 16:9 long-form map documentary, sample

Remotion project for the first 5 minutes (300 s = 9000 frames @ 30 fps, 1920x1080) of the approved Tokyo script.

- `src/` — Remotion compositions, scenes, prefecture map (from `@svg-maps/japan`), timing.
- `assets/vo/` — VO 01–09 only (voice-01). VO 10–14 are intentionally not included in this sample.
- `src/data/vo-cues.json` — VO start offsets from SAMPLE-BOUNDARY.md.
- `src/data/sfx-events.json` — SFX event times aligned to the visual beats.
- `scripts/make-audio.mjs` — generates the Dm-Bb-C-Am pad (peak 0.066) and SFX bed.
- `scripts/assemble-sample.sh` — stream-copy concat of frame chunks, audio mix, verification.
- `.github/workflows/render-sample.yml` — manual workflow: 6 parallel render chunks, then assemble + verify.

Run: Actions → render-sample → Run workflow. Artifact: `testdoc-sample-300s`.
