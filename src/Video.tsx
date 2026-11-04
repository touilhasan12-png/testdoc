import React, {useEffect, useState} from 'react';
import {AbsoluteFill, cancelRender, continueRender, delayRender, useCurrentFrame} from 'remotion';
import '@fontsource/montserrat/600.css';
import '@fontsource/montserrat/700.css';
import '@fontsource/montserrat/800.css';
import '@fontsource/montserrat/900.css';
import {MapStage} from './components/MapStage';
import {FONT} from './components/ui';
import {PlaneScene} from './scenes/PlaneScene';
import {ScreenScene} from './scenes/ScreenScene';
import {camOf, shotAt, SHOTS} from './lib/core';
import {StageCtx, useStage} from './lib/ctx';

const useFonts = () => {
  const [handle] = useState(() => delayRender('fonts'));
  useEffect(() => {
    Promise.all(['600', '700', '800', '900'].map((w) => document.fonts.load(`${w} 40px Montserrat`)))
      .then(() => document.fonts.ready)
      .then(() => continueRender(handle))
      .catch((e) => cancelRender(e));
  }, [handle]);
};

const CREDIT = 'IMAGERY: GSI Japan (Geospatial Information Authority of Japan) seamless photo · BOUNDARIES: © OpenStreetMap contributors via geoBoundaries (ODbL / CC BY-SA 2.0)';

const SourceBar: React.FC = () => {
  const {frame} = useStage();
  const shot = shotAt(frame);
  const idx = SHOTS.indexOf(shot);
  const prev = idx > 0 ? SHOTS[idx - 1] : null;
  const fresh = !prev || prev.src !== shot.src;
  const o = fresh ? Math.min(1, (frame - shot.f0) / 8) : 1;
  return (
    <div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: 120, background: 'linear-gradient(180deg, rgba(0,0,0,0), rgba(0,0,0,.78))', fontFamily: FONT}}>
      <div style={{position: 'absolute', left: 60, right: 60, bottom: 24, opacity: o}}>
        <div style={{fontSize: 21, fontWeight: 700, letterSpacing: 0.8, color: 'rgba(255,255,255,.95)', textShadow: '0 2px 5px #000', textTransform: 'uppercase'}}>{shot.src}</div>
        <div style={{marginTop: 6, fontSize: 16, fontWeight: 600, letterSpacing: 0.6, color: 'rgba(255,255,255,.72)', textShadow: '0 2px 4px #000'}}>{CREDIT}</div>
      </div>
    </div>
  );
};

export const TokyoSample: React.FC = () => {
  useFonts();
  const frame = useCurrentFrame();
  const shot = shotAt(frame);
  const cam = camOf(shot, frame);
  return (
    <StageCtx.Provider value={{frame, cam, shotId: shot.id}}>
      <AbsoluteFill style={{background: '#05080c', fontFamily: FONT}}>
        <MapStage>
          <PlaneScene />
        </MapStage>
        <ScreenScene />
        <SourceBar />
      </AbsoluteFill>
    </StageCtx.Provider>
  );
};
