import React,{useMemo} from 'react';
import {ThreeCanvas} from '@remotion/three';
import {useGLTF} from '@react-three/drei';
import {staticFile,useCurrentFrame,useVideoConfig} from 'remotion';
import * as THREE from 'three';
function Mesh(){
 const {scene}=useGLTF(staticFile('private/ship_triposr_new.glb'));const f=useCurrentFrame();
 const model=useMemo(()=>{const o=scene.clone(true);o.traverse(x=>{if((x as THREE.Mesh).isMesh){const m=x as THREE.Mesh;m.material=new THREE.MeshStandardMaterial({vertexColors:true,side:THREE.DoubleSide,roughness:.8});}});return o},[scene]);
 const axis=new THREE.Matrix4().set(0,1,0,0, 0,0,1,0, 1,0,0,0, 0,0,0,1);
 const q=new THREE.Quaternion().setFromRotationMatrix(axis);
 return <group rotation={[0,f>0?.7:0,0]} scale={3}><group quaternion={q}><primitive object={model}/></group></group>;
}
export const MeshPreview:React.FC=()=>{const {width,height}=useVideoConfig();return <ThreeCanvas width={width} height={height} camera={{position:[0,0,5],fov:35,near:.1,far:50}} gl={{antialias:true,preserveDrawingBuffer:true}}><color attach="background" args={['#263e4a']}/><ambientLight intensity={1.4}/><directionalLight position={[3,4,6]} intensity={2}/><Mesh/></ThreeCanvas>};
