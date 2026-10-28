# Cinematic history-map renderer

A frame-accurate experimental film engine using **Remotion**, **Three.js / React Three Fiber**, **d3-geo**, **Turf** and the **Natural Earth** country data distributed with world-atlas. The map is a graded NASA satellite/topography/bathymetry composite. It is a modern reference backdrop; highlights do **not** depict 16th-century political borders.

This is an original, work-in-progress renderer, not a copy of any reference video's imagery, narration, score or edit. The supplied `HistoryMapPreview` composition uses only public-safe sample graphics. `HistoryMapFull` is 120 seconds, 1920×1080, 24 fps and additionally expects the original project's privately supplied audio, captions and transparent illustrations under `public/private/`. That directory is git-ignored and is **not** published here.

## Manual public-safe smoke test

```sh
npm ci
npm test
npx remotion browser ensure
npx remotion still src/index.ts HistoryMapPreview output/map-frame.png --frame=48 --gl=swangle --scale=0.75
npx remotion render src/index.ts HistoryMapPreview output/map-smoke.mp4 --frames=0-47 --gl=swangle --scale=0.5 --concurrency=1
```

The `Test 3D map engine` workflow runs this test on `workflow_dispatch`. It renders a small generic sample, **not** the final film. A GPU is not assumed; the software OpenGL backend is slower. Check the workflow result and inspect its artifact before claiming that rendering succeeded.

## Project input contract (not checked in)

`public/private/` must contain `narration_and_score.m4a`, `subtitles.json`, and PNG illustrations named `victoria`, `magellan`, `elcano`, `lapulapu`, `mutiny`, `wreck`, `scarcity`, `spice`, and `canoe`. The JSON is an array of `{from,to,text}` times in seconds. Ensure any mechanism used to supply these assets and retrieve the finished film respects their confidentiality. Public-repository workflow artifacts can be visible to others: do not upload private media as an unencrypted artifact.

## Attribution and editorial notes

- NASA Blue Marble / GIBS, modern imagery: <https://science.nasa.gov/earth/earth-observatory/blue-marble-next-generation/base-topography-bathymetry/>
- Natural Earth, modern reference geography: <https://www.naturalearthdata.com/about/terms-of-use/>
- Anton and Lato typefaces are distributed under the SIL Open Font License, included with the fonts.
- Route timing and shape are schematic editorial approximations. Trinidad attempted its eastward route later, after repairs; the dashed coral arrow is illustrative.
- The Cross of Burgundy and Portuguese banner in code are simplified editorial illustrations, not claims of an exact documented ship ensign. AI-generated people and vessels are illustrations, not authenticated likenesses.
- Remotion has separate license terms; review <https://www.remotion.dev/docs/license> for the intended use.

The optional `grade_map.py` accepts a NASA Mercator JPEG and a Natural Earth GeoJSON as explicit command-line inputs; it requires Python with Pillow and NumPy. A pre-graded public-domain texture is included so the demo needs no private files.
