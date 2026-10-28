import React,{useEffect,useRef} from 'react';
import {EffectComposer,Bloom} from '@react-three/postprocessing';
import type {EffectComposer as ComposerImpl} from 'postprocessing';
import {delayRender,continueRender,getRemotionEnvironment} from 'remotion';
import * as THREE from 'three';

// ThreeCanvas manually steps frames; render the mounted composer explicitly.
export const ManualEffects:React.FC<{time:number}>=({time})=>{
 const ref=useRef<ComposerImpl|null>(null);
 useEffect(()=>{
  const handle=getRemotionEnvironment().isRendering?delayRender('Rendering optical map grade'):null;
  const timer=setTimeout(()=>{ref.current?.render(1/24);if(handle!==null)continueRender(handle)},30);
  return ()=>{clearTimeout(timer);if(handle!==null)continueRender(handle)};
 },[time]);
 return <EffectComposer ref={ref} multisampling={0} frameBufferType={THREE.UnsignedByteType}>
  <Bloom intensity={.16} luminanceThreshold={.92} luminanceSmoothing={.18}/>
 </EffectComposer>;
};
