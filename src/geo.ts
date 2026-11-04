import {Easing, interpolate} from 'remotion';
import japan from '@svg-maps/japan';
import centroids from './data/japan-centroids.json';

export type Cam = {s: number; fx: number; fy: number};
export type Cen = {name: string; cx: number; cy: number; w: number; h: number};
export type Pt = {x: number; y: number};
export type Prefecture = {id: string; name: string; path: string};

// Base framing: whole archipelago centred on a 1920x1080 frame.
export const BASE: Cam = {s: 1.85, fx: 219, fy: 258};
export const HOME = {x: 960, y: 540};

export const CEN = centroids as unknown as Record<string, Cen>;
export const PREFS: Prefecture[] = (japan as unknown as {locations: Prefecture[]}).locations;
// Tokyo's bbox centre falls in the sea (the Izu islands stretch it south), so anchor on the mainland strip.
export const TOKYO = {...CEN.tokyo, cx: 306, cy: 248};
export const OKI = CEN.okinawa;

export const camTransform = (c: Cam): string =>
  `translate(${HOME.x} ${HOME.y}) scale(${c.s}) translate(${-c.fx} ${-c.fy})`;

export const toScreen = (c: Cam, x: number, y: number): Pt => ({
  x: HOME.x + (x - c.fx) * c.s,
  y: HOME.y + (y - c.fy) * c.s,
});

// Eased 0->1 (or custom range) ramp, clamped at both ends.
export const ease = (f: number, a: number, b: number, from = 0, to = 1): number =>
  interpolate(f, [a, b], [from, to], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.bezier(0.33, 0, 0.2, 1),
  });

// Camera path through keyframes [frame, camera].
export const camAt = (f: number, keys: Array<[number, Cam]>): Cam => {
  if (f <= keys[0][0]) return keys[0][1];
  for (let i = 0; i < keys.length - 1; i++) {
    const [f0, a] = keys[i];
    const [f1, b] = keys[i + 1];
    if (f <= f1) {
      const t = ease(f, f0, f1);
      return {s: a.s + (b.s - a.s) * t, fx: a.fx + (b.fx - a.fx) * t, fy: a.fy + (b.fy - a.fy) * t};
    }
  }
  return keys[keys.length - 1][1];
};

export type Arrow = {p0: Pt; c: Pt; p1: Pt};

// Schematic flow from a prefecture centroid into Tokyo (quadratic bezier).
export const arrow = (id: string): Arrow => {
  const p = CEN[id];
  const t = TOKYO;
  const dx = t.cx - p.cx;
  const dy = t.cy - p.cy;
  const len = Math.hypot(dx, dy);
  const nx = -dy / len;
  const ny = dx / len;
  const bend = len * 0.16;
  return {
    p0: {x: p.cx, y: p.cy},
    c: {x: (p.cx + t.cx) / 2 + nx * bend, y: (p.cy + t.cy) / 2 + ny * bend},
    p1: {x: t.cx, y: t.cy},
  };
};

export const bez = (g: Arrow, t: number): Pt => {
  const u = 1 - t;
  return {
    x: u * u * g.p0.x + 2 * u * t * g.c.x + t * t * g.p1.x,
    y: u * u * g.p0.y + 2 * u * t * g.c.y + t * t * g.p1.y,
  };
};

export const pathD = (g: Arrow): string =>
  `M${g.p0.x},${g.p0.y} Q${g.c.x},${g.c.y} ${g.p1.x},${g.p1.y}`;

// Seeded PRNG so every render frame sees the same random layout.
export const lcg = (seed: number) => () => {
  seed = (seed * 1664525 + 1013904223) >>> 0;
  return seed / 4294967296;
};
