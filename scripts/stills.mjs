// QA stills: bundles the project once, renders chosen frames with one shared browser (no video render).
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition, openBrowser} from '@remotion/renderer';
import path from 'node:path';
import fs from 'node:fs';

const frames = (process.env.FRAMES || '30').split(',').map((s) => parseInt(s.trim(), 10)).filter((n) => Number.isFinite(n));
const outDir = path.resolve('out/stills');
fs.mkdirSync(outDir, {recursive: true});
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts')});
const browser = await openBrowser('chrome', {browserExecutable: null, chromiumOptions: {}});
const comp = await selectComposition({serveUrl, id: 'TokyoSample', puppeteerInstance: browser});
for (const f of frames) {
  const t0 = Date.now();
  await renderStill({
    composition: comp,
    serveUrl,
    frame: f,
    output: path.join(outDir, `f${String(f).padStart(4, '0')}.jpg`),
    imageFormat: 'jpeg',
    jpegQuality: 72,
    scale: 0.6667,
    puppeteerInstance: browser,
    timeoutInMilliseconds: 120000,
  });
  console.log('still', f, Date.now() - t0, 'ms');
}
await browser.close({silent: true});
