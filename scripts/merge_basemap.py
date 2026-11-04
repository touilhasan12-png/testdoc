"""GSI seamless photo has no data over much of the Pacific at low zoom (flat RGB 53,53,53 fill).
Fill ONLY those no-data pixels with NASA GIBS Blue Marble Next Generation (real satellite composite), so every
pixel of the ground is real imagery. Source: NASA EOSDIS GIBS WMTS (open NASA data, credit shown on screen)."""
import os, glob, io, sys
import numpy as np, requests
from PIL import Image
from scipy import ndimage
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GIBS = 'https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/BlueMarble_NextGeneration/default/GoogleMapsCompatible_Level8/{z}/{y}/{x}.jpeg'
cache = {}
def gibs(z, x, y):
    k = (z, x, y)
    if k not in cache:
        r = requests.get(GIBS.format(z=z, x=x, y=y), timeout=60); r.raise_for_status()
        cache[k] = Image.open(io.BytesIO(r.content)).convert('RGB')
    return cache[k]
def basemap_tile(z, x, y):
    if z <= 8: return gibs(z, x, y).resize((256, 256), Image.BICUBIC)
    s = 2 ** (z - 8); t = gibs(8, x // s, y // s)
    n = 256 // s if s <= 256 else 1
    px, py = (x % s) * 256 // s, (y % s) * 256 // s
    return t.crop((px, py, px + 256 // s, py + 256 // s)).resize((256, 256), Image.BICUBIC)
files = [f for f in sorted(glob.glob(os.path.join(ROOT, 'public/tiles/*/*/*.jpg'))) if int(f.split('/')[-3]) <= 12]  # no-data only exists at low zoom
def parse(f): return [int(p) for p in f[:-4].split('/')[-3:]]
def flat_mask(a):
    flat = (np.abs(a - 53).max(2) <= 7)
    blk = ndimage.binary_opening(a.max(2) <= 4, iterations=3)  # pure-black no-data (z9+ Pacific)
    flat = ndimage.binary_opening(flat, iterations=1) | (ndimage.binary_closing(flat, iterations=2) & flat) | blk
    return flat
# pass 1: colour gain so that the Blue Marble fill matches GSI ocean tone next to it
ratios = []
for f in files:
    z, x, y = parse(f)
    a = np.asarray(Image.open(f).convert('RGB')).astype(float)
    fl = flat_mask(a)
    if not (0.1 < fl.mean() < 0.9): continue
    valid = ~ndimage.binary_dilation(fl, iterations=6)
    b = np.asarray(basemap_tile(z, x, y)).astype(float)
    sel = valid & (a.mean(2) < 70) & (b.mean(2) < 70)
    if sel.sum() > 800: ratios.append(a[sel].mean(0) / np.maximum(b[sel].mean(0), 1))
gain = np.clip(np.median(np.array(ratios), axis=0), 1.0, 12.0) if ratios else np.ones(3)
print('colour gain', gain.round(2), 'from', len(ratios), 'tiles')
changed = 0; log = []
for f in files:
    z, x, y = parse(f)
    a = np.asarray(Image.open(f).convert('RGB')).astype(float)
    fl = flat_mask(a)
    if fl.mean() < 0.002: continue
    m = ndimage.binary_dilation(fl, iterations=8)
    m = ndimage.gaussian_filter(m.astype(float), 5)[..., None]
    rng = np.random.default_rng(z * 1000003 + x * 1009 + y)  # seeded: deterministic
    nz = ndimage.gaussian_filter(rng.normal(size=(256, 256)), 4); nz = nz / (nz.std() + 1e-9)
    b = np.asarray(basemap_tile(z, x, y)).astype(float) * gain * (1 + 0.28 * nz)[..., None]
    out = a * (1 - m) + b * m
    Image.fromarray(out.clip(0, 255).astype(np.uint8)).save(f, quality=62)
    changed += 1; log.append(f'{z}/{x}/{y}')
print('tiles filled with NASA GIBS:', changed)
open(os.path.join(ROOT, 'src/data/gibs-filled.txt'), 'w').write('\n'.join(log))
