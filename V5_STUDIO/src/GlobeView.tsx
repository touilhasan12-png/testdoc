import React, {useMemo} from 'react';
import {ThreeCanvas} from '@remotion/three';
import {useLoader} from '@react-three/fiber';
import {Line} from '@react-three/drei';
import {staticFile,useCurrentFrame,useVideoConfig,interpolate} from 'remotion';
import * as THREE from 'three';
import ThreeGlobe from 'three-globe';
import countries from '../public/generated/world-countries.json';
import voyage from '../public/generated/route.json';

function Globe({time}:{time:number}){
 const texture=useLoader(THREE.TextureLoader,staticFile('map/earth_graded.jpg'));texture.colorSpace=THREE.SRGBColorSpace;
 const globe=useMemo(()=>{
  const g=new ThreeGlobe({waitForGlobeReady:false,animateIn:false});
  g.globeMaterial(new THREE.MeshBasicMaterial({map:texture}));
  g.showAtmosphere(true).atmosphereColor('#a3c4c1').atmosphereAltitude(.13);
  g.polygonsTransitionDuration(0).polygonsData(countries.features as object[])
   .polygonAltitude(.001).polygonCapColor(()=> 'rgba(0,0,0,0)')
   .polygonSideColor(()=> 'rgba(0,0,0,0)').polygonStrokeColor(()=> 'rgba(229,211,172,0.23)');
  return g;
 },[texture]);
 const k=Math.max(2,Math.min(voyage.samples.length,Math.floor(interpolate(time,[7.5,10.6],[2,voyage.samples.length],{extrapolateLeft:'clamp',extrapolateRight:'clamp'}))));
 const points=useMemo(()=>voyage.samples.slice(0,k).map(([lon,lat])=>{const p=globe.getCoords(lat,lon,.014);return new THREE.Vector3(p.x,p.y,p.z)}),[globe,k]);
 const spin=interpolate(time,[7.0,11.2],[.70,.20],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});
 return <group position={[1.28,-.02,0]} rotation={[.16,spin,.08]} scale={.016}>
  <primitive object={globe}/>
  {points.length>1?<Line points={points} color="#f8cc77" lineWidth={3.5} transparent opacity={.95} depthWrite={false}/>:null}
 </group>;
}
export const GlobeView:React.FC<{start:number}> = ({start})=>{
 const frame=useCurrentFrame(),{width,height,fps}=useVideoConfig();const time=start+frame/fps;
 return <ThreeCanvas width={width} height={height} camera={{position:[0,0,6],fov:35,near:.1,far:50}} gl={{antialias:true,preserveDrawingBuffer:true,alpha:true}}>
  <ambientLight intensity={1}/><Globe time={time}/>
 </ThreeCanvas>;
};
