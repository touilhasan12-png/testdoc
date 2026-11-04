import React from 'react';
import {interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {T} from './theme';
import {
  BASE,
  CEN,
  OKI,
  PREFS,
  TOKYO,
  arrow,
  bez,
  camAt,
  ease,
  lcg,
  pathD,
  toScreen,
} from './geo';
import {
  ChapterCard,
  Chip,
  Counter,
  JapanMap,
  Paint,
  Person,
  Pop,
  Pyramid,
  Source,
  Svg,
} from './ui';

// ---------- shared data (all taken from Tokyo-SCRIPT.md SOURCES) ----------
const WARDS_23 = [
  ['Chiyoda', 'Chuo', 'Minato', 'Shinjuku', 'Bunkyo'],
  ['Taito', 'Sumida', 'Koto', 'Shinagawa', 'Meguro'],
  ['Ota', 'Setagaya', 'Shibuya', 'Nakano', 'Suginami'],
  ['Toshima', 'Kita', 'Arakawa', 'Itabashi', 'Nerima'],
  ['Adachi', 'Katsushika', 'Edogawa', '', ''],
];
// 16 "black-hole" wards, in the order they are lit on screen.
const BLACK_HOLE_16 = [
  'Shinjuku', 'Bunkyo', 'Taito', 'Sumida', 'Shinagawa', 'Meguro', 'Ota', 'Setagaya',
  'Shibuya', 'Nakano', 'Suginami', 'Toshima', 'Kita', 'Arakawa', 'Itabashi', 'Nerima',
];

const OLD_PYRAMID = [1.0, 0.98, 0.95, 0.92, 0.88, 0.82, 0.74, 0.62, 0.5, 0.38, 0.25];
const NEW_PYRAMID = [0.55, 0.6, 0.7, 0.8, 0.9, 0.95, 0.92, 0.9, 0.85, 0.7, 0.5];
const MID_PYRAMID = [0.9, 0.95, 0.98, 0.95, 0.9, 0.85, 0.8, 0.7, 0.6, 0.5, 0.4];

// Municipal grid: 1,729 cells, 744 flagged, lit in a seeded random order.
const N_MUN = 1729;
const N_RISK = 744;
const munRank: number[] = new Array(N_MUN).fill(-1);
(() => {
  const rnd = lcg(20240424);
  const idx = Array.from({length: N_MUN}, (_, i) => i);
  for (let i = N_MUN - 1; i > 0; i--) {
    const j = Math.floor(rnd() * (i + 1));
    [idx[i], idx[j]] = [idx[j], idx[i]];
  }
  idx.slice(0, N_RISK).forEach((m, r) => {
    munRank[m] = r;
  });
})();

// ---------- 1. COLD OPEN (local 0..1046) ----------
export const ColdOpen: React.FC = () => {
  const f = useCurrentFrame();
  const cam = camAt(f, [
    [0, BASE],
    [700, BASE],
    [1046, {s: 2.2, fx: 318, fy: 280}],
  ]);
  const paint = (id: string, _cx: number, idx: number): Paint =>
    id === 'tokyo'
      ? {fill: T.blue, op: ease(f, 56, 84)}
      : {fill: T.red, op: ease(f, 4 + idx * 0.8, 22 + idx * 0.8)};
  const tk = toScreen(BASE, TOKYO.cx, TOKYO.cy);
  const glowR = ease(f, 60, 120, 0, 30);
  return (
    <>
      <Svg>
        <defs>
          <radialGradient id="tokyoGlow">
            <stop offset="0%" stopColor="#7fd3ff" stopOpacity={0.95} />
            <stop offset="100%" stopColor="#7fd3ff" stopOpacity={0} />
          </radialGradient>
        </defs>
        <JapanMap cam={cam} paint={paint}>
          <circle cx={TOKYO.cx} cy={TOKYO.cy} r={glowR} fill="url(#tokyoGlow)" opacity={ease(f, 60, 90)} />
        </JapanMap>
      </Svg>

      <Pop start={30} style={{left: 80, top: 96}}>
        <div style={{fontSize: 22, letterSpacing: 4, color: T.mute}}>DEATHS MINUS BIRTHS · 2025</div>
        <div style={{fontSize: 150, fontWeight: 800, lineHeight: 1}}>
          <Counter to={918253} start={40} dur={110} prefix="−" />
        </div>
      </Pop>

      {f >= 150 && f < 172 && (
        <div
          style={{
            position: 'absolute',
            left: tk.x - 280,
            top: tk.y - 190,
            width: 560,
            textAlign: 'center',
            border: `8px solid ${T.red}`,
            color: T.red,
            fontFamily: T.font,
            fontSize: 92,
            fontWeight: 900,
            letterSpacing: 6,
            padding: '8px 0',
            background: 'rgba(7,13,24,0.5)',
            transform: `rotate(-7deg) scale(${interpolate(f, [150, 156], [1.5, 1], {
              extrapolateLeft: 'clamp',
              extrapolateRight: 'clamp',
            })})`,
            opacity: interpolate(f, [150, 153, 166, 172], [0, 1, 1, 0], {
              extrapolateLeft: 'clamp',
              extrapolateRight: 'clamp',
            }),
          }}
        >
          BLACK HOLE
        </div>
      )}

      <Chip start={300} style={{left: 1270, top: 150}}>
        46 of 47 prefectures: Japanese residents are falling
      </Chip>
      <Chip start={470} style={{left: 1270, top: 260}} color={T.blue}>
        Tokyo is the only prefecture where Japanese residents rose: +12,540 (+0.09%)
      </Chip>

      <Source text="MHLW 2025 preliminary vital statistics (Jun 2026) · MIC resident register (Jul 2026)" />
    </>
  );
};

// ---------- 2. ARROWS (local 0..752, global 1047..1799) ----------
export const Arrows: React.FC = () => {
  const f = useCurrentFrame();
  const ids = PREFS.map((p) => p.id).filter((id) => id !== 'tokyo');
  const paint = (id: string): Paint => (id === 'tokyo' ? {fill: T.blue} : {fill: T.land});
  return (
    <>
      <Svg>
        <JapanMap cam={BASE} paint={paint}>
          {ids.map((id, i) => {
            const p = ease(f, 30 + i * 3, 70 + i * 3);
            return (
              <path
                key={'a' + id}
                d={pathD(arrow(id))}
                pathLength={100}
                fill="none"
                stroke={T.cyan}
                strokeWidth={2.2}
                strokeOpacity={0.8}
                strokeLinecap="round"
                strokeDasharray={100}
                strokeDashoffset={100 * (1 - p)}
              />
            );
          })}
          {ids.map((id, i) => {
            const k = (((f + i * 7 - 200) % 60) + 60) % 60;
            const pt = bez(arrow(id), k / 60);
            return <circle key={'d' + id} cx={pt.x} cy={pt.y} r={1.4} fill={T.gold} opacity={f >= 200 ? 1 : 0} />;
          })}
        </JapanMap>
      </Svg>

      <Pop start={120} style={{right: 80, top: 96, textAlign: 'right'}}>
        <div style={{fontSize: 22, letterSpacing: 4, color: T.mute}}>NET MOVE INTO TOKYO · 2025</div>
        <div style={{fontSize: 132, fontWeight: 800, color: T.cyan, lineHeight: 1.05}}>
          <Counter to={65219} start={130} dur={70} prefix="+" />
        </div>
      </Pop>

      <Chip start={420} style={{right: 80, top: 330, textAlign: 'left'}} color={T.gold}>
        Largest net group: age 20–24 (2024 data; the 2025 age split was not found)
      </Chip>

      <ChapterCard label="ACT 1 · THE PARADOX" title="Where the young go" end={100} />
      <Source text="MIC Basic Resident Register migration reports via nippon.com / Japan Times (2025). Arrow directions schematic, widths not to scale per prefecture." />
    </>
  );
};

// ---------- 3. FERTILITY (local 0..755, global 1800..2555) ----------
export const Fertility: React.FC = () => {
  const f = useCurrentFrame();
  const sweep = interpolate(f, [0, 36], [-200, 700], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const paint = (id: string, cx: number): Paint => {
    if (cx < sweep) {
      if (id === 'tokyo') return {fill: T.redDeep};
      if (id === 'okinawa') return {fill: '#21c59a'};
      return {fill: T.grey};
    }
    return id === 'tokyo' ? {fill: T.blue} : {fill: T.land};
  };
  const tk = toScreen(BASE, TOKYO.cx, TOKYO.cy);
  const ok = toScreen(BASE, OKI.cx, OKI.cy);
  return (
    <>
      <Svg>
        <JapanMap cam={BASE} paint={paint} />
        {/* scanline that flips the map from migration to fertility */}
        <rect
          x={960 + (sweep - BASE.fx) * BASE.s}
          y={0}
          width={4}
          height={1080}
          fill={T.cyan}
          opacity={f > 0 && f < 36 ? 0.8 : 0}
        />
      </Svg>

      <Pop start={20} style={{left: 80, top: 96}}>
        <div style={{fontSize: 22, letterSpacing: 4, color: T.mute}}>JAPAN · TOTAL FERTILITY 2025</div>
        <div style={{fontSize: 150, fontWeight: 800, lineHeight: 1}}>
          <Counter to={1.14} dec={2} start={30} dur={60} />
        </div>
        <div style={{fontSize: 24, color: T.mute}}>record low, 10th straight year</div>
      </Pop>

      <Pop start={110} style={{left: tk.x + 60, top: tk.y - 130}}>
        <div style={{fontSize: 34, fontWeight: 800, color: '#ff8a80'}}>TOKYO · 0.96</div>
        <div style={{fontSize: 22, color: T.ink}}>lowest in Japan</div>
      </Pop>
      <Pop start={160} style={{left: ok.x + 40, top: ok.y - 70}}>
        <div style={{fontSize: 34, fontWeight: 800, color: '#21c59a'}}>OKINAWA · 1.52</div>
        <div style={{fontSize: 22, color: T.ink}}>highest in Japan</div>
      </Pop>

      <Chip start={250} style={{left: 1270, top: 260}} color={T.red}>
        Tokyo: below 1.0 for the third straight year — 0.99 (2023) · 0.96 (2024) · 0.96 (2025)
      </Chip>

      <Pop start={300} style={{left: 1370, top: 580, fontSize: 20, color: T.mute, letterSpacing: 2}}>
        AGE SHAPE · SCHEMATIC, 1990 → 2025
      </Pop>
      <svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{position: 'absolute', left: 0, top: 0}}>
        <g opacity={ease(f, 300, 330)}>
          <Pyramid x={1420} y={620} w={170} h={300} from={OLD_PYRAMID} to={NEW_PYRAMID} p={ease(f, 330, 600)} color={T.blue} />
          <Pyramid x={1660} y={620} w={170} h={300} from={OLD_PYRAMID} to={MID_PYRAMID} p={ease(f, 330, 600)} color={T.gold} />
        </g>
      </svg>
      <Pop start={330} style={{left: 1400, top: 940, fontSize: 24, color: T.ink}}>
        <span style={{color: T.blue}}>Tokyo</span> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <span style={{color: T.gold}}>Okinawa</span>
      </Pop>

      <Source text="MHLW prelim. 2025 vital statistics (Jun 2026) via nippon.com · Okinawa 1.52 per the same series. Pyramid shapes are illustrative, not census data." />
    </>
  );
};

// ---------- 4. PARADOX (local 0..651, global 2556..3207) ----------
const PARADOX_TEXT = 'THE PARADOX';
export const Paradox: React.FC = () => {
  const f = useCurrentFrame();
  const ids = PREFS.map((p) => p.id).filter((id) => id !== 'tokyo');
  const paint = (id: string): Paint => (id === 'tokyo' ? {fill: T.blue} : {fill: T.dim});
  return (
    <>
      <Svg>
        <JapanMap cam={BASE} paint={paint}>
          {ids.map((id) => (
            <path
              key={'pa' + id}
              d={pathD(arrow(id))}
              fill="none"
              stroke={T.cyan}
              strokeWidth={1.6}
              strokeOpacity={0.35}
            />
          ))}
          {ids.map((id, i) => {
            if (i % 2 === 1) return null;
            const k = (((f + i * 9) % 90) + 90) % 90;
            const pt = bez(arrow(id), k / 90);
            return <circle key={'yd' + id} cx={pt.x} cy={pt.y} r={2.2} fill={T.gold} opacity={f >= 40 ? 1 : 0} />;
          })}
        </JapanMap>
      </Svg>

      <ChapterCard label="ACT 1 · THE PARADOX" title="Two facts that don't fit" end={100} />

      <Pop start={30} style={{left: 80, top: 360, width: 520}}>
        <div style={{fontSize: 22, letterSpacing: 4, color: T.mute}}>AGE 20–24 · BIGGEST INFLOW GROUP</div>
        <div style={{fontSize: 130, fontWeight: 800, color: T.gold, lineHeight: 1}}>20–24</div>
        <div style={{fontSize: 24, color: T.ink}}>young adults flowing into Tokyo</div>
      </Pop>
      <Pop start={150} style={{right: 80, top: 360, width: 520, textAlign: 'right'}}>
        <div style={{fontSize: 22, letterSpacing: 4, color: T.mute}}>TOKYO FERTILITY · 2025</div>
        <div style={{fontSize: 130, fontWeight: 800, color: '#ff8a80', lineHeight: 1}}>0.96</div>
        <div style={{fontSize: 24, color: T.ink}}>the lowest in the country</div>
      </Pop>

      <div
        style={{
          position: 'absolute',
          left: 0,
          top: 820,
          width: 1920,
          textAlign: 'center',
          fontFamily: T.font,
          fontSize: 96,
          fontWeight: 900,
          letterSpacing: 10,
        }}
      >
        {PARADOX_TEXT.split('').map((c, i) => (
          <span key={i} style={{opacity: ease(f, 240 + i * 3, 252 + i * 3)}}>
            {c === ' ' ? '\u00a0' : c}
          </span>
        ))}
      </div>

      <Chip start={420} style={{left: 80, top: 960 - 90, maxWidth: 1000}} color={T.gold}>
        2024 · Population Strategy Council: a private policy group, not the government
      </Chip>

      <Source text="MIC Basic Resident Register (2024–2025) · MHLW 2025 prelim. (TFR) · Population Strategy Council (Apr 2024)" />
    </>
  );
};

// ---------- 5. DIVE (local 0..831, global 3208..4039) ----------
export const Dive: React.FC = () => {
  const f = useCurrentFrame();
  const cam = camAt(f, [
    [0, BASE],
    [110, {s: 5, fx: 300, fy: 270}],
    [300, {s: 10, fx: TOKYO.cx, fy: TOKYO.cy}],
    [470, {s: 12, fx: TOKYO.cx, fy: TOKYO.cy}],
    [600, {s: 12, fx: TOKYO.cx, fy: TOKYO.cy}],
    [800, BASE],
  ]);
  const paint = (id: string): Paint => (id === 'tokyo' ? {fill: '#2f74c4'} : {fill: T.dim});
  return (
    <>
      <Svg>
        <JapanMap cam={cam} paint={paint}>
          <circle cx={TOKYO.cx + 1.6} cy={TOKYO.cy + 0.4} r={0.9} fill={T.red} opacity={ease(f, 380, 400)} />
          <text x={TOKYO.cx + 2.8} y={TOKYO.cy - 0.8} fontSize={1.5} fill={T.ink} fontFamily={T.font} fontWeight={700} opacity={ease(f, 380, 400)}>
            SHINJUKU
          </text>
        </JapanMap>
      </Svg>

      <ChapterCard label="REASON 1 · THE SPACE SQUEEZE" title="Dive into Tokyo" end={100} />

      <Chip start={390} style={{right: 80, top: 150}} color={T.red}>
        SHINJUKU — one of 16 “black hole” wards
      </Chip>
      <Chip start={520} style={{right: 80, top: 260}}>
        Tiny apartments, some of Japan’s most expensive square meters, and commutes that can eat nearly two hours a day
      </Chip>

      <Source text="Ward grid schematic, not to scale · Tokyo average one-way commute ~47.5 min (2021 survey via secondary source) · Population Strategy Council (Apr 2024)" />
    </>
  );
};

// ---------- 6. AKIYA (local 0..840, global 4040..4880) ----------
const HOUSE = 'M-5,0 L0,-5 L5,0 V5 H-5 Z';
export const Akiya: React.FC = () => {
  const f = useCurrentFrame();
  const paint = (id: string): Paint => (id === 'tokyo' ? {fill: '#2f74c4'} : {fill: T.dim});
  // three schematic house icons per prefecture; ~43% turn red (3.856 / 9.002 M abandoned)
  const houses: React.ReactNode[] = [];
  PREFS.forEach((p, i) => {
    const c = CEN[p.id];
    for (let k = 0; k < 3; k++) {
      const n = i * 3 + k;
      const x = c.cx + (((k * 37 + i * 13) % 9) - 4) * (c.w / 12);
      const y = c.cy + (((k * 29 + i * 17) % 9) - 4) * (c.h / 12);
      const abandoned = n % 7 < 3;
      const appear = ease(f, 30 + n * 2, 40 + n * 2);
      const turn = abandoned ? ease(f, 220 + n * 0.5, 230 + n * 0.5) : 0;
      houses.push(
        <g key={'h' + n} transform={`translate(${x} ${y}) scale(0.55)`} opacity={appear}>
          <path d={HOUSE} fill="#8fa0ba" />
          <path d={HOUSE} fill={T.red} opacity={turn} />
        </g>,
      );
    }
  });
  const segs = [
    {v: 4.436, c: T.blue, l: 'For rent 4.44M'},
    {v: 0.326, c: T.cyan, l: 'For sale 0.33M'},
    {v: 0.384, c: T.green, l: 'Second homes 0.38M'},
    {v: 3.856, c: T.red, l: 'Other / abandoned 3.86M'},
  ];
  const barX = 120;
  const barW = 1680;
  const total = 9.002;
  let acc = 0;
  return (
    <>
      <Svg>
        <JapanMap cam={BASE} paint={paint}>
          {houses}
        </JapanMap>
        {segs.map((s, i) => {
          const x = barX + (acc / total) * barW;
          acc += s.v;
          const w = (s.v / total) * barW * ease(f, 300 + i * 25, 340 + i * 25);
          return <rect key={'seg' + i} x={x} y={900} width={w} height={40} fill={s.c} />;
        })}
      </Svg>

      <Pop start={40} style={{left: 80, top: 96}}>
        <div style={{fontSize: 22, letterSpacing: 4, color: T.mute}}>VACANT HOMES · 2023</div>
        <div style={{fontSize: 140, fontWeight: 800, lineHeight: 1}}>
          <Counter to={9.002} dec={3} start={50} dur={170} suffix="M" />
        </div>
        <div style={{fontSize: 24, color: T.mute}}>13.8% of all homes · doubled since 1993</div>
      </Pop>

      <Pop start={230} style={{left: 80, top: 390}}>
        <div style={{fontSize: 22, letterSpacing: 4, color: '#ff8a80'}}>FULLY ABANDONED</div>
        <div style={{fontSize: 90, fontWeight: 800, color: T.red, lineHeight: 1}}>
          <Counter to={3.856} dec={3} start={240} dur={80} suffix="M" />
        </div>
      </Pop>

      <Chip start={380} style={{right: 80, top: 150}} color={T.gold}>
        Not every vacant home is abandoned: 4.44M are for rent, 0.33M for sale, 0.38M second homes
      </Chip>
      <Chip start={520} style={{right: 80, top: 300}} color={T.cyan}>
        Japan has more homes than households: 65.0M homes vs 56.2M households
      </Chip>
      <Chip start={640} style={{right: 80, top: 400}}>
        Tokyo itself: about 898,000 vacant homes (10.9%)
      </Chip>

      <Pop start={300} style={{left: 120, top: 960, fontSize: 20, color: T.ink}}>
        {segs.map((s) => (
          <span key={s.l} style={{marginRight: 28, color: s.c}}>
            ■ {s.l}
          </span>
        ))}
      </Pop>

      <ChapterCard label="REASON 1 · CONTINUED" title="The empty side" end={100} />
      <Source text="MIC Housing and Land Survey 2023 (via japan.co.jp, ISVD) · house icons schematic, placement not geographic" />
    </>
  );
};

// ---------- 7. TIME SQUEEZE (local 0..1269, global 4881..6150) ----------
export const TimeSqueeze: React.FC = () => {
  const f = useCurrentFrame();
  const cam = camAt(f, [
    [0, BASE],
    [120, {s: 3.2, fx: TOKYO.cx, fy: TOKYO.cy}],
    [1269, {s: 3.6, fx: TOKYO.cx, fy: TOKYO.cy - 2}],
  ]);
  const paint = (id: string): Paint => (id === 'tokyo' ? {fill: T.blue} : {fill: T.dim});
  const tk = toScreen(cam, TOKYO.cx, TOKYO.cy);
  const ringR = interpolate(f, [80, 240], [280, 120], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const ringOp = ease(f, 80, 110);
  const bars = [
    {label: '2019 (≈)', v: 599000, c: T.dim},
    {label: '2024 (derived)', v: 485092, c: T.blue},
    {label: '2025', v: 489119, c: T.cyan},
  ];
  return (
    <>
      <Svg>
        <JapanMap cam={cam} paint={paint} />
        <circle cx={tk.x} cy={tk.y} r={ringR} fill="none" stroke={T.gold} strokeWidth={10} opacity={ringOp} strokeDasharray="1200 400" />
        <g opacity={ringOp}>
          <Person x={tk.x} y={tk.y} s={2.4} color={T.gold} />
        </g>
        {bars.map((b, i) => {
          const h = (b.v / 600000) * 240 * ease(f, 460 + i * 20, 520 + i * 20);
          return <rect key={'mb' + i} x={1300 + i * 170} y={900 - h} width={120} height={h} fill={b.c} />;
        })}
      </Svg>

      <ChapterCard label="REASON 2 · THE TIME SQUEEZE" title="Hours that leave nothing behind" end={100} />

      <Pop start={280} style={{left: 80, top: 96}}>
        <div style={{fontSize: 22, letterSpacing: 4, color: T.mute}}>AVERAGE AGE · FIRST-TIME MOTHER</div>
        <div style={{fontSize: 140, fontWeight: 800, lineHeight: 1, color: T.gold}}>
          <Counter to={31} dec={1} from={20} start={290} dur={120} />
        </div>
        <div style={{fontSize: 24, color: T.mute}}>2025 · same as 2024</div>
      </Pop>

      <Pop start={460} style={{left: 1300, top: 600, fontSize: 22, color: T.mute, letterSpacing: 2}}>MARRIAGES PER YEAR</Pop>
      <Pop start={460} style={{left: 1290, top: 912, fontSize: 19, color: T.ink, width: 600}}>
        <span style={{marginRight: 40}}>2019 ≈599k</span>
        <span style={{marginRight: 40}}>2024 485k</span>
        <span>2025 489k</span>
      </Pop>

      <Chip start={760} style={{left: 80, top: 360}} color={T.red}>
        Outside marriage: 2.4% of births (OECD 2023), so under 3%, and late marriage is low fertility
      </Chip>
      <Chip start={900} style={{left: 80, top: 520}} color={T.green}>
        Marriages rose for a second year in a row, but the curve has not bent yet
      </Chip>

      <Source text="MHLW 2025 vital statistics via Shaho/PNA/nippon.com (marriages 489,119, +4,027) · OECD Family Database SF2.4 · 2024 value derived from the +4,027 change" />
    </>
  );
};

// ---------- 8. MACHINE (local 0..1558, global 6151..7709) ----------
const N_COLS = 61;
const CELL = 14;
const PITCH = 17;
const GX = 443;
const GY = 262;
export const Machine: React.FC = () => {
  const f = useCurrentFrame();
  const mapOp = 1 - 0.85 * ease(f, 560, 600) + 0.85 * ease(f, 1100, 1140);
  const gridOp = ease(f, 600, 620) - ease(f, 1080, 1110);
  const akita = arrow('akita');
  const traveller = bez(akita, ease(f, 120, 200));
  const travellerOp = interpolate(f, [120, 130, 196, 206], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const akitaShrink = 1 - 0.55 * ease(f, 200, 330);
  const tokyoShrink = 1 - 0.03 * ease(f, 200, 330);
  const paint = (id: string): Paint => (id === 'tokyo' ? {fill: T.blue} : {fill: T.dim});
  const cells: React.ReactNode[] = [];
  for (let i = 0; i < N_MUN; i++) {
    const rank = munRank[i];
    const col = i % N_COLS;
    const row = Math.floor(i / N_COLS);
    const lit = rank >= 0 ? ease(f, 620 + rank * 0.6, 626 + rank * 0.6) : 0;
    cells.push(
      <rect
        key={i}
        x={GX + col * PITCH}
        y={GY + row * PITCH}
        width={CELL}
        height={CELL}
        rx={2}
        fill={T.land}
      />,
    );
    if (rank >= 0) {
      cells.push(
        <rect
          key={'r' + i}
          x={GX + col * PITCH}
          y={GY + row * PITCH}
          width={CELL}
          height={CELL}
          rx={2}
          fill={T.red}
          opacity={lit}
        />,
      );
    }
  }
  return (
    <>
      <Svg>
        <JapanMap cam={BASE} paint={paint} opacity={mapOp}>
          <Person x={traveller.x} y={traveller.y} s={0.24} color={T.gold} op={travellerOp} />
        </JapanMap>
        <g opacity={gridOp}>
          <rect x={GX - 16} y={GY - 16} width={N_COLS * PITCH} height={29 * PITCH} fill="#070d18" fillOpacity={0.8} rx={8} />
          {cells}
        </g>
      </Svg>

      <ChapterCard label="REASON 3 · THE MIGRATION MACHINE" title="It eats twice" end={100} />

      <Pop start={20} style={{left: 80, top: 96}}>
        <div style={{fontSize: 22, letterSpacing: 4, color: T.mute}}>THE MACHINE, ANIMATED</div>
      </Pop>

      <Chip start={300} style={{right: 80, top: 150}} color={T.gold}>
        Her hometown loses her, and the children she might have had there
      </Chip>
      <Chip start={420} style={{right: 80, top: 260}} color={T.red}>
        Tokyo doesn’t gain those children either: fertility there is the lowest in Japan
      </Chip>

      <Pop start={620} style={{left: GX - 16, top: 130, fontSize: 30, fontWeight: 800}}>
        1,729 MUNICIPALITIES · <span style={{color: '#ff8a80'}}>744 AT RISK</span> BY 2050 (43%)
      </Pop>
      <Pop start={600} style={{left: GX - 16, top: 800, width: 1100}}>
        <Counter to={744} start={640} dur={440} style={{fontSize: 46, fontWeight: 800, color: '#ff8a80'}} />
        <span style={{fontSize: 24, color: T.mute, marginLeft: 16}}>each square is one municipality · order schematic, not geographic</span>
      </Pop>
      <Chip start={1090} style={{left: GX - 16, top: 890}} color={T.red}>
        PROJECTION · women aged 20–39 halved, 2020 → 2050 (Population Strategy Council)
      </Chip>

      <Chip start={1200} style={{right: 80, top: 150}} color={T.red}>
        The births vanish: Tokyo is where fertility drops below one
      </Chip>

      <Source text="Population Strategy Council (Apr 2024), a private body; 744 of 1,729 municipalities; Tokyo Shimbun (Apr 24, 2024) · projections are scenarios" />
    </>
  );
};

// ---------- 9. BLACK HOLE + calm hold (local 0..1289, global 7710..8999) ----------
export const BlackHole: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const cam = camAt(f, [
    [0, BASE],
    [220, {s: 4.6, fx: TOKYO.cx, fy: TOKYO.cy}],
    [1289, {s: 4.9, fx: TOKYO.cx + 1, fy: TOKYO.cy + 1}],
  ]);
  const paint = (id: string): Paint => (id === 'tokyo' ? {fill: T.red} : {fill: T.dim});
  const stamp = spring({frame: f, fps, config: {damping: 12, stiffness: 180}});
  const stampScale = interpolate(stamp, [0, 1], [1.8, 1]);
  const stampOp = ease(f, 6, 14);
  return (
    <>
      <Svg>
        <JapanMap cam={cam} paint={paint} opacity={0.55} />
      </Svg>

      <div
        style={{
          position: 'absolute',
          left: 440,
          top: 96,
          width: 1080,
          textAlign: 'center',
          whiteSpace: 'nowrap',
          fontFamily: T.font,
          fontSize: 50,
          fontWeight: 900,
          color: T.red,
          border: `9px solid ${T.red}`,
          padding: '6px 0',
          background: 'rgba(7,13,24,0.6)',
          opacity: stampOp,
          transform: `rotate(-3deg) scale(${stampScale})`,
          letterSpacing: 3,
        }}
      >
        BLACK-HOLE MUNICIPALITIES · 25
      </div>
      <Pop start={40} style={{left: 440, top: 226, width: 1040, textAlign: 'center', fontSize: 26, color: T.mute}}>
        Population Strategy Council · private body · April 2024 · 16 of them are Tokyo wards
      </Pop>

      <Pop start={130} style={{left: 80, top: 96}}>
        <div style={{fontSize: 22, letterSpacing: 4, color: T.mute}}>TOKYO WARDS FLAGGED</div>
        <div style={{fontSize: 140, fontWeight: 800, lineHeight: 1, color: '#ff8a80'}}>
          <Counter to={16} start={150} dur={700} />
          <span style={{fontSize: 60, color: T.ink}}> / 23</span>
        </div>
      </Pop>

      <div style={{position: 'absolute', left: 0, top: 0, width: 1920, height: 1080}}>
        {WARDS_23.map((row, r) =>
          row.map((name, c) => {
            if (!name) return null;
            const litIdx = BLACK_HOLE_16.indexOf(name);
            const lit = litIdx >= 0;
            const start = 150 + litIdx * 45;
            const x = 561 + c * 162;
            const y = 300 + r * 108;
            return (
              <div
                key={name}
                style={{
                  position: 'absolute',
                  left: x,
                  top: y,
                  width: 150,
                  height: 96,
                  borderRadius: 8,
                  background: '#101a2c',
                  border: `1.5px solid ${lit ? T.red : '#24406a'}`,
                  boxSizing: 'border-box',
                  overflow: 'hidden',
                  fontFamily: T.font,
                  fontSize: 22,
                  fontWeight: 700,
                  color: lit ? T.ink : T.mute,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  textAlign: 'center',
                }}
              >
                <div
                  style={{
                    position: 'absolute',
                    inset: 0,
                    background: 'linear-gradient(135deg, #e5483b, #7e1714)',
                    opacity: lit ? ease(f, start, start + 10) : 0,
                  }}
                />
                <span style={{position: 'relative'}}>{name}</span>
              </div>
            );
          }),
        )}
      </div>

      <Pop start={1000} end={1289} style={{left: 80, top: 880, maxWidth: 1100}}>
        <div
          style={{
            background: 'rgba(7,13,24,0.84)',
            border: `1.5px solid ${T.cyan}`,
            borderRadius: 10,
            padding: '14px 22px',
            fontSize: 27,
            lineHeight: 1.3,
          }}
        >
          Some researchers criticize the council’s method and its “extinction” label (RIETI). Either way, the arithmetic is brutal.
        </div>
      </Pop>

      <ChapterCard label="REASON 3 · THE BLACK HOLE" title="Sixteen of twenty-three" end={100} />
      <Source text="Population Strategy Council (Apr 2024, private body) via Tokyo Shimbun, ISVD, Japanese Wikipedia · ward grid schematic, not to scale · labels not geographic" />
    </>
  );
};
