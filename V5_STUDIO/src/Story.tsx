import React, {useMemo} from 'react';
import {AbsoluteFill,Img,Sequence,staticFile,useCurrentFrame,useVideoConfig,interpolate as rInterpolate} from 'remotion';
import {interpolate as morph} from 'flubber';
import {MapView,projected} from './MapView';
import {GlobeView} from './GlobeView';
import {PortraitView} from './PortraitView';

const ease=(v:number,a:number,b:number)=>rInterpolate(v,[a,b],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});
const fade=(t:number,a:number,b:number,c:number,d:number)=>ease(t,a,b)*(1-ease(t,c,d));
const anton='Anton, Impact, sans-serif',lato='Lato, Arial, sans-serif';
const gold='#f1d196',cream='#f5ead7';
const frameStyle:React.CSSProperties={position:'absolute',inset:0,overflow:'hidden'};
function Fonts(){return <style>{`@font-face{font-family:Anton;src:url('${staticFile('fonts/Anton-Regular.ttf')}') format('truetype')}@font-face{font-family:Lato;src:url('${staticFile('fonts/Lato-Regular.ttf')}') format('truetype')}@font-face{font-family:Lato;src:url('${staticFile('fonts/Lato-Bold.ttf')}') format('truetype');font-weight:700}`}</style>}
function Vignette(){return <AbsoluteFill style={{pointerEvents:'none',background:'radial-gradient(ellipse at 55% 48%, transparent 42%, rgba(3,11,15,.23) 77%, rgba(3,10,13,.55) 100%)'}}/>}
function LeftShade(){return <AbsoluteFill style={{pointerEvents:'none',background:'linear-gradient(90deg, rgba(5,15,20,.88) 0%, rgba(7,17,21,.71) 26%, rgba(7,17,21,.20) 53%, transparent 69%)'}}/>}
function Caption({t}:{t:number}){
 const p=projected(-6.35,36.77,t,1920,1080),a=fade(t,3.55,3.90,6.85,7.2);
 return <div style={{position:'absolute',left:p.x,top:p.y-79,opacity:a,pointerEvents:'none'}}>
  <svg width="230" height="100" viewBox="0 0 230 100" style={{position:'absolute',left:0,top:0}}><path d="M0 80 L32 48 L220 48" fill="none" stroke="#ead5a8" strokeWidth="2" opacity=".9"/></svg>
  <div style={{position:'absolute',left:40,top:10,width:185,textAlign:'left',fontFamily:lato,fontSize:22,fontWeight:700,letterSpacing:3,color:cream,textShadow:'0 2px 5px #000'}}>SANLÚCAR</div>
 </div>;
}
function MapTitles({t}:{t:number}){
 const a=fade(t,.65,1.05,4.3,4.75),b=fade(t,4.70,5.05,7.0,7.35),five=ease(t,2.78,3.07),one=ease(t,6.06,6.20);
 const p5='M95 10 L14 10 L14 61 L68 61 L68 102 L14 102 L14 130 L99 130 L99 52 L43 52 L43 36 L95 36 Z';
 const p1='M43 12 L72 12 L72 103 L98 103 L98 130 L12 130 L12 103 L40 103 L40 47 L14 58 L14 31 Z';
 const shape=useMemo(()=>morph(p5,p1,{maxSegmentLength:2}),[]);
 return <>
  <div style={{position:'absolute',left:130,top:140,opacity:a,color:cream}}>
   <div style={{fontFamily:lato,fontSize:32,fontWeight:700,letterSpacing:7,color:gold}}>SEPTEMBER</div>
   <div style={{fontFamily:anton,fontSize:204,lineHeight:.98,letterSpacing:3,textShadow:'0 5px 18px #071014'}}>1519</div>
   <div style={{opacity:five,transform:`translateY(${(1-five)*25}px)`,marginTop:20}}>
    <div style={{fontFamily:anton,fontSize:86,lineHeight:1,letterSpacing:2}}>FIVE SHIPS</div>
    <div style={{fontFamily:lato,fontSize:27,letterSpacing:4,marginTop:14,color:'#e2c99f'}}>SAILED FROM SPAIN</div>
    <Img src={staticFile('generated/fleet-five.svg')} style={{width:550,height:85,marginTop:25}}/>
   </div>
  </div>
  <div style={{position:'absolute',left:130,top:167,width:700,opacity:b,color:cream}}>
   <div style={{position:'relative',height:38,fontFamily:lato,fontSize:30,fontWeight:700,letterSpacing:4,color:gold}}>
    <div style={{position:'absolute',left:0,top:0,opacity:1-ease(t,5.93,6.02)}}>THE ORIGINAL FLEET</div>
    <div style={{position:'absolute',left:0,top:0,opacity:ease(t,6.22,6.38)}}>NEARLY THREE YEARS LATER</div>
   </div>
   <div style={{display:'flex',alignItems:'center',gap:36,marginTop:20}}>
    <svg width="175" height="215" viewBox="0 0 110 140" aria-label="fleet count"><path d={shape(one)} fill={cream}/></svg>
    <div style={{position:'relative',width:430,height:240,fontFamily:anton,fontSize:73,lineHeight:1.03,letterSpacing:1}}>
     <div style={{position:'absolute',inset:0,opacity:1-ease(t,5.93,6.02)}}>SHIPS<br/><span style={{color:gold}}>SET SAIL</span></div>
     <div style={{position:'absolute',inset:0,opacity:ease(t,6.22,6.38)}}>SHIP<br/><span style={{color:gold}}>COMPLETED</span><br/>THE VOYAGE</div>
    </div>
   </div>
   <Img src={staticFile(one>.5?'generated/fleet-one.svg':'generated/fleet-five.svg')} style={{width:550,height:85,marginTop:22}}/>
  </div>
  <div style={{position:'absolute',left:130,bottom:79,opacity:fade(t,1.2,1.7,6.8,7.2),display:'flex',alignItems:'center',gap:17}}>
   <Img src={staticFile('generated/castilian-standard.svg')} style={{width:66,height:49,boxShadow:'0 2px 9px #0009'}}/>
   <span style={{fontFamily:lato,fontSize:22,fontWeight:700,letterSpacing:3,color:'#dfd0b6'}}>CASTILIAN CROWN</span>
  </div>
 </>;
}
function HeroShip({t}:{t:number}){
 const o=fade(t,.25,1,6.80,7.22),x=rInterpolate(t,[0,7],[15,-15],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});
 return <Img src={staticFile('private/ship_cutout_trim.png')} style={{position:'absolute',right:560+x,top:390,width:720,height:'auto',opacity:o,filter:'drop-shadow(0 22px 22px rgba(0,0,0,.65))'}}/>;
}
function Orbit({t}:{t:number}){
 const index=Math.max(1,Math.min(71,Math.floor((t-7.52)*24)+1));
 return <Img src={staticFile(`private/manim_frames/${String(index).padStart(3,'0')}.png`)} style={{position:'absolute',left:-265,top:-360,width:3200,height:1800,opacity:fade(t,7.48,7.85,10.95,11.3),pointerEvents:'none'}}/>;
}
function GlobeTitles({t}:{t:number}){
 const alpha=fade(t,7.7,8.18,10.98,11.35),word=ease(t,9.35,9.65);
 return <div style={{position:'absolute',left:130,top:285,width:935,opacity:alpha,color:cream}}>
  <div style={{fontFamily:lato,fontSize:30,fontWeight:700,letterSpacing:6,color:gold}}>THE FIRST RECORDED</div>
  <div style={{fontFamily:anton,fontSize:90,lineHeight:1.04,letterSpacing:1.4,marginTop:28,textShadow:'0 5px 20px #0009',opacity:word,transform:`translateY(${(1-word)*22}px)`}}>CIRCUMNAVIGATION</div>
  <div style={{fontFamily:lato,fontSize:30,letterSpacing:4,marginTop:23,opacity:ease(t,10.26,10.52)}}>OF THE EARTH</div>
 </div>;
}
function CharacterTitles({t}:{t:number}){
 const eyebrow=fade(t,12.42,12.76,14.7,15),name=fade(t,13.38,13.70,14.7,15);
 return <div style={{position:'absolute',left:130,top:315,width:880,color:cream}}>
  <div style={{fontFamily:lato,fontSize:30,fontWeight:700,letterSpacing:5,color:gold,opacity:eyebrow}}>PORTUGUESE NAVIGATOR</div>
  <div style={{fontFamily:lato,fontSize:49,letterSpacing:7,marginTop:35,opacity:name}}>FERDINAND</div>
  <div style={{fontFamily:anton,fontSize:145,lineHeight:1.04,letterSpacing:2,marginTop:10,textShadow:'0 6px 22px #000a',opacity:name,transform:`translateY(${(1-name)*20}px)`}}>MAGELLAN</div>
 </div>;
}
export const MagellanPilot:React.FC=()=>{
 const frame=useCurrentFrame(),{fps}=useVideoConfig();const t=frame/fps;
 const globe=fade(t,7.08,7.55,11.05,11.42),character=ease(t,11.03,11.42),first=1-ease(t,7.08,7.55);
 return <AbsoluteFill style={{backgroundColor:'#0b1d22',color:cream}}>
  <Fonts/>
  <Sequence from={0} durationInFrames={Math.ceil(7.6*fps)}><AbsoluteFill style={{opacity:first}}><MapView/><Vignette/><LeftShade/><Caption t={t}/><HeroShip t={t}/><MapTitles t={t}/></AbsoluteFill></Sequence>
  <AbsoluteFill style={{opacity:globe,background:'radial-gradient(circle at 69% 46%,#25414a 0%,#10242d 40%,#07131a 100%)'}}>
   <Sequence from={7*fps} durationInFrames={Math.ceil(4.5*fps)}><GlobeView start={7}/></Sequence>
   <Orbit t={t}/><GlobeTitles t={t}/><Vignette/>
  </AbsoluteFill>
  <AbsoluteFill style={{opacity:character}}>
   <Sequence from={11*fps}><MapView timeOffset={11}/></Sequence><Vignette/><LeftShade/>
   <Sequence from={11*fps}><PortraitView start={11}/></Sequence><CharacterTitles t={t}/>
  </AbsoluteFill>
  <AbsoluteFill style={{pointerEvents:'none',backgroundColor:'#050b0e',opacity:ease(t,14.75,15)}}/>
 </AbsoluteFill>;
};
