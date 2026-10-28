// All cues are measured against the existing 120-second English narration.
// Locations and route are editorial approximations, not navigation data.
export type Point = [number, number, number]; // seconds, unwrapped longitude, latitude
export type Beat = {
  from: number; to: number; title: string; subtitle: string;
  image?: string; secondImage?: string; side?: 'left' | 'right';
  flag?: 'spain' | 'portugal'; region?: string; color?: string;
};
export const ROUTE: Point[] = [
  [0,-6.35,36.78],[15.1,-6.35,36.78],[17.7,-15.5,28.2],[22.2,-38,-13],
  [24.7,-43.2,-22.9],[27.1,-49,-29.0],[30.8,-57,-36.0],[32.3,-67.8,-49.3],
  [35.4,-68.5,-50.2],[40.1,-68.5,-51.5],[42.6,-69.9,-52.5],[48.4,-73.5,-53.2],
  [52.4,-77,-50],[55,-110,-25],[57.5,-145,-15],[59.5,-180,-6],
  [61.5,-215.25,13.45],[64.4,-229.5,10],[69,-236,10.3],[76.7,-236,10.3],
  [79.2,-232.55,.68],[85.8,-232.55,.68],[88.9,-235,-4],[90.1,-262,-15],
  [92.8,-305,-27],[94.8,-341.55,-34.35],[99.8,-370,5],[101.9,-383.5,15.1],
  [105.4,-366.35,36.78],[111,-366.35,36.78],[120,-366.35,36.78]
];
// Horizontal field of view in map longitude units; moves follow narration.
export const VIEWS: [number,number][] = [
  [0,78],[8,78],[12,76],[18,78],[22,84],[29,74],[31,52],[35,44],[41,39],
  [46,34],[49,46],[53,84],[58,118],[61.5,92],[64.6,72],[69,46],[71,36],
  [75.6,55],[77,90],[80,65],[84,74],[89,95],[92,117],[95,82],[99,96],
  [102,84],[105.5,78],[110,86],[113,80],[116,92],[120,106]
];
export const BEATS: Beat[] = [
 {from:.66,to:4.033,title:'FIVE SHIPS',subtitle:'SANLÚCAR · 1519',flag:'spain',region:'724',color:'#ca9b62'},
 {from:4.033,to:6.998,title:'ONE RETURNS',subtitle:'THE LONGEST VOYAGE'},
 {from:6.998,to:10.780,title:'FIRST RECORDED',subtitle:'CIRCUMNAVIGATION'},
 {from:11.29,to:14.286,title:'FERDINAND MAGELLAN',subtitle:'PORTUGUESE NAVIGATOR',image:'magellan',side:'left',region:'620',color:'#8fa99d'},
 {from:14.286,to:18.734,title:'A SPANISH FLEET',subtitle:'BACKED BY THE CROWN',flag:'spain',region:'724',color:'#ca9b62'},
 {from:18.734,to:21.730,title:'SAILING WEST',subtitle:'THE SPICE ISLANDS'},
 {from:22.24,to:27.306,title:'BRAZIL',subtitle:'THE ATLANTIC COAST',region:'076',color:'#ce9d58'},
 {from:27.306,to:30.76,title:'FIND THE PASSAGE',subtitle:'SOUTH ALONG THE COAST'},
 {from:31.27,to:34.857,title:'WINTER & MUTINY',subtitle:'PATAGONIA · 1520',image:'mutiny',side:'left'},
 {from:34.857,to:37.139,title:'SANTIAGO',subtitle:'LOST IN A STORM',image:'wreck',side:'left'},
 {from:37.139,to:42.03,title:'SAN ANTONIO',subtitle:'DESERTS AND RETURNS'},
 {from:42.54,to:46.441,title:'THE STRAIT',subtitle:'A DANGEROUS PASSAGE'},
 {from:46.441,to:48.439,title:'THREE SHIPS',subtitle:'THROUGH THE STRAIT'},
 {from:48.439,to:52.34,title:'THE PACIFIC',subtitle:'A VAST UNKNOWN OCEAN'},
 {from:52.85,to:56.543,title:'THE CROSSING',subtitle:'NOT SO PEACEFUL'},
 {from:56.543,to:61.035,title:'98 DAYS',subtitle:'HUNGER · SCURVY · THIRST',image:'scarcity',side:'left'},
 {from:61.035,to:63.93,title:'MARIANA ISLANDS',subtitle:'ARRIVAL · 1521'},
 {from:64.44,to:69.176,title:'THE PHILIPPINES',subtitle:'LOCAL RIVALRIES',region:'608',color:'#c77e61',image:'canoe',side:'right'},
 {from:69.176,to:73.45,title:'BATTLE OF MACTAN',subtitle:'LAPULAPU RESISTS',region:'608',color:'#c77e61',image:'lapulapu',secondImage:'magellan',side:'right'},
 {from:73.45,to:76.8,title:'MAGELLAN KILLED',subtitle:'27 APRIL 1521',region:'608',color:'#c77e61',image:'magellan',side:'left'},
 {from:77.31,to:81.678,title:'THE SPICE ISLANDS',subtitle:'TIDORE · MALUKU',image:'spice',side:'right'},
 {from:81.678,to:86.046,title:'TRINIDAD',subtitle:'A LATER EASTWARD ATTEMPT'},
 {from:86.046,to:88.71,title:'VICTORIA',subtitle:'WESTWARD FOR HOME'},
 {from:89.22,to:92.83,title:'JUAN SEBASTIÁN ELCANO',subtitle:'COMMANDS VICTORIA',image:'elcano',side:'left'},
 {from:92.83,to:95.66,title:'CAPE OF GOOD HOPE',subtitle:'ROUNDING AFRICA'},
 {from:95.66,to:99.66,title:'PORTUGUESE PATROLS',subtitle:'THREATS ON THE RETURN',flag:'portugal'},
 {from:100.17,to:103.599,title:'CAPE VERDE',subtitle:'SAILORS DETAINED',flag:'portugal'},
 {from:103.599,to:107.028,title:'SANLÚCAR',subtitle:'6 SEPTEMBER 1522',flag:'spain',region:'724',color:'#ca9b62'},
 {from:107.028,to:110.931,title:'18 EUROPEANS',subtitle:'ABOARD VICTORIA'},
 {from:110.931,to:112.5,title:'ONE SHIP',subtitle:'THE FIRST RECORDED CIRCUIT'},
 {from:112.941,to:116.37,title:'PACIFIC NAVIGATORS',subtitle:'INDIGENOUS KNOWLEDGE',image:'canoe',side:'right'},
 {from:116.42,to:119.9,title:'A SHARED WORLD',subtitle:'ONE SHIP · THREE OCEANS'}
];
const ease = (x: number) => {x=Math.max(0,Math.min(1,x));return x*x*(3-2*x);};
export const smooth = ease;
export function interpolatePoint(t:number, ps:Point[]):[number,number] {
  if(t<=ps[0][0]) return [ps[0][1],ps[0][2]];
  for(let i=1;i<ps.length;i++) if(t<=ps[i][0]) {const a=ps[i-1],b=ps[i],q=ease((t-a[0])/(b[0]-a[0])); return [a[1]+(b[1]-a[1])*q,a[2]+(b[2]-a[2])*q];}
  const last=ps[ps.length-1];return [last[1],last[2]];
}
export function viewAt(t:number):number {
  for(let i=1;i<VIEWS.length;i++)if(t<=VIEWS[i][0]){const [a,x]=VIEWS[i-1],[b,y]=VIEWS[i];return x+(y-x)*ease((t-a)/(b-a));}return VIEWS[VIEWS.length-1][1];
}
export function scenePosition(t:number):[number,number] {
  if(t>=112.5){const q=ease((t-112.5)/.5);const [x,y]=interpolatePoint(111,ROUTE);return [x+(-236-x)*q,y+(10.3-y)*q];}
  return interpolatePoint(Math.max(0,t-.55),ROUTE);
}
export function activeBeat(t:number):Beat|undefined{return BEATS.find(x=>t>=x.from&&t<x.to);}
export function opacity(t:number,a:number,b:number):number{return ease((t-a)/.38)*ease((b-t)/.32);}
