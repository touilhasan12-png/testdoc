import React from 'react';
import {Easing, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {clamp01, eo3, fmt, item, life, prog} from '../lib/core';

export const FONT = "Montserrat, 'Helvetica Neue', Arial, sans-serif";
export const C = {
  red: '#ff4a5a',
  redSoft: '#ff9e91',
  blue: '#46b4ff',
  cyan: '#8ef5ef',
  amber: '#ffd75e',
  yellow: '#ffe78a',
  cream: '#fff5ec',
  ink: '#05080c',
  gray: '#7d8a96',
};
// card 07 glow
export const GLOW = '0 0 5px rgba(255,255,255,.85), 0 0 18px rgba(255,102,92,.82), 0 0 40px rgba(255,55,65,.45)';
export const GLOW_BLUE = '0 0 5px rgba(255,255,255,.85), 0 0 18px rgba(70,180,255,.85), 0 0 40px rgba(40,140,255,.45)';
export const GLOW_GOLD = '0 0 5px rgba(255,255,255,.85), 0 0 18px rgba(255,200,80,.85), 0 0 40px rgba(255,150,40,.45)';
const clampOpt = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

// ---------------------------------------------------------------- Card 07 motion (rebuilt): spring entry, diagonal drift, animated exit, light tilt
export const Float07: React.FC<{
  id: string;
  x: number;
  y: number;
  vx?: number;
  vy?: number;
  rx?: number;
  ry?: number;
  rz?: number;
  glow?: string;
  children: (local: number) => React.ReactNode;
}> = ({id, x, y, vx = 40, vy = -40, rx = 8, ry = -10, rz = -4, glow = GLOW, children}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {f0: start, f1: end} = item(id);
  const local = frame - start;
  if (local < 0 || frame > end) return null;
  const enter = spring({frame: local, fps, config: {damping: 17, stiffness: 105, mass: 0.85}});
  const exit = interpolate(frame, [end - 22, end], [0, 1], {...clampOpt, easing: Easing.bezier(0.4, 0, 0.7, 0.2)});
  const t = local / (end - start);
  const px = x + vx * t + 55 * (1 - enter) - 45 * exit;
  const py = y + vy * t + 65 * (1 - enter) - 30 * exit;
  const scale = (0.8 + 0.2 * enter) * (1 + 0.055 * t - 0.06 * exit);
  const opacity = interpolate(local, [0, 5], [0, 1], clampOpt) * (1 - exit);
  return (
    <div
      style={{
        position: 'absolute',
        left: 0,
        top: 0,
        fontFamily: FONT,
        color: C.cream,
        opacity,
        transform: `translate3d(${px}px, ${py}px, 0) rotateX(${rx}deg) rotateY(${ry}deg) rotateZ(${rz}deg) skewX(-2deg) scale(${scale})`,
        transformOrigin: 'left top',
        textShadow: glow,
      }}
    >
      {children(local)}
    </div>
  );
};

export const Perspective: React.FC<{children: React.ReactNode}> = ({children}) => (
  <div style={{position: 'absolute', inset: 0, perspective: 1400, transformStyle: 'preserve-3d'}}>{children}</div>
);

export const Label: React.FC<{children: React.ReactNode; projection?: boolean; color?: string; size?: number}> = ({children, projection, color, size = 24}) => (
  <div
    style={{
      fontSize: size,
      fontWeight: 800,
      letterSpacing: 2.1,
      color: color ?? (projection ? C.yellow : '#ffe9dc'),
      borderBottom: projection ? '3px dotted rgba(255,231,138,.9)' : undefined,
      paddingBottom: projection ? 7 : 0,
      textShadow: '0 0 9px rgba(255,82,68,.7), 0 2px 5px rgba(0,0,0,.85)',
      textTransform: 'uppercase',
      whiteSpace: 'nowrap',
    }}
  >
    {children}
  </div>
);

// ---------------------------------------------------------------- Chip
export const Chip: React.FC<{
  id: string;
  x: number;
  y: number;
  accent?: string;
  w?: number;
  from?: 'left' | 'right' | 'bottom';
  right?: boolean;
  children: React.ReactNode;
}> = ({id, x, y, accent = C.amber, w, from = 'left', right, children}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const it = item(id);
  const local = frame - it.f0;
  if (local < 0 || frame > it.f1) return null;
  const e = spring({frame: local, fps, config: {damping: 18, stiffness: 120, mass: 0.8}});
  const out = prog(frame, it.f1 - 14, it.f1);
  const dx = from === 'left' ? -70 : from === 'right' ? 70 : 0;
  const dy = from === 'bottom' ? 50 : 0;
  return (
    <div
      style={{
        position: 'absolute',
        left: right ? undefined : x,
        right: right ? x : undefined,
        top: y,
        width: w,
        fontFamily: FONT,
        color: C.cream,
        padding: '18px 28px 20px 26px',
        background: 'linear-gradient(90deg, rgba(5,10,16,.86), rgba(5,10,16,.72))',
        borderLeft: `7px solid ${accent}`,
        borderRadius: 6,
        boxShadow: '0 12px 34px rgba(0,0,0,.5)',
        opacity: clamp01(local / 5) * (1 - out),
        transform: `translate(${dx * (1 - e) + 40 * out * (from === 'right' ? 1 : -1)}px, ${dy * (1 - e)}px)`,
      }}
    >
      {children}
    </div>
  );
};
export const ChipTitle: React.FC<{children: React.ReactNode; size?: number; color?: string}> = ({children, size = 44, color}) => (
  <div style={{fontSize: size, fontWeight: 900, lineHeight: 1.08, letterSpacing: -0.5, color: color ?? C.cream, textTransform: 'uppercase'}}>{children}</div>
);
export const ChipSub: React.FC<{children: React.ReactNode; size?: number; color?: string; projection?: boolean}> = ({children, size = 26, color, projection}) => (
  <div
    style={{
      fontSize: size,
      fontWeight: 700,
      letterSpacing: 1.4,
      marginTop: 8,
      color: color ?? 'rgba(255,245,236,.86)',
      textTransform: 'uppercase',
      display: 'inline-block',
      borderBottom: projection ? '3px dotted rgba(255,231,138,.9)' : undefined,
      paddingBottom: projection ? 5 : 0,
    }}
  >
    {children}
  </div>
);

// ---------------------------------------------------------------- Stamp
export const Stamp: React.FC<{
  id: string;
  x: number;
  y: number;
  rot?: number;
  color?: string;
  size?: number;
  sub?: string;
  children: React.ReactNode;
}> = ({id, x, y, rot = -7, color = C.red, size = 120, sub, children}) => {
  const frame = useCurrentFrame();
  const it = item(id);
  const local = frame - it.f0;
  if (local < 0 || frame > it.f1) return null;
  const e = eo4(clamp01(local / 6));
  const out = prog(frame, it.f1 - 10, it.f1);
  const scale = (2.3 - 1.3 * e) * (1 + 0.06 * out);
  const flash = clamp01(1 - local / 10);
  return (
    <div style={{position: 'absolute', left: x, top: y, transform: `translate(-50%, -50%) rotate(${rot}deg) scale(${scale})`, opacity: e * (1 - out), fontFamily: FONT}}>
      <div
        style={{
          border: `${Math.max(8, size / 11)}px solid ${color}`,
          padding: `${size * 0.1}px ${size * 0.26}px`,
          borderRadius: 12,
          color,
          fontSize: size,
          fontWeight: 900,
          letterSpacing: size * 0.04,
          lineHeight: 1,
          background: `rgba(5,8,12,${0.62 + 0.2 * flash})`,
          boxShadow: `0 0 ${30 + 60 * flash}px ${color}88, inset 0 0 22px ${color}55`,
          textAlign: 'center',
          textTransform: 'uppercase',
          whiteSpace: 'nowrap',
        }}
      >
        {children}
        {sub ? <div style={{fontSize: size * 0.2, letterSpacing: size * 0.03, marginTop: size * 0.1, color: '#ffd6d0', fontWeight: 800}}>{sub}</div> : null}
      </div>
    </div>
  );
};
const eo4 = (t: number) => 1 - Math.pow(1 - t, 4);

// ---------------------------------------------------------------- Typed text
export const Typed: React.FC<{text: string; start: number; cps?: number; style?: React.CSSProperties}> = ({text, start, cps = 1.1, style}) => {
  const f = useCurrentFrame();
  const n = Math.max(0, Math.min(text.length, Math.floor((f - start) * cps)));
  return <span style={style}>{text.slice(0, n)}</span>;
};

// ---------------------------------------------------------------- Counter
export const Counter: React.FC<{from?: number; to: number; start: number; dur: number; decimals?: number; prefix?: string; suffix?: string}> = ({from = 0, to, start, dur, decimals = 0, prefix = '', suffix = ''}) => {
  const f = useCurrentFrame();
  const v = from + (to - from) * eo3(prog(f, start, start + dur));
  const s = decimals ? v.toFixed(decimals) : fmt(v);
  return <>{prefix + s + suffix}</>;
};

// ---------------------------------------------------------------- Leader line (screen space)
export const Leader: React.FC<{id: string; from: [number, number]; to: [number, number]; color?: string; delay?: number}> = ({id, from, to, color = C.amber, delay = 6}) => {
  const f = useCurrentFrame();
  const it = item(id);
  const p = eo3(prog(f, it.f0 + delay, it.f0 + delay + 16)) * (1 - prog(f, it.f1 - 10, it.f1));
  if (p <= 0.001) return null;
  const x2 = from[0] + (to[0] - from[0]) * p;
  const y2 = from[1] + (to[1] - from[1]) * p;
  return (
    <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0, pointerEvents: 'none', overflow: 'visible'}}>
      <line x1={from[0]} y1={from[1]} x2={x2} y2={y2} stroke={color} strokeWidth={3} strokeDasharray="2 8" strokeLinecap="round" style={{filter: `drop-shadow(0 0 6px ${color})`}} />
      <circle cx={x2} cy={y2} r={9 * p} fill={color} style={{filter: `drop-shadow(0 0 8px ${color})`}} />
    </svg>
  );
};

// ---------------------------------------------------------------- Photographic cutouts (clip-path of REAL photos; nothing is drawn)
export type PhotoId = 'sf_skyline' | 'lifeboat' | 'young_adults' | 'couple' | 'commuters' | 'office_worker' | 'young_woman' | 'akiya' | 'shinjuku';
// polygons in a 400x300 box (percent of the 4:3 photo)
export const CUT: Record<PhotoId, number[][]> = {
  sf_skyline: [[0, 300], [0, 158], [55, 152], [108, 130], [128, 124], [162, 134], [200, 130], [232, 118], [262, 100], [276, 48], [288, 8], [299, 46], [318, 100], [332, 66], [346, 20], [353, 12], [361, 22], [367, 62], [382, 108], [400, 118], [400, 300]],
  lifeboat: [[60, 175], [78, 132], [118, 108], [200, 100], [268, 108], [312, 128], [338, 152], [340, 196], [318, 214], [250, 222], [120, 222], [66, 206]],
  young_adults: [[0, 300], [6, 128], [30, 80], [64, 60], [118, 66], [152, 52], [205, 36], [228, 56], [252, 38], [292, 70], [332, 58], [372, 48], [400, 66], [400, 300]],
  couple: [[52, 300], [56, 112], [72, 52], [106, 36], [140, 46], [162, 92], [186, 108], [204, 84], [226, 44], [262, 50], [294, 58], [326, 100], [356, 150], [376, 300]],
  commuters: [[0, 300], [0, 58], [34, 28], [112, 14], [172, 4], [232, 8], [304, 22], [380, 14], [400, 64], [400, 300]],
  office_worker: [[100, 300], [110, 196], [150, 122], [170, 78], [200, 70], [226, 96], [232, 122], [262, 116], [338, 116], [350, 152], [352, 300]],
  young_woman: [[24, 300], [28, 84], [92, 40], [190, 28], [300, 66], [400, 54], [400, 300]],
  akiya: [[0, 300], [0, 44], [58, 24], [112, 30], [180, 58], [252, 86], [330, 92], [400, 100], [400, 300]],
  shinjuku: [[0, 300], [0, 60], [40, 40], [80, 12], [120, 34], [190, 20], [240, 44], [300, 28], [360, 52], [400, 30], [400, 300]],
};
const polyStr = (id: PhotoId) => 'polygon(' + CUT[id].map(([x, y]) => `${((x / 400) * 100).toFixed(2)}% ${((y / 300) * 100).toFixed(2)}%`).join(',') + ')';
const STICKER = 'drop-shadow(4px 0 0 #f4efe3) drop-shadow(-4px 0 0 #f4efe3) drop-shadow(0 4px 0 #f4efe3) drop-shadow(0 -4px 0 #f4efe3) drop-shadow(0 22px 22px rgba(0,0,0,.55))';

export const PhotoInner: React.FC<{id: PhotoId; w: number}> = ({id, w}) => (
  <div style={{width: w, height: (w * 3) / 4, clipPath: polyStr(id)}}>
    <Img src={staticFile(`photos/${id}.jpg`)} style={{width: w, height: (w * 3) / 4, display: 'block'}} />
  </div>
);

/** Photo clipping with sticker edge. p = life 0..1 (entry/exit), dissolve 0..1 slices it away upward. */
export const Cutout: React.FC<{
  photo: PhotoId;
  id: string;
  x: number;
  y: number;
  w: number;
  rot?: number;
  from?: 'left' | 'right' | 'top' | 'bottom';
  dissolveAt?: number;
  dissolveDur?: number;
  noExit?: boolean;
}> = ({photo, id, x, y, w, rot = -2.5, from = 'right', dissolveAt, dissolveDur = 34, noExit}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const it = item(id);
  const local = frame - it.f0;
  if (local < 0 || frame > it.f1) return null;
  const e = spring({frame: local, fps, config: {damping: 16, stiffness: 95, mass: 0.9}});
  const out = noExit ? 0 : prog(frame, it.f1 - 14, it.f1);
  const off = 260;
  const dx = from === 'left' ? -off : from === 'right' ? off : 0;
  const dy = from === 'top' ? -off : from === 'bottom' ? off : 0;
  const dis = dissolveAt !== undefined ? prog(frame, dissolveAt, dissolveAt + dissolveDur) : 0;
  const scale = 0.88 + 0.12 * e;
  const base: React.CSSProperties = {
    position: 'absolute',
    left: x,
    top: y,
    width: w,
    height: (w * 3) / 4,
    opacity: clamp01(local / 4) * (1 - out),
    transform: `translate(${dx * (1 - e) + 50 * out}px, ${dy * (1 - e)}px) rotate(${rot * e}deg) scale(${scale})`,
    transformOrigin: 'center',
  };
  if (dis > 0) {
    const N = 16;
    return (
      <div style={base}>
        {Array.from({length: N}, (_, i) => {
          const d = clamp01(dis * 1.5 - (i / N) * 0.5);
          return (
            <div
              key={i}
              style={{
                position: 'absolute',
                left: (i * w) / N,
                top: 0,
                width: w / N + 1,
                height: (w * 3) / 4,
                overflow: 'hidden',
                opacity: 1 - d,
                transform: `translate(${d * 30}px, ${-d * (60 + (i % 5) * 18)}px) rotate(${d * (i % 2 ? 5 : -5)}deg)`,
                filter: `blur(${d * 6}px)`,
              }}
            >
              <div style={{position: 'absolute', left: (-i * w) / N, top: 0}}>
                <PhotoInner id={photo} w={w} />
              </div>
            </div>
          );
        })}
      </div>
    );
  }
  return (
    <div style={base}>
      <div style={{filter: STICKER}}>
        <PhotoInner id={photo} w={w} />
      </div>
    </div>
  );
};

export const RedX: React.FC<{id: string; x: number; y: number; w: number; h: number}> = ({id, x, y, w, h}) => {
  const f = useCurrentFrame();
  const it = item(id);
  const p = eo3(prog(f, it.f0, it.f0 + 10));
  const p2 = eo3(prog(f, it.f0 + 6, it.f0 + 16));
  const out = prog(f, it.f1 - 14, it.f1);
  if (f < it.f0 || f > it.f1) return null;
  return (
    <svg width={w} height={h} style={{position: 'absolute', left: x, top: y, opacity: 1 - out, overflow: 'visible'}}>
      <line x1={0} y1={0} x2={w * p} y2={h * p} stroke={C.red} strokeWidth={22} strokeLinecap="round" style={{filter: 'drop-shadow(0 0 14px rgba(255,60,70,.9))'}} />
      <line x1={w} y1={0} x2={w - w * p2} y2={h * p2} stroke={C.red} strokeWidth={22} strokeLinecap="round" style={{filter: 'drop-shadow(0 0 14px rgba(255,60,70,.9))'}} />
    </svg>
  );
};
