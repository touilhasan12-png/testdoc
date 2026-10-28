# Tool-use audit — V5 design test

This ledger distinguishes actual project output from installation. The film is a 15-second pilot only. Verification of the final video is recorded separately after rendering.

| Requested tool or data | Actual use in the pilot | Evidence / limitation |
|---|---|---|
| Apache ECharts | Rendered five-vessel and one-completing-vessel SVG pictograms used in the fleet comparison. | `scripts/build-chart.mjs`; `public/generated/fleet-*.svg`. |
| Three.js | Perspective map, geometry, sphere, projection, 3D overlays and materials. | `src/MapView.tsx`, `src/GlobeView.tsx`. |
| React Three Fiber / drei | Scene composition, geographic lines and GLB loading. | `MapView.tsx`, `GlobeView.tsx`, `PortraitView.tsx`. |
| React Three postprocessing | Bloom/optical grade applied to the map. Initial normal composer rendering produced a black map; explicit delayed per-frame rendering fixed the tested stills and a 31-frame continuity test. | `src/ManualEffects.tsx`; software WebGL, no GPU. |
| Remotion | Frame-accurate timing, scene composition and pilot rendering on GitHub Actions. | `src/Story.tsx`; `.github/workflows/v5-pilot.yml`. |
| Manim | Rendered a 71-frame transparent animated orbit used in the circumnavigation shot. | `scripts/compass_manim.py`; private frame sequence. |
| Blender | Imported geography and TripoSR output; produced a geographic GLB and inspection renders in Blender 4.0.2. The first coarse ship reconstruction was rejected visually. | Encrypted job logs and output; GIS GLB appears in the map. |
| TripoSR | Two real CPU inference attempts. The first mesh reconstructed an unwanted slab and was rejected; the second used the rembg alpha and produced a recognizable but coarse 4,457-vertex ship. It is reoriented and used only as a small route marker, not as the hero artwork. | `scripts/triposr_cpu.py`; second mesh inspected in two R3F views. CPU marching cubes uses a documented scikit-image shim. The second automated Blender preview failed due to missing NumPy; the local R3F inspection succeeded. |
| Natural Earth | World-atlas's 1:110m countries and a BlenderGIS 1:50m import. | Derived data and `blendergis_layer.py`. |
| Historical Basemaps | 1500 Castille, Aragón and Portugal overlays rendered in the Iberian map, simplified with mapshaper. | GPL-3.0 source and license in `data/`; not a verified 1519 boundary map. |
| d3-geo / world-atlas | Geodesic first-leg interpolation, spherical containment checks, and globe country shapes. | `scripts/build-geodata.mjs`, `scripts/check-story.mjs`, `GlobeView.tsx`. |
| flag-icons | Used the Spain icon's field and 4:3 geometry as the base for an illustrative historical Burgundian-cross repaint. The modern flag is not used as a 1519 flag. | `scripts/build-flag.mjs`, `generated/castilian-standard.svg`. |
| flubber | Morphs the fleet count 5 into 1; labels are separated in time to avoid overlap. | `src/Story.tsx`. |
| Turf | Calculated cumulative approximate route distance and equally spaced route samples on the sphere. | `scripts/build-geodata.mjs`. |
| mapshaper | Filtered and simplified the three historical regions and the Natural Earth Iberian shapefile used by BlenderGIS. | `build-geodata.mjs`, `run_carto_manim.sh`. |
| three-globe | Constructed a textured 3D globe and country outlines; route is drawn along its surface. | `src/GlobeView.tsx`. |
| BlenderGIS | Imported actual Natural Earth country shapefile, created an extruded/georeferenced Iberian layer and exported GLB; that layer is registered onto the map. | `scripts/blendergis_layer.py`, private GLB. |
| rembg | Segmented both the ship and portrait. | `scripts/preprocess.py`, encrypted preprocessing output. |
| Depth Anything V2 | CPU quantized-ONNX inference produced relative portrait depth; used for the 3D displacement/parallax portrait. | `scripts/preprocess.py`, `src/PortraitView.tsx`. Not measured physical depth. |
| Real-ESRGAN | CPU tiled x4v3 ONNX enhancement produced a 2816×1536 portrait, which is used in the parallax shot. | `scripts/preprocess.py`, encrypted output. |
| faster-whisper / stable-ts | CPU transcription and refined word timestamps for the pilot; cues checked against the English audio. | Encrypted word-time JSON. Initial attempt failed on missing ffmpeg/CUDA-linked torchaudio; CPU wheel and ffmpeg fixed it. |
| micromamba | Created and ran separate CPU Python environments for preprocessing and TripoSR inference. | `run_preprocess.sh`, `run_triposr.sh`, encrypted logs. |

Public GitHub Actions standard runners have no GPU; all described AI and graphics jobs ran on CPU. The source and intermediate logs do not imply that a complete two-minute film has been made or approved.
