import fs from 'node:fs';
// Repaint the 4:3 flag-icons Spain icon's field as an early-16th-century
// Burgundian saltire. The modern red-yellow-red flag is intentionally NOT
// shown as though it were used in 1519.
const original=fs.readFileSync('node_modules/flag-icons/flags/4x3/es.svg','utf8');
const box=original.match(/viewBox="([^"]+)"/)?.[1];
const field=original.match(/<path fill="#[0-9A-Fa-f]+" d="([^"]+)"\s*\/>/)?.[1];
if(!box||!field)throw new Error('flag-icons source shape changed');
const svg=`<svg xmlns="http://www.w3.org/2000/svg" viewBox="${box}"><path d="${field}" fill="#e6ddc8"/><path d="M70 52 L564 420 M570 54 L76 424" fill="none" stroke="#7c201c" stroke-width="46" stroke-linecap="square"/><path d="M171 88l-30 39m83 11-29 38m84 10-30 38m83 10-29 38m82 10-28 38m83 12-29 37M467 87l30 39m-82 11 29 38m-83 11 29 38m-83 10 29 38m-82 10 29 38m-82 12 29 37" fill="none" stroke="#7c201c" stroke-width="13"/></svg>`;
fs.writeFileSync('public/generated/castilian-standard.svg',svg);
console.log('Repainted the flag-icons Spain field as a historical Burgundian saltire.');
