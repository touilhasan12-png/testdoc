import React from 'react';
import {Img, staticFile} from 'remotion';
import {C, Chip, ChipSub, ChipTitle, Counter, Cutout, Float07, FONT, GLOW, GLOW_BLUE, GLOW_GOLD, Label, Leader, Perspective, PhotoInner, RedX, Stamp, Typed} from '../components/ui';
import {ArcRing, BigNumber, Columns, DotRows, FlowChevrons, Gauge, LineChart, StackBar, Waffle, horizBar} from '../components/viz';
import {Paper05} from '../components/Paper05';
import timeline from '../data/timeline.json';
import {FLAGGED_16, HOMETOWN, PREFS, SHINJUKU, TOKYO, WARDS, clamp01, curvePt, eo3, fmt, item, life, metersPerPx, on, planePt, planeToScreen, pref, prog, toScreen} from '../lib/core';
import {useStage} from '../lib/ctx';

const Rule: React.FC<{c: string}> = ({c}) => <span style={{display: 'inline-block', width: 22, height: 22, background: c, marginRight: 10, borderRadius: 4, verticalAlign: -3, boxShadow: `0 0 12px ${c}`}} />;

// ======================================================= UNIT 1  (VO 01)
const Unit1: React.FC = () => {
  const {frame: f, cam} = useStage();
  const [tx, ty] = toScreen(cam, TOKYO[0], TOKYO[1]);
  return (
    <>
      <Perspective>
        <Float07 id="cnt918" x={110} y={200} vx={26} vy={-18}>
          {(l) => (
            <BigNumber
              value={'−' + fmt(918253 * eo3(prog(l, 4, 78)))}
              label="NATURAL DECREASE · JAPAN · 2025"
              sub="BIRTHS 671,236 − DEATHS 1,589,489"
              size={176}
              color={C.cream}
            />
          )}
        </Float07>
        <Float07 id="p46" x={110} y={170} vx={26} vy={-16} glow={GLOW}>
          {(l) => (
            <div>
              <BigNumber value={`${Math.round(46 * eo3(prog(l, 6, 64)))} / 47`} label="PREFECTURES LOSING JAPANESE RESIDENTS" size={150} />
              <div style={{marginTop: 26}}>
                <DotRows local={l} rows={[{n: 46, color: C.red}, {n: 1, color: C.blue}]} dot={24} gap={12} perRow={12} />
              </div>
            </div>
          )}
        </Float07>
        <Float07 id="tokyo_up" x={110} y={300} vx={30} vy={-18} glow={GLOW_BLUE}>
          {() => <BigNumber value="+12,540" label="TOKYO · POPULATION · 2026" sub="+0.09% · THE ONE PLACE STILL GROWING" size={150} color="#d9efff" />}
        </Float07>
      </Perspective>
      <Leader id="tokyo_up" from={[640, 470]} to={[tx, ty]} color={C.blue} delay={14} />

      <Stamp id="stamp1" x={960} y={500} size={150} sub="POPULATION STRATEGY COUNCIL · 2024">BLACK HOLE</Stamp>

      <Cutout photo="sf_skyline" id="sf_photo" x={1060} y={90} w={780} from="right" rot={2} dissolveAt={262} dissolveDur={36} />
      <Chip id="sf_photo" x={1090} y={700} accent={C.amber} from="bottom" w={700}>
        <ChipTitle size={40}>Bigger than San Francisco</ChipTitle>
        <ChipSub size={24}>San Francisco · 873,965 residents (2020 census)</ChipSub>
      </Chip>
      <Chip id="gone_chip" x={1090} y={300} accent={C.red} from="right" w={700}>
        <ChipTitle size={60} color={C.redSoft}>Gone in 12 months</ChipTitle>
      </Chip>

      <Cutout photo="lifeboat" id="lifeboat" x={1050} y={250} w={780} from="right" rot={-2} />
      <RedX id="lifeboat_x" x={1160} y={410} w={540} h={250} />
      <Chip id="lifeboat" x={1050} y={110} accent={C.amber} from="right" w={780}>
        <ChipTitle size={44}>Tokyo isn’t Japan’s lifeboat</ChipTitle>
      </Chip>

      <Chip id="council_chip" x={100} y={170} accent={C.red} w={820}>
        <ChipSub size={24} color={C.yellow}>A leading independent policy council</ChipSub>
        <ChipTitle size={46}>Population Strategy Council</ChipTitle>
        <ChipSub size={24}>Private · April 2024 · calls Tokyo a “demographic black hole”</ChipSub>
      </Chip>
      <Chip id="legend1" x={100} y={780} accent={C.blue} from="bottom">
        <div style={{fontSize: 34, fontWeight: 800, letterSpacing: 1.5}}>
          <Rule c={C.red} />Shrinking &nbsp;&nbsp; <Rule c={C.blue} />Growing
        </div>
      </Chip>
    </>
  );
};

// ======================================================= UNIT 2  (VO 02)
const AgeTag: React.FC = () => {
  const {frame: f, cam} = useStage();
  const it = item('age2024');
  if (f < it.f0 + 30 || f > it.f1) return null;
  const a = planePt(cam, 135.5, 34.7);
  const b = planePt(cam, TOKYO[0], TOKYO[1]);
  const [px, py] = curvePt(a, b, 0.15, 0.5);
  const [sx, sy] = planeToScreen(cam, px, py);
  const e = eo3(clamp01((f - it.f0 - 30) / 12)) * (1 - prog(f, it.f1 - 14, it.f1));
  return (
    <div style={{position: 'absolute', left: sx, top: sy, transform: 'translate(-50%,-135%) rotate(-3deg)', fontFamily: FONT, fontWeight: 900, fontSize: 84, color: '#fff3c4', textShadow: GLOW_GOLD, opacity: e, whiteSpace: 'nowrap'}}>20–24</div>
  );
};
const Unit2: React.FC = () => (
  <>
    <AgeTag />
    <Perspective>
      <Float07 id="cnt65" x={110} y={200} vx={30} vy={-20} glow={GLOW_BLUE}>
        {(l) => <FlowChevrons local={l} big={'+' + fmt(65219 * eo3(prog(l, 4, 50)))} label="Tokyo net migration · 2025" target="TOKYO" />}
      </Float07>
      <Float07 id="bars_yoy" x={1010} y={210} vx={-30} vy={-24} rx={6} ry={-8}>
        {(l) => (
          <Columns
            local={l}
            title="Tokyo net inflow"
            max={79285}
            cols={[
              {label: '2024', value: 79285, text: '79,285', color: '#8fb8ff'},
              {label: '2025', value: 65219, text: '65,219', color: '#ff766e'},
            ]}
          />
        )}
      </Float07>
      <Float07 id="age2024" x={110} y={200} vx={28} vy={-20}>
        {(l) => (
          <div style={{width: 760}}>
            <BigNumber value="20–24" label="Largest group moving to Tokyo" size={190} />
            <div style={{marginTop: 30}}>{horizBar(0.808 * eo3(prog(l, 14, 56)), '#ffd75e', 700, 30)}</div>
            <div style={{marginTop: 14, fontSize: 25, fontWeight: 750, letterSpacing: 1.3, textTransform: 'uppercase'}}>64,070 of 79,285 net inflow · 2024</div>
          </div>
        )}
      </Float07>
    </Perspective>
    <Chip id="rank1" x={100} y={800} accent={C.blue} from="bottom">
      <ChipTitle size={42}>#1 net inflow of any prefecture</ChipTitle>
      <ChipSub size={24}>Slower than 2024 — still the biggest</ChipSub>
    </Chip>
    <Cutout photo="young_adults" id="young_photo" x={1110} y={380} w={720} from="right" rot={2} />
    <Chip id="corners" x={100} y={820} accent={C.amber} from="bottom">
      <ChipTitle size={40}>Draining from nearly every corner</ChipTitle>
    </Chip>
  </>
);

// ======================================================= UNIT 3  (VO 03)
const Unit3: React.FC = () => {
  const {frame: f, cam} = useStage();
  const [tx, ty] = toScreen(cam, TOKYO[0], TOKYO[1]);
  const ok = pref('Okinawa').c;
  const [ox, oy] = toScreen(cam, ok[0], ok[1]);
  const scan = prog(f, 1800, 1850);
  return (
    <>
      {f >= 1800 && f <= 1860 ? (
        <div style={{position: 'absolute', left: 1920 * scan - 6, top: 0, width: 12, height: 1080, background: 'linear-gradient(180deg, transparent, #fff, transparent)', boxShadow: '0 0 40px 10px rgba(255,255,255,.5)', opacity: 1 - prog(f, 1850, 1860)}} />
      ) : null}
      <Chip id="flip" x={100} y={120} accent={C.cream} from="left">
        <ChipTitle size={46}>Now: babies per woman</ChipTitle>
        <ChipSub size={24}>Total fertility rate by prefecture</ChipSub>
      </Chip>
      <Perspective>
        <Float07 id="nat114" x={110} y={260} vx={30} vy={-20}>
          {() => <BigNumber value="1.14" label="Japan · total fertility rate · 2025" sub="10th straight record low" size={190} />}
        </Float07>
        <Float07 id="tokyo096" x={1040} y={150} vx={26} vy={-18} glow={GLOW}>
          {() => <BigNumber value="0.96" label="Tokyo · lowest in Japan" size={190} color="#ffd0cc" />}
        </Float07>
        <Float07 id="third_year" x={1060} y={500} vx={-26} vy={-16} rx={6} ry={-8}>
          {(l) => (
            <div style={{width: 760}}>
              <Label>Tokyo · third year below 1.0</Label>
              <div style={{marginTop: 8}}>
                <LineChart local={l} w={720} h={330} yMin={0.9} yMax={1.06} thresh={{y: 1.0, label: '1.00 = ONE CHILD PER WOMAN'}} pts={[{x: '2023', y: 0.99}, {x: '2024', y: 0.96}, {x: '2025', y: 0.96}]} />
              </div>
            </div>
          )}
        </Float07>
        <Float07 id="okinawa152" x={110} y={180} vx={28} vy={-18} glow={'0 0 5px #fff, 0 0 18px rgba(52,224,200,.9), 0 0 40px rgba(30,200,170,.5)'}>
          {() => <BigNumber value="1.52" label="Okinawa · highest in Japan" sub="Islands farthest from Tokyo" size={190} color="#c8fff6" />}
        </Float07>
      </Perspective>
      <Leader id="tokyo096" from={[1180, 430]} to={[tx, ty]} color="#ff8d8d" delay={16} />
      <Leader id="okinawa152" from={[640, 330]} to={[ox, oy]} color="#34e0c8" delay={16} />
    </>
  );
};

// ======================================================= UNIT 4  (VO 04)
const Unit4: React.FC = () => (
  <>
    <Perspective>
      <Float07 id="facts_split" x={100} y={210} vx={26} vy={-18} glow={GLOW_BLUE}>
        {() => <BigNumber value="+65,219" label="Young people moved in" size={130} color="#d9efff" />}
      </Float07>
      <Float07 id="facts_split" x={1080} y={210} vx={-26} vy={-18} glow={GLOW}>
        {() => <BigNumber value="0.96" label="Babies per woman in Tokyo" size={130} color="#ffd0cc" />}
      </Float07>
    </Perspective>
    <Cutout photo="couple" id="couple_photo" x={1090} y={290} w={720} from="right" rot={2} />
    <Chip id="couple_photo" x={1090} y={840} accent={C.amber} from="bottom" w={720}>
      <ChipTitle size={38}>Millions of future parents</ChipTitle>
    </Chip>
    <Stamp id="paradox" x={620} y={330} size={130} rot={-5}>The paradox</Stamp>
    <Chip id="named" x={100} y={760} accent={C.red} from="bottom" w={960}>
      <ChipTitle size={42}>2024 · a private council gives it a name</ChipTitle>
      <ChipSub size={24}>Population Strategy Council · April 24, 2024</ChipSub>
    </Chip>
  </>
);

// ======================================================= UNIT 5  (VO 05) signature dive
const Unit5: React.FC = () => {
  const {frame: f, cam} = useStage();
  const visible = f >= 3242 && f < 4040;
  const level = f < 3300 ? 'JAPAN' : f < 3400 ? 'KANTŌ' : f < 3698 ? 'TOKYO · 23 WARDS' : f < 3990 ? 'SHINJUKU' : 'JAPAN';
  const mpp = metersPerPx(cam);
  const target = mpp * 240;
  const nice = [10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000, 500000].reduce((b, v) => (Math.abs(v - target) < Math.abs(b - target) ? v : b), 10);
  const barPx = nice / mpp;
  const [sx, sy] = toScreen(cam, SHINJUKU[0], SHINJUKU[1]);
  return (
    <>
      {visible ? (
        <div style={{position: 'absolute', left: 100, top: 96, fontFamily: FONT, color: C.cream, opacity: clamp01((f - 3242) / 12) * (1 - prog(f, 4020, 4040))}}>
          <div style={{fontSize: 22, fontWeight: 700, letterSpacing: 4, color: C.yellow}}>DIVING IN</div>
          <div style={{fontSize: 62, fontWeight: 900, letterSpacing: -1, textShadow: GLOW, lineHeight: 1.05}}>{level}</div>
          <div style={{marginTop: 16, display: 'flex', alignItems: 'center', gap: 14}}>
            <div style={{width: barPx, height: 10, borderLeft: '4px solid #fff', borderRight: '4px solid #fff', borderBottom: '4px solid #fff', boxShadow: '0 0 10px #000'}} />
            <div style={{fontSize: 24, fontWeight: 800, textShadow: '0 2px 6px #000'}}>{nice >= 1000 ? nice / 1000 + ' km' : nice + ' m'}</div>
          </div>
        </div>
      ) : null}
      <Cutout photo="shinjuku" id="shinjuku_photo" x={100} y={300} w={640} from="left" rot={-2} />
      <Chip id="shinjuku_photo" x={100} y={790} accent={C.amber} from="bottom" w={800}>
        <ChipTitle size={34}>Some of Japan’s priciest square meters</ChipTitle>
      </Chip>
      <Chip id="tiny_chip" x={1100} y={200} accent={C.amber} w={720}>
        <ChipTitle size={42}>Tiny apartments</ChipTitle>
      </Chip>
      <Chip id="lbl_shinjuku" x={1100} y={200} accent={C.red} w={730}>
        <ChipTitle size={60}>Shinjuku</ChipTitle>
        <ChipSub size={24}>One of Tokyo’s 16 “black-hole” wards</ChipSub>
      </Chip>
      <Leader id="lbl_shinjuku" from={[1100, 330]} to={[sx, sy]} color={C.red} delay={8} />
      <Cutout photo="commuters" id="commuters_photo" x={1180} y={470} w={640} from="right" rot={2} />
      <Chip id="commute_chip" x={100} y={700} accent={C.amber} from="bottom" w={880}>
        <ChipTitle size={38}>Commutes can eat nearly 2 hours a day</ChipTitle>
        <ChipSub size={22}>Average one-way ≈ 47.5 min (survey, approx.)</ChipSub>
      </Chip>
    </>
  );
};

// ======================================================= UNIT 6  (VO 06)
const Unit6: React.FC = () => {
  const {cam} = useStage();
  const [tx, ty] = toScreen(cam, TOKYO[0], TOKYO[1]);
  return (
    <>
      <Perspective>
        <Float07 id="cnt9m" x={110} y={200} vx={26} vy={-16}>
          {(l) => (
            <div style={{display: 'flex', alignItems: 'center', gap: 44}}>
              <ArcRing local={l} share={0.138} size={300} color={C.amber} center={<div style={{fontSize: 70, fontWeight: 900}}>13.8%</div>} />
              <BigNumber value={(9.002 * eo3(prog(l, 4, 50))).toFixed(1) + 'M'} label="Empty homes in Japan · 2023" size={160} color={C.cream} />
            </div>
          )}
        </Float07>
        <Float07 id="stack_bar" x={200} y={640} vx={20} vy={-10} rx={4} ry={-5} rz={-2}>
          {(l) => (
            <StackBar
              local={l}
              width={1480}
              hotAt={30}
              segs={[
                {label: 'For rent', value: 4.436, text: '4.44M', color: '#4aa3d8'},
                {label: 'For sale', value: 0.326, text: '326K', color: '#5fd0a0'},
                {label: 'Second homes', value: 0.384, text: '384K', color: '#e0b84a'},
                {label: 'Other · abandoned-type', value: 3.856, text: '3.86M', color: '#ff4a5a', hot: true},
              ]}
            />
          )}
        </Float07>
        <Float07 id="homes_vs_hh" x={110} y={200} vx={26} vy={-16}>
          {(l) => (
            <Columns
              local={l}
              title="Japan · 2023"
              max={65.05}
              colW={200}
              cols={[
                {label: 'Homes', value: 65.05, text: '65.05M', color: '#ffb27a'},
                {label: 'Households', value: 56.2, text: '56.2M', color: '#9ec8ff'},
              ]}
            />
          )}
        </Float07>
      </Perspective>
      <Cutout photo="akiya" id="akiya_photo" x={1190} y={80} w={640} from="right" rot={2} />
      <Chip id="akiya_photo" x={100} y={150} accent={C.red} from="left" w={900}>
        <ChipTitle size={36}>Some old homes sell for under $10,000</ChipTitle>
      </Chip>
      <Chip id="lacks" x={100} y={170} accent={C.amber} w={1000}>
        <div>
          <ChipTitle size={44}>What Japan lacks is people</ChipTitle>
          <LacksLines />
        </div>
      </Chip>
      <Leader id="lacks" from={[900, 330]} to={[tx, ty]} color={C.blue} delay={80} />
    </>
  );
};
const LacksLines: React.FC = () => {
  const {frame: f} = useStage();
  const a = clamp01((f - 4674) / 10);
  const b = clamp01((f - 4746) / 10);
  return (
    <>
      <div style={{marginTop: 12, fontSize: 36, fontWeight: 900, color: '#bfe3ff', textTransform: 'uppercase', opacity: a, transform: `translateX(${(1 - a) * 30}px)`}}>…except one city</div>
      <div style={{marginTop: 10, fontSize: 36, fontWeight: 900, color: C.redSoft, textTransform: 'uppercase', opacity: b, transform: `translateX(${(1 - b) * 30}px)`}}>Too expensive to raise kids in</div>
    </>
  );
};

// ======================================================= UNIT 7  (VO 07)
const DotGrid: React.FC<{local: number; hi: number}> = ({local, hi}) => (
  <svg width={10 * 40} height={10 * 40} style={{overflow: 'visible'}}>
    {Array.from({length: 100}, (_, i) => {
      const e = clamp01((local - i * 0.35) / 8);
      const frac = clamp01(hi - i);
      const col = frac > 0 ? '#ff6a5a' : '#9ec8ff';
      return <circle key={i} cx={(i % 10) * 40 + 20} cy={Math.floor(i / 10) * 40 + 20} r={14 * e * (frac > 0 ? 0.55 + 0.45 * frac : 1)} fill={col} opacity={frac > 0 ? 1 : 0.5} style={frac > 0 ? {filter: 'drop-shadow(0 0 8px #ff6a5a)'} : undefined} />;
    })}
  </svg>
);
const Unit7: React.FC = () => (
  <>
    <Perspective>
      <Float07 id="commute47" x={110} y={200} vx={26} vy={-16}>
        {() => <BigNumber value="≈47.5 min" label="Average one-way commute · Tokyo area" sub="Rail commuters ≈ 70 min (approx.)" size={140} />}
      </Float07>
      <Float07 id="gauge31" x={110} y={290} vx={26} vy={-16}>
        {(l) => <Gauge local={l} label="First-time mother · average age · Japan · 2025" value={31.0} min={28} max={34} />}
      </Float07>
      <Float07 id="outside24" x={110} y={170} vx={26} vy={-16}>
        {(l) => (
          <div style={{display: 'flex', gap: 60, alignItems: 'center'}}>
            <DotGrid local={l} hi={2.4 * eo3(prog(l, 36, 60))} />
            <BigNumber value="2.4%" label="Births outside marriage · Japan" sub="Per 100 births · OECD 2023" size={170} />
          </div>
        )}
      </Float07>
      <Float07 id="marriages" x={1000} y={200} vx={-26} vy={-16} rx={6} ry={-8}>
        {(l) => (
          <Columns
            local={l}
            title="Marriages in Japan"
            max={620000}
            colW={140}
            gap={50}
            height={250}
            cols={[
              {label: '2019', value: 599000, text: '≈599K', color: '#ffb27a'},
              {label: '2024', value: 485092, text: '485,092', color: '#ff766e'},
              {label: '2025', value: 489119, text: '489,119', color: '#9ef0c8', sub: '+4,027'},
            ]}
          />
        )}
      </Float07>
      <Float07 id="flatline" x={110} y={200} vx={26} vy={-16}>
        {(l) => (
          <div style={{width: 980}}>
            <Label>Japan · total fertility rate</Label>
            <div style={{marginTop: 8}}>
              <LineChart local={l} w={940} h={400} yMin={1.0} yMax={1.32} pts={[{x: '2022', y: 1.26}, {x: '2023', y: 1.2}, {x: '2024', y: 1.15}, {x: '2025', y: 1.14}]} />
            </div>
          </div>
        )}
      </Float07>
    </Perspective>
    <Cutout photo="office_worker" id="clock" x={1100} y={260} w={720} from="right" rot={2} />
    <Chip id="clock" x={100} y={220} accent={C.amber} w={820}>
      <ChipTitle size={60}>Tokyo runs on hours</ChipTitle>
      <ChipSub size={24}>Long workdays · long commutes</ChipSub>
    </Chip>
    <Cutout photo="commuters" id="commute47" x={1180} y={360} w={640} from="right" rot={2} />
    <Chip id="flatline" x={1000} y={640} accent={C.red} w={820}>
      <ChipTitle size={42}>One flicker hasn’t bent the curve</ChipTitle>
    </Chip>
    <Chip id="marriages" x={1000} y={720} accent={C.cream} from="bottom" w={700}>
      <ChipTitle size={36}>A flicker of hope</ChipTitle>
    </Chip>
  </>
);

// ======================================================= UNIT 8  (VO 08)
const WomanToken: React.FC = () => {
  const {frame: f, cam} = useStage();
  const it = item('woman_arrow');
  if (f < it.f0 || f > it.f1) return null;
  const a = planePt(cam, HOMETOWN[0], HOMETOWN[1]);
  const b = planePt(cam, TOKYO[0], TOKYO[1]);
  const u = eo3(prog(f, it.f0, it.f0 + 150));
  const [px, py] = curvePt(a, b, 0.12, u);
  const [sx, sy, s] = planeToScreen(cam, px, py);
  const w = 250 * Math.min(1.15, s);
  const grow = eo3(prog(f, it.f0, it.f0 + 10));
  const out = prog(f, it.f1 - 10, it.f1);
  return (
    <div style={{position: 'absolute', left: sx - w / 2, top: sy - (w * 3) / 8, width: w, height: (w * 3) / 4, opacity: grow * (1 - out), transform: `rotate(-3deg) scale(${1 - 0.25 * out})`, filter: 'drop-shadow(4px 0 0 #f4efe3) drop-shadow(-4px 0 0 #f4efe3) drop-shadow(0 4px 0 #f4efe3) drop-shadow(0 -4px 0 #f4efe3) drop-shadow(0 18px 18px rgba(0,0,0,.55))'}}>
      <PhotoInner id="young_woman" w={w} />
    </div>
  );
};
const Unit8: React.FC = () => {
  const {frame: f} = useStage();
  return (
    <>
      <Chip id="machine_lbl" x={100} y={140} accent={C.red} w={1160}>
        {f < 6335 ? (
          <>
            <ChipSub size={24} color={C.yellow}>Reason three</ChipSub>
            <ChipTitle size={48}>The engine of the whole crisis</ChipTitle>
          </>
        ) : (
          <>
            <ChipSub size={24} color={C.yellow}>Reason three</ChipSub>
            <ChipTitle size={52}>The migration machine eats twice</ChipTitle>
          </>
        )}
      </Chip>
      <Cutout photo="young_woman" id="town_photo" x={110} y={380} w={720} from="left" rot={-2} />
      <WomanToken />
      <Chip id="ghost_kids" x={100} y={160} accent={C.amber} from="left" w={980}>
        <ChipTitle size={38}>…and every child she might have had there</ChipTitle>
      </Chip>
      <Chip id="tokyo_lands" x={1060} y={160} accent={C.red} w={760}>
        <ChipTitle size={40}>Tokyo can’t make up for it</ChipTitle>
        <ChipSub size={26}>Fertility 0.96 — below one</ChipSub>
      </Chip>
      <Chip id="births_vanish" x={100} y={160} accent={C.red} w={760}>
        <ChipTitle size={60} color={C.redSoft}>The births just vanish</ChipTitle>
      </Chip>
      <Chip id="multiply" x={100} y={200} accent={C.amber} w={1000}>
        <ChipTitle size={50}>× tens of thousands of young people a year</ChipTitle>
        <ChipSub size={28}>For decades</ChipSub>
      </Chip>
      <Paper05 />
      <Perspective>
        <Float07 id="waffle" x={90} y={190} vx={14} vy={-8} rx={4} ry={-5} rz={-2}>
          {(l) => (
            <div style={{position: 'relative', width: 1700, height: 640}}>
              <Waffle local={l} total={1729} hi={744} cols={52} dot={12} gap={6} hiColor="#ff3b4e" baseColor="#9ec8ff" hiStart={44} />
              <div style={{position: 'absolute', left: 990, top: 0}}>
                <BigNumber value={`${Math.round(744 * eo3(prog(l, 40, 90)))}`} label="of 1,729 municipalities" sub="43% · at risk of disappearing by 2050" size={160} color="#ffd0cc" projection />
              </div>
            </div>
          )}
        </Float07>
        <Float07 id="halve" x={1030} y={520} vx={-14} vy={-10} rx={5} ry={-7}>
          {(l) => (
            <Columns
              local={l}
              title="Young women 20–39 in those towns"
              max={100}
              height={200}
              colW={150}
              gap={60}
              projection
              cols={[
                {label: '2020', value: 100, text: '100%', color: '#ff766e'},
                {label: '2050 · projection', value: 50, text: '≤ 50%', dotted: true},
              ]}
            />
          )}
        </Float07>
      </Perspective>
    </>
  );
};

// ======================================================= UNIT 9  (VO 09)
const WardTag: React.FC<{name: string; t0: number}> = ({name, t0}) => {
  const {frame: f, cam} = useStage();
  const w = WARDS.find((x) => x.name === name)!;
  const [x, y] = toScreen(cam, w.c[0], w.c[1]);
  const e = clamp01((f - t0) / 8) * (1 - prog(f, t0 + 70, t0 + 84));
  if (e <= 0) return null;
  return (
    <div style={{position: 'absolute', left: x, top: y - 70 * e, transform: 'translate(-50%,-50%)', fontFamily: FONT, fontWeight: 900, fontSize: 30, letterSpacing: 2, color: '#fff', textTransform: 'uppercase', textShadow: '0 0 12px #ff2d4d, 0 2px 6px #000', opacity: e, whiteSpace: 'nowrap'}}>
      {name}
    </div>
  );
};
const Unit9: React.FC = () => {
  const {frame: f} = useStage();
  const w0 = item('wards_lit').f0;
  return (
    <>
      <Chip id="bh_label" x={100} y={170} accent={C.red} w={1000}>
        <ChipSub size={24} color={C.yellow}>The same report · a brand-new category</ChipSub>
        <ChipTitle size={50}>
          <Typed text="“Black-hole” municipalities" start={item('bh_label').f0 + 8} cps={0.9} />
        </ChipTitle>
        <ChipSub size={24}>People pour in · births stay low</ChipSub>
      </Chip>
      <Stamp id="cnt25" x={1500} y={330} size={220} rot={-6} color={C.amber} sub="made the list">25</Stamp>
      <Stamp id="stamp2" x={620} y={540} size={150} rot={-8} sub="from the council’s report">Black hole</Stamp>
      <Chip id="counter16" x={100} y={170} accent={C.red} w={760} from="left">
        <ChipTitle size={72}>16 of 23</ChipTitle>
        <ChipSub size={28}>Tokyo wards carry the label</ChipSub>
      </Chip>
      {on(f, 'wards_lit') ? (
        <div style={{position: 'absolute', right: 70, top: 150, width: 520, fontFamily: FONT, background: 'rgba(5,10,16,.72)', borderRadius: 6, padding: '16px 24px', borderLeft: `7px solid ${C.red}`, opacity: clamp01((f - w0) / 8) * (1 - prog(f, 8990, 9000))}}>
          <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '4px 12px'}}>
            {FLAGGED_16.map((n, i) => {
              const t = w0 + i * 9;
              const e = clamp01((f - t) / 6);
              return (
                <div key={n} style={{fontSize: 27, fontWeight: 800, letterSpacing: 1, color: C.cream, opacity: e, transform: `translateX(${(1 - e) * 16}px)`, textTransform: 'uppercase', whiteSpace: 'nowrap'}}>
                  <span style={{display: 'inline-block', width: 12, height: 12, borderRadius: 6, background: C.red, marginRight: 10, boxShadow: '0 0 10px #ff2d4d'}} />
                  {n}
                </div>
              );
            })}
          </div>
        </div>
      ) : null}
      <WardTag name="Shinjuku" t0={w0} />
      <WardTag name="Shibuya" t0={w0 + 9} />
      <WardTag name="Toshima" t0={w0 + 18} />
      <Chip id="private_chip" x={100} y={420} accent={C.amber} w={900}>
        <ChipTitle size={44}>Given by a private council</ChipTitle>
        <ChipSub size={28}>Not the government</ChipSub>
      </Chip>
      <Chip id="critic_chip" x={100} y={640} accent={C.cream} w={1000}>
        <ChipSub size={22} color={C.yellow}>To be fair</ChipSub>
        <ChipTitle size={34}>Some researchers criticize the method and its dramatic labels</ChipTitle>
      </Chip>
      <Chip id="final_card" x={100} y={640} accent={C.red} w={1260}>
        <ChipTitle size={46}>25 black-hole municipalities nationwide</ChipTitle>
        <ChipSub size={30} color={C.redSoft}>16 of them are Tokyo’s own wards</ChipSub>
      </Chip>
    </>
  );
};


// ======================================================= kickers: VO key-phrase beat, one slot (top right)
const KICKERS = (timeline as unknown as {kickers: [number, string][]}).kickers;
const Kicker: React.FC = () => {
  const {frame: f} = useStage();
  let idx = -1;
  for (let i = 0; i < KICKERS.length; i++) if (KICKERS[i][0] <= f) idx = i;
  if (idx < 0) return null;
  const [f0, text] = KICKERS[idx];
  const nxt = idx + 1 < KICKERS.length ? KICKERS[idx + 1][0] : f0 + 60;
  const dur = Math.min(60, nxt - f0);
  const local = f - f0;
  if (local > dur) return null;
  const e = eo3(clamp01(local / 7));
  const out = prog(f, f0 + dur - 6, f0 + dur);
  const dim = f >= 7186 && f < 7470; // above the paper block
  return (
    <div style={{position: 'absolute', right: 60, top: 58, fontFamily: FONT, fontSize: 30, fontWeight: 800, letterSpacing: 1.2, color: C.cream, textTransform: 'uppercase', background: 'rgba(5,10,16,.80)', padding: '10px 22px 11px', borderRadius: 6, borderRight: `6px solid ${C.yellow}`, opacity: e * (1 - out) * (dim ? 0.95 : 1), transform: `translateX(${(1 - e) * 40 - out * 20}px)`, boxShadow: '0 8px 24px rgba(0,0,0,.45)', whiteSpace: 'nowrap'}}>
      {text}
    </div>
  );
};

export const ScreenScene: React.FC = () => (
  <>
    <Kicker />
    <Unit1 />
    <Unit2 />
    <Unit3 />
    <Unit4 />
    <Unit5 />
    <Unit6 />
    <Unit7 />
    <Unit8 />
    <Unit9 />
  </>
);
