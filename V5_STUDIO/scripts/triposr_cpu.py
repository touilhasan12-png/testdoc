"""Run official TripoSR inference on CPU; use scikit-image for CPU marching cubes."""
import json, os, sys, types, time
from pathlib import Path
import numpy as np
import torch
from PIL import Image
from skimage.measure import marching_cubes as sk_marching_cubes

out=Path(os.environ['V5_OUT']);src=Path(os.environ['V5_ROOT'])/'public/private';repo=Path(os.environ['TRIPOSR_DIR']);sys.path.insert(0,str(repo))
def marching(volume,level):
 a,b,_,_=sk_marching_cubes(volume.detach().cpu().numpy(),level=level)
 # TripoSR's original helper swaps the z/x columns supplied by torchmcubes.
 return torch.from_numpy(a[:,[2,1,0]].copy()),torch.from_numpy(b.astype('int64').copy())
shim=types.ModuleType('torchmcubes');shim.marching_cubes=marching;sys.modules['torchmcubes']=shim
from tsr.system import TSR

torch.set_num_threads(4)
model_dir=Path(os.environ['TRIPOSR_MODEL'])
start=time.time();print('Loading official TripoSR checkpoint on CPU.',flush=True)
original_load=torch.load
def load_compatible(*args,**kwargs):
 kwargs.setdefault('weights_only',False)
 return original_load(*args,**kwargs)
torch.load=load_compatible
model=TSR.from_pretrained(str(model_dir),config_name='config.yaml',weight_name='model.ckpt').to('cpu').eval()
model.renderer.set_chunk_size(2048)
# Use the rembg alpha, not a rectangular photo against a second grey panel:
# otherwise TripoSR reconstructs the boundary as a giant flat slab.
cutout=src/'ship_cutout.png'
if not cutout.exists():raise RuntimeError('rembg ship_cutout.png is required')
im=Image.open(cutout).convert('RGBA');bbox=im.getchannel('A').point(lambda a:255 if a>30 else 0).getbbox()
if not bbox:raise RuntimeError('Empty ship cutout')
im=im.crop(bbox);im.thumbnail((435,435),Image.Resampling.LANCZOS)
canvas=Image.new('RGB',(512,512),(127,127,127));canvas.paste(im,((512-im.width)//2,(512-im.height)//2),im.getchannel('A'))
print('Inferring scene code.',flush=True)
with torch.no_grad():
 codes=model([canvas],device='cpu')
 print('Extracting a 96-cubed colored mesh.',flush=True)
 mesh=model.extract_mesh(codes,True,resolution=96)[0]
if len(mesh.vertices)<30 or len(mesh.faces)<30:raise RuntimeError('Generated mesh too small')
path=out/'ship_triposr.glb';mesh.export(path)
(out/'triposr_status.json').write_text(json.dumps({'ok':True,'device':'CPU','marching_cubes':'scikit-image CPU shim','resolution':96,'vertices':len(mesh.vertices),'faces':len(mesh.faces),'seconds':round(time.time()-start,1)},indent=2))
print('PASS TripoSR: generated colored 3D mesh; vertices:',len(mesh.vertices),'faces:',len(mesh.faces),flush=True)
