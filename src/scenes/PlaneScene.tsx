import React from 'react';
import rural from '../data/rural-points.json';
import {Arrows, ArrowSpec, BlackHole, DottedRing, PlaneSvg, RegionLayer, RegionStyle} from '../components/plane';
import {FLAGGED_16, HOMETOWN, PREFS, SHINJUKU, TOKYO, WARDS, clamp01, eo3, item, mulberry32, planePt, prog, pref} from '../lib/core';
import {useStage} from '../lib/ctx';

const OTHERS = PREFS.filter((p) => p.name !== 'Tokyo');
const lonNorm = (lon: number) => clamp01((lon - 128) / 18);
const RED = '#ff3b4e';
const BLUE = '#3aa8ff';

// arrows from every prefecture to Tokyo (ILLUSTRATIVE, uniform width)
const ALL_ARROWS = (color: string, step: number): ArrowSpec[] =>
  OTHERS.map((p, i) => ({a: p.c, b: TOKYO, curv: i % 2 ? 0.16 : -0.16, delay: i * step, color, width: 3.2, n: 2, speed: 0.011}));

const CORNERS: ArrowSpec[] = ['Hokkaido', 'Kagoshima', 'Okinawa', 'Nagasaki', 'Aomori', 'Shimane'].map((n, i) => ({
  a: pref(n).c, b: TOKYO, curv: i % 2 ? 0.14 : -0.14, delay: i * 9, color: '#ffe78a', width: 6.5, n: 4, speed: 0.013,
}));
const RING_SRC = (r: number, n: number, off: number): [number, number][] =>
  Array.from({length: n}, (_, i) => {
    const a = off + (i / n) * Math.PI * 2;
    return [TOKYO[0] + Math.cos(a) * r * 1.25, TOKYO[1] + Math.sin(a) * r] as [number, number];
  });
const LOCAL_YOUNG: ArrowSpec[] = RING_SRC(0.42, 10, 0.3).map((a, i) => ({a, b: i % 3 === 0 ? SHINJUKU : i % 3 === 1 ? [139.70, 35.659] : [139.72, 35.73], curv: 0.14, delay: i * 6, color: '#8ef5ef', width: 4, n: 3, speed: 0.014}));
const LOCAL_SUCK: ArrowSpec[] = RING_SRC(0.5, 12, 0.1).map((a, i) => ({a, b: TOKYO, curv: i % 2 ? 0.12 : -0.12, delay: i * 5, color: '#9ec8ff', width: 4, n: 3, speed: 0.013}));
const RURAL_SRC = ['Akita', 'Iwate', 'Shimane', 'Kochi', 'Yamagata', 'Tottori', 'Aomori', 'Nagasaki', 'Saga', 'Oita', 'Fukui', 'Tokushima'];
const MULTIPLY: ArrowSpec[] = RURAL_SRC.map((n, i) => ({a: pref(n).c, b: TOKYO, curv: i % 2 ? 0.15 : -0.15, delay: i * 7, color: '#ffd75e', width: 4, n: 3, speed: 0.012}));
const AGE_ARROW: ArrowSpec[] = [{a: [135.5, 34.7], b: TOKYO, curv: 0.15, color: '#ffd75e', width: 13, n: 5, speed: 0.012}];
const WOMAN: ArrowSpec[] = [{a: HOMETOWN, b: TOKYO, curv: 0.12, color: '#ffd75e', width: 8, n: 5, speed: 0.01}];

const rnd = mulberry32(777);
const RURAL = (rural as number[][]).map(([lon, lat], i) => ({lon, lat, i, abandoned: rnd() < 0.43}));
const GHOST = [[0.05, 0.03], [-0.07, 0.02], [0.03, -0.06], [-0.04, -0.04], [0.08, -0.02]];

export const PlaneScene: React.FC = () => {
  const {frame: f, cam} = useStage();
  const z = cam.z;

  // ---- prefecture choropleth style (mode by time)
  const prefStyle = (r: (typeof PREFS)[number]): RegionStyle => {
    const isT = r.name === 'Tokyo';
    const zFade = 1 - prog(z, 8.6, 10.0);
    if (zFade <= 0.01) return null;
    const sweep = clamp01((f - 6 - 42 * lonNorm(r.c[0])) / 10);
    if (f < 1800) {
      const dim = f < 1047 ? 1 : 0.55;
      if (isT) {
        const grow = eo3(prog(f, 470, 500));
        return {fill: grow > 0 ? BLUE : undefined, opacity: 0.75 * grow * zFade, stroke: '#ffffff', strokeOpacity: 0.9 * zFade, strokeWidth: 3};
      }
      if (f < 6) return {stroke: '#fff', strokeOpacity: 0.12 * zFade, strokeWidth: 1};
      return {fill: RED, opacity: 0.5 * sweep * dim * zFade, stroke: '#fff', strokeOpacity: 0.42 * zFade, strokeWidth: 1.4};
    }
    if (f < 2556) {
      const rv = clamp01((f - 1800 - 40 * lonNorm(r.c[0])) / 12);
      if (isT) return {fill: '#ff2a44', opacity: (0.35 + 0.4 * rv) * zFade, stroke: '#fff', strokeOpacity: 0.9 * zFade, strokeWidth: 3};
      if (r.name === 'Okinawa') {
        const hot = eo3(prog(f, 2346, 2380));
        return {fill: hot > 0.01 ? '#34e0c8' : '#c9b27a', opacity: (0.3 + 0.45 * hot) * rv * zFade, stroke: '#fff', strokeOpacity: 0.5 * zFade};
      }
      return {fill: '#c9b27a', opacity: 0.3 * rv * zFade, stroke: '#fff', strokeOpacity: 0.35 * zFade, strokeWidth: 1.2};
    }
    if (f >= 4040 && f < 4890) {
      const g = prog(f, 4335, 4600);
      return {fill: isT ? BLUE : '#7d8a96', opacity: (isT ? 0.6 : 0.18 + 0.2 * g) * zFade, stroke: '#fff', strokeOpacity: 0.3 * zFade};
    }
    if (f >= 6936 && f < 7692) {
      return {fill: isT ? BLUE : '#7d8a96', opacity: (isT ? 0.55 : 0.32) * zFade, stroke: '#fff', strokeOpacity: 0.3 * zFade};
    }
    return {stroke: '#fff', strokeOpacity: 0.3 * zFade, strokeWidth: 1.2, fill: isT ? '#3aa8ff' : undefined, opacity: isT ? 0.3 * zFade : 0};
  };

  // ---- wards
  const wardVis = prog(z, 9.4, 10.6);
  const wardStyle = (r: (typeof WARDS)[number]): RegionStyle => {
    if (wardVis <= 0.01) return null;
    const idx = FLAGGED_16.indexOf(r.name);
    const flagged = idx >= 0;
    let fillOp = 0;
    let fill = '#ff2d4d';
    if (f >= 150 && f < 166) fillOp = flagged ? 0.62 : 0;
    else if (f >= 3380 && f < 4040 && flagged) fillOp = 0.38 * prog(f, 3380, 3700) * (1 - prog(f, 3990, 4030));
    else if (f >= 8121) {
      const t0 = item('wards_lit').f0 + idx * 9;
      fillOp = flagged ? 0.62 * eo3(prog(f, t0, t0 + 12)) : 0;
      if (!flagged) {
        fill = '#000';
        fillOp = 0.28 * prog(f, 8121, 8200);
      }
    }
    return {fill, opacity: fillOp, stroke: '#ffffff', strokeOpacity: 0.75 * wardVis, strokeWidth: 1.8};
  };

  // ---- black hole
  const bhP = f >= 744 && f <= 1047 ? eo3(prog(f, 744, 800)) * (1 - prog(f, 1020, 1047)) : 0;
  const [tx, ty] = planePt(cam, TOKYO[0], TOKYO[1]);

  const rural = RURAL;
  const showRural = f >= 4045 && f < 4890;
  const grayP = prog(f, 4335, 4600);
  const abP = eo3(prog(f, 4337, 4420));

  const ghostP = f >= 6565 && f <= 6730 ? 1 - prog(f, 6570, 6700) : 0;
  const vanish = f >= 6940 && f <= 7012 ? prog(f, 6940, 7005) : -1;

  return (
    <PlaneSvg>
      <RegionLayer regions={PREFS} style={prefStyle} />
      <RegionLayer regions={WARDS} style={wardStyle} />

      {/* Tokyo markers */}
      {f >= 1048 && f <= 1810 ? <DottedRing lon={TOKYO[0]} lat={TOKYO[1]} r={46} opacity={eo3(prog(f, 1048, 1075)) * (1 - prog(f, 1790, 1810))} spin={f * 0.3} /> : null}
      {(f >= 2062 && f <= 2556) ? <DottedRing lon={TOKYO[0]} lat={TOKYO[1]} r={46} color="#ff8d8d" opacity={eo3(prog(f, 2062, 2090)) * (1 - prog(f, 2530, 2556))} spin={-f * 0.3} /> : null}
      <BlackHole lon={TOKYO[0]} lat={TOKYO[1]} R={85} p={bhP} frame={f} />

      {/* arrows */}
      {f >= 724 && f <= 1047 ? <Arrows specs={ALL_ARROWS('#ff8a66', 4)} f0={item('gravity').f0} f1={item('gravity').f1} dur={40} /> : null}
      {f >= 1060 && f <= 1810 ? <Arrows specs={ALL_ARROWS('#8ec9ff', 3)} f0={item('flow_in').f0} f1={item('flow_in').f1} dur={38} /> : null}
      {f >= 1434 && f <= 1700 ? <Arrows specs={AGE_ARROW} f0={item('age2024').f0} f1={item('age2024').f1} dur={46} /> : null}
      {f >= 1600 && f <= 1800 ? <Arrows specs={CORNERS} f0={item('corners').f0} f1={item('corners').f1} dur={40} /> : null}
      {f >= 2640 && f <= 2935 ? <Arrows specs={LOCAL_YOUNG} f0={item('young_stream').f0} f1={item('young_stream').f1} dur={46} /> : null}
      {f >= 6561 && f <= 6736 ? <Arrows specs={WOMAN} f0={item('woman_arrow').f0} f1={item('woman_arrow').f1} dur={150} /> : null}
      {f >= 7020 && f <= 7186 ? <Arrows specs={MULTIPLY} f0={item('multiply').f0} f1={item('multiply').f1} dur={44} /> : null}
      {f >= 7882 && f <= 8050 ? <Arrows specs={LOCAL_SUCK} f0={item('suck_arrows').f0} f1={item('suck_arrows').f1} dur={38} /> : null}

      {/* illustrative home dots (seeded, NOT real locations) */}
      {showRural
        ? rural.map((d) => {
            const [x, y] = planePt(cam, d.lon, d.lat);
            const ap = clamp01((f - 4045 - d.i * 0.9) / 10);
            const col = d.abandoned && abP > 0.5 ? RED : grayP > 0.5 ? '#78858f' : '#ffd75e';
            return <circle key={d.i} cx={x} cy={y} r={7 * ap} fill={col} opacity={(0.95 - 0.35 * grayP) * ap * (1 - prog(f, 4860, 4890))} style={{filter: col === RED ? 'drop-shadow(0 0 6px #ff3b4e)' : undefined}} />;
          })
        : null}

      {/* hometown ghosts: the children she might have had */}
      {ghostP > 0
        ? GHOST.map((g, i) => {
            const [x, y] = planePt(cam, HOMETOWN[0] + g[0], HOMETOWN[1] + g[1]);
            return <circle key={i} cx={x} cy={y} r={11} fill="none" stroke="#ffe78a" strokeWidth={3} strokeDasharray="3 6" opacity={ghostP * (1 - i * 0.08)} />;
          })
        : null}
      {vanish >= 0
        ? GHOST.concat([[0.0, 0.0], [0.06, 0.05], [-0.06, 0.05]]).map((g, i) => {
            const [x, y] = planePt(cam, TOKYO[0] + g[0] * 1.3, TOKYO[1] + g[1] * 1.3);
            return <circle key={i} cx={x} cy={y - vanish * (30 + i * 5)} r={12 * (1 - 0.5 * vanish)} fill="#ffe78a" opacity={0.9 * (1 - vanish)} style={{filter: 'blur(' + vanish * 4 + 'px)'}} />;
          })
        : null}

      {/* reference to avoid tree-shaking unused */}
      <circle cx={tx} cy={ty} r={0} />
    </PlaneSvg>
  );
};
