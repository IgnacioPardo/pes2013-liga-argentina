"""Compare actual emulator recording against encoded chant waveforms."""
from pathlib import Path
import subprocess,json
import numpy as np
r=Path(__file__).resolve().parent.parent
rate=5512
def pcm(path):
 p=subprocess.run(['ffmpeg','-v','error','-i',str(path),'-vn','-ar',str(rate),'-ac','1','-f','f32le','-'],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,check=True)
 return np.frombuffer(p.stdout,dtype='<f4').astype(float)
y=pcm(r/'pes2013-import-test/evidence/boca-river-chant-test.mkv')
print('Recorded seconds',len(y)/rate,flush=True)
# High-pass by first differences reduces generic shared crowd rumble.
y=np.diff(y);n=1<<(len(y)+rate*2-1).bit_length();fy=np.fft.rfft(y,n);power=np.r_[0,np.cumsum(y*y)]
results=[]
for i in range(692,702):
 x=np.diff(pcm(r/'conversion/encoded-chants'/f'{i:04}.at3'))
 best=dict(correlation=0)
 for sec in [2,6,10,15]:
  a=x[sec*rate:(sec+2)*rate]
  if len(a)<rate*2:continue
  corr=np.fft.irfft(fy*np.fft.rfft(a[::-1],n),n)[len(a)-1:len(y)]
  energy=power[len(a):]-power[:-len(a)]
  den=np.sqrt(np.maximum(energy*np.dot(a,a),1e-16))
  scores=np.abs(corr)/den
  scores[energy<1e-8]=0
  k=int(np.argmax(scores))
  if scores[k]>best['correlation']:best=dict(correlation=float(scores[k]),recording_seconds=k/rate,source_seconds=sec)
 best['track']=i;results.append(best);print(best,flush=True)
(r/'pes2013-import-test/evidence/chant-waveform-check.json').write_text(json.dumps(results,indent=2))
