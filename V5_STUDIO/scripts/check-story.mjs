import assert from 'node:assert/strict';
import fs from 'node:fs';
import {geoContains} from 'd3-geo';
const iberia=JSON.parse(fs.readFileSync('public/generated/iberian-realms-1500.json'));
assert.deepEqual(iberia.features.map(f=>f.properties.NAME).sort(),['Aragón','Castille','Portugal'].sort());
const route=JSON.parse(fs.readFileSync('public/generated/route.json'));
const countries=JSON.parse(fs.readFileSync('public/generated/world-countries.json')).features;
const intersections=route.samples.map((p,i)=>({p,i,hit:countries.filter(c=>geoContains(c,p)).map(c=>c.properties.name)})).filter(p=>p.hit.length);
// Modern low-resolution land polygons do not resolve the Strait of Magellan.
// Home port is naturally a land sample. Reject other coarse land intersections.
const unexpected=intersections.filter(({p,i,hit})=>!(i===0||i===route.samples.length-1||(p[0]<-66&&p[0]>-77&&p[1]<-50&&hit.every(h=>h==='Chile'||h==='Argentina'))));
assert.equal(unexpected.length,0,`Unexpected coarse land intersections: ${JSON.stringify(unexpected)}`);
assert.equal(route.samples.length,241);
assert(fs.existsSync('public/generated/fleet-five.svg'));
assert(fs.existsSync('public/generated/fleet-one.svg'));
assert(fs.existsSync('public/generated/castilian-standard.svg'));
assert(route.approxKm>40000 && route.approxKm<100000);
console.log('PASS route water checks outside coarse strait, historical layer, and generated infographics.');
console.log('Limitations: route is illustrative; 1500 borders approximate the 1519 scene.');
