// Build-time helper: derives prefecture bounding-box centres from the bundled
// @svg-maps/japan paths, so every overlay is placed on the real prefecture geometry.
import { createRequire } from 'node:module';
import { writeFileSync } from 'node:fs';
const require = createRequire(import.meta.url);
const bbox = require('svg-path-bbox').svgPathBbox;
const japan = (await import('@svg-maps/japan')).default;
const out = {};
for (const loc of japan.locations) {
  const [x1, y1, x2, y2] = bbox(loc.path);
  out[loc.id] = { name: loc.name, cx: +((x1 + x2) / 2).toFixed(2), cy: +((y1 + y2) / 2).toFixed(2), w: +(x2 - x1).toFixed(2), h: +(y2 - y1).toFixed(2) };
}
writeFileSync('src/data/japan-centroids.json', JSON.stringify(out, null, 1));
console.log('prefectures:', Object.keys(out).length, 'tokyo:', out.tokyo, 'okinawa:', out.okinawa);
