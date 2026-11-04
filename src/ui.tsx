import React from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';
import {T, fmtNum} from './theme';
import {Cam, camTransform, PREFS, CEN, ease} from './geo';

export type Paint = {fill: string; op?: number; sw?: number};

const full: React.CSSProperties = {position: 'absolute', left: 0, top: 0, overflow: 'visible'};

export const Svg: React.FC<{children?: React.ReactNode}> = ({children}) => (
  <svg width={1920} height={1080} viewBox="0 0 1920 1080" style={full}>
    {children}
  </svg>
);

// Static background: deep ocean gradient + graticule. Never animated.
export const Backdrop: React.FC = () => {
  const lines: React.ReactNode[] = [];
  for (let x = 0; x <= 1920; x += 120) {
    lines.push(<line key={'v' + x} x1={x} y1={0} x2={x} y2={1080} stroke="#1a2c48" strokeOpacity={0.35} />);
  }
  for (let y = 0; y <= 1080; y += 120) {
    lines.push(<line key={'h' + y} x1={0} y1={y} x2={1920} y2={y} stroke="#1a2c48" strokeOpacity={0.35} />);
  }
  return (
    <Svg>
      <defs>
        <radialGradient id="bgGrad" cx="50%" cy="45%" r="75%">
          <stop offset="0%" stopColor="#0e1b30" />
          <stop offset="65%" stopColor="#070d18" />
          <stop offset="100%" stopColor="#02040a" />
        </radialGradient>
      </defs>
      <rect width={1920} height={1080} fill="url(#bgGrad)" />
      {lines}
    </Svg>
  );
};

// Japan prefectures from the bundled SVG paths, camera-transformed.
export const JapanMap: React.FC<{
  cam: Cam;
  paint: (id: string, cx: number, idx: number) => Paint;
  opacity?: number;
  children?: React.ReactNode;
}> = ({cam, paint, opacity = 1, children}) => (
  <g transform={camTransform(cam)} opacity={opacity}>
    {PREFS.map((p, i) => {
      const pt = paint(p.id, CEN[p.id].cx, i);
      return (
        <path
          key={p.id}
          d={p.path}
          fill={pt.fill}
          fillOpacity={pt.op ?? 1}
          stroke="#0a1322"
          strokeWidth={pt.sw ?? 0.7}
          strokeLinejoin="round"
        />
      );
    })}
    {children}
  </g>
);

// Fades/rises in at `start`; optional fade-out at `end`.
export const Pop: React.FC<{
  start: number;
  end?: number;
  style?: React.CSSProperties;
  children: React.ReactNode;
}> = ({start, end, style, children}) => {
  const f = useCurrentFrame();
  const inOp = ease(f, start, start + 14);
  const outOp =
    end === undefined
      ? 1
      : interpolate(f, [end, end + 12], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const y = ease(f, start, start + 14, 10, 0);
  return (
    <div
      style={{
        position: 'absolute',
        fontFamily: T.font,
        color: T.ink,
        opacity: inOp * outOp,
        transform: `translateY(${y}px)`,
        ...style,
      }}
    >
      {children}
    </div>
  );
};

export const Counter: React.FC<{
  to: number;
  start: number;
  dur: number;
  dec?: number;
  from?: number;
  prefix?: string;
  suffix?: string;
  style?: React.CSSProperties;
}> = ({to, start, dur, dec = 0, from = 0, prefix = '', suffix = '', style}) => {
  const f = useCurrentFrame();
  const v = interpolate(f, [start, start + dur], [from, to], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });
  return (
    <span style={{fontVariantNumeric: 'tabular-nums', ...style}}>
      {prefix}
      {fmtNum(v, dec)}
      {suffix}
    </span>
  );
};

export const Chip: React.FC<{
  start: number;
  end?: number;
  style?: React.CSSProperties;
  color?: string;
  children: React.ReactNode;
}> = ({start, end, style, color = T.cyan, children}) => (
  <Pop
    start={start}
    end={end}
    style={{
      maxWidth: 600,
      background: 'rgba(7,13,24,0.84)',
      border: `1.5px solid ${color}`,
      borderRadius: 10,
      padding: '14px 22px',
      fontSize: 27,
      lineHeight: 1.3,
      ...style,
    }}
  >
    {children}
  </Pop>
);

export const Source: React.FC<{text: string}> = ({text}) => (
  <div
    style={{
      position: 'absolute',
      left: 80,
      bottom: 30,
      maxWidth: 1600,
      fontFamily: T.font,
      fontSize: 17,
      color: T.mute,
      letterSpacing: 0.4,
    }}
  >
    SOURCE · {text}
  </div>
);

// Torn-paper archive card that slides in, holds, and leaves.
export const ChapterCard: React.FC<{label: string; title: string; start?: number; end?: number}> = ({
  label,
  title,
  start = 0,
  end = 100,
}) => {
  const f = useCurrentFrame();
  const x = ease(f, start, start + 10, -60, 0);
  const out = interpolate(f, [end - 14, end], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const op = ease(f, start, start + 10) * out;
  return (
    <div
      style={{
        position: 'absolute',
        left: 90,
        top: 690,
        opacity: op,
        transform: `translateX(${x}px) rotate(-1.2deg)`,
        filter: 'drop-shadow(0 8px 18px rgba(0,0,0,0.55))',
      }}
    >
      <div
        style={{
          width: 560,
          padding: '26px 34px 30px',
          background: T.paper,
          color: '#1b1f2a',
          fontFamily: T.font,
          clipPath:
            'polygon(0% 6%, 4% 0%, 9% 5%, 15% 0%, 22% 4%, 30% 0%, 38% 5%, 46% 0%, 55% 4%, 63% 0%, 72% 5%, 80% 0%, 88% 4%, 94% 0%, 100% 6%, 97% 50%, 100% 94%, 92% 100%, 84% 95%, 76% 100%, 66% 95%, 56% 100%, 46% 95%, 36% 100%, 26% 95%, 16% 100%, 8% 95%, 0% 100%, 3% 50%)',
        }}
      >
        <div style={{fontSize: 20, letterSpacing: 4, color: '#b3261e', fontWeight: 700}}>{label}</div>
        <div style={{fontSize: 44, fontWeight: 800, marginTop: 8, lineHeight: 1.1}}>{title}</div>
      </div>
    </div>
  );
};

// Simple person glyph in the local coordinate system of its parent.
export const Person: React.FC<{x: number; y: number; s?: number; color?: string; op?: number}> = ({
  x,
  y,
  s = 1,
  color = T.ink,
  op = 1,
}) => (
  <g transform={`translate(${x} ${y}) scale(${s})`} opacity={op} fill={color}>
    <circle cx={0} cy={-22} r={7} />
    <path d="M-9,-12 h18 q5,0 5,5 v14 h-4 v18 h-7 v-12 h-4 v12 h-7 v-18 h-4 v-14 q0,-5 5,-5 z" />
  </g>
);

// Schematic age-structure pyramid. Shapes are illustrative, not census data.
export const Pyramid: React.FC<{
  x: number;
  y: number;
  w: number;
  h: number;
  from: number[];
  to: number[];
  p: number;
  color: string;
  scale?: number;
}> = ({x, y, w, h, from, to, p, color, scale = 1}) => {
  const cx = x + w / 2;
  const bh = h / from.length;
  const bars: React.ReactNode[] = [];
  from.forEach((a, i) => {
    const v = a + (to[i] - a) * p;
    const half = (w / 2) * v;
    const by = y + h - (i + 1) * bh + 1;
    bars.push(<rect key={'l' + i} x={cx - half} y={by} width={half} height={bh - 2} fill={color} fillOpacity={0.85} />);
    bars.push(<rect key={'r' + i} x={cx} y={by} width={half} height={bh - 2} fill={color} fillOpacity={0.55} />);
  });
  return (
    <g transform={`translate(${cx} ${y + h}) scale(${scale}) translate(${-cx} ${-(y + h)})`}>
      {bars}
    </g>
  );
};
