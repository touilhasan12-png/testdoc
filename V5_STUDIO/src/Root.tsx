import React from 'react';
import {Composition} from 'remotion';
import {MagellanPilot} from './Story';
import {MeshPreview} from './MeshPreview';

export const Root:React.FC=()=> <><Composition id="MagellanPilot" component={MagellanPilot} width={1920} height={1080} fps={24} durationInFrames={360}/><Composition id="MeshPreview" component={MeshPreview} width={960} height={720} fps={24} durationInFrames={2}/></>;
