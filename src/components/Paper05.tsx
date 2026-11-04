import React from 'react';
import {Easing, Img, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {item} from '../lib/core';
import {FONT} from './ui';

/**
 * Library card 05 (LabPaperMorph) rebuilt for this render:
 * one wad (0-3f) -> fast unfold (8-34f) -> hold -> reverse close -> clean vanish. No flight, tumble or shake.
 * Wad = new photo of blank paper; sheets = card-05 paper texture with the sample text removed and NEW text baked in.
 */
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const CENTER_ORDER = [3, 4, 2, 5, 1, 6, 0, 7];

const Sheet: React.FC<{src: string; x: number; y: number; w: number; h: number; p: number; offsetY: number}> = ({src, x, y, w, h, p, offsetY}) => {
  const strips = 8;
  const stripW = w / strips;
  const opacity = interpolate(p, [0, 0.1], [0, 1], clamp);
  const scale = 0.42 + p * 0.58;
  return (
    <div style={{position: 'absolute', left: x, top: y, width: w, height: h, opacity, transform: `translateY(${(1 - p) * offsetY}px) scale(${scale})`, transformOrigin: 'center', perspective: '1150px', transformStyle: 'preserve-3d', filter: 'drop-shadow(0 20px 20px rgba(0,0,0,.46))'}}>
      {Array.from({length: strips}, (_, i) => {
        const rank = CENTER_ORDER.indexOf(i);
        const delay = rank * 0.045;
        const sp = interpolate(p, [delay, 0.55 + delay], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
        const direction = i % 2 === 0 ? -1 : 1;
        return (
          <div key={i} style={{position: 'absolute', left: i * stripW, top: 0, width: stripW, height: h, overflow: 'hidden', backfaceVisibility: 'hidden', transformOrigin: i % 2 === 0 ? 'left center' : 'right center', transform: `translateZ(${(1 - sp) * -105}px) rotateY(${(1 - sp) * direction * 78}deg)`, filter: `brightness(${0.52 + sp * 0.48})`}}>
            <Img src={staticFile(src)} style={{position: 'absolute', left: -i * stripW, top: 0, width: w, height: h, maxWidth: 'none', objectFit: 'fill'}} />
            <div style={{position: 'absolute', inset: 0, background: direction < 0 ? 'linear-gradient(90deg, rgba(0,0,0,.78), rgba(255,255,255,.28))' : 'linear-gradient(90deg, rgba(255,255,255,.28), rgba(0,0,0,.78))', opacity: (1 - sp) * 0.72, pointerEvents: 'none'}} />
          </div>
        );
      })}
    </div>
  );
};

export const Paper05: React.FC = () => {
  const frame = useCurrentFrame();
  const it = item('paper_block');
  const local = frame - it.f0;
  if (local < 0 || local > 270) return null;
  const openP = interpolate(local, [8, 34, 239, 265], [0, 1, 1, 0], {...clamp, easing: Easing.inOut(Easing.cubic)});
  const appear = Math.min(
    interpolate(local, [0, 3], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)}),
    interpolate(local, [265, 268], [1, 0], {...clamp, easing: Easing.in(Easing.cubic)})
  );
  const wadOut = interpolate(openP, [0.1, 0.34], [0, 1], clamp);
  const wadOpacity = appear * (1 - wadOut);
  const mainP = interpolate(openP, [0.3, 0.9], [0, 1], clamp);
  const stripP = interpolate(openP, [0.42, 1], [0, 1], clamp);
  return (
    <div style={{position: 'absolute', inset: 0, fontFamily: FONT}}>
      <div style={{position: 'absolute', inset: 0, background: `radial-gradient(ellipse at 50% 50%, rgba(0,0,0,${0.35 * appear}) 0%, rgba(0,0,0,${0.7 * appear}) 100%)`}} />
      <div style={{position: 'absolute', left: 760, top: 735, width: 400, height: 55, borderRadius: '50%', background: 'rgba(0,0,0,.52)', filter: 'blur(20px)', opacity: wadOpacity * 0.72, transform: `scaleX(${0.55 + appear * 0.45})`}} />
      <div style={{position: 'absolute', left: 750, top: 330, width: 420, height: 429, opacity: wadOpacity, clipPath: `circle(${appear * 76}% at 50% 50%)`, transform: `scale(${(0.35 + appear * 0.65) * (1 + openP * 0.12)})`, transformOrigin: 'center', filter: 'drop-shadow(0 22px 22px rgba(0,0,0,.58))'}}>
        <Img src={staticFile('paper/wad.png')} style={{width: '100%', height: '100%', objectFit: 'contain'}} />
      </div>
      <Sheet src="paper/sheet_strip.png" x={410} y={40} w={1100} h={460} p={stripP} offsetY={170} />
      <Sheet src="paper/sheet_main.png" x={420} y={470} w={1080} h={516} p={mainP} offsetY={-245} />
    </div>
  );
};
