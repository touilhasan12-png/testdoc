"""Post-render gate. Usage: verify_video.py out/Tokyo-sample-300s.mp4"""
import json, os, subprocess, sys
import numpy as np
from scipy.signal import fftconvolve
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(__file__))
from camlib import load_timeline
FF = os.environ.get('FFMPEG', 'ffmpeg'); FP = os.environ.get('FFPROBE', 'ffprobe')
path = sys.argv[1]
tl = load_timeline(); FPS = 30
rep = {'file': os.path.basename(path), 'size_bytes': os.path.getsize(path)}
def run(*a, **k): return subprocess.run(a, capture_output=True, text=True, **k)

# ---- container facts
pr = json.loads(run(FP, '-v', 'error', '-show_streams', '-show_format', '-of', 'json', path).stdout)
v = next(s for s in pr['streams'] if s['codec_type'] == 'video'); a = next(s for s in pr['streams'] if s['codec_type'] == 'audio')
rep['video'] = {'codec': v['codec_name'], 'w': v['width'], 'h': v['height'], 'fps': v['r_frame_rate'], 'pix_fmt': v['pix_fmt'], 'duration': float(v.get('duration', 0))}
rep['audio'] = {'codec': a['codec_name'], 'sr': a['sample_rate'], 'ch': a['channels'], 'duration': float(a.get('duration', 0))}
rep['format_duration'] = float(pr['format']['duration'])
cf = json.loads(run(FP, '-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries', 'stream=nb_read_frames', '-of', 'json', path).stdout)
rep['frames_read'] = int(cf['streams'][0]['nb_read_frames'])
# ---- full decode: errors + tail
dec = run(FF, '-v', 'error', '-i', path, '-f', 'null', '-')
rep['decode_errors'] = dec.stderr.strip()[:500]
# ---- silence (any dead air in final audio?)
sd = run(FF, '-hide_banner', '-nostats', '-i', path, '-af', 'silencedetect=n=-55dB:d=0.3', '-vn', '-f', 'null', '-')
rep['silence_events_-55dB_0.3s'] = [l.strip() for l in sd.stderr.splitlines() if 'silence_' in l]

# ---- audio decode & VO placement (cross-correlation with the source VO files)
SR = 44100
raw = subprocess.run([FF, '-v', 'error', '-i', path, '-vn', '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout
au = np.frombuffer(raw, dtype=np.float32).astype(np.float64)
rep['audio_samples_decoded'] = len(au); rep['audio_seconds_decoded'] = len(au) / SR
VO = [('01-coldopen', 24), ('02-act1-arrows', 1047), ('03-act1-fertility', 1800), ('04-act1-paradox', 2556), ('05-space-dive', 3208), ('06-space-akiya', 4040), ('07-time', 4881), ('08-machine', 6151), ('09-blackhole', 7710)]
vo_rep = []
for name, fr in VO:
    src = np.frombuffer(subprocess.run([FF, '-v', 'error', '-i', os.path.join(ROOT, 'assets/vo', name + '.mp3'), '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout, dtype=np.float32).astype(np.float64)
    s0 = fr * SR // FPS
    pad = 3000
    seg = au[max(0, s0 - pad): s0 + len(src) + pad]
    c = fftconvolve(seg, src[::-1], mode='valid')
    lag = int(np.argmax(c)) - (s0 - max(0, s0 - pad))
    # correlation at best lag
    b0 = s0 + lag
    x = au[b0: b0 + len(src)]
    n = min(len(x), len(src))
    corr = float(np.corrcoef(x[:n], src[:n])[0, 1])
    vo_rep.append({'vo': name, 'start_frame': fr, 'start_s': fr / FPS, 'dur_s': round(len(src) / SR, 3), 'end_s': round((s0 + len(src)) / SR, 3), 'best_lag_ms': round(lag * 1000 / SR, 2), 'corr': round(corr, 4)})
rep['vo_placement'] = vo_rep
rep['vo_last_end_s'] = vo_rep[-1]['end_s']
rep['reading_hold_s'] = round(300 - vo_rep[-1]['end_s'], 2)
# loudness consistency
rms = lambda x: float(np.sqrt(np.mean(x ** 2)) + 1e-12)
rep['vo_window_rms_db'] = [round(20 * np.log10(rms(au[int(r['start_s'] * SR): int(r['end_s'] * SR)])), 1) for r in vo_rep]
rep['music_only_rms_db_hold'] = round(20 * np.log10(rms(au[int(297 * SR): int(299.5 * SR)])), 1)
rep['peak'] = round(float(np.abs(au).max()), 4)

# ---- rhythm from timeline (what the renderer reads)
skip = {'sf_gone', 'lifeboat_x', 'wards_lit', 'stamp2'}
ev = sorted([x['f0'] for k, x in tl['items'].items() if k not in skip] + [k[0] for k in tl['kickers']] + tl['beats'] + [8121 + 9 * i for i in range(16)])
gaps = [b - a_ for a_, b in zip(ev, ev[1:])]
rep['rhythm'] = {'events': len(ev), 'first_event_frame': ev[0], 'max_gap_frames': max(gaps), 'gaps_over_60': [(a_, b) for a_, b in zip(ev, ev[1:]) if b - a_ > 60],
                 'median_gap_frames': float(np.median(gaps)), 'shots': len(tl['shots']), 'shot_len_frames_min_med_max': [min(s['f1'] - s['f0'] for s in tl['shots']), float(np.median([s['f1'] - s['f0'] for s in tl['shots']])), max(s['f1'] - s['f0'] for s in tl['shots'])],
                 'reading_hold_no_new_event_frames': 9000 - ev[-1]}

# ---- video motion: per-shot first vs last frame + dead-run detection
W_, H_ = 192, 108
raw = subprocess.run([FF, '-v', 'error', '-i', path, '-vf', f'fps=10,scale={W_}:{H_},format=gray', '-f', 'rawvideo', '-'], capture_output=True).stdout
fr10 = np.frombuffer(raw, dtype=np.uint8).reshape(-1, H_, W_).astype(np.float32)
rep['sampled_frames_10fps'] = int(len(fr10))
diff = np.abs(np.diff(fr10, axis=0)).mean(axis=(1, 2))
dead = 0; longest = 0
for d in diff:
    dead = dead + 1 if d < 0.08 else 0; longest = max(longest, dead)
rep['longest_near_static_run_s'] = longest / 10
shots = []
for s in tl['shots']:
    if s['f1'] - s['f0'] < 40: continue
    i0 = int((s['f0'] + 4) / 3); i1 = min(len(fr10) - 1, int((s['f1'] - 5) / 3))
    shots.append({'shot': s['id'], 'mean_abs_diff_first_vs_last': round(float(np.abs(fr10[i0] - fr10[i1]).mean()), 2)})
rep['camera_frame_change'] = shots
rep['camera_frame_change_min'] = min(x['mean_abs_diff_first_vs_last'] for x in shots)
# ---- QA frames: start / middle / end of every shot
qa = os.path.join(ROOT, 'out', 'qa-frames'); os.makedirs(qa, exist_ok=True)
for s in tl['shots']:
    for tag, f in (('a', s['f0'] + 2), ('b', (s['f0'] + s['f1']) // 2), ('c', s['f1'] - 3)):
        f = min(f, 8999)
        subprocess.run([FF, '-v', 'error', '-y', '-ss', f'{f / FPS:.4f}', '-i', path, '-frames:v', '1', '-vf', 'scale=640:-1', '-q:v', '5', os.path.join(qa, f"{s['id']}_{tag}_f{f}.jpg")])
# ---- verdict
fails = []
if abs(rep['format_duration'] - 300) > 0.05: fails.append('duration')
if rep['frames_read'] != 9000: fails.append('frames')
if (rep['video']['w'], rep['video']['h']) != (1920, 1080): fails.append('resolution')
if rep['decode_errors']: fails.append('decode errors')
if abs(rep['audio_seconds_decoded'] - 300) > 0.1: fails.append('audio duration')
if any(abs(r['best_lag_ms']) > 25 or r['corr'] < 0.9 for r in vo_rep): fails.append('VO placement')
if rep['rhythm']['gaps_over_60']: fails.append('rhythm gaps')
if rep['camera_frame_change_min'] < 4: fails.append('camera frame change too small')
rep['verdict'] = 'PASS' if not fails else 'FAIL: ' + ', '.join(fails)
json.dump(rep, open(os.path.join(ROOT, 'out', 'verify-report.json'), 'w'), indent=1)
print(json.dumps(rep, indent=1))
sys.exit(0 if not fails else 1)
