"""Restore Argentina/Brazil editable kits while retaining the current save."""
from pathlib import Path
import argparse,struct
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
data=bytearray(a.input.read_bytes());source=(ROOT/'conversion/2012-decrypted.bin').read_bytes()
for team in (44,45):
 src=762152+team*456;dst=754264+team*456
 data[dst:dst+352]=source[src:src+352]
 for k in range(4):struct.pack_into('<H',data,dst+k*88+80,65535)
a.output.write_bytes(data)
