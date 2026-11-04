"""Download exactly the GSI seamlessphoto tiles the camera paths need, re-encode, write manifest.
Source: https://cyberjapandata.gsi.go.jp/xyz/seamlessphoto/{z}/{x}/{y}.jpg  (c) Geospatial Information Authority of Japan"""
import io, json, os, sys, time, requests
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from camlib import plan_tiles, ROOT

OUT = os.path.join(ROOT, 'public/tiles')
URL = 'https://cyberjapandata.gsi.go.jp/xyz/seamlessphoto/{z}/{x}/{y}.jpg'
need = sorted(plan_tiles())
print('planned', len(need))
sess = requests.Session()

def get(t):
    z, x, y = t
    path = os.path.join(OUT, str(z), str(x), f'{y}.jpg')
    if os.path.exists(path): return t, os.path.getsize(path)
    for attempt in range(4):
        try:
            r = sess.get(URL.format(z=z, x=x, y=y), timeout=30)
            if r.status_code == 404: return t, 0
            r.raise_for_status()
            im = Image.open(io.BytesIO(r.content)).convert('RGB')
            os.makedirs(os.path.dirname(path), exist_ok=True)
            im.save(path, 'JPEG', quality=55, optimize=True, progressive=True)
            return t, os.path.getsize(path)
        except Exception as e:
            time.sleep(1+attempt)
    return t, -1

t0 = time.time()
with ThreadPoolExecutor(12) as ex:
    res = list(ex.map(get, need))
ok = [t for t, s in res if s > 0]
miss = [t for t, s in res if s == 0]
bad = [t for t, s in res if s < 0]
total = sum(s for _, s in res if s > 0)
print('ok', len(ok), 'missing404', len(miss), 'failed', len(bad), 'MB', round(total/1e6, 1), 'sec', round(time.time()-t0))
man = {}
for z, x, y in ok: man.setdefault(str(z), []).append(f'{x}/{y}')
json.dump({'source': 'GSI Japan seamlessphoto', 'tiles': man}, open(os.path.join(ROOT, 'src/data/tile-manifest.json'), 'w'), separators=(',', ':'))
if bad: sys.exit('FAILED tiles: %d' % len(bad))
