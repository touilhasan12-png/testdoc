import {readFile} from 'node:fs/promises';
import ts from 'typescript';
const input=await readFile(new URL('../src/timeline.ts',import.meta.url),'utf8');
const js=ts.transpileModule(input,{compilerOptions:{module:ts.ModuleKind.ESNext,target:ts.ScriptTarget.ES2020}}).outputText;
const t=await import('data:text/javascript;base64,'+Buffer.from(js).toString('base64'));
for(let i=0;i<t.BEATS.length;i++){
 const b=t.BEATS[i];
 if(!(b.from>=0&&b.to<=120&&b.from<b.to))throw Error('Invalid beat '+JSON.stringify(b));
 if(i&&t.BEATS[i-1].to>b.from+1e-6)throw Error('Overlapping timed beat labels: '+i);
}
for(let i=1;i<t.ROUTE.length;i++)if(t.ROUTE[i][0]<=t.ROUTE[i-1][0])throw Error('Route is not time ordered');
for(let i=1;i<t.VIEWS.length;i++)if(t.VIEWS[i][0]<=t.VIEWS[i-1][0])throw Error('Camera is not time ordered');
for(let f=0;f<2880;f++){
 const time=f/24;const [lon,lat]=t.scenePosition(time),v=t.viewAt(time);
 if(!Number.isFinite(lon)||!Number.isFinite(lat)||!Number.isFinite(v)||v<=0||lat < -80||lat > 80)throw Error('Invalid camera at frame '+f);
}
console.log(`PASS: ${t.BEATS.length} non-overlapping beats; ${t.ROUTE.length} route points; 2880 camera samples.`);
console.log('Text/portrait vertical safe zones are defined separately in Overlay.tsx and require visual review.');
