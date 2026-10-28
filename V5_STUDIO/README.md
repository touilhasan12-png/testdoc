# Magellan–Elcano visual pilot (V5)

A 15-second, English, 1920×1080, 24 fps design test. This is a pilot for approval, **not** the requested two-minute finished film.

## Visual structure

* 0–7.5 s: true-perspective tilted map, Sanlúcar and departure, a large ship illustration, an animated fleet count and an approximate historical political overlay.
* 7.1–11.5 s: globe and progressively drawn approximate voyage track; an orbit drawn in Manim reinforces the global circuit.
* 11–15 s: illustrated portrait of Magellan with depth-based parallax. It is a fictionalized artistic interpretation, not a documented likeness.

Titles and transitions use measured word timings from faster-whisper and stable-ts. Timing is manually checked against the provided narration. Country shapes are modern geography plus **approximate 1500** political outlines; they are not a precise map of 1519 and should not be used for navigation. The 3D ship reconstructed by TripoSR is a low-poly route marker; the much more detailed hero ship is an image cutout. The standard is an illustrative Cross of Burgundy, not the modern red-yellow-red flag.

## Source and security

This repository contains code, public-domain/licensed map data, and derived public graphics only. User media, AI illustrations, audio, private word timing files, the private Blender/TripoSR outputs, and rendered video are deliberately absent from git. The GitHub Actions workflow obtains them through an OIDC-authenticated encrypted transfer; only encrypted render segments are uploaded. Never commit any credential, relay key, private input, or decrypted video to this public repository.

`npm ci && npm test` checks TypeScript and rough geographic constraints. `npm run build:geodata`, `npm run build:chart`, and `node scripts/build-flag.mjs` regenerate public map and graphic outputs. The graded NASA map was made with `scripts/grade_map.py` from the NASA SVS Blue Marble and its matching land mask, referenced in CREDITS.md. Private assets must be supplied separately under `public/private/` before rendering.

When approved, the full film requires its own narration-by-narration redesign, historical review, visual QA, and render; this pilot does not claim that work is complete.
