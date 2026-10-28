import React, {useMemo, useLayoutEffect} from 'react';
import {ThreeCanvas} from '@remotion/three';
import {useLoader, useThree} from '@react-three/fiber';
import {useCurrentFrame, useVideoConfig, staticFile} from 'remotion';
import * as THREE from 'three';
import {geoMercator} from 'd3-geo';
import centroid from '@turf/centroid';
import {feature} from 'topojson-client';
import countryAtlas from 'world-atlas/countries-50m.json';
import {activeBeat, interpolatePoint, ROUTE, scenePosition, viewAt, opacity} from './timeline';

// The texture and geometry use the same modern Mercator projection. Map colors
// identify locations, not historical sovereignty or exact sixteenth-century borders.
const mercator=geoMercator().scale(180/Math.PI).translate([0,0]);
const merc=(lat:number)=>-(mercator([0,Math.max(-80,Math.min(80,lat))])?.[1] ?? 0);
const HALF_HEIGHT=merc(80);
const radians=(degrees:number)=>degrees*Math.PI/180;
const MAP_PITCH=radians(35);
const countries=(feature(countryAtlas as never,(countryAtlas as any).objects.countries) as any).features as any[];

const worldGeo=(lon:number,lat:number,z=0)=>new THREE.Vector3(lon,merc(lat),z);

function MapPlane(){
  const texture=useLoader(THREE.TextureLoader,staticFile('map/nasa_world_mercator.jpg'));
  texture.colorSpace=THREE.SRGBColorSpace;
  texture.anisotropy=2;
  return <>{[-720,-360,0,360].map(x=><mesh key={x} position={[x,0,0]}>
    <planeGeometry args={[360,2*HALF_HEIGHT]}/><meshBasicMaterial map={texture}/>
  </mesh>)}</>;
}

function polygonGeometries(id:string):THREE.ShapeGeometry[] {
 const country=countries.find(x=>String(x.id).padStart(3,'0')===id);
 if(!country)return [];
 const polys=country.geometry.type==='Polygon'?[country.geometry.coordinates]:country.geometry.coordinates;
 const output:THREE.ShapeGeometry[]=[];
 for(const poly of polys){
  if(!poly?.[0]?.length)continue;
  // Selected regions do not span the antimeridian. Exclude any impossible rings.
  if(Math.max(...poly[0].map((p:number[])=>p[0]))-Math.min(...poly[0].map((p:number[])=>p[0]))>180)continue;
  const shape=new THREE.Shape();
  for(let ring=0;ring<poly.length;ring++){
    const path=ring===0?shape:new THREE.Path();
    poly[ring].forEach((p:number[],i:number)=>{const x=p[0],y=merc(p[1]);if(i===0)path.moveTo(x,y);else path.lineTo(x,y);});
    if(ring>0)shape.holes.push(path as THREE.Path);
  }
  output.push(new THREE.ShapeGeometry(shape));
 }
 return output;
}
function Region({id,color,alpha}:{id:string;color:string;alpha:number}){
 const geos=useMemo(()=>polygonGeometries(id),[id]);
 const center=useMemo(()=>{
  const country=countries.find(x=>String(x.id).padStart(3,'0')===id);
  return country?centroid(country).geometry.coordinates:null;
 },[id]);
 return <>{[-720,-360,0,360].map(offset=><group key={offset} position={[offset,0,.08]}>
  {geos.map((geo,i)=><mesh key={i} geometry={geo}><meshBasicMaterial color={color} transparent opacity={alpha*.48} depthWrite={false} side={THREE.DoubleSide}/></mesh>)}
  {center?<mesh position={[center[0],merc(center[1]),.06]}><ringGeometry args={[.28,.40,32]}/><meshBasicMaterial color="#f8e7bd" transparent opacity={alpha*.9} side={THREE.DoubleSide}/></mesh>:null}
 </group>)}</>;
}

function PathSegment({a,b,color,radius}:{a:THREE.Vector3;b:THREE.Vector3;color:string;radius:number}){
 const delta=b.clone().sub(a),len=delta.length();
 if(len<0.0001)return null;
 const mid=a.clone().add(b).multiplyScalar(.5);
 const angle=Math.atan2(delta.y,delta.x)-Math.PI/2;
 return <mesh position={[mid.x,mid.y,.20]} rotation={[0,0,angle]}>
  <cylinderGeometry args={[radius,radius,len,8,1]}/><meshBasicMaterial color={color}/>
 </mesh>;
}
function Journey({time,view}:{time:number;view:number}){
 // Don't leave old route lines behind portraits or turn them into decoration.
 if(time<15.1||activeBeat(time)?.image)return null;
 const from=Math.max(15.1,time-12),[sx,sy]=interpolatePoint(from,ROUTE);
 const points:{time:number;pos:THREE.Vector3}[]=[{time:from,pos:worldGeo(sx,sy,.2)}];
 for(const p of ROUTE)if(p[0]>from&&p[0]<=time)points.push({time:p[0],pos:worldGeo(p[1],p[2],.2)});
 const [lon,lat]=interpolatePoint(time,ROUTE);points.push({time,pos:worldGeo(lon,lat,.2)});
 return <>{points.slice(1).map((b,i)=><PathSegment key={i} a={points[i].pos} b={b.pos} radius={view/1050} color={b.time>=88.9?'#71d0c2':'#f1cb85'}/>)}</>;
}
function Branch({time,view}:{time:number;view:number}){
 const isAnt=time>=37.139&&time<42.03, isTri=time>=81.678&&time<86.046;
 if(!isAnt&&!isTri)return null;
 const from=isAnt?37.139:81.678, end=isAnt?42.03:86.046;
 const A=isAnt?worldGeo(-69.5,-52.5):worldGeo(-232.55,.68);
 const B=isAnt?worldGeo(-53,-37):worldGeo(-218,16);
 const q=Math.max(0,Math.min(1,(time-from)/Math.min(2.2,end-from)));
 const stop=A.clone().lerp(B,q);const parts=10;const nodes=[];
 for(let i=0;i<parts;i+=2){const a=A.clone().lerp(stop,i/parts),b=A.clone().lerp(stop,(i+1)/parts);nodes.push(<PathSegment key={i} a={a} b={b} radius={view/850} color="#e78b75"/>);}
 const angle=Math.atan2(stop.y-A.y,stop.x-A.x),size=view*.016;
 const triangle=new THREE.Shape();triangle.moveTo(0,0);triangle.lineTo(-size,-size*.5);triangle.lineTo(-size,size*.5);triangle.closePath();
 return <>{nodes}<mesh position={[stop.x,stop.y,.3]} rotation={[0,0,angle]}><shapeGeometry args={[triangle]}/><meshBasicMaterial color="#e78b75" side={THREE.DoubleSide}/></mesh></>;
}

// Original lightweight 3D silhouette. For important people and events the
// privately staged project illustrations are composed separately in 2D.
function Ship({time,view}:{time:number;view:number}){
 const [lon,lat]=interpolatePoint(time,ROUTE);
 const [prevLon,prevLat]=interpolatePoint(Math.max(0,time-.3),ROUTE);
 const dx=lon-prevLon,dy=merc(lat)-merc(prevLat);
 const turn=Math.abs(dx)+Math.abs(dy)>.001?Math.atan2(dy,dx):Math.PI;
 const hull=useMemo(()=>{const s=new THREE.Shape();s.moveTo(-3,-.8);s.lineTo(2.7,-.8);s.lineTo(3.3,.0);s.lineTo(2.8,.8);s.lineTo(-2.5,.8);s.lineTo(-3,-.8);return s;},[]);
 const scale=view/150;
 return <group position={[lon,merc(lat),.7]} rotation={[0,0,turn]} scale={[scale,scale,scale]}>
   <mesh><extrudeGeometry args={[hull,{depth:.52,bevelEnabled:true,bevelSize:.12,bevelThickness:.12,bevelSegments:1}]}/><meshStandardMaterial color="#523d2d" roughness={.9}/></mesh>
   {[-1.3,1.1].map(x=><group key={x} position={[x,0,.55]}>
      <mesh position={[0,0,1.6]} rotation={[Math.PI/2,0,0]}><cylinderGeometry args={[.075,.09,3.5,7]}/><meshStandardMaterial color="#443327"/></mesh>
      <mesh position={[0,0,2]} rotation={[Math.PI/2,0,0]}><planeGeometry args={[2,2.4]}/><meshStandardMaterial color="#e5d8bc" side={THREE.DoubleSide} roughness={1}/></mesh>
   </group>)}
 </group>;
}

function CameraRig({distance}:{distance:number}) {
 const {camera}=useThree();
 useLayoutEffect(()=>{camera.position.set(0,0,distance);camera.lookAt(0,0,0);camera.updateProjectionMatrix();camera.updateMatrixWorld();},[camera,distance]);
 return null;
}
function ShipArtwork({time,view}:{time:number;view:number}){
 const texture=useLoader(THREE.TextureLoader,staticFile('private/victoria.png'));
 texture.colorSpace=THREE.SRGBColorSpace;
 const [lon,lat]=interpolatePoint(time,ROUTE);
 // Fleet counts appear only when the narration refers to the vessels.
 const five=time>=.66 && time<4.033, three=time>=48.439 && time<52.34;
 const fleet=five||three;
 // Place the extra vessels westward on the sea side of the coastline.
 const offsets=five?[0,1,2,3,4]:three?[0,1,2]:[0];
 const width=view*(fleet?.045:.080);
 return <>{offsets.map((i)=><sprite key={i} position={[lon-i*view*.068,merc(lat)-i*view*.003,1.3]} scale={[width,width*.73,1]}>
  <spriteMaterial map={texture} transparent depthWrite={false}/>
 </sprite>)}</>;
}
function Scene({time,view,distance,privateAssets}:{time:number;view:number;distance:number;privateAssets:boolean}){
 const [centerLon,centerLat]=scenePosition(time),b=activeBeat(time);
 return <>
  <CameraRig distance={distance}/><ambientLight intensity={1.3}/><directionalLight position={[12,15,40]} intensity={2}/>
  <group rotation={[-MAP_PITCH,0,radians(-20)]}>
   <group position={[-centerLon,-merc(centerLat),0]}>
    <MapPlane/>
    {b?.region&&b.color?<Region id={b.region} color={b.color} alpha={opacity(time,b.from,b.to)}/>:null}
    <Journey time={time} view={view}/><Branch time={time} view={view}/>{privateAssets?<ShipArtwork time={time} view={view}/>:<Ship time={time} view={view}/>}
   </group>
  </group>
 </>;
}
export const Map3D:React.FC<{privateAssets:boolean}>=({privateAssets})=>{
 const frame=useCurrentFrame(),{width,height,fps}=useVideoConfig();
 const time=frame/fps,view=viewAt(time),fov=40;
 const dist=view/(2*(width/height)*Math.tan(radians(fov/2)));
 return <ThreeCanvas width={width} height={height} camera={{position:[0,0,dist],fov,near:.1,far:2000}} gl={{antialias:true,preserveDrawingBuffer:true}}>
  <color attach="background" args={['#072337']}/><Scene time={time} view={view} distance={dist} privateAssets={privateAssets}/>
 </ThreeCanvas>;
};
