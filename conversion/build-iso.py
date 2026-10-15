"""Create a separate PES 2013 image with additional Argentine chants.

Preserves the existing audio ID inventory and patches only the Argentine team rows in
the executable's five-chant table. Source ISO is opened read-only.
"""
from pathlib import Path
import argparse,io,json,struct,shutil
from cpk_ids import UtfTable,index

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'release';OUT.mkdir(exist_ok=True)
parser=argparse.ArgumentParser()
parser.add_argument('--source',type=Path,required=True,help='Your original PES 2013 PSP USA ISO (ULUS10597)')
parser.add_argument('--output',type=Path,default=OUT/'PES 2013 - Liga Argentina .iso')
args=parser.parse_args()
SOURCE=args.source
ISO=args.output
if SOURCE.resolve()==ISO.resolve():
    parser.error('The output must differ from the original ISO.')
if not SOURCE.is_file():
    parser.error('Source ISO does not exist.')
ISO.parent.mkdir(parents=True,exist_ok=True)
manifest=json.loads((ROOT/'conversion/encoded-chants/manifest.json').read_text())
CPK=ROOT/'audio-original/PSP_GAME/USRDIR/0SOUND.cpk'
h,entries=index(CPK)
files={e['ID']:(ROOT/f"audio-original/files/{e['ID']:04}.bin").read_bytes() for e in entries}
# This PSP executable has a fixed sound-ID inventory. Reuse IDs exclusive to
# the replaced clubs, keeping the existing 692-entry archive.
original_elf=(ROOT/'conversion/game-code/EBOOT.elf').read_bytes()
chant_table=0x29a678
target_rows={67+i for i in list(range(20,40))+list(range(126,130))}
rows=[struct.unpack_from('<5I',original_elf,chant_table+i*20) for i in range(344)]
ours={x for i,row in enumerate(rows) if i in target_rows for x in row}
others={x for i,row in enumerate(rows) if i not in target_rows for x in row}
reusable=sorted(ours-others)
assert len(reusable)>=len(manifest)
for e,new_id in zip(manifest,reusable):e['id']=new_id
files.update({e['id']:(ROOT/e['file']).read_bytes() for e in manifest})

def table_bytes(t,magic,name,nested=False):
    stream=io.BytesIO();t.write(stream,magic,name);b=stream.getvalue()
    # CRI supports both; use the plaintext UTF encoding of the input archives.
    plain=UtfTable.crypt(b[16:])
    return bytes(plain) if nested else b[:4]+struct.pack('<I',255)+b[8:16]+plain

def subtable(items,small):
    t=UtfTable();ty=UtfTable.UtfDatumType
    t.columns=[UtfTable.Column('ID',ty.int16),UtfTable.Column('FileSize',ty.int16 if small else ty.int32),
               UtfTable.Column('ExtractSize',ty.int16 if small else ty.int32)]
    t.rows=[dict(ID=i,FileSize=len(b),ExtractSize=len(b)) for i,b in items]
    return table_bytes(t,'TEMP','CpkItocL' if small else 'CpkItocH',True)

low=[(i,b) for i,b in sorted(files.items()) if len(b)<65536]
high=[(i,b) for i,b in sorted(files.items()) if len(b)>=65536]
itoc=UtfTable();ty=UtfTable.UtfDatumType
itoc.columns=[UtfTable.Column('FilesL',ty.int32),UtfTable.Column('FilesH',ty.int32),
              UtfTable.Column('DataL',ty.bytestring),UtfTable.Column('DataH',ty.bytestring)]
itoc.rows=[dict(FilesL=len(low),FilesH=len(high),DataL=subtable(low,True),DataH=subtable(high,False))]
itoc_bytes=table_bytes(itoc,'ITOC','CpkItocInfo')
align=2048;content_offset=(2048+len(itoc_bytes)+align-1)//align*align
header=UtfTable()
with CPK.open('rb') as f:header.read(f,0,'CPK ')
row=header.rows[0]
row.update(Files=len(files),ContentOffset=content_offset,ItocOffset=2048,ItocSize=len(itoc_bytes),
           ContentSize=sum((len(b)+align-1)//align*align for b in files.values()),
           EnabledPackedSize=sum(map(len,files.values())),EnabledDataSize=sum(map(len,files.values())))
header_bytes=table_bytes(header,'CPK ','CpkHeader')
assert len(header_bytes)<=2048
cpk_out=ROOT/'conversion/0SOUND-Argentina.cpk'
with cpk_out.open('wb') as f:
    f.write(header_bytes);f.write(bytes(2048-f.tell()));f.write(itoc_bytes)
    f.write(bytes(content_offset-f.tell()))
    for i,b in sorted(files.items()):
        f.write(b);f.write(bytes((-len(b))%align))
assert len(index(cpk_out)[1])==len(files)

elf=bytearray((ROOT/'conversion/game-code/EBOOT.elf').read_bytes())
chant_table=0x29a678
# National-team row order verifies the table: England=6, Argentina=44.
assert struct.unpack_from('<5I',elf,chant_table+44*20)==(424,425,426,427,204)
assert struct.unpack_from('<5I',elf,chant_table+6*20)==(376,377,378,379,366)
assert struct.unpack_from('<I',elf,0x2a0840)[0]==5824
clubs=list(range(20,40))+list(range(126,130))
mapping={}
for slot in clubs:
    selected=[e['id'] for e in manifest if e['slot']==slot]
    ids=selected or [200,201,202,203,204]  # stock South American crowd set
    assert len(ids)==5
    struct.pack_into('<5I',elf,chant_table+(67+slot)*20,*ids)
    mapping[slot]=ids

def directory_records(f,extent,length):
    start=extent*2048;off=0
    while off<length:
        f.seek(start+off);n=f.read(1)[0]
        if not n:off=(off//2048+1)*2048;continue
        f.seek(start+off);b=f.read(n)
        yield start+off,b
        off+=n

def find_record(f,path):
    f.seek(16*2048+156);root=f.read(34)
    extent,length=struct.unpack_from('<I',root,2)[0],struct.unpack_from('<I',root,10)[0]
    for component in path.split('/'):
        found=None
        for address,b in directory_records(f,extent,length):
            name=b[33:33+b[32]].decode('ascii',errors='replace').split(';')[0]
            if name==component:found=(address,b);break
        if found is None:raise ValueError('ISO file not found: '+path)
        address,b=found;extent,length=struct.unpack_from('<I',b,2)[0],struct.unpack_from('<I',b,10)[0]
    return address,extent,length

def add_ssound_record(f):
    # The USA disc does not include Spanish-from-Spain audio, although the
    # engine contains its event tables. Add the audio file to its directory.
    address,extent,length=find_record(f,'PSP_GAME/USRDIR')
    entries=list(directory_records(f,extent,length))
    template=next(bytearray(b) for _,b in entries if b[33:33+b[32]].split(b';')[0]==b'MSOUND.cpk')
    template[33:33+template[32]]=template[33:33+template[32]].replace(b'MSOUND',b'SSOUND')
    end=entries[-1][0]+len(entries[-1][1])
    if end//2048!=(end+len(template)-1)//2048:end=(end//2048+1)*2048
    assert end+len(template)<=extent*2048+length, 'No spare directory space'
    f.seek(end);f.write(template)

shutil.copyfile(SOURCE,ISO)
with ISO.open('r+b') as f:
    add_ssound_record(f)
    for path,payload in [('PSP_GAME/SYSDIR/EBOOT.BIN',bytes(elf)),
                         ('PSP_GAME/USRDIR/0SOUND.cpk',cpk_out.read_bytes()),
                         ('PSP_GAME/USRDIR/SSOUND.cpk',(ROOT/'conversion/SSOUND-Closs.cpk').read_bytes())]:
        address,extent,old_size=find_record(f,path)
        if len(payload)<=old_size:
            f.seek(extent*2048);f.write(payload)
        else:
            f.seek(0,2);f.write(bytes((-f.tell())%2048));extent=f.tell()//2048
            f.write(payload);f.write(bytes((-f.tell())%2048))
        f.seek(address+2);f.write(struct.pack('<I',extent)+struct.pack('>I',extent))
        f.seek(address+10);f.write(struct.pack('<I',len(payload))+struct.pack('>I',len(payload)))
    f.seek(0,2);sectors=f.tell()//2048
    for sector in range(16,32):
        f.seek(sector*2048);descriptor=f.read(7)
        if descriptor[1:6]!=b'CD001':break
        if descriptor[0] in (1,2):
            f.seek(sector*2048+80);f.write(struct.pack('<I',sectors)+struct.pack('>I',sectors))
        if descriptor[0]==255:break
(OUT/'chant-tracks.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False))
(OUT/'chant-mapping.json').write_text(json.dumps(mapping,indent=2))
print(ISO,ISO.stat().st_size,'bytes;',len(manifest),'replacement chants')
