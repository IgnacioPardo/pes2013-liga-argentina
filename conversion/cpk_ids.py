"""Read old PSP ID-only CRI CPK archives, using pes-file-tools' UTF parser."""
import io
import struct
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'tools/pes-file-tools/lib'))
from pes_file_tools.cpk import UtfTable
from pes_file_tools.crilayla import decompressCrilayla

def index(path):
    with open(path,'rb') as f:
        header=UtfTable();header.read(f,0,'CPK '); h=header.rows[0]
        toc=UtfTable();toc.read(f,h['ItocOffset'],'ITOC')
        entries=[]
        for name in ['DataL','DataH']:
            b=toc.rows[0][name]
            if b is None:continue
            sub=UtfTable();sub.read(io.BytesIO(struct.pack('<4sIQ',b'TEMP',0,len(b))+b),0,'TEMP')
            entries.extend(sub.rows)
        entries.sort(key=lambda e:e['ID'])
        offset=h['ContentOffset'];align=h['Align']
        for entry in entries:
            entry['offset']=offset
            offset+=(entry['FileSize']+align-1)//align*align
        assert len(entries)==h['Files']
        return h,entries

def extract(path,directory):
    out=Path(directory);out.mkdir(parents=True,exist_ok=True)
    h,entries=index(path)
    with open(path,'rb') as f:
        for e in entries:
            f.seek(e['offset']);data=f.read(e['FileSize'])
            assert len(data)==e['FileSize']
            if e['FileSize']!=e['ExtractSize']:
                data=decompressCrilayla(data)
                assert len(data)==e['ExtractSize']
            (out/f"{e['ID']:04}.bin").write_bytes(data)
    return h,entries

if __name__=='__main__':
    h,entries=extract(sys.argv[1],sys.argv[2]);print('Extracted',len(entries),'files')
