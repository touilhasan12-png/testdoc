"""Process the private V5 pilot inputs on a CPU runner. Public logs contain no media."""
import json, os, subprocess, urllib.request, traceback
from pathlib import Path
import numpy as np
from PIL import Image

root=Path(os.environ['V5_ROOT']); src=root/'public/private'; out=Path(os.environ['V5_OUT']); out.mkdir(parents=True,exist_ok=True)
status={}
def task(name,func):
 try:
  detail=func();status[name]={'ok':True,'detail':detail};print('PASS',name,flush=True)
 except Exception as e:
  status[name]={'ok':False,'error':str(e)[:350]};print('FAILED',name,type(e).__name__,flush=True)

def rembg_task():
 import rembg
 session=rembg.new_session('u2netp')
 for input_name,output_name in [('carrack_clean.png','ship_cutout.png'),('magellan_reference.png','portrait_cutout.png')]:
  source=(src/input_name).read_bytes(); result=rembg.remove(source,session=session)
  (out/output_name).write_bytes(result)
  im=Image.open(out/output_name).convert('RGBA')
  if not im.getchannel('A').getbbox():raise RuntimeError('empty alpha')
 return 'u2netp removed background from ship and portrait'

def depth_task():
 import onnxruntime as ort
 url='https://huggingface.co/onnx-community/depth-anything-v2-small/resolve/main/onnx/model_quantized.onnx'
 model=out/'depth_model.onnx';urllib.request.urlretrieve(url,model)
 opts=ort.SessionOptions();opts.intra_op_num_threads=4
 sess=ort.InferenceSession(str(model),sess_options=opts,providers=['CPUExecutionProvider'])
 im=Image.open(src/'magellan_reference.png').convert('RGB'); small=im.resize((518,518),Image.Resampling.BICUBIC)
 x=np.asarray(small,dtype=np.float32)/255.;x=(x-np.array([.485,.456,.406],np.float32))/np.array([.229,.224,.225],np.float32)
 x=np.transpose(x,(2,0,1))[None,...]; raw=sess.run(None,{sess.get_inputs()[0].name:x})[0][0]
 raw=raw-np.nanmin(raw); raw=raw/max(float(np.nanmax(raw)),1e-6)
 Image.fromarray((raw*255).astype('uint8'),'L').resize(im.size,Image.Resampling.BICUBIC).save(out/'portrait_depth.png')
 model.unlink()
 return 'Depth Anything V2 Small quantized ONNX produced a relative depth map'

def upscale_task():
 import onnxruntime as ort
 url='https://huggingface.co/vlad-grig/realesr-general-x4v3-onnx/resolve/main/onnx/model.onnx'
 model=out/'upscale_model.onnx';urllib.request.urlretrieve(url,model)
 opts=ort.SessionOptions();opts.intra_op_num_threads=4
 sess=ort.InferenceSession(str(model),sess_options=opts,providers=['CPUExecutionProvider'])
 im=Image.open(src/'magellan_reference.png').convert('RGB');im.thumbnail((704,704),Image.Resampling.LANCZOS)
 a=np.asarray(im,dtype=np.float32)/255.;h,w=a.shape[:2]
 result=np.zeros((h*4,w*4,3),np.uint8);tile=128;pad=12
 for y in range(0,h,tile):
  for x in range(0,w,tile):
   x0=max(0,x-pad);y0=max(0,y-pad);x1=min(w,x+tile+pad);y1=min(h,y+tile+pad)
   patch=np.transpose(a[y0:y1,x0:x1],(2,0,1))[None,...].astype('float32')
   pred=sess.run(None,{sess.get_inputs()[0].name:patch})[0][0].transpose(1,2,0)
   pred=np.clip(pred*255,0,255).astype('uint8')
   tw=min(tile,w-x);th=min(tile,h-y)
   result[y*4:(y+th)*4,x*4:(x+tw)*4]=pred[(y-y0)*4:(y-y0+th)*4,(x-x0)*4:(x-x0+tw)*4]
 im=Image.fromarray(result);cut=Image.open(out/'portrait_cutout.png').convert('RGBA') if (out/'portrait_cutout.png').exists() else None
 if cut is not None:im.putalpha(cut.getchannel('A').resize(im.size,Image.Resampling.LANCZOS))
 im.save(out/'portrait_upscaled.png',optimize=True);model.unlink()
 return f'Real-ESRGAN general x4v3, tiled CPU inference, output {im.width}x{im.height}'

def speech_task():
 from faster_whisper import WhisperModel
 wav=out/'pilot_audio.wav';subprocess.run(['ffmpeg','-v','error','-y','-i',str(src/'narration_and_score.m4a'),'-t','15','-ar','16000','-ac','1',str(wav)],check=True)
 model=WhisperModel('tiny.en',device='cpu',compute_type='int8',cpu_threads=4)
 segs,info=model.transcribe(str(wav),language='en',beam_size=2,word_timestamps=True,vad_filter=False)
 words=[]
 for seg in segs:
  for w in seg.words or []:words.append({'start':round(w.start,3),'end':round(w.end,3),'word':w.word,'probability':round(w.probability,3)})
 (out/'faster_whisper_words.json').write_text(json.dumps({'language':info.language,'words':words},indent=2))
 if not words:raise RuntimeError('No words returned')
 return f'Faster-whisper tiny.en int8 returned {len(words)} word timestamps'

def stable_task():
 import stable_whisper
 wav=out/'pilot_audio.wav'
 if not wav.exists():raise RuntimeError('audio clip missing')
 model=stable_whisper.load_faster_whisper('tiny.en',device='cpu',compute_type='int8',cpu_threads=4)
 result=model.transcribe_stable(str(wav),language='en',regroup=True,vad=False,verbose=None)
 result.save_as_json(str(out/'stable_ts_words.json'))
 return 'stable-ts refined word-level speech timestamps with faster-whisper'

for name,fn in [('rembg',rembg_task),('depth_anything_v2',depth_task),('real_esrgan',upscale_task),('faster_whisper',speech_task),('stable_ts',stable_task)]:task(name,fn)
(out/'ai_status.json').write_text(json.dumps(status,indent=2))
print('Preprocessing audit saved; no media printed.',flush=True)
