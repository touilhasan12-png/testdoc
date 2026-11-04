"""Build simplified boundary data from geoBoundaries gbOpen JPN (OpenStreetMap-derived, 2017).
ADM1 ODbL, ADM2 CC BY-SA 2.0. Input files are the pinned raw GitHub release files (commit 9469f09)."""
import json, os, random, sys
from shapely.geometry import shape, Point, mapping
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1] if len(sys.argv) > 1 else '/home/user/scratch'
OUT = os.path.join(ROOT, 'src/data')

def rings_of(geom, min_area):
    polys = list(geom.geoms) if geom.geom_type == 'MultiPolygon' else [geom]
    res = []
    for p in polys:
        if p.area < min_area: continue
        res.append([[round(x, 4), round(y, 4)] for x, y in p.exterior.coords])
    return res

pref = []
adm1 = json.load(open(f'{SRC}/adm1s.geojson'))
for ft in adm1['features']:
    g = shape(ft['geometry']).simplify(0.004, preserve_topology=True)
    name = ft['properties']['shapeName'].replace(' Prefecture', '').replace(' Metropolis', '').replace(' Fu', '').strip()
    c = g.representative_point()
    pref.append({'name': name, 'iso': ft['properties']['shapeISO'], 'rings': rings_of(g, 0.0006), 'c': [round(c.x, 3), round(c.y, 3)]})
json.dump(pref, open(f'{OUT}/prefectures.json', 'w'), separators=(',', ':'))
print('prefectures', len(pref), [p['name'] for p in pref][:5])

WARDS = ['Chiyoda','Chuo','Minato','Shinjuku','Bunkyo','Taito','Sumida','Koto','Shinagawa','Meguro','Ota','Setagaya','Shibuya','Nakano','Suginami','Toshima','Kita','Arakawa','Itabashi','Nerima','Adachi','Katsushika','Edogawa']
adm2 = json.load(open(f'{SRC}/adm2.geojson'))
wards = {}
for ft in adm2['features']:
    n = (ft['properties'].get('shapeName') or '').strip()
    if n not in WARDS: continue
    g = shape(ft['geometry'])
    c = g.centroid
    if not (139.55 <= c.x <= 139.93 and 35.50 <= c.y <= 35.83): continue
    gs = g.simplify(0.0003, preserve_topology=True)
    wards[n] = {'name': n, 'rings': rings_of(gs, 0.00002), 'c': [round(c.x, 4), round(c.y, 4)]}
missing = [w for w in WARDS if w not in wards]
assert not missing, missing
json.dump([wards[w] for w in WARDS], open(f'{OUT}/wards.json', 'w'), separators=(',', ':'))
print('wards', len(wards))

# Seeded illustrative "rural dots": points inside non-Kanto prefectures. NOT real locations of homes.
rnd = random.Random(20261104)
polys = []
for ft in adm1['features']:
    nm = ft['properties']['shapeName']
    if any(k in nm for k in ('Tokyo', 'Kanagawa', 'Saitama', 'Chiba', 'Osaka')): continue
    polys.append((nm, shape(ft['geometry'])))
pts = []
tries = 0
while len(pts) < 260 and tries < 200000:
    tries += 1
    nm, g = rnd.choice(polys)
    minx, miny, maxx, maxy = g.bounds
    x, y = rnd.uniform(minx, maxx), rnd.uniform(miny, maxy)
    if g.contains(Point(x, y)): pts.append([round(x, 3), round(y, 3)])
json.dump(pts, open(f'{OUT}/rural-points.json', 'w'), separators=(',', ':'))
print('rural pts', len(pts))
