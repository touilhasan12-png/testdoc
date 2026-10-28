import React from 'react';
import {AbsoluteFill, Audio, Composition, staticFile} from 'remotion';
import {Map3D} from './Map3D';
import {Overlay} from './Overlay';

const HistoryMap:React.FC<{privateAssets:boolean}>=({privateAssets})=><AbsoluteFill>
 <Map3D privateAssets={privateAssets}/><Overlay privateAssets={privateAssets}/>
 {privateAssets?<Audio src={staticFile('private/narration_and_score.m4a')}/>:null}
</AbsoluteFill>;

export const Root:React.FC=()=> <>
 <Composition id="HistoryMapPreview" component={HistoryMap} width={1280} height={720} fps={24} durationInFrames={12*24} defaultProps={{privateAssets:false}}/>
 <Composition id="HistoryMapFull" component={HistoryMap} width={1920} height={1080} fps={24} durationInFrames={120*24} defaultProps={{privateAssets:true}}/>
</>;
