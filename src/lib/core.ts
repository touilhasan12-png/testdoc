import timeline from '../data/timeline.json';
import manifestJson from '../data/tile-manifest.json';
import prefData from '../data/prefectures.json';
import wardData from '../data/wards.json';

// ---------- constants
export const W = 1920;
export const H = 1080;
export const D = 2000; // CSS perspective distance (px)
export const FPS = 30;
export const TOTAL = 9000;

// ---------- animation helpers (pure, deterministic)
export const clamp01 = (x: number) => Math.max(0, Math.min(1, x));
export const prog = (f: number, a: number, b: number) => clamp01((f - a) / (b - a));
export const eo3 = (t: number) => 1 - Math.pow(1 - t, 3);
export const eo4 = (t: number) => 1 - Math.pow(1 - t, 4);
export const ei3 = (t: number) => t * t * t;
export const eio = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
export const fmt = (n: number) => Math.round(n).toLocaleString('en-US');
export const mulberry32 = (seed: number) => {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
};

// ---------- timeline items
export type Item = {f0: number; f1: number; sfx: string};
export const ITEMS = timeline.items as Record<string, Item>;
export const item = (id: string): Item => {
  const it = ITEMS[id];
  if (!it) throw new Error('unknown item ' + id);
  return it;
};
/** visibility 0..1 with entry/exit ramps (frames) */
export const life = (f: number, id: string, inD = 10, outD = 12) => {
  const it = item(id);
  if (f < it.f0 || f > it.f1) return 0;
  return Math.min(prog(f, it.f0, it.f0 + inD), 1 - prog(f, it.f1 - outD, it.f1));
};
export const on = (f: number, id: string) => {
  const it = item(id);
  return f >= it.f0 && f <= it.f1;
};

// ---------- camera
export type Cam = {lon: number; lat: number; z: number; pitch: number; bearing: number};
type Shot = {id: string; f0: number; f1: number; keys: number[][]; src: string};
export const SHOTS = timeline.shots as Shot[];

const pchip = (ts: number[], ys: number[], t: number) => {
  const n = ts.length;
  if (t <= ts[0]) return ys[0];
  if (t >= ts[n - 1]) return ys[n - 1];
  const h: number[] = [];
  const d: number[] = [];
  for (let i = 0; i < n - 1; i++) {
    h.push(ts[i + 1] - ts[i]);
    d.push((ys[i + 1] - ys[i]) / h[i]);
  }
  const m = new Array(n).fill(0);
  for (let i = 1; i < n - 1; i++) {
    if (d[i - 1] * d[i] <= 0) m[i] = 0;
    else {
      const w1 = 2 * h[i] + h[i - 1];
      const w2 = h[i] + 2 * h[i - 1];
      m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i]);
    }
  }
  let i = 0;
  while (i < n - 2 && t > ts[i + 1]) i++;
  const x = (t - ts[i]) / h[i];
  const h00 = 2 * x ** 3 - 3 * x ** 2 + 1;
  const h10 = x ** 3 - 2 * x ** 2 + x;
  const h01 = -2 * x ** 3 + 3 * x ** 2;
  const h11 = x ** 3 - x ** 2;
  return h00 * ys[i] + h10 * h[i] * m[i] + h01 * ys[i + 1] + h11 * h[i] * m[i + 1];
};

export const shotAt = (f: number): Shot => {
  for (const s of SHOTS) if (f >= s.f0 && f < s.f1) return s;
  return SHOTS[SHOTS.length - 1];
};
export const camOf = (s: Shot, f: number): Cam => {
  const ts = s.keys.map((k) => k[0]);
  const g = (j: number) => pchip(ts, s.keys.map((k) => k[j]), f);
  return {lon: g(1), lat: g(2), z: g(3), pitch: g(4), bearing: g(5)};
};
export const camAt = (f: number): Cam => camOf(shotAt(f), f);

// ---------- projection
export const mercY = (lat: number) => (1 - Math.asinh(Math.tan((lat * Math.PI) / 180)) / Math.PI) / 2;
export const worldPx = (lon: number, lat: number, z: number): [number, number] => {
  const s = 256 * 2 ** z;
  return [((lon + 180) / 360) * s, mercY(lat) * s];
};
/** plane (pre-tilt) pixel coordinates; the camera centre maps to (W/2,H/2) */
export const planePt = (cam: Cam, lon: number, lat: number): [number, number] => {
  const [x, y] = worldPx(lon, lat, cam.z);
  const [cx, cy] = worldPx(cam.lon, cam.lat, cam.z);
  return [W / 2 + x - cx, H / 2 + y - cy];
};
/** true screen position after CSS rotateX(pitch) rotateZ(bearing) + perspective(D) */
export const toScreen = (cam: Cam, lon: number, lat: number): [number, number, number] => {
  const [px, py] = planePt(cam, lon, lat);
  const x = px - W / 2;
  const y = py - H / 2;
  const b = (cam.bearing * Math.PI) / 180;
  const a = (cam.pitch * Math.PI) / 180;
  const x1 = x * Math.cos(b) - y * Math.sin(b);
  const y1 = x * Math.sin(b) + y * Math.cos(b);
  const y2 = y1 * Math.cos(a);
  const z2 = y1 * Math.sin(a);
  const s = D / (D - z2);
  return [W / 2 + x1 * s, H / 2 + y2 * s, s];
};
export const planeHalfExtents = (pitch: number, bearing: number): [number, number] => {
  const a = (pitch * Math.PI) / 180;
  const b = (bearing * Math.PI) / 180;
  const eyTop = ((H / 2) * D) / (D * Math.cos(a) - (H / 2) * Math.sin(a));
  const eyBot = ((H / 2) * D) / (D * Math.cos(a) + (H / 2) * Math.sin(a));
  const sFar = D / (D + eyTop * Math.sin(a));
  const ex = W / 2 / sFar;
  const ey = Math.max(eyTop, eyBot);
  const hx = Math.abs(Math.cos(b)) * ex + Math.abs(Math.sin(b)) * ey;
  const hy = Math.abs(Math.sin(b)) * ex + Math.abs(Math.cos(b)) * ey;
  return [hx + 48, hy + 48];
};
export const levelFor = (z: number) => Math.max(2, Math.min(18, Math.floor(z + 0.2)));

// ---------- tiles
export const TILE_SET = new Set<string>(
  Object.entries((manifestJson as {tiles: Record<string, string[]>}).tiles).flatMap(([z, arr]) => arr.map((s) => `${z}/${s}`))
);

// ---------- geodata
export type Region = {name: string; rings: number[][][]; c: [number, number]; iso?: string};
export const PREFS = prefData as unknown as Region[];
export const WARDS = wardData as unknown as Region[];
export const pref = (n: string) => {
  const p = PREFS.find((x) => x.name === n);
  if (!p) throw new Error('pref ' + n);
  return p;
};
export const TOKYO: [number, number] = [139.7, 35.69];
export const SHINJUKU: [number, number] = [139.703, 35.6905];
export const FLAGGED_16 = [
  'Shinjuku', 'Shibuya', 'Toshima', 'Bunkyo', 'Taito', 'Sumida', 'Shinagawa', 'Meguro',
  'Ota', 'Setagaya', 'Nakano', 'Suginami', 'Kita', 'Arakawa', 'Itabashi', 'Nerima',
];

// ---------- scale bar
export const metersPerPx = (cam: Cam) => (156543.03392 * Math.cos((cam.lat * Math.PI) / 180)) / 2 ** cam.z;

// ---------- curved flow paths (plane pixels)
export const curvePt = (a: [number, number], b: [number, number], curv: number, t: number): [number, number] => {
  const mx = (a[0] + b[0]) / 2;
  const my = (a[1] + b[1]) / 2;
  const dx = b[0] - a[0];
  const dy = b[1] - a[1];
  const cx = mx - dy * curv;
  const cy = my + dx * curv;
  const u = 1 - t;
  return [u * u * a[0] + 2 * u * t * cx + t * t * b[0], u * u * a[1] + 2 * u * t * cy + t * t * b[1]];
};
export const curvePath = (a: [number, number], b: [number, number], curv: number) => {
  const mx = (a[0] + b[0]) / 2;
  const my = (a[1] + b[1]) / 2;
  const cx = mx - (b[1] - a[1]) * curv;
  const cy = my + (b[0] - a[0]) * curv;
  return `M ${a[0].toFixed(1)} ${a[1].toFixed(1)} Q ${cx.toFixed(1)} ${cy.toFixed(1)} ${b[0].toFixed(1)} ${b[1].toFixed(1)}`;
};

/** same projection as toScreen but starting from plane pixels */
export const planeToScreen = (cam: Cam, px: number, py: number): [number, number, number] => {
  const x = px - W / 2;
  const y = py - H / 2;
  const b = (cam.bearing * Math.PI) / 180;
  const a = (cam.pitch * Math.PI) / 180;
  const x1 = x * Math.cos(b) - y * Math.sin(b);
  const y1 = x * Math.sin(b) + y * Math.cos(b);
  const y2 = y1 * Math.cos(a);
  const z2 = y1 * Math.sin(a);
  const s = D / (D - z2);
  return [W / 2 + x1 * s, H / 2 + y2 * s, s];
};
export const HOMETOWN: [number, number] = [140.1, 39.7];
