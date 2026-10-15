"""Convert Surling's 2012 ADX chant packs to PSP-compatible ATRAC3+ RIFF."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json, struct, subprocess

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'conversion/encoded-chants';OUT.mkdir(exist_ok=True)
ENC=ROOT/'tools/atracdenc/build/src/atracdenc'
clubs=[('Boca',25),('River',34),('Racing',33),('Independiente',29),('San-Lorenzo',35)]
jobs=[]
for club,slot in clubs:
    files=sorted((ROOT/'chants-surling'/club).rglob('*.adx'))
    assert len(files)==5
    for p in files: jobs.append(dict(id=692+len(jobs),club=club,slot=slot,source=str(p.relative_to(ROOT))))

def chunks(data):
    result={};off=12
    while off+8<=len(data):
        tag,size=struct.unpack_from('<4sI',data,off)
        result[tag]=data[off+8:off+8+size];off+=8+size+(size%2)
    return result

def convert(job):
    stem=OUT/f"{job['id']:04}"
    wav=stem.with_suffix('.wav');encoded=stem.with_suffix('.at3');out=stem.with_suffix('.bin')
    if not out.exists():
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(ROOT/job['source']),
            '-ar','44100','-ac','2','-af','loudnorm=I=-23:TP=-3:LRA=11',
            '-c:a','pcm_s16le',str(wav)],check=True)
        with stem.with_suffix('.log').open('w') as log:
            subprocess.run([str(ENC),'-e','atrac3plus','--container','riff',
                '-i',str(wav),'-o',str(encoded)],stdout=log,stderr=log,check=True)
        c=chunks(encoded.read_bytes())
        # Keep the native game's 100-byte RIFF layout and the actual bitrate.
        fmt=bytearray((ROOT/'audio-original/files/0567.bin').read_bytes()[20:72])
        # CRI expects the Sony ATRAC extension as well as the WAVE GUID.
        # Keep compressed bits-per-sample=0 and 2048 samples per block.
        struct.pack_into('<I',fmt,8,44100)
        struct.pack_into('<H',fmt,12,2048)
        fmt[42:44]=bytes.fromhex('28ff')  # 44.1 kHz, stereo, 2048-byte frames
        # Use the native extended fact delay: 2232-184+368 = 2416.
        # The inclusive end sample must stay inside the encoded frame count.
        samples=len(c[b'data']) // 2048 * 2048 - 2416
        fact=struct.pack('<III',samples,2048,2232)
        body=b'WAVE'+b'fmt '+struct.pack('<I',52)+fmt+b'fact'+struct.pack('<I',12)+fact
        body+=b'data'+struct.pack('<I',len(c[b'data']))+c[b'data']
        out.write_bytes(b'RIFF'+struct.pack('<I',len(body))+body)
        wav.unlink()
    job['file']=str(out.relative_to(ROOT));job['bytes']=out.stat().st_size
    print(job['club'],Path(job['source']).name,'->',job['id'],flush=True)
    return job

with ThreadPoolExecutor(max_workers=3) as pool: report=list(pool.map(convert,jobs))
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
