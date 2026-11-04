"""Rebuild card-05 paper assets for THIS script.
 - wad: generated photo of blank crumpled paper, keyed from black -> public/paper/wad.png
 - sheets: card-05 crumpled paper texture (crump-paper-2d.png). Its baked sample text is removed by
   mirror-patching clean paper rows, then NEW text is baked with Montserrat; the strip gets a synthetic
   yellow highlighter band. Sample text from card 05 is NOT reused."""
import os, sys, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import ndimage as ndi
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1] if len(sys.argv) > 1 else '/home/user/google_drive/crump-paper-2d.png'
FONT = os.path.join(ROOT, 'node_modules/@fontsource/montserrat/files/montserrat-latin-%d-normal.woff')
OUT = os.path.join(ROOT, 'public/paper'); os.makedirs(OUT, exist_ok=True)

# ---- wad
im = Image.open(os.path.join(OUT, 'wad_raw.jpg')).convert('RGB')
a = np.asarray(im).astype(np.float32)
m = a.max(axis=2)
alpha = np.clip((m-14)/26, 0, 1)
mask = alpha > 0.5
lab, n = ndi.label(mask)
if n > 1:
    sizes = ndi.sum(mask, lab, range(1, n+1)); keep = lab == (1+int(np.argmax(sizes)))
    keep = ndi.binary_dilation(keep, iterations=3)
    alpha = alpha*keep
alpha = ndi.binary_fill_holes(alpha > 0.5).astype(np.float32)*0 + alpha  # keep soft edge
ys, xs = np.where(alpha > 0.3)
x0, x1, y0, y1 = xs.min()-6, xs.max()+6, ys.min()-6, ys.max()+6
rgba = np.dstack([a, alpha*255]).astype(np.uint8)[y0:y1, x0:x1]
w = Image.fromarray(rgba, 'RGBA'); w.thumbnail((760, 760), Image.LANCZOS)
w.save(os.path.join(OUT, 'wad.png'), optimize=True); print('wad', w.size)

# ---- clean paper
p = Image.open(SRC).convert('RGBA'); P = np.asarray(p).copy()
Hh, Ww = P.shape[:2]
orig = P.copy()
def reflect(y0, y1, pivot):
    for y in range(y0, y1):
        sy = y - pivot
        P[y, :, :3] = orig[sy, :, :3]
reflect(196, 296, 96); reflect(296, 384, -104)   # straight copies of clean rows 100-200 and 400-488
# low-frequency (lighting) correction: patched rows get the lighting interpolated between the clean rows above/below
Y0, Y1 = 196, 384
alf = (orig[..., 3] > 128).astype(np.float32)
def nblur(rgb, w, sig):
    num = ndi.gaussian_filter(rgb*w[..., None], (sig[0], sig[1], 0)); den = ndi.gaussian_filter(w, sig)[..., None]+1e-4
    return num/den
blk = P[Y0:Y1, :, :3].astype(np.float32)
lp_patch = nblur(blk, alf[Y0:Y1], (22, 30))
top = nblur(orig[170:200, :, :3].astype(np.float32), alf[170:200], (14, 30)).mean(axis=0)
bot = nblur(orig[384:420, :, :3].astype(np.float32), alf[384:420], (14, 30)).mean(axis=0)
for y in range(Y0, Y1):
    t = (y-Y0)/(Y1-Y0)
    tgt = (1-t)*top + t*bot
    P[y, :, :3] = np.clip(blk[y-Y0] - lp_patch[y-Y0] + tgt, 0, 255)
# torn edge handling: only trust patched pixels well inside the sheet; fill the 5..14px band from nearest interior
al = P[..., 3] > 128
dist = ndi.distance_transform_edt(al)
rows = np.zeros_like(al); rows[190:392, :] = True
trust = al & (dist > 34)
need = rows & al & (dist > 5) & (~trust)
if need.any():
    idx = ndi.distance_transform_edt(~(trust & rows), return_distances=False, return_indices=True)
    yy, xx = np.where(need)
    P[yy, xx, :3] = P[idx[0][yy, xx], idx[1][yy, xx], :3]
clean = Image.fromarray(P, 'RGBA')
clean.save(os.path.join(OUT, 'paper_clean.png'))

def paper_arr(img): return np.asarray(img).astype(np.float32)

def bake(img, lines, size, weight=800, color=(34, 34, 36), x=44, y=205, lh=1.18, band=None):
    base = paper_arr(img)
    rgb = base[..., :3]/255.0
    if band is not None:
        by0, by1, rng = band
        h, w_ = rgb.shape[:2]
        yy = np.arange(h)[:, None]; xx = np.arange(w_)[None, :]
        wob = 6*np.sin(xx/95.0+rng)+4*np.sin(xx/37.0+2*rng)
        top = by0+wob; bot = by1+wob*0.6
        edge = np.clip((yy-top)/5, 0, 1)*np.clip((bot-yy)/5, 0, 1)
        left = np.ones_like(xx, dtype=np.float32)
        bristle = 0.85+0.15*np.sin(yy*1.7+xx/60.0)
        k = (edge*left*bristle)[..., None]
        yel = np.array([236, 190, 36])/255.0
        lum = rgb.mean(axis=2, keepdims=True)
        tint = lum*yel*1.08
        rgb = rgb*(1-k)+tint*k
    # text layer
    lay = Image.new('L', (rgb.shape[1], rgb.shape[0]), 0)
    d = ImageDraw.Draw(lay)
    f = ImageFont.truetype(FONT % weight, size)
    yy_ = y
    for ln in lines:
        d.text((x, yy_), ln, font=f, fill=255); yy_ += int(size*lh)
    lay = np.asarray(lay.filter(ImageFilter.GaussianBlur(0.6))).astype(np.float32)/255.0
    # multiply ink with paper luminance so wrinkles show through
    lum = np.asarray(img.convert('L')).astype(np.float32)/255.0
    ink = np.array(color)/255.0
    inkc = ink[None, None, :]*(0.55+0.45*lum[..., None])
    rgb = rgb*(1-lay[..., None]*0.96)+inkc*(lay[..., None]*0.96)
    out = np.dstack([np.clip(rgb, 0, 1)*255, base[..., 3]]).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')

# main sheet 1187x567 : the council's task (matches VO08 "ran the numbers on all 1,729 municipalities")
main = bake(clean, ['Independent council ran the', 'numbers on all 1,729 municipalities'], 54, 800, x=60, y=214)
main.save(os.path.join(OUT, 'sheet_main.png'), optimize=True)
# strip: flipped texture so the crinkle pattern differs, yellow highlighter, new text
strip_src = clean.transpose(Image.FLIP_LEFT_RIGHT).resize((1446, 605), Image.LANCZOS)
strip = bake(strip_src, ['POPULATION STRATEGY COUNCIL'], 56, 900, color=(26, 22, 14), x=84, y=222, band=(196, 318, 1.7))
strip = bake(strip, ['SUSTAINABILITY REPORT · APRIL 2024'], 38, 600, color=(40, 40, 42), x=88, y=362)
strip.save(os.path.join(OUT, 'sheet_strip.png'), optimize=True)
print('ok', main.size, strip.size)
