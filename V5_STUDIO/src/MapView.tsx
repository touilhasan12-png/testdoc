import React, {useLayoutEffect, useMemo} from 'react';
import {ThreeCanvas} from '@remotion/three';
import {useLoader, useThree} from '@react-three/fiber';
import {Line, useGLTF} from '@react-three/drei';
import {ManualEffects} from './ManualEffects';
import {staticFile, useCurrentFrame, useVideoConfig, interpolate} from 'remotion';
import * as THREE from 'three';
import historical from '../public/generated/iberian-realms-1500.json';
import voyage from '../public/generated/route.json';

const D=Math.PI/180;
export const geoPoint=(lon:number,lat:number,z=0)=>new THREE.Vector3(lon/180*8,lat/90*4,z);
export function viewForTime(t:number){
 const q=THREE.MathUtils.smoothstep(t,0,7);
 if(t>=11)return {lon:-9.5,lat:37,distance:1.65,pitch:35};
 return {lon:-22-q*1.5,lat:35-q*.6,distance:1.55+q*.23,pitch:35};
}
export function createMapCamera(t:number,w:number,h:number){
 const view=viewForTime(t), target=geoPoint(view.lon,view.lat);
 const camera=new THREE.PerspectiveCamera(36,w/h,.01,100);
 camera.position.set(target.x,target.y-view.distance*Math.sin(view.pitch*D),view.distance*Math.cos(view.pitch*D));
 camera.up.set(0,1,0);camera.lookAt(target);camera.updateProjectionMatrix();camera.updateMatrixWorld();return camera;
}
export function projected(lon:number,lat:number,t:number,w:number,h:number){
 const p=geoPoint(lon,lat,.02).project(createMapCamera(t,w,h));return {x:(p.x*.5+.5)*w,y:(.5-p.y*.5)*h};
}
function Rig({time}:{time:number}){
 const {camera,size}=useThree();
 useLayoutEffect(()=>{const next=createMapCamera(time,size.width,size.height);camera.position.copy(next.position);camera.quaternion.copy(next.quaternion);camera.up.copy(next.up);camera.updateProjectionMatrix();camera.updateMatrixWorld();},[camera,size.width,size.height,time]);
 return null;
}
function BaseMap(){
 const texture=useLoader(THREE.TextureLoader,staticFile('map/earth_graded.jpg'));texture.colorSpace=THREE.SRGBColorSpace;texture.anisotropy=4;
 return <mesh><planeGeometry args={[16,8]}/><meshBasicMaterial map={texture} toneMapped={false}/></mesh>;
}
type XY=number[];
function makeShapes(g:any){
 const polys=g.type==='Polygon'?[g.coordinates]:g.coordinates;
 const out:{geometry:THREE.ShapeGeometry;outline:THREE.Vector3[]}[]=[];
 for(const poly of polys){
  if(!poly?.[0]?.length)continue;
  const outer:XY[]=poly[0];
  if(Math.max(...outer.map(p=>p[0]))-Math.min(...outer.map(p=>p[0]))>180)continue;
  const shape=new THREE.Shape();
  poly.forEach((ring:XY[],j:number)=>{
   const path=j===0?shape:new THREE.Path();
   ring.forEach((a,i)=>{const p=geoPoint(a[0],a[1]);i?path.lineTo(p.x,p.y):path.moveTo(p.x,p.y);});
   path.closePath();if(j>0)shape.holes.push(path as THREE.Path);
  });
  out.push({geometry:new THREE.ShapeGeometry(shape),outline:outer.map(p=>geoPoint(p[0],p[1],.015))});
 }
 return out;
}
// The BlenderGIS mesh is a faint modern-coastline relief, registered to the
// same equirectangular coordinates as the satellite map. Historical borders
// are drawn separately from the approximate 1500 basemap.
function BlenderGISRelief(){
 const asset=useGLTF(staticFile('private/iberia_blendergis.glb'));
 const scene=useMemo(()=>{
  const clone=asset.scene.clone(true);
  clone.traverse((o)=>{if((o as THREE.Mesh).isMesh){const m=o as THREE.Mesh;m.material=new THREE.MeshBasicMaterial({color:'#d6b575',transparent:true,opacity:.15,depthWrite:false,side:THREE.DoubleSide});}});
  return clone;
 },[asset]);
 const center=geoPoint((-18.00078125+3.46181640625)/2,(27.74697265625+43.76455078125)/2,.003);
 const mapScale=(8/180)/ (6/(3.46181640625-(-18.00078125)));
 return <group position={center} rotation={[Math.PI/2,0,0]} scale={mapScale}><primitive object={scene}/></group>;
}
function HistoricalRealms(){
 const realms=useMemo(()=>historical.features.map((f:any)=>({name:f.properties.NAME,shapes:makeShapes(f.geometry)})),[]);
 const colors:Record<string,string>={'Castille':'#d8a65d','Portugal':'#7b9b89','Aragón':'#bf8456'};
 return <>{realms.map(r=><group key={r.name}>{r.shapes.map((s,i)=><group key={i}>
  <mesh geometry={s.geometry} position={[0,0,.007]}><meshBasicMaterial color={colors[r.name]||'#b8956d'} transparent opacity={.26} depthWrite={false} side={THREE.DoubleSide}/></mesh>
  <Line points={s.outline} color="#e1c79c" lineWidth={1.35} transparent opacity={.70} depthWrite={false}/>
 </group>)}</group>)}</>;
}
function PointMarker({time}:{time:number}){
 const p=geoPoint(-6.35,36.77,.028);const pulse=.027+(.012*(.5+.5*Math.sin(time*3)));
 return <group position={p}>
  <mesh><circleGeometry args={[.010,32]}/><meshBasicMaterial color="#fff0b7" toneMapped={false}/></mesh>
  <mesh><ringGeometry args={[pulse,pulse+.003,48]}/><meshBasicMaterial color="#f6d795" transparent opacity={.8} toneMapped={false} side={THREE.DoubleSide}/></mesh>
 </group>;
}
function ReconstructedShip({time}:{time:number}){
 const asset=useGLTF(staticFile('private/ship_triposr_new.glb'));
 const model=useMemo(()=>{
  const clone=asset.scene.clone(true);
  clone.traverse(o=>{if((o as THREE.Mesh).isMesh){
   const mesh=o as THREE.Mesh,geometry=mesh.geometry.clone();
   const pos=geometry.getAttribute('position') as THREE.BufferAttribute;
   // Reorient TripoSR's reconstructed axes: x=length, y=depth, z=height.
   for(let i=0;i<pos.count;i++){const x=pos.getX(i),y=pos.getY(i),z=pos.getZ(i);pos.setXYZ(i,y,x,z);}
   pos.needsUpdate=true;geometry.computeVertexNormals();mesh.geometry=geometry;
   mesh.material=new THREE.MeshStandardMaterial({color:'#dcc49b',roughness:.8,side:THREE.DoubleSide});
  }});
  return clone;
 },[asset]);
 const q=Math.min(1,Math.max(0,(time-3.5)/3.4));
 const samples=voyage.firstLeg, idx=Math.min(samples.length-1,Math.floor(q*(samples.length-1)));
 const [lon,lat]=samples[idx];
 return <group position={geoPoint(lon,lat,.035)} scale={.075}><primitive object={model}/></group>;
}
function DepartingRoute({time}:{time:number}){
 const n=Math.floor(interpolate(time,[3.5,6.9],[2,voyage.firstLeg.length],{extrapolateLeft:'clamp',extrapolateRight:'clamp'}));
 const pts=voyage.firstLeg.slice(0,n).map(p=>geoPoint(p[0],p[1],.035));
 return time>=3.4&&pts.length>1?<Line points={pts} color="#f9cf7d" lineWidth={4} transparent opacity={.95} depthWrite={false}/>:null;
}
function MapScene({time}:{time:number}){
 return <><Rig time={time}/><ambientLight intensity={1.5}/><directionalLight position={[-3,-4,8]} intensity={2}/><BaseMap/><BlenderGISRelief/><HistoricalRealms/>{time<7.2?<><PointMarker time={time}/><DepartingRoute time={time}/>{time>=3.5?<ReconstructedShip time={time}/>:null}</>:null}
 <ManualEffects time={time}/></>;
}
export const MapView:React.FC<{timeOffset?:number}> = ({timeOffset=0})=>{
 const f=useCurrentFrame(),{width,height,fps}=useVideoConfig();const time=f/fps+timeOffset;
 return <ThreeCanvas width={width} height={height} camera={{fov:36,near:.01,far:100}} gl={{antialias:true,preserveDrawingBuffer:true,alpha:false}}>
  <color attach="background" args={['#142f39']}/><MapScene time={time}/>
 </ThreeCanvas>;
};
