import React from 'react';
import {Composition} from 'remotion';
import {Sample} from './Sample';

// 300 s sample = 9000 frames @ 30 fps, 1920x1080. Visuals only; audio is mixed in CI.
export const RemotionRoot: React.FC = () => (
  <Composition
    id="Sample"
    component={Sample}
    durationInFrames={9000}
    fps={30}
    width={1920}
    height={1080}
  />
);
