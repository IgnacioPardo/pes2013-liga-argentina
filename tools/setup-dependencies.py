"""Fetch pinned source dependencies, preserving existing working copies."""
import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--check', action='store_true', help='Check installed commits without downloading')
args = parser.parse_args()

def run(command, **kwargs):
    return subprocess.run(command, check=True, **kwargs)

for dependency in json.loads((ROOT / 'tools/dependencies.json').read_text()):
    target = ROOT / 'tools' / dependency['name']
    if not target.exists():
        if args.check:
            raise SystemExit(f'Missing dependency: {target.name}')
        run(['git', 'clone', '--no-checkout', dependency['url'], str(target)])
        run(['git', '-C', str(target), 'checkout', '--detach', dependency['commit']])
    head = subprocess.check_output(['git', '-C', str(target), 'rev-parse', 'HEAD'], text=True).strip()
    if head != dependency['commit']:
        raise SystemExit(f'{target.name}: expected {dependency["commit"]}, found {head}; existing checkout preserved')
    if not args.check and (target / '.gitmodules').exists():
        run(['git', '-C', str(target), 'submodule', 'update', '--init', '--recursive'])
    patch = dependency.get('patch')
    if patch:
        patch_path = str(ROOT / patch)
        applied = subprocess.run(['git', '-C', str(target), 'apply', '--reverse', '--check', patch_path],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
        if not applied:
            if args.check:
                raise SystemExit(f'{target.name}: required local patch is not applied')
            run(['git', '-C', str(target), 'apply', '--check', patch_path])
            run(['git', '-C', str(target), 'apply', patch_path])
    print(f'{target.name}: {head}', flush=True)
