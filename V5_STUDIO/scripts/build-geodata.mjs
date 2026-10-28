import fs from 'node:fs';
import {execFileSync} from 'node:child_process';
import {feature} from 'topojson-client';
import {geoDistance,geoInterpolate} from 'd3-geo';
import {lineString} from '@turf/helpers';
import length from '@turf/length';
import along from '@turf/along';

fs.mkdirSync('public/generated',{recursive:true});
const topo=JSON.parse(fs.readFileSync('node_modules/world-atlas/countries-110m.json','utf8'));
const features=feature(topo,topo.objects.countries);
fs.writeFileSync('public/generated/world-countries.json',JSON.stringify(features));
// Historical Basemaps: 1500 is an approximation for the 1519 political scene.
// Source data is GPL-3.0; original and license are distributed in data/.
execFileSync('node',['node_modules/mapshaper/bin/mapshaper','data/historical_world_1500.geojson','-filter',"NAME == 'Portugal' || NAME == 'Castille' || NAME == 'Aragón'",'-simplify','15%','keep-shapes','-o','format=geojson','public/generated/iberian-realms-1500.json'],{stdio:'inherit'});
const iberia=JSON.parse(fs.readFileSync('public/generated/iberian-realms-1500.json'));
if(iberia.features.length!==3)throw new Error('Expected three historic Iberian realms');
// Approximate sea-waypoints; not a certified navigation reconstruction.
const stops=[[-6.35,36.77],[-9,35.4],[-16.5,28.2],[-25,10],[-30,0],[-33,-8],[-38,-16],[-40,-22],[-42,-24],[-44,-26],[-46,-29],[-48,-35],[-54,-38],[-61,-43],[-63,-47],[-65,-50],[-66,-52],[-68.315,-52.35],[-68.4,-52.435],[-69.445,-52.405],[-69.9,-52.665],[-70.42,-52.72],[-71.065,-53.935],[-72.06,-53.785],[-72.44,-53.56],[-72.55,-53.56],[-73.26,-53.235],[-73.575,-52.98],[-74.225,-52.815],[-74.53,-52.68],[-77,-50],[-95,-30],[-135,-12],[-150,-8],[-175,6],[165,13],[145,14],[130,13],[127,11.5],[126,10.5],[126.7,8.2],[127.8,5],[127,2],[127.4,1],[127.5,.5],[123.5,-3.5],[123.5,-5],[120.5,-8],[120,-8],[116.5,-11.5],[116,-11.5],[115.5,-12],[115,-12],[95,-12],[72,-20],[42,-29],[23,-35],[18,-35],[7,-22],[-15,5],[-23,15],[-12,33],[-6.35,36.77]];
const route=lineString(stops),total=length(route,{units:'kilometers'}),samples=[];
for(let i=0;i<=240;i++){const p=along(route,total*i/240,{units:'kilometers'});samples.push(p.geometry.coordinates)}
// d3-geo provides spherical distance and a smoothly interpolated first leg.
const firstLeg=geoInterpolate(stops[0],stops[1]);
const d3Samples=Array.from({length:21},(_,i)=>firstLeg(i/20));
fs.writeFileSync('public/generated/route.json',JSON.stringify({stops,samples,firstLeg:d3Samples,approxKm:Math.round(total),firstLegRadians:geoDistance(stops[0],stops[1])}));
console.log(`Built ${features.features.length} world features, ${iberia.features.length} historical realms, and ${samples.length} Turf route samples.`);
