import fs from 'node:fs';
import * as echarts from 'echarts';
// Reproducible server-side SVG.  The illuminated ship is Victoria; four dim
// ships do not imply that all four sank (one deserted, others were lost).
const ship='path://M 5 36 L 68 36 L 58 48 L 19 48 Z M 24 33 L 24 7 L 27 7 L 27 33 Z M 29 8 L 29 30 L 54 30 Z M 20 11 L 4 30 L 20 30 Z';
function make(active,name){
 const chart=echarts.init(null,null,{renderer:'svg',ssr:true,width:650,height:100});
 chart.setOption({animation:false,backgroundColor:'transparent',grid:{left:0,right:0,top:0,bottom:0},
  xAxis:{type:'category',data:['1','2','3','4','5'],show:false},yAxis:{type:'value',max:1,show:false},
  series:[{type:'pictorialBar',symbol:ship,symbolSize:[100,66],symbolPosition:'center',
   data:[0,1,2,3,4].map((v)=>({value:1,itemStyle:{color:v<active?'#efce89':'rgba(238,221,182,0.18)'}}))}]});
 fs.writeFileSync(`public/generated/${name}.svg`,chart.renderToSVGString());chart.dispose();
}
fs.mkdirSync('public/generated',{recursive:true});make(5,'fleet-five');make(1,'fleet-one');
console.log('ECharts rendered the five-ship and one-completed-voyage SVG infographics.');
