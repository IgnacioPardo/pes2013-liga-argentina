"""Encrypt the converted option file into a new, isolated savedata directory."""
import argparse
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--base-save', type=Path, required=True,
                    help='Original ULUS1059700008000 savedata directory')
parser.add_argument('--output', type=Path, required=True,
                    help='New ULUS1059700008000 directory; must not exist')
parser.add_argument('--input', type=Path,
                    default=ROOT / 'conversion/argentina-2013-decrypted.bin')
parser.add_argument('--key', type=Path, default=ROOT / 'conversion/2013.key')
args = parser.parse_args()
if args.output.exists():
    parser.error('Output already exists. Choose a new directory to preserve saves.')
for path in (args.base_save / 'PARAM.SFO', args.input, args.key):
    if not path.is_file():
        parser.error(f'Missing input: {path}')
if args.key.stat().st_size != 16:
    parser.error('The savedata key must contain 16 bytes.')
shutil.copytree(args.base_save, args.output)
# The encryptor updates PARAM.SFO in place: only pass the copied version.
temporary = args.output / 'DATA.BIN.tmp'
with temporary.open('wb') as stream:
    subprocess.run([
        str(ROOT / 'tools/psp-savedata-endecrypter/endecrypter'),
        str(args.input), str(args.key), str(args.output / 'PARAM.SFO')
    ], stdout=stream, check=True)
temporary.replace(args.output / 'DATA.BIN')
print(args.output)
