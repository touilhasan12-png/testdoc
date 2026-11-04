import React from 'react';
import {Composition} from 'remotion';
import {TokyoSample} from './Video';
import {FPS, TOTAL} from './lib/core';

export const Root: React.FC = () => (
  <Composition id="TokyoSample" component={TokyoSample} durationInFrames={TOTAL} fps={FPS} width={1920} height={1080} />
);
