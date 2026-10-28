import React, {useEffect, useState} from 'react';
import {AbsoluteFill, Img, continueRender, delayRender, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {activeBeat, opacity, smooth} from './timeline';

type Caption={from:number;to:number;text:string};
const Flag:React.FC<{kind:'spain'|'portugal';size:number}>=({kind,size})=>kind==='spain'?
  <svg width={size} height={size*.66} viewBox="0 0 120 80" aria-label="Simplified Cross of Burgundy"><rect width="120" height="80" fill="#f0eadb"/><path d="M7 5 L113 75 M113 5 L7 75" stroke="#a31e29" strokeWidth="11"/></svg>:
  <svg width={size} height={size*.66} viewBox="0 0 120 80" aria-label="Simplified Portuguese royal banner"><rect width="120" height="80" fill="#eee8d9"/><rect x="38" y="8" width="44" height="60" rx="17" fill="#9b2731"/><rect x="44" y="14" width="32" height="47" rx="12" fill="#e8dfca"/><path d="M60 17 v31 M48 29 h24" stroke="#224d83" strokeWidth="7"/></svg>;

function Captions({enabled,time,scale}:{enabled:boolean;time:number;scale:number}) {
 const [captions,setCaptions]=useState<Caption[]>([]);
 const [handle]=useState(()=>enabled?delayRender('Loading the original timed captions'):null);
 useEffect(()=>{if(!enabled||handle===null)return;fetch(staticFile('private/subtitles.json')).then(x=>{if(!x.ok)throw new Error('Caption file unavailable');return x.json();}).then(setCaptions).finally(()=>continueRender(handle));},[enabled,handle]);
 if(!enabled)return null;
 const c=captions.find(x=>time>=x.from&&time<x.to);if(!c)return null;
 return <div style={{position:'absolute',bottom:37*scale,left:'11%',right:'11%',textAlign:'center',fontFamily:'Lato, sans-serif',fontSize:30*scale,fontWeight:700,lineHeight:1.25,color:'#f7f5ea',textShadow:'0 2px 5px #07141b, 0 0 20px #07141b'}}>{c.text}</div>;
}

export const Overlay:React.FC<{privateAssets:boolean}>=({privateAssets})=>{
 const frame=useCurrentFrame(),{width,fps}=useVideoConfig();const t=frame/fps,sc=width/1920,b=activeBeat(t);
 const a=b?opacity(t,b.from,b.to):0;
 const portraitSide=b?.side??'left';
 const fade=a;
 const titleRight=!!b?.image && portraitSide==='left';
 const titleStyle:React.CSSProperties={position:'absolute',top:64*sc,
  ...(titleRight?{right:100*sc,textAlign:'right'}:{left:100*sc,textAlign:'left'}),
  maxWidth:'51%',opacity:fade,color:'#f8f3e5',textShadow:'0 2px 6px #06151d,0 0 24px #06151d',
  transform:`translateY(${(1-fade)*12*sc}px)`};
 return <AbsoluteFill style={{pointerEvents:'none',overflow:'hidden'}}>
  <style>{`@font-face{font-family:Anton;src:url('${staticFile('fonts/Anton-Regular.ttf')}')} @font-face{font-family:Lato;src:url('${staticFile('fonts/Lato-Regular.ttf')}')} @font-face{font-family:Lato;src:url('${staticFile('fonts/Lato-Bold.ttf')}');font-weight:700}`}</style>
  {/* A gentle exposure treatment and bottom subtitle gradient, no top bar or map frame. */}
  <AbsoluteFill style={{background:'linear-gradient(0deg,rgba(3,12,18,.76) 0%,rgba(3,12,18,.17) 16%,transparent 38%), radial-gradient(ellipse at 50% 42%,transparent 40%,rgba(5,15,22,.35) 100%)'}}/>
  {b?<div style={titleStyle}>
    <div style={{fontFamily:'Anton, sans-serif',fontSize:(b.title.length>21?60:73)*sc,lineHeight:1.08,letterSpacing:1.1*sc}}>{b.title}</div>
    <div style={{fontFamily:'Lato, sans-serif',fontWeight:700,fontSize:23*sc,letterSpacing:3.2*sc,color:'#e4c497',marginTop:9*sc}}>{b.subtitle}</div>
  </div>:null}
  {privateAssets&&b?.image?<div style={{position:'absolute',bottom:'17.5%',[portraitSide]:70*sc,width:'30%',height:'53%',opacity:fade,
       transform:`translateY(${(1-fade)*22*sc}px)`,display:'flex',alignItems:'end',justifyContent:'center'}}>
    <Img src={staticFile(`private/${b.image}.png`)} style={{maxHeight:'100%',maxWidth:'100%',objectFit:'contain',filter:'drop-shadow(0 8px 12px rgba(0,0,0,.62))'}}/>
  </div>:null}
  {privateAssets&&b?.secondImage?<div style={{position:'absolute',bottom:'17.5%',left:65*sc,width:'26%',height:'48%',opacity:fade,display:'flex',alignItems:'end',justifyContent:'center'}}>
    <Img src={staticFile(`private/${b.secondImage}.png`)} style={{maxHeight:'100%',maxWidth:'100%',objectFit:'contain',filter:'drop-shadow(0 8px 12px rgba(0,0,0,.62))'}}/>
  </div>:null}
  {b?.flag?<div style={{position:'absolute',left:'55%',top:'38%',opacity:fade,filter:'drop-shadow(0 3px 6px #06131a)',transform:`translateY(${(1-fade)*10*sc}px)`}}><Flag kind={b.flag} size={120*sc}/></div>:null}
  <Captions enabled={privateAssets} time={t} scale={sc}/>
 </AbsoluteFill>;
};
