import React from 'react';
import {AbsoluteFill, Sequence} from 'remotion';
import {T} from './theme';
import {Backdrop} from './ui';
import {
  Akiya,
  Arrows,
  BlackHole,
  ColdOpen,
  Dive,
  Fertility,
  Machine,
  Paradox,
  TimeSqueeze,
} from './scenes';

// Scene boundaries are aligned to the measured VO starts in SAMPLE-BOUNDARY.md.
export const Sample: React.FC = () => (
  <AbsoluteFill style={{background: T.bg}}>
    <Backdrop />
    <Sequence from={0} durationInFrames={1047}>
      <ColdOpen />
    </Sequence>
    <Sequence from={1047} durationInFrames={753}>
      <Arrows />
    </Sequence>
    <Sequence from={1800} durationInFrames={756}>
      <Fertility />
    </Sequence>
    <Sequence from={2556} durationInFrames={652}>
      <Paradox />
    </Sequence>
    <Sequence from={3208} durationInFrames={832}>
      <Dive />
    </Sequence>
    <Sequence from={4040} durationInFrames={841}>
      <Akiya />
    </Sequence>
    <Sequence from={4881} durationInFrames={1270}>
      <TimeSqueeze />
    </Sequence>
    <Sequence from={6151} durationInFrames={1559}>
      <Machine />
    </Sequence>
    <Sequence from={7710} durationInFrames={1290}>
      <BlackHole />
    </Sequence>
    <div
      style={{
        position: 'absolute',
        right: 30,
        top: 22,
        fontFamily: T.font,
        fontSize: 16,
        letterSpacing: 3,
        color: T.mute,
        opacity: 0.7,
      }}
    >
      SAMPLE · FIRST 5:00
    </div>
  </AbsoluteFill>
);
