"""Map PES 2014 Closs event audio into PES 2013's Spanish commentary bank.

The realconditionS overlays have identical event records and condition graphs.
Only audio IDs and relocated pointers change. Match records, not file numbers.
Unmapped player/team callnames are silent: the Argentine roster disables them.
"""
from pathlib import Path
import io,json,struct,subprocess
from cpk_ids import UtfTable,index
R=Path(__file__).resolve().parent.parent
original=(R/'conversion/game-code/over/0059.bin').read_bytes()
donor=(R/'commentary-closs/over/0059.bin').read_bytes()
assert original[32:64].split(b'\0')[0]==donor[32:64].split(b'\0')[0]==b'realconditionS.ovl'
assert len(original)==len(donor)==106496
mapping={}
event_start,event_end=0x80,0xd0c0
for offset in range(event_start,event_end,16):
    old=struct.unpack_from('<4I',original,offset)
    new=struct.unpack_from('<4I',donor,offset)
    assert old[:3]==new[:3], hex(offset)
    if 0x20000 <= old[3] < 0x20000+5824:
        assert 0x20000 <= new[3] < 0x20000+4918
        target,source=old[3]-0x20000,new[3]-0x20000
        assert target not in mapping or mapping[target]==source
        mapping[target]=source
    else:
        assert old==new  # six special commands, not audio file references
assert len(mapping)==3326 and mapping[5169]==4374
# Verify the entire condition graph after the event records is unchanged,
# allowing only the documented overlay load-address relocation.
base_old=struct.unpack_from('<I',original,8)[0]
base_new=struct.unpack_from('<I',donor,8)[0]
for offset in range(event_end,len(original),4):
    old=struct.unpack_from('<I',original,offset)[0]
    new=struct.unpack_from('<I',donor,offset)[0]
    assert old==new or (base_old<=old<base_old+len(original)
        and base_new<=new<base_new+len(donor)
        and old-base_old==new-base_new), hex(offset)

source_dir=R/'commentary-closs/files'
silence=(source_dir/'1300.bin').read_bytes()
pcm=subprocess.check_output(['ffmpeg','-v','error','-i',str(source_dir/'1300.bin'),
    '-f','s16le','-'])
assert pcm and max(abs(x) for x in struct.unpack('<'+'h'*(len(pcm)//2),pcm))==0
files={i:silence for i in range(5824)}
converted=R/'conversion/converted-commentary';converted.mkdir(exist_ok=True)
converted_ids=[]
for target,source in sorted(mapping.items()):
    path=source_dir/f'{source:04}.bin';data=path.read_bytes()
    if data[:4]!=b'RIFF':
        # Three donor entries are still PS2 ADX. Transcode them to PSP ATRAC3.
        assert data[:4]==bytes.fromhex('80000020'),(target,source,data[:4])
        wav=converted/f'{source:04}.wav';encoded=converted/f'{source:04}.at3'
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(path),'-ar','44100',
            '-ac','2','-c:a','pcm_s16le',str(wav)],check=True)
        with (converted/f'{source:04}.log').open('w') as log:
            subprocess.run([str(R/'tools/atracdenc/build/src/atracdenc'),'-e',
                'atrac3_lp4','--container','riff','-i',str(wav),'-o',str(encoded)],
                stdout=log,stderr=log,check=True)
        data=encoded.read_bytes();converted_ids.append(source)
    assert data[:4]==b'RIFF' and data[8:12]==b'WAVE'
    files[target]=data
assert len(files)==5824
report=dict(event_count=len(mapping),silent_unmapped_count=5824-len(mapping),
    verified_identical_condition_graph=True,converted_adx_ids=converted_ids,
    mapping=mapping)
(R/'conversion/commentary-mapping.json').write_text(json.dumps(report,indent=2))

def table(t,magic,name,nested=False):
 s=io.BytesIO();t.write(s,magic,name);b=s.getvalue();plain=UtfTable.crypt(b[16:])
 return bytes(plain) if nested else b[:4]+struct.pack('<I',255)+b[8:16]+plain

def sub(items,small):
 t=UtfTable();ty=UtfTable.UtfDatumType
 t.columns=[UtfTable.Column('ID',ty.int16),UtfTable.Column('FileSize',ty.int16 if small else ty.int32),UtfTable.Column('ExtractSize',ty.int16 if small else ty.int32)]
 t.rows=[dict(ID=i,FileSize=len(b),ExtractSize=len(b)) for i,b in items]
 return table(t,'TEMP','CpkItocL' if small else 'CpkItocH',True)
low=[(i,b) for i,b in sorted(files.items()) if len(b)<65536];high=[(i,b) for i,b in sorted(files.items()) if len(b)>=65536]
t=UtfTable();ty=UtfTable.UtfDatumType
t.columns=[UtfTable.Column('FilesL',ty.int32),UtfTable.Column('FilesH',ty.int32),UtfTable.Column('DataL',ty.bytestring),UtfTable.Column('DataH',ty.bytestring)]
t.rows=[dict(FilesL=len(low),FilesH=len(high),DataL=sub(low,True),DataH=sub(high,False))]
itoc=table(t,'ITOC','CpkItocInfo');offset=(2048+len(itoc)+2047)//2048*2048
h=UtfTable()
with (R/'commentary-original/PSP_GAME/USRDIR/MSOUND.cpk').open('rb') as f:h.read(f,0,'CPK ')
h.rows[0].update(Files=len(files),ContentOffset=offset,ItocOffset=2048,ItocSize=len(itoc),ContentSize=sum((len(b)+2047)//2048*2048 for b in files.values()),EnabledPackedSize=sum(map(len,files.values())),EnabledDataSize=sum(map(len,files.values())))
hb=table(h,'CPK ','CpkHeader');out=R/'conversion/SSOUND-Closs.cpk'
with out.open('wb') as f:
 f.write(hb);f.write(bytes(2048-f.tell()));f.write(itoc);f.write(bytes(offset-f.tell()))
 for _,b in sorted(files.items()):f.write(b);f.write(bytes((-len(b))%2048))
assert len(index(out)[1])==len(files)
print(out,out.stat().st_size)
