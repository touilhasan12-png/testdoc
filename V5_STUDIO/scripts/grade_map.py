"""A mild antique-ocean grade of NASA's equirectangular Blue Marble."""
import numpy as np
from PIL import Image
from pathlib import Path
import sys
src=Path(sys.argv[1]);mask=Path(sys.argv[2]);dst=Path(sys.argv[3])
a=np.asarray(Image.open(src).convert('RGB'),dtype=np.float32)
m=np.asarray(Image.open(mask).convert('L'),dtype=np.float32)[...,None]/255
land=np.clip(a*.72+np.array([76,61,39],dtype=np.float32),0,255)
sea=np.clip(a*.35+np.array([16,43,52],dtype=np.float32),0,255)
out=np.clip(land*m+sea*(1-m),0,255).astype(np.uint8)
Image.fromarray(out).save(dst,'JPEG',quality=91,subsampling=0,optimize=True)
