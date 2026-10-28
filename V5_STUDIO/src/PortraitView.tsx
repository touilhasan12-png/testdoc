import React from 'react';
import {ThreeCanvas} from '@remotion/three';
import {useLoader} from '@react-three/fiber';
import {staticFile,useCurrentFrame,useVideoConfig,interpolate} from 'remotion';
import * as THREE from 'three';

function Portrait({time}:{time:number}){
 const color=useLoader(THREE.TextureLoader,staticFile('private/portrait_upscaled_trim.png'));
 const depth=useLoader(THREE.TextureLoader,staticFile('private/portrait_depth_trim.png'));
 color.colorSpace=THREE.SRGBColorSpace;depth.colorSpace=THREE.NoColorSpace;
 const turn=interpolate(time,[11,15],[-.055,.06],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});
 return <mesh position={[1.13,-.26,0]} rotation={[0,turn,0]}>
  <planeGeometry args={[3.0,2.84,90,90]}/>
  <meshStandardMaterial map={color} transparent alphaTest={.015} displacementMap={depth} displacementScale={.13} displacementBias={-.055} roughness={1} side={THREE.DoubleSide}/>
 </mesh>;
}
export const PortraitView:React.FC<{start:number}> = ({start})=>{
 const frame=useCurrentFrame(),{width,height,fps}=useVideoConfig();const time=start+frame/fps;
 return <ThreeCanvas width={width} height={height} camera={{position:[0,0,5],fov:35,near:.1,far:50}} gl={{antialias:true,preserveDrawingBuffer:true,alpha:true}}>
  <ambientLight intensity={1.8}/><directionalLight position={[-3,3,5]} intensity={1.1}/><Portrait time={time}/>
 </ThreeCanvas>;
};
