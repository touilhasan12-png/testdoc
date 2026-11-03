import React from 'react';
import {AbsoluteFill,Audio,Composition,Img,interpolate,staticFile,useCurrentFrame} from 'remotion';
const clamp={extrapolateLeft:'clamp',extrapolateRight:'clamp'} as const;
const Opening:React.FC=()=>{
 const f=useCurrentFrame(), shot=f<240?0:1,t=shot===0?f:f-240;
 const reveal=interpolate(f,[18,55],[0,1],clamp),number=interpolate(f,[55,90],[0,1],clamp);
 const zoom=shot===0?1.04+t*.00014:1.13+t*.00012;
 const x=(139.6917-124)/26*1920,y=(47-35.6895)/19*1403;
 return <AbsoluteFill style={{background:'#030b11',fontFamily:'Arial, sans-serif',color:'#f1eee4',overflow:'hidden'}}>
  <AbsoluteFill style={{transform:`translate(${-t*.035}px, ${-145-t*.018}px) scale(${zoom})`,transformOrigin:'55% 55%',height:1403}}>
   <Img src={staticFile('japan.jpg')} style={{width:1920,height:1403,filter:'brightness(.27) saturate(.4) contrast(1.2)'}}/>
   <svg width="1920" height="1403" style={{position:'absolute',inset:0}}>
    <defs><radialGradient id="city"><stop stopColor="#ffedb1" stopOpacity=".9"/><stop offset=".18" stopColor="#ffb24e" stopOpacity=".7"/><stop offset="1" stopColor="#ed8126" stopOpacity="0"/></radialGradient></defs>
    <g stroke="#aac2c7" strokeWidth="1" opacity=".09">{[0,1,2,3,4,5,6].map(i=><path key={i} d={`M ${i*320} 0 V1403 M0 ${i*240} H1920`}/>)}</g>
    <g opacity={reveal}><ellipse cx={x} cy={y} rx="95" ry="65" fill="url(#city)"/><circle cx={x} cy={y} r="6" fill="#fff4cd"/><path d={`M${x+13} ${y}h62l22 -25h130`} fill="none" stroke="#edc17e" strokeWidth="2"/><text x={x+105} y={y-39} fontSize="31" letterSpacing="7" fill="#ffe8bb">TOKYO</text></g>
    <text x="1110" y="490" fontSize="35" letterSpacing="15" fill="#c7d1cd" opacity=".55">J A P A N</text>
    <text x="1450" y="1070" fontSize="20" letterSpacing="7" fill="#9cafb7" opacity=".4">PACIFIC OCEAN</text>
   </svg>
  </AbsoluteFill>
  <div style={{position:'absolute',top:65,left:75,fontSize:21,letterSpacing:5,color:'#9baeb7'}}>THE DEMOGRAPHIC PARADOX</div>
  <div style={{position:'absolute',right:76,top:61,border:'1px solid #8e9b9b',padding:'14px 22px',fontSize:28,letterSpacing:5}}>2025</div>
  <div style={{position:'absolute',left:90,top:350,opacity:number}}>
   <div style={{fontSize:123,fontWeight:700,letterSpacing:-5,color:'#ffad83',textShadow:'0 0 36px #a8392870'}}>−{Math.round(918253*number).toLocaleString('en-US')}</div>
   <div style={{fontSize:23,letterSpacing:4,marginTop:13,color:'#e7c4b4'}}>DEATHS MINUS BIRTHS</div>
   <div style={{fontSize:19,letterSpacing:2,marginTop:18,color:'#a6b4b9'}}>JAPANESE NATIONALS · ONE YEAR</div>
  </div>
  {shot===1&&<div style={{position:'absolute',left:94,bottom:158,fontSize:33,letterSpacing:1,color:'#e7e1d4',opacity:interpolate(t,[0,22],[0,1],clamp)}}>Bigger than San Francisco. Gone.</div>}
  <div style={{position:'absolute',bottom:0,height:98,left:0,right:0,background:'linear-gradient(transparent,#020811)',display:'flex',alignItems:'center',padding:'25px 75px 0',fontSize:17,letterSpacing:1,color:'#9cabaf'}}>DATA: MHLW · 2025 VITAL STATISTICS (APPROVED SCRIPT) <span style={{marginLeft:'auto'}}>BASEMAP: NASA GIBS · BLUE MARBLE</span></div>
  <Audio src={staticFile('vo.mp3')}/><Audio src={staticFile('pad.wav')} volume={.40}/><Audio src={staticFile('sfx.wav')} volume={.5}/>
 </AbsoluteFill>
};
export const Root=()=> <Composition id="TokyoOpening" component={Opening} width={1920} height={1080} fps={30} durationInFrames={630}/>;
