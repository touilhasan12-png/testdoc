import math,wave,struct,json
sr=24000;duration=21;n=sr*duration
chords=[(146.832,174.614,220),(116.541,146.832,174.614),(130.813,164.814,195.998),(110,130.813,164.814)]
a=[];fx=[]
for i in range(n):
 t=i/sr;value=0
 for j,chord in enumerate(chords):
  local=t-j*5
  if 0<=local<=7:
   env=min(1,local/1.8)*min(1,(7-local)/2)
   value+=env*sum(math.sin(2*math.pi*f*t)+.18*math.sin(2*math.pi*f*2*t) for f in chord)/3
 a.append(value*min(1,t/2,(duration-t)/2))
 u=t-.6;v=t-1.84
 fx.append((.022*math.exp(-u*5)*math.sin(2*math.pi*860*u) if 0<=u<1.5 else 0)+(.045*math.exp(-v*4)*math.sin(2*math.pi*52*v) if 0<=v<2 else 0))
peak=max(map(abs,a));a=[x*.066/peak for x in a]
for name,values in [('pad',a),('sfx',fx)]:
 with wave.open('public/'+name+'.wav','wb') as w:
  w.setparams((1,2,sr,0,'NONE','not compressed'));w.writeframes(b''.join(struct.pack('<h',round(x*32767)) for x in values))
print(json.dumps({'pad_peak':max(map(abs,a)),'chords':'Dm-Bb-C-Am','duration':duration}))
