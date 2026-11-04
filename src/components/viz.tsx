import React from 'react';
import {spring} from 'remotion';
import {clamp01, eo3, fmt, lerp, mulberry32, prog} from '../lib/core';
import {C, FONT, GLOW, Label} from './ui';

const sp = (local: number, delay = 0, damping = 18, stiffness = 95) => spring({frame: Math.max(0, local - delay), fps: 30, config: {damping, stiffness}});

// ---------- card 07 form: big number + label
export const BigNumber: React.FC<{value: string; label: React.ReactNode; size?: number; color?: string; sub?: React.ReactNode; projection?: boolean}> = ({value, label, size = 150, color = C.cream, sub, projection}) => (
  <div style={{whiteSpace: 'nowrap'}}>
    <div style={{fontSize: size, fontWeight: 900, lineHeight: 0.95, letterSpacing: -size / 25, color}}>{value}</div>
    <div style={{marginTop: 22}}>
      <Label projection={projection}>{label}</Label>
    </div>
    {sub ? <div style={{marginTop: 12, fontSize: 24, fontWeight: 700, letterSpacing: 1.5, color: 'rgba(255,245,236,.85)', textTransform: 'uppercase'}}>{sub}</div> : null}
  </div>
);

// ---------- card 07 form: columns (solid = data, dotted = projection/scenario)
export type Col = {label: string; value: number; text: string; color?: string; dotted?: boolean; sub?: string};
export const Columns: React.FC<{local: number; title: React.ReactNode; cols: Col[]; max: number; height?: number; colW?: number; gap?: number; projection?: boolean}> = ({local, title, cols, max, height = 240, colW = 150, gap = 64, projection}) => (
  <div style={{width: cols.length * (colW + gap) + 40}}>
    <Label projection={projection}>{title}</Label>
    <div style={{height: height + 110, display: 'flex', alignItems: 'flex-end', gap, borderBottom: '2px solid rgba(255,255,255,.55)', padding: '0 34px', marginTop: 20}}>
      {cols.map((c, i) => {
        const g = sp(local, i * 8);
        const col = c.color ?? '#ff766e';
        return (
          <div key={i} style={{width: colW, textAlign: 'center'}}>
            <div style={{fontSize: 36, fontWeight: 850, marginBottom: 12, color: c.dotted ? C.yellow : C.cream}}>{c.text}</div>
            <div
              style={
                c.dotted
                  ? {height: Math.max(2, (height * c.value) / max * g), background: 'rgba(255,231,138,.13)', border: '3px dotted #ffe78a', boxSizing: 'border-box', boxShadow: '0 0 24px rgba(255,213,92,.4)'}
                  : {height: Math.max(2, (height * c.value) / max * g), background: `linear-gradient(180deg,#fff3e8,${col})`, boxShadow: `0 0 24px ${col}`}
              }
            />
            <div style={{fontSize: 24, fontWeight: 800, letterSpacing: 1.5, marginTop: 14, color: c.dotted ? C.yellow : C.cream}}>{c.label}</div>
            {c.sub ? <div style={{fontSize: 17, fontWeight: 700, color: C.yellow, letterSpacing: 1.2}}>{c.sub}</div> : null}
          </div>
        );
      })}
    </div>
  </div>
);

// ---------- card 07 form: dot matrix
export const DotRows: React.FC<{local: number; rows: {n: number; color: string}[]; dot?: number; gap?: number; perRow?: number}> = ({local, rows, dot = 25, gap = 12, perRow}) => (
  <div style={{display: 'grid', gap: 18}}>
    {rows.map((r, ri) => (
      <div key={ri} style={{display: 'flex', gap, flexWrap: perRow ? 'wrap' : 'nowrap', width: perRow ? perRow * (dot + gap) : undefined}}>
        {Array.from({length: r.n}, (_, i) => {
          const e = sp(local, ri * 9 + i * 1.1, 15, 120);
          return <span key={i} style={{width: dot, height: dot, borderRadius: '50%', background: r.color, opacity: e, transform: `scale(${0.25 + 0.75 * e})`, boxShadow: `0 0 15px ${r.color}`}} />;
        })}
      </div>
    ))}
  </div>
);

// ---------- card 07 form: gauge
export const Gauge: React.FC<{local: number; label: string; value: number; min: number; max: number; unit?: string}> = ({local, label, value, min, max}) => {
  const lineGrow = sp(local, 0, 19, 100);
  const marker = sp(local, 8, 14, 110);
  const ticks: number[] = [];
  for (let t = min; t <= max; t++) ticks.push(t);
  const step = 630 / (ticks.length - 1);
  const mx = ((value - min) / (max - min)) * 630;
  return (
    <div style={{width: 760}}>
      <Label>{label}</Label>
      <div style={{height: 120, display: 'flex', alignItems: 'flex-end', justifyContent: 'center'}}>
        <div style={{fontSize: 96, fontWeight: 900, color: C.cream, opacity: marker, transform: `translateY(${28 * (1 - marker)}px)`}}>{value.toFixed(1)}</div>
      </div>
      <div style={{position: 'relative', width: 630, height: 100, marginLeft: 22}}>
        <div style={{position: 'absolute', left: 0, top: 20, height: 3, width: 630 * lineGrow, background: C.cream, boxShadow: GLOW}} />
        {ticks.map((tick, i) => {
          const hit = tick === Math.round(value);
          return (
            <div key={tick} style={{position: 'absolute', left: i * step, top: 10, textAlign: 'center', transform: 'translateX(-50%)'}}>
              <div style={{height: hit ? 30 : 20, width: hit ? 4 : 2, background: hit ? C.yellow : C.cream, margin: '0 auto'}} />
              <div style={{fontSize: 22, fontWeight: hit ? 850 : 600, marginTop: 10, color: hit ? C.yellow : C.cream}}>{tick}</div>
            </div>
          );
        })}
        <div style={{position: 'absolute', left: mx, top: -14, width: 4, height: 70, background: C.yellow, boxShadow: '0 0 20px #ffd75e', opacity: marker, transform: `scaleY(${marker})`, transformOrigin: 'bottom'}} />
      </div>
    </div>
  );
};

// ---------- card 07 form: chevron flow into a dotted circle
export const FlowChevrons: React.FC<{local: number; big: string; label: string; target: string}> = ({local, big, label, target}) => (
  <div style={{width: 940}}>
    <div style={{display: 'flex', alignItems: 'baseline', gap: 30}}>
      <div style={{fontSize: 124, fontWeight: 900, letterSpacing: -5, whiteSpace: 'nowrap'}}>{big}</div>
      <Label>{label}</Label>
    </div>
    <svg width="880" height="170" viewBox="0 0 850 150" style={{overflow: 'visible', marginTop: 10}}>
      <g fill="none" stroke="#9ec8ff" strokeWidth="12" strokeLinecap="round" strokeLinejoin="round" style={{filter: 'drop-shadow(0 0 9px rgba(70,160,255,.9))'}}>
        {[0, 1, 2, 3, 4].map((i) => {
          const pulse = 0.32 + 0.68 * (0.5 + 0.5 * Math.sin(local / 4.5 - i * 0.95));
          return <path key={i} d={`M ${55 + i * 92} 35 L ${100 + i * 92} 75 L ${55 + i * 92} 115`} opacity={pulse} />;
        })}
      </g>
      <circle cx="715" cy="75" r="57" fill="rgba(255,231,138,.09)" stroke="#ffe78a" strokeWidth="4" strokeDasharray="5 9" style={{filter: 'drop-shadow(0 0 12px rgba(255,220,90,.65))'}} />
      <text x="715" y="83" textAnchor="middle" fill="#fff5ec" fontFamily={FONT} fontSize="23" fontWeight="800" letterSpacing="1">{target}</text>
    </svg>
  </div>
);

// ---------- waffle: n dots, k highlighted
export const Waffle: React.FC<{local: number; total: number; hi: number; cols: number; dot: number; gap: number; hiColor: string; baseColor: string; hiStart: number}> = ({local, total, hi, cols, dot, gap, hiColor, baseColor, hiStart}) => {
  const rnd = mulberry32(1729);
  const order = Array.from({length: total}, (_, i) => i);
  for (let i = total - 1; i > 0; i--) {
    const j = Math.floor(rnd() * (i + 1));
    [order[i], order[j]] = [order[j], order[i]];
  }
  const rank = new Array(total);
  order.forEach((idx, r) => (rank[idx] = r));
  const rows = Math.ceil(total / cols);
  return (
    <svg width={cols * (dot + gap)} height={rows * (dot + gap)} style={{overflow: 'visible'}}>
      {Array.from({length: total}, (_, i) => {
        const x = (i % cols) * (dot + gap) + dot / 2;
        const y = Math.floor(i / cols) * (dot + gap) + dot / 2;
        const appear = clamp01((local - (i / total) * 40) / 8);
        const isHi = rank[i] < hi;
        const hp = clamp01((local - hiStart - (rank[i] / hi) * 40) / 10);
        const col = isHi && hp > 0.5 ? hiColor : baseColor;
        return <circle key={i} cx={x} cy={y} r={(dot / 2) * (0.3 + 0.7 * appear) * (isHi && hp > 0 ? 1 + 0.12 * hp : 1)} fill={col} opacity={appear * (isHi && hp > 0.5 ? 1 : 0.55)} />;
      })}
    </svg>
  );
};

// ---------- stacked horizontal bar
export type Seg = {label: string; value: number; text: string; color: string; hot?: boolean};
export const StackBar: React.FC<{local: number; segs: Seg[]; width: number; height?: number; hotAt?: number}> = ({local, segs, width, height = 78, hotAt = 40}) => {
  const total = segs.reduce((s, x) => s + x.value, 0);
  let acc = 0;
  const g = eo3(prog(local, 0, 26));
  const hot = eo3(prog(local, hotAt, hotAt + 18));
  return (
    <div style={{width}}>
      <div style={{position: 'relative', height, width, display: 'flex', borderRadius: 8, overflow: 'hidden', boxShadow: '0 0 30px rgba(0,0,0,.6)'}}>
        {segs.map((s, i) => {
          const w = (s.value / total) * width * g;
          return <div key={i} style={{width: w, height, background: s.color, filter: s.hot ? `brightness(${1 + 0.35 * hot}) saturate(${1 + 0.3 * hot})` : `brightness(${1 - 0.25 * hot})`}} />;
        })}
      </div>
      <div style={{position: 'relative', height: 120, width}}>
        {segs.map((s, i) => {
          const x0 = acc;
          acc += s.value;
          const cx = ((x0 + s.value / 2) / total) * width;
          const big = s.value / total > 0.2;
          return (
            <div key={i} style={{position: 'absolute', left: cx + (big ? 0 : (i % 2 ? -85 : 85)), top: 14, transform: 'translateX(-50%)', textAlign: 'center', opacity: clamp01((local - 14 - i * 5) / 10), width: big ? 330 : 150}}>
              <div style={{fontSize: big ? 44 : 28, fontWeight: 900, color: s.hot ? C.redSoft : C.cream, textShadow: s.hot ? GLOW : '0 2px 6px #000'}}>{s.text}</div>
              <div style={{fontSize: big ? 21 : 15, fontWeight: 750, letterSpacing: 1.2, color: 'rgba(255,245,236,.88)', textTransform: 'uppercase'}}>{s.label}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// ---------- line chart with dashed threshold
export const LineChart: React.FC<{local: number; pts: {x: string; y: number}[]; yMin: number; yMax: number; w: number; h: number; color?: string; thresh?: {y: number; label: string}; ptLabels?: string[]; dotted?: boolean}> = ({local, pts, yMin, yMax, w, h, color = C.redSoft, thresh, ptLabels}) => {
  const px = (i: number) => 40 + (i / (pts.length - 1)) * (w - 120);
  const py = (v: number) => h - 50 - ((v - yMin) / (yMax - yMin)) * (h - 100);
  const g = eo3(prog(local, 0, 34));
  let d = '';
  pts.forEach((p, i) => (d += (i ? 'L' : 'M') + px(i) + ' ' + py(p.y)));
  return (
    <svg width={w} height={h} style={{overflow: 'visible'}}>
      {thresh ? (
        <g opacity={clamp01(local / 8)}>
          <line x1={20} x2={w - 40} y1={py(thresh.y)} y2={py(thresh.y)} stroke={C.yellow} strokeWidth={3} strokeDasharray="4 10" />
          <text x={w - 40} y={py(thresh.y) - 12} textAnchor="end" fill={C.yellow} fontFamily={FONT} fontSize={22} fontWeight={800} letterSpacing={1}>{thresh.label}</text>
        </g>
      ) : null}
      <path d={d} fill="none" stroke={color} strokeWidth={9} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray={`${g} 2`} style={{filter: `drop-shadow(0 0 10px ${color})`}} />
      {pts.map((p, i) => {
        const e = clamp01((g * (pts.length - 1) - (i - 0.2)) / 0.5);
        return (
          <g key={i} opacity={e}>
            <circle cx={px(i)} cy={py(p.y)} r={12} fill={C.cream} style={{filter: `drop-shadow(0 0 8px ${color})`}} />
            <text x={px(i)} y={py(p.y) - 28} textAnchor="middle" fill={C.cream} fontFamily={FONT} fontSize={34} fontWeight={900} style={{filter: 'drop-shadow(0 2px 4px #000)'}}>{ptLabels ? ptLabels[i] : p.y.toFixed(2)}</text>
            <text x={px(i)} y={h - 8} textAnchor="middle" fill="rgba(255,245,236,.9)" fontFamily={FONT} fontSize={24} fontWeight={800}>{p.x}</text>
          </g>
        );
      })}
    </svg>
  );
};

// ---------- ring (share arc)
export const ArcRing: React.FC<{local: number; share: number; size: number; color: string; center: React.ReactNode}> = ({local, share, size, color, center}) => {
  const r = size / 2 - 14;
  const circ = 2 * Math.PI * r;
  const g = eo3(prog(local, 0, 36));
  return (
    <div style={{position: 'relative', width: size, height: size}}>
      <svg width={size} height={size} style={{transform: 'rotate(-90deg)'}}>
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="rgba(255,255,255,.18)" strokeWidth={16} />
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={color} strokeWidth={16} strokeLinecap="round" strokeDasharray={`${circ * share * g} ${circ}`} style={{filter: `drop-shadow(0 0 12px ${color})`}} />
      </svg>
      <div style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column'}}>{center}</div>
    </div>
  );
};

export const horizBar = (frac: number, color: string, w: number, h: number) => (
  <div style={{width: w, height: h, background: 'rgba(255,255,255,.14)', borderRadius: 6, overflow: 'hidden'}}>
    <div style={{width: w * frac, height: h, background: color, boxShadow: `0 0 18px ${color}`}} />
  </div>
);
export {lerp, fmt};
