import React from 'react';
import {Cam, H, Region, W, curvePath, curvePt, eo3, mercY, planeHalfExtents, planePt, prog, clamp01} from '../lib/core';
import {useStage} from '../lib/ctx';

// cached unit-mercator coordinates per region
const cache = new Map<Region, {u: Float64Array; v: Float64Array; off: number[]; bb: number[][]}>();
const unit = (r: Region) => {
  let c = cache.get(r);
  if (c) return c;
  const pts: number[][] = r.rings.flat();
  const u = new Float64Array(pts.length);
  const v = new Float64Array(pts.length);
  const off: number[] = [];
  const bb: number[][] = [];
  let k = 0;
  for (const ring of r.rings) {
    off.push(k);
    let x0 = 9, x1 = -9, y0 = 9, y1 = -9;
    for (const [lon, lat] of ring) {
      u[k] = (lon + 180) / 360;
      v[k] = mercY(lat);
      x0 = Math.min(x0, u[k]); x1 = Math.max(x1, u[k]); y0 = Math.min(y0, v[k]); y1 = Math.max(y1, v[k]);
      k++;
    }
    bb.push([x0, x1, y0, y1]);
  }
  off.push(k);
  c = {u, v, off, bb};
  cache.set(r, c);
  return c;
};

export const regionPath = (cam: Cam, r: Region): string => {
  const c = unit(r);
  const S = 256 * 2 ** cam.z;
  const cu = (cam.lon + 180) / 360;
  const cv = mercY(cam.lat);
  const [hx, hy] = planeHalfExtents(cam.pitch, cam.bearing);
  let d = '';
  for (let i = 0; i < r.rings.length; i++) {
    const [x0, x1, y0, y1] = c.bb[i];
    const sx0 = W / 2 + (x0 - cu) * S, sx1 = W / 2 + (x1 - cu) * S;
    const sy0 = H / 2 + (y0 - cv) * S, sy1 = H / 2 + (y1 - cv) * S;
    if (sx1 < W / 2 - hx || sx0 > W / 2 + hx || sy1 < H / 2 - hy || sy0 > H / 2 + hy) continue;
    for (let k = c.off[i]; k < c.off[i + 1]; k++) {
      const x = W / 2 + (c.u[k] - cu) * S;
      const y = H / 2 + (c.v[k] - cv) * S;
      d += (k === c.off[i] ? 'M' : 'L') + x.toFixed(1) + ' ' + y.toFixed(1);
    }
    d += 'Z';
  }
  return d;
};

export const PlaneSvg: React.FC<{children: React.ReactNode}> = ({children}) => (
  <svg width={W} height={H} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
    {children}
  </svg>
);

export type RegionStyle = {fill?: string; opacity?: number; stroke?: string; strokeOpacity?: number; strokeWidth?: number} | null;

export const RegionLayer: React.FC<{regions: Region[]; style: (r: Region, i: number) => RegionStyle}> = ({regions, style}) => {
  const {cam} = useStage();
  return (
    <>
      {regions.map((r, i) => {
        const s = style(r, i);
        if (!s) return null;
        const d = regionPath(cam, r);
        if (!d) return null;
        return (
          <path
            key={r.name}
            d={d}
            fill={s.fill ?? 'none'}
            fillOpacity={s.opacity ?? 0.5}
            stroke={s.stroke ?? 'none'}
            strokeOpacity={s.strokeOpacity ?? 0.6}
            strokeWidth={s.strokeWidth ?? 1.4}
            strokeLinejoin="round"
          />
        );
      })}
    </>
  );
};

export type ArrowSpec = {a: [number, number]; b: [number, number]; curv?: number; delay?: number; color?: string; width?: number; n?: number; speed?: number};

/** Curved flow arrows with travelling particles. Draws from f0; fades out before f1. */
export const Arrows: React.FC<{specs: ArrowSpec[]; f0: number; f1: number; dur?: number; head?: boolean}> = ({specs, f0, f1, dur = 34, head = true}) => {
  const {cam, frame} = useStage();
  if (frame < f0 || frame > f1) return null;
  const fade = 1 - prog(frame, f1 - 14, f1);
  return (
    <g opacity={fade}>
      {specs.map((s, i) => {
        const a = planePt(cam, s.a[0], s.a[1]);
        const b = planePt(cam, s.b[0], s.b[1]);
        const curv = s.curv ?? 0.18;
        const p = eo3(prog(frame, f0 + (s.delay ?? 0), f0 + (s.delay ?? 0) + dur));
        if (p <= 0.001) return null;
        const col = s.color ?? '#8ec9ff';
        const w = s.width ?? 3.5;
        const parts: React.ReactNode[] = [];
        const n = s.n ?? 3;
        for (let k = 0; k < n; k++) {
          const u = (((frame - f0) * (s.speed ?? 0.012) + k / n) % 1) * p;
          const [x, y] = curvePt(a, b, curv, u);
          parts.push(<circle key={k} cx={x} cy={y} r={w * 1.35} fill="#fff" opacity={0.95} />);
        }
        const [hx, hy] = curvePt(a, b, curv, p);
        const [px, py] = curvePt(a, b, curv, Math.max(0, p - 0.03));
        const ang = (Math.atan2(hy - py, hx - px) * 180) / Math.PI;
        return (
          <g key={i} style={{filter: `drop-shadow(0 0 5px ${col})`}}>
            <path d={curvePath(a, b, curv)} fill="none" stroke={col} strokeWidth={w} strokeLinecap="round" pathLength={1} strokeDasharray={`${p} 2`} opacity={0.9} />
            {parts}
            {head ? <polygon points={`0,${-w * 2.6} ${w * 4.4},0 0,${w * 2.6}`} fill={col} transform={`translate(${hx} ${hy}) rotate(${ang})`} /> : null}
          </g>
        );
      })}
    </g>
  );
};

export const DottedRing: React.FC<{lon: number; lat: number; r: number; color?: string; opacity?: number; label?: string; spin?: number}> = ({lon, lat, r, color = '#ffe78a', opacity = 1, spin = 0}) => {
  const {cam} = useStage();
  const [x, y] = planePt(cam, lon, lat);
  return (
    <g opacity={opacity} transform={`translate(${x} ${y})`} style={{filter: `drop-shadow(0 0 10px ${color})`}}>
      <circle r={r} fill={`${color}18`} stroke={color} strokeWidth={4} strokeDasharray="5 11" transform={`rotate(${spin})`} />
    </g>
  );
};

export const BlackHole: React.FC<{lon: number; lat: number; R: number; p: number; frame: number}> = ({lon, lat, R, p, frame}) => {
  const {cam} = useStage();
  if (p <= 0.001) return null;
  const [x, y] = planePt(cam, lon, lat);
  const r = R * eo3(clamp01(p));
  return (
    <g transform={`translate(${x} ${y})`} opacity={clamp01(p * 1.4)}>
      <defs>
        <radialGradient id="bhg" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#000" stopOpacity="0.95" />
          <stop offset="45%" stopColor="#10040a" stopOpacity="0.85" />
          <stop offset="62%" stopColor="#ff5a3c" stopOpacity="0.55" />
          <stop offset="78%" stopColor="#ff2a4a" stopOpacity="0.22" />
          <stop offset="100%" stopColor="#ff2a4a" stopOpacity="0" />
        </radialGradient>
      </defs>
      <circle r={r * 2.1} fill="url(#bhg)" />
      <circle r={r * 1.25} fill="none" stroke="#ffb27a" strokeWidth={5} strokeDasharray="60 38" transform={`rotate(${frame * 0.5})`} opacity={0.8} />
      <circle r={r * 1.6} fill="none" stroke="#ff6a5a" strokeWidth={3.5} strokeDasharray="22 44" transform={`rotate(${-frame * 0.35})`} opacity={0.75} />
      <circle r={r * 0.92} fill="#000" style={{filter: 'drop-shadow(0 0 18px rgba(255,90,60,.9))'}} />
    </g>
  );
};
