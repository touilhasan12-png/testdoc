"""Camera interpolation + visible-tile planning. MUST mirror src/lib/camera.ts and src/lib/tiles.ts."""
import json, math, os

W, H, D = 1920, 1080, 2000.0
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_timeline():
    return json.load(open(os.path.join(ROOT, 'src/data/timeline.json')))

def pchip(ts, ys, t):
    n = len(ts)
    if t <= ts[0]: return ys[0]
    if t >= ts[-1]: return ys[-1]
    h = [ts[i+1]-ts[i] for i in range(n-1)]
    d = [(ys[i+1]-ys[i])/h[i] for i in range(n-1)]
    m = [0.0]*n
    for i in range(1, n-1):
        if d[i-1]*d[i] <= 0: m[i] = 0.0
        else:
            w1 = 2*h[i]+h[i-1]; w2 = h[i]+2*h[i-1]
            m[i] = (w1+w2)/(w1/d[i-1]+w2/d[i])
    i = 0
    while i < n-2 and t > ts[i+1]: i += 1
    x = (t-ts[i])/h[i]
    h00 = 2*x**3-3*x**2+1; h10 = x**3-2*x**2+x; h01 = -2*x**3+3*x**2; h11 = x**3-x**2
    return h00*ys[i]+h10*h[i]*m[i]+h01*ys[i+1]+h11*h[i]*m[i+1]

def cam_at(shot, f):
    ks = shot['keys']
    ts = [k[0] for k in ks]
    return [pchip(ts, [k[j] for k in ks], f) for j in range(1, 6)]  # lon,lat,z,pitch,bearing

def world_px(lon, lat, z):
    s = 256 * 2**z
    x = (lon+180)/360*s
    y = (1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*s
    return x, y

def plane_half_extents(pitch, bearing):
    a = math.radians(pitch); b = math.radians(bearing)
    ext_y_top = (H/2)*D/(D*math.cos(a)-(H/2)*math.sin(a))
    ext_y_bot = (H/2)*D/(D*math.cos(a)+(H/2)*math.sin(a))
    s_far = D/(D+ext_y_top*math.sin(a))
    ext_x = (W/2)/s_far
    ey = max(ext_y_top, ext_y_bot)
    hx = abs(math.cos(b))*ext_x+abs(math.sin(b))*ey
    hy = abs(math.sin(b))*ext_x+abs(math.cos(b))*ey
    return hx+48, hy+48

def level_for(z):
    return max(2, min(18, math.floor(z+0.2)))

def tiles_for(cam):
    lon, lat, z, pitch, bearing = cam
    hx, hy = plane_half_extents(pitch, bearing)
    L = level_for(z)
    out = set()
    levels = [L]
    if L-3 >= 2: levels.append(L-3)
    for l in levels:
        s = 2**(z-l)
        cx, cy = world_px(lon, lat, l)
        n = 2**l
        x0 = math.floor((cx-hx/s)/256); x1 = math.floor((cx+hx/s)/256)
        y0 = math.floor((cy-hy/s)/256); y1 = math.floor((cy+hy/s)/256)
        for x in range(max(0, x0), min(n-1, x1)+1):
            for y in range(max(0, y0), min(n-1, y1)+1):
                out.add((l, x, y))
    return out

def plan_tiles(step=2):
    tl = load_timeline()
    need = set()
    for sh in tl['shots']:
        for f in list(range(sh['f0'], sh['f1']+1, step))+[sh['f1']]:
            need |= tiles_for(cam_at(sh, f))
    return need

if __name__ == '__main__':
    need = plan_tiles()
    from collections import Counter
    c = Counter(l for l, _, _ in need)
    print(len(need), sorted(c.items()))
