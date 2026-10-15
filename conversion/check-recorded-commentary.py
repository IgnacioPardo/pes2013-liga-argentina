"""Match native emulator output to known Closs clips; no synthesized audio."""
from pathlib import Path
import subprocess,json,re,struct
import numpy as np
r=Path(__file__).resolve().parent.parent;rate=5512
record=r/'pes2013-import-test/evidence/patched-game-test.mkv'
def pcm(p):
 q=subprocess.run(['ffmpeg','-v','error','-i',str(p),'-vn','-ar',str(rate),'-ac','1','-f','f32le','-'],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,check=True)
 return np.frombuffer(q.stdout,dtype='<f4').astype(float)
y=np.diff(pcm(record));n=1<<(len(y)+rate-1).bit_length();fy=np.fft.rfft(y,n);power=np.r_[0,np.cumsum(y*y)]
log=(r/'pes2013-import-test/retroarch.log').read_text(errors='replace');sizes={int(x) for x in re.findall(r'DATA chunk found at offset 60 with size (\d+)',log)}
ids=[]
for p in (r/'commentary-closs/files').glob('*.bin'):
 if int(p.stem)>=4918:continue
 b=p.read_bytes()
 if b[:4]==b'RIFF' and b[52:56]==b'data' and struct.unpack_from('<I',b,56)[0] in sizes:ids.append(int(p.stem))
# Initial kickoff audio has an exact mapping from the compared overlays.
ids=sorted(set([4374]+ids));print('Recorded seconds',len(y)/rate,'candidates',ids,flush=True)
results=[]
for i in ids:
 x=np.diff(pcm(r/'commentary-closs/files'/f'{i:04}.bin'));best=dict(correlation=0)
 for sec in [.3,.8,1.3,2.0]:
  a=x[int(sec*rate):int(sec*rate)+rate]
  if len(a)<rate or np.dot(a,a)<1e-7:continue
  corr=np.fft.irfft(fy*np.fft.rfft(a[::-1],n),n)[len(a)-1:len(y)]
  energy=power[len(a):]-power[:-len(a)];scores=np.abs(corr)/np.sqrt(np.maximum(energy*np.dot(a,a),1e-16));scores[energy<1e-8]=0;k=int(np.argmax(scores))
  if scores[k]>best['correlation']:best=dict(correlation=float(scores[k]),recording_seconds=k/rate,source_seconds=sec)
 best['donor_audio_id']=i;results.append(best)
 if best['correlation']>.3:print(best,flush=True)
report=dict(recording=str(record.relative_to(r)),seconds=len(y)/rate,matches=[x for x in results if x['correlation']>.3],all_candidates=results)
(r/'pes2013-import-test/evidence/closs-waveform-check.json').write_text(json.dumps(report,indent=2))
