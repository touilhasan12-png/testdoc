// Builds the non-VO beds for the sample: a quiet pad (Dm-Bb-C-Am, peak 0.066)
// and event-synced SFX. Output is 48 kHz stereo 16-bit WAV in out/audio/.
// VO files are NOT regenerated here; they are placed unchanged by assemble-sample.sh.
import {mkdirSync, readFileSync, writeFileSync} from 'node:fs';

const SR = 48000;
const DUR = 300; // seconds
const N = SR * DUR;
const PAD_PEAK = 0.066;

const L = new Float32Array(N);
const R = new Float32Array(N);

const hz = (midi) => 440 * Math.pow(2, (midi - 69) / 12);
// Chord voicings (MIDI): Dm, Bb, C, Am; each held 9 s with 2 s crossfades.
const CHORDS = [
  [50, 57, 62, 65, 69], // Dm  (D3 A3 D4 F4 A4)
  [46, 53, 58, 62, 65], // Bb
  [48, 55, 60, 64, 67], // C
  [45, 52, 57, 60, 64], // Am
];
const SEG = 9;
const XF = 2;

// Pad: detuned sines with a slow amplitude drift; no randomness, fully deterministic.
for (let i = 0; i < N; i++) {
  const t = i / SR;
  const k = Math.floor(t / SEG);
  const inSeg = t - k * SEG;
  const cur = CHORDS[k % CHORDS.length];
  const nxt = CHORDS[(k + 1) % CHORDS.length];
  // crossfade over the last XF seconds of each segment
  const mix = Math.min(1, Math.max(0, (inSeg - (SEG - XF)) / XF));
  let l = 0;
  let r = 0;
  const lfo = 0.85 + 0.15 * Math.sin((2 * Math.PI * t) / 17);
  const fade = Math.min(1, t / 3) * Math.min(1, (DUR - t) / 3);
  const addNotes = (notes, w) => {
    for (let n = 0; n < notes.length; n++) {
      const f = hz(notes[n]);
      const ph = 2 * Math.PI * f * t;
      const v = Math.sin(ph) + 0.35 * Math.sin(2 * ph) + 0.12 * Math.sin(3 * ph);
      const det = 1.0035;
      const v2 = Math.sin(ph * det) + 0.35 * Math.sin(2 * ph * det);
      l += w * (v * 0.6 + v2 * 0.4) * (n % 2 ? 0.9 : 1.1);
      r += w * (v * 0.4 + v2 * 0.6) * (n % 2 ? 1.1 : 0.9);
    }
  };
  addNotes(cur, (1 - mix) / cur.length);
  addNotes(nxt, mix / nxt.length);
  L[i] = l * lfo * fade;
  R[i] = r * lfo * fade;
}

// Normalise the pad so its peak is exactly PAD_PEAK.
let peak = 0;
for (let i = 0; i < N; i++) peak = Math.max(peak, Math.abs(L[i]), Math.abs(R[i]));
const padGain = PAD_PEAK / peak;
for (let i = 0; i < N; i++) {
  L[i] *= padGain;
  R[i] *= padGain;
}

// SFX bed: each event is synthesised from a deterministic LCG noise source.
const SFX = new Float32Array(N * 2);
const sfxEvents = JSON.parse(readFileSync('src/data/sfx-events.json', 'utf8'));
let seed = 7;
const noise = () => {
  seed = (seed * 1664525 + 1013904223) >>> 0;
  return seed / 4294967296 - 0.5;
};
const addAt = (startSec, dur, gen, amp, pan = 0) => {
  const s0 = Math.round(startSec * SR);
  const len = Math.round(dur * SR);
  for (let j = 0; j < len && s0 + j < N; j++) {
    const v = gen(j / SR, j) * amp;
    SFX[(s0 + j) * 2] += v * (1 - Math.max(0, pan));
    SFX[(s0 + j) * 2 + 1] += v * (1 + Math.min(0, pan));
  }
};
let lp = 0;
const whoosh = (t) => {
  const env = Math.min(1, t / 0.35) * Math.exp(-t * 2.4);
  lp += (noise() - lp) * (0.02 + 0.2 * Math.min(1, t / 0.8));
  return lp * env * 2.2;
};
const tick = (t) => Math.sin(2 * Math.PI * 1800 * t) * Math.exp(-t * 220);
const thud = (t) => {
  const f = 90 * Math.exp(-t * 6) + 40;
  return (Math.sin(2 * Math.PI * f * t) * Math.exp(-t * 5) + noise() * Math.exp(-t * 60) * 0.5);
};
const stampGen = (t) => thud(t) * (t < 0.6 ? 1 : 0);
const chime = (t) =>
  (Math.sin(2 * Math.PI * 660 * t) + 0.6 * Math.sin(2 * Math.PI * 990 * t)) * Math.exp(-t * 2.2);

for (const ev of sfxEvents) {
  if (ev.kind === 'whoosh') addAt(ev.t, 1.4, whoosh, 0.5, 0.2);
  else if (ev.kind === 'tick') addAt(ev.t, 0.06, tick, 0.35, -0.1);
  else if (ev.kind === 'stamp') addAt(ev.t, 0.7, stampGen, 0.8, 0);
  else if (ev.kind === 'chime') addAt(ev.t, 2.5, chime, 0.25, 0);
}
let sfxPeak = 0;
for (let i = 0; i < SFX.length; i++) sfxPeak = Math.max(sfxPeak, Math.abs(SFX[i]));
const sfxGain = sfxPeak > 0 ? 0.5 / sfxPeak : 1;

// WAV writer: 16-bit PCM stereo.
const writeWav = (path, samples /* interleaved Float32 */) => {
  const dataLen = samples.length * 2;
  const buf = Buffer.alloc(44 + dataLen);
  buf.write('RIFF', 0);
  buf.writeUInt32LE(36 + dataLen, 4);
  buf.write('WAVE', 8);
  buf.write('fmt ', 12);
  buf.writeUInt32LE(16, 16);
  buf.writeUInt16LE(1, 20);
  buf.writeUInt16LE(2, 22);
  buf.writeUInt32LE(SR, 24);
  buf.writeUInt32LE(SR * 4, 28);
  buf.writeUInt16LE(4, 32);
  buf.writeUInt16LE(16, 34);
  buf.write('data', 36);
  buf.writeUInt32LE(dataLen, 40);
  for (let i = 0; i < samples.length; i++) {
    const v = Math.max(-1, Math.min(1, samples[i]));
    buf.writeInt16LE(Math.round(v * 32767), 44 + i * 2);
  }
  writeFileSync(path, buf);
};

const padI = new Float32Array(N * 2);
for (let i = 0; i < N; i++) {
  padI[i * 2] = L[i];
  padI[i * 2 + 1] = R[i];
}
const sfxI = new Float32Array(SFX.length);
for (let i = 0; i < SFX.length; i++) sfxI[i] = SFX[i] * sfxGain;

mkdirSync('out/audio', {recursive: true});
writeWav('out/audio/pad.wav', padI);
writeWav('out/audio/sfx.wav', sfxI);
console.log(`pad peak=${PAD_PEAK} (gain ${padGain.toFixed(4)}); sfx events=${sfxEvents.length}; sfx peak=0.5`);
