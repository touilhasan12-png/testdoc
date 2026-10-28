"""Style NASA's Mercator composite with a Natural Earth land mask.
The boundary polygons are MODERN geographical references, not historical claims.
"""
import argparse,json,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np
here=Path(__file__).parent
ap=argparse.ArgumentParser(description='Grade NASA Mercator imagery with a modern Natural Earth land mask')
ap.add_argument('--imagery',type=Path,required=True,help='Mercator-projected NASA JPEG')
ap.add_argument('--geodata',type=Path,required=True,help='Natural Earth country GeoJSON')
args=ap.parse_args();raw=args.imagery;geo=args.geodata
im=Image.open(raw).convert('RGB').resize((4096,3176),Image.Resampling.LANCZOS);w,h=im.size
mask=Image.new('L',(w,h),0);draw=ImageDraw.Draw(mask)
def merc(lat):
 lat=max(-80,min(80,lat));return math.degrees(math.log(math.tan(math.pi/4+math.radians(lat)/2)))
def projected(ring):
 out=[];last=None
 for lon,lat,*_ in ring:
  if last is not None:
   while lon-last>180:lon-=360
   while lon-last<-180:lon+=360
  out.append((lon,lat));last=lon
 return out
def px(points,shift):return [((lon+shift+180)/360*w,(merc(80)-merc(lat))/360*w) for lon,lat in points]
for f in json.loads(geo.read_text())['features']:
 g=f.get('geometry') or {};c=g.get('coordinates',[]);polys=[c] if g.get('type')=='Polygon' else c if g.get('type')=='MultiPolygon' else []
 for poly in polys:
  if not poly:continue
  rings=[projected(r) for r in poly if len(r)>2]
  if not rings:continue
  outer=rings[0]
  # Repeat any unwrapped polygon across the map seam.
  for shift in (-720,-360,0,360,720):
   pts=px(outer,shift)
   if max(x for x,_ in pts)<0 or min(x for x,_ in pts)>w:continue
   draw.polygon(pts,fill=255)
   for hole in rings[1:]:
    # Hole coordinates are a local part of the same polygon.
    draw.polygon(px(hole,shift),fill=0)
mask=mask.filter(ImageFilter.GaussianBlur(1.1));m=np.asarray(mask,dtype=np.float32)/255.
a=np.asarray(im,dtype=np.float32)
out=np.empty_like(a,dtype=np.uint8)
for i,(land,water) in enumerate(zip((196,181,147),(62,98,116))):
 l=a[:,:,i]*.42+land*.58;s=a[:,:,i]*.60+water*.40
 out[:,:,i]=np.clip(l*m+s*(1-m),0,255).astype('uint8')
Image.fromarray(out,'RGB').save(here/'public/map/nasa_world_mercator.jpg',quality=90,optimize=True)
print('Wrote 4096x3176 graded NASA map using Natural Earth land mask')
