import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {D, H, TILE_SET, W, levelFor, planeHalfExtents, worldPx, clamp01} from '../lib/core';
import {useStage} from '../lib/ctx';

const Tiles: React.FC = () => {
  const {cam} = useStage();
  const L = levelFor(cam.z);
  const levels = L - 3 >= 2 ? [L - 3, L] : [L];
  const [hx, hy] = planeHalfExtents(cam.pitch, cam.bearing);
  const out: React.ReactNode[] = [];
  for (const l of levels) {
    const s = 2 ** (cam.z - l);
    const [cx, cy] = worldPx(cam.lon, cam.lat, l);
    const n = 2 ** l;
    const x0 = Math.max(0, Math.floor((cx - hx / s) / 256));
    const x1 = Math.min(n - 1, Math.floor((cx + hx / s) / 256));
    const y0 = Math.max(0, Math.floor((cy - hy / s) / 256));
    const y1 = Math.min(n - 1, Math.floor((cy + hy / s) / 256));
    for (let x = x0; x <= x1; x++) {
      for (let y = y0; y <= y1; y++) {
        const key = `${l}/${x}/${y}`;
        if (!TILE_SET.has(key)) continue;
        out.push(
          <Img
            key={key}
            src={staticFile(`tiles/${key}.jpg`)}
            style={{
              position: 'absolute',
              left: W / 2 + (x * 256 - cx) * s,
              top: H / 2 + (y * 256 - cy) * s,
              width: 256 * s + 1,
              height: 256 * s + 1,
              maxWidth: 'none',
            }}
          />
        );
      }
    }
  }
  return <>{out}</>;
};

/** Real satellite/aerial base (GSI Japan seamless photo tiles) with a real tilted camera. Children are drawn ON the map plane. */
export const MapStage: React.FC<{children?: React.ReactNode}> = ({children}) => {
  const {cam} = useStage();
  const horizon = clamp01(cam.pitch / 18);
  return (
    <AbsoluteFill style={{background: '#08121c', perspective: D, perspectiveOrigin: '50% 50%', overflow: 'hidden'}}>
      <div
        style={{
          position: 'absolute',
          left: 0,
          top: 0,
          width: W,
          height: H,
          transformOrigin: '50% 50%',
          transform: `rotateX(${cam.pitch}deg) rotateZ(${cam.bearing}deg)`,
        }}
      >
        <div style={{position: 'absolute', left: 0, top: 0, width: W, height: H, filter: 'brightness(0.74) saturate(0.88) contrast(1.08)'}}>
          <Tiles />
        </div>
        {children}
      </div>
      <AbsoluteFill style={{background: `linear-gradient(180deg, rgba(5,9,14,${0.9 * horizon}) 0%, rgba(5,9,14,0) 30%)`}} />
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 50%, rgba(0,0,0,0) 45%, rgba(0,0,0,0.55) 100%)'}} />
    </AbsoluteFill>
  );
};
