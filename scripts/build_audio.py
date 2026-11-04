"""Deterministic audio mix: VO 01-09 (untouched, placed on exact frames) + Dm-Bb-C-Am pad (peak 0.066) + event SFX
synthesised from src/data/timeline.json. No randomness without a fixed seed."""
import json, os, subprocess, sys, wave
import numpy as np
from scipy.signal import butter, sosfilt, lfilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 44100
FPS = 30
TOTAL = 9000
N = TOTAL * SR // FPS  # exactly 300 s
FF = os.environ.get('FFMPEG', 'ffmpeg')
OUT = os.path.join(ROOT, 'out', 'audio'); os.makedirs(OUT, exist_ok=True)
tl = json.load(open(os.path.join(ROOT, 'src/data/timeline.json')))

VO = [('01-coldopen', 24), ('02-act1-arrows', 1047), ('03-act1-fertility', 1800), ('04-act1-paradox', 2556), ('05-space-dive', 3208),
      ('06-space-akiya', 4040), ('07-time', 4881), ('08-machine', 6151), ('09-blackhole', 7710)]

def decode(path):
    raw = subprocess.run([FF, '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)

# ---------------------------------------------------------------- VO
vo = np.zeros(N)
vo_info = []
for name, fr in VO:
    x = decode(os.path.join(ROOT, 'assets/vo', name + '.mp3'))
    s = fr * SR // FPS
    assert s + len(x) <= N, name
    vo[s:s+len(x)] += x
    vo_info.append({'name': name, 'start_frame': fr, 'start_s': fr/FPS, 'samples': len(x), 'dur_s': len(x)/SR, 'end_s': (s+len(x))/SR, 'peak': float(np.abs(x).max())})

# ---------------------------------------------------------------- pad (Dm - Bb - C - Am)
def midi(m): return 440.0 * 2 ** ((m - 69) / 12)
CHORDS = [[38, 45, 50, 53, 57, 62], [34, 41, 46, 50, 53, 58], [36, 43, 48, 52, 55, 60], [33, 40, 45, 48, 52, 57]]
BELL = [81, 77, 79, 76]  # A5, F5, G5, E5  (5th/3rd colour tones)
CH = 8.0; XF = 3.0
t_all = np.arange(N) / SR
pad = np.zeros(N)
nchords = int(np.ceil(300 / CH)) + 1
for k in range(nchords):
    t0 = k * CH - XF / 2
    t1 = t0 + CH + XF
    i0 = max(0, int(t0 * SR)); i1 = min(N, int(t1 * SR))
    if i1 <= i0: continue
    t = t_all[i0:i1]
    env = np.ones_like(t)
    a = np.clip((t - t0) / XF, 0, 1); b = np.clip((t1 - t) / XF, 0, 1)
    env = (0.5 - 0.5 * np.cos(np.pi * a)) * (0.5 - 0.5 * np.cos(np.pi * b))
    ch = CHORDS[k % 4]
    sig = np.zeros_like(t)
    for j, m in enumerate(ch):
        f = midi(m)
        w = 1.0 / (1 + 0.35 * j)
        for det in (-0.0018, 0.0, 0.0018):
            ph = 2 * np.pi * f * (1 + det) * t + j * 1.3 + det * 900
            sig += w * (np.sin(ph) + 0.32 * np.sin(2 * ph + 0.4) + 0.12 * np.sin(3 * ph + 1.1)) / 3
    pad[i0:i1] += sig * env
    # bell at chord start (very soft)
    tb = t_all[int(max(0, k*CH*SR)):min(N, int((k*CH+6)*SR))]
    if len(tb):
        tt = tb - k * CH
        fb = midi(BELL[k % 4])
        bell = np.sin(2*np.pi*fb*tt) * np.minimum(tt/0.6, 1) * np.exp(-tt/1.8) * 0.07
        bell += np.sin(2*np.pi*fb*2.001*tt) * np.exp(-tt/0.9) * 0.015
        pad[int(max(0, k*CH*SR)):int(max(0, k*CH*SR))+len(bell)] += bell
sos = butter(2, 1700, 'low', fs=SR, output='sos')
pad = sosfilt(sos, pad)
# gentle delay for air
d = int(0.43 * SR)
pad2 = pad.copy(); pad2[d:] += 0.28 * pad[:-d]
pad = pad2
fade = np.minimum(t_all / 2.0, 1) * np.minimum((300 - t_all) / 4.0, 1)
pad *= fade
PAD_PEAK = 0.066
MASTER = 0.84   # one uniform gain for the whole mix (VO 05 decodes to 1.12 full-scale; uniform gain keeps VO untouched and un-clipped)
pad *= (PAD_PEAK / MASTER) / np.abs(pad).max()   # => pad peak in the FINAL mix is exactly 0.066

# ---------------------------------------------------------------- SFX
def noise(n, seed): return np.random.RandomState(seed).randn(n)
def bp(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], 'band', fs=SR, output='sos'), x)
def exp_env(n, tau): return np.exp(-np.arange(n) / (tau * SR))
def sweep_noise(dur, f_start, f_end, seed, att=0.1):
    """band-crossfaded noise sweep: smooth, click-free"""
    n = int(dur * SR); x = noise(n, seed); u = np.arange(n) / n
    out = np.zeros(n); K = 7
    for k in range(K):
        c = f_start * (f_end / f_start) ** (k / (K - 1))
        band = bp(x, max(60, c * 0.65), min(SR/2 - 100, c * 1.55))
        pos = k / (K - 1)
        out += band * np.exp(-((u - pos) ** 2) / (2 * (0.55 / K) ** 2))
    t = u
    env = np.minimum(t / att, 1) * np.minimum((1 - t) / 0.35, 1)
    return out * env / np.sqrt(K / 3)
def tone(f, dur, tau, att=0.004, harm=(1, 0.3)):
    n = int(dur * SR); t = np.arange(n) / SR
    x = sum(h * np.sin(2*np.pi*f*(i+1)*t) for i, h in enumerate(harm))
    return x * np.minimum(t / att, 1) * np.exp(-t / tau)
def add(*arrs):
    n = max(len(a) for a in arrs); o = np.zeros(n)
    for a in arrs: o[:len(a)] += a
    return o

def sfx(kind, seed, rise=1.0):
    if kind == 'pop':      return add(0.55 * tone(520 * rise, 0.22, 0.05), 0.25 * tone(1040 * rise, 0.15, 0.03))
    if kind == 'tick':     return 0.4 * tone(1800, 0.03, 0.006, 0.0005, (1,))
    if kind == 'ping':     return add(0.6 * tone(880 * rise, 0.7, 0.18, 0.003, (1, 0.2)), 0.2 * tone(1320 * rise, 0.5, 0.12))
    if kind == 'thud':     return 0.9 * tone(68, 0.5, 0.11, 0.003, (1, 0.4))
    if kind == 'stamp':
        x = 1.0 * tone(58, 0.6, 0.13, 0.002, (1, 0.5)); n = len(x)
        h = bp(noise(n, seed), 800, 5000) * exp_env(n, 0.03) * 0.5
        return x + h
    if kind == 'whoosh':   return 0.9 * sweep_noise(0.65, 500, 3200, seed, 0.3)
    if kind == 'whoosh_down': return 1.0 * sweep_noise(1.0, 4500, 350, seed, 0.1)
    if kind == 'flip':     return 0.8 * sweep_noise(0.35, 700, 5000, seed, 0.2)
    if kind == 'sweep':    return 0.6 * sweep_noise(1.5, 300, 2500, seed, 0.5)
    if kind == 'swell':
        n = int(1.6 * SR); t = np.arange(n)/SR
        return (0.5*np.sin(2*np.pi*(55+25*t/1.6)*t) + 0.25*sweep_noise(1.6, 200, 900, seed, 0.7)) * (t/1.6)**1.5 * np.minimum((1.6-t)/0.2, 1)
    if kind == 'riser':
        n = int(2.3 * SR); t = np.arange(n)/SR; u = t/2.3
        tn = np.sin(2*np.pi*(180 + 900*u**2)*t) * 0.25
        return (tn + 0.55*sweep_noise(2.3, 300, 5000, seed, 0.8)) * u**1.4 * np.minimum((2.3-t)/0.15, 1)
    if kind == 'glow':     return add(0.5*tone(660, 1.3, 0.35, 0.02), 0.35*tone(990, 1.2, 0.3, 0.02), 0.2*tone(1320, 1.0, 0.25, 0.02))
    if kind == 'chime':    return add(0.5*tone(523.25, 2.4, 0.7, 0.01, (1, 0.35)), 0.4*tone(783.99, 2.4, 0.8, 0.01, (1, 0.3)), 0.25*tone(1046.5, 2.0, 0.6, 0.01))
    if kind == 'dust':
        n = int(1.0*SR); x = noise(n, seed); x = sosfilt(butter(2, 2500, 'high', fs=SR, output='sos'), x)
        g = (np.random.RandomState(seed+1).rand(n) > 0.82).astype(float)
        return 0.7 * x * g * exp_env(n, 0.3)
    if kind == 'pull':     return add(0.45 * tone(330, 1.2, 1.0, 0.1, (1, 0.2)) * np.linspace(0.2, 1, int(1.2*SR)), 0.3*sweep_noise(1.2, 400, 1800, seed, 0.6))
    if kind == 'paper':
        n = int(0.28*SR); return 0.9 * bp(noise(n, seed), 1500, 7000) * exp_env(n, 0.05) * (1 + 0.6*np.sin(np.arange(n)/70.0))
    if kind == 'paper_open':
        n = int(0.8*SR); x = bp(noise(n, seed), 1200, 7500); g = (np.random.RandomState(seed+3).rand(n//200 + 1).repeat(200)[:n] > 0.35)
        env = np.minimum(np.arange(n)/(0.05*SR), 1) * np.minimum((n-np.arange(n))/(0.15*SR), 1)
        return 0.8 * x * g * env
    if kind == 'paper_close':
        n = int(0.8*SR); x = bp(noise(n, seed), 1200, 7500); g = (np.random.RandomState(seed+3).rand(n//200 + 1).repeat(200)[:n] > 0.35)
        env = np.minimum(np.arange(n)/(0.15*SR), 1) * np.minimum((n-np.arange(n))/(0.06*SR), 1)
        return 0.8 * x[::-1] * g * env
    raise KeyError(kind)

GAIN = {'pop': 0.20, 'tick': 0.10, 'ping': 0.17, 'thud': 0.22, 'stamp': 0.26, 'whoosh': 0.13, 'whoosh_down': 0.14, 'flip': 0.12, 'sweep': 0.09,
        'swell': 0.16, 'riser': 0.15, 'glow': 0.14, 'chime': 0.16, 'dust': 0.13, 'pull': 0.12, 'paper': 0.16, 'paper_open': 0.14, 'paper_close': 0.14}
events = []
for name, it in tl['items'].items():
    k = it['sfx']
    if name == 'wards_lit':
        for i in range(16):
            events.append((it['f0'] + 9 * i, 'ping', 1.0 + 0.04 * i, name))
        continue
    events.append((it['f0'], k, 1.0, name))
for fk, _t in tl.get('kickers', []): events.append((fk, 'tick', 1, 'kicker'))
for f in range(336, 402, 6): events.append((f, 'tick', 1, 'p46_count'))
for f in range(22, 96, 5): events.append((f, 'tick', 1, 'cnt918_roll'))
for s in tl['shots']:
    if s['f0'] > 0 and s['id'] in ('B_stamp_flash',): events.append((s['f0'], 'flip', 1, s['id']))
sfx_bus = np.zeros(N)
log = []
for i, (fr, kind, rise, why) in enumerate(sorted(events, key=lambda e: e[0])):
    x = sfx(kind, 1000 + i, rise) if kind in ('pop', 'ping') else sfx(kind, 1000 + i)
    peak = np.abs(x).max()
    x = x / peak * GAIN[kind] * (0.6 if why == 'kicker' else 1.0) if peak > 0 else x
    s = fr * SR // FPS
    e = min(N, s + len(x))
    sfx_bus[s:e] += x[:e-s]
    log.append({'frame': fr, 'sec': round(fr/FPS, 3), 'kind': kind, 'tied_to': why})

raw_mix = vo + pad + sfx_bus
mix = raw_mix * MASTER
peak = float(np.abs(mix).max())
assert peak < 0.985, peak
# verify VO untouched: (mix - pad - sfx) equals vo
resid = float(np.abs((raw_mix - pad - sfx_bus) - vo).max())
stereo = np.stack([mix, mix], axis=1)
pcm = (np.clip(stereo, -1, 1) * 32767).astype('<i2')
with wave.open(os.path.join(OUT, 'mix.wav'), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())

# ---- report
sec = lambda a, b: slice(int(a*SR), int(b*SR))
rms = lambda x: float(np.sqrt(np.mean(x**2)))
per_sec = [round(20*np.log10(max(rms(mix[i*SR:(i+1)*SR]), 1e-9)), 1) for i in range(300)]
rep = {
  'samples': int(N), 'duration_s': N / SR, 'sr': SR,
  'pad_peak_final': float(np.abs(pad*MASTER).max()), 'master_gain': MASTER, 'mix_peak': peak, 'sfx_peak_final': float(np.abs(sfx_bus*MASTER).max()),
  'vo_untouched_max_residual': resid,
  'vo': vo_info, 'sfx_events': len(log),
  'vo_gap_after_last_s': 300 - vo_info[-1]['end_s'],
  'inter_vo_gaps_s': [round(vo_info[i+1]['start_s'] - vo_info[i]['end_s'], 3) for i in range(8)],
  'rms_db_per_second_min': min(per_sec), 'rms_db_per_second_max': max(per_sec),
  'pad_rms_db_min_after_2s': round(20*np.log10(min(rms(pad[i*SR:(i+1)*SR]*MASTER) for i in range(2, 296))), 1),
  'pad_rms_db_median': round(float(np.median([20*np.log10(rms(pad[i*SR:(i+1)*SR]*MASTER)) for i in range(2, 296)])), 1),
  'vo_rms_db': [round(20*np.log10(rms(vo[int(v['start_s']*SR):int(v['end_s']*SR)])), 1) for v in vo_info],
}
json.dump(rep, open(os.path.join(OUT, 'audio-report.json'), 'w'), indent=1)
json.dump(log, open(os.path.join(OUT, 'sfx-log.json'), 'w'), indent=1)
print(json.dumps({k: v for k, v in rep.items() if k not in ('vo',)}, indent=1))
for v in vo_info: print(v['name'], round(v['start_s'], 3), '->', round(v['end_s'], 3))
