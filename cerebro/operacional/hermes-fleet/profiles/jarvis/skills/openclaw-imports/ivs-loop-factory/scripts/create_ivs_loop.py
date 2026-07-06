#!/usr/bin/env python3
import argparse, json, shutil
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]

def slug(s):
    return ''.join(c.lower() if c.isalnum() else '-' for c in s).strip('-').replace('--','-')

ap = argparse.ArgumentParser(description='Create an IVS loop run directory from templates/presets.')
ap.add_argument('--preset', default='custom')
ap.add_argument('--goal', default='')
ap.add_argument('--owner', default='')
ap.add_argument('--out', required=True)
args = ap.parse_args()

out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + slug(args.preset or 'custom')

for name in ['loop-spec.md','trace.md','stop-reason.md']:
    shutil.copyfile(ROOT/'templates'/name, out/name)
state = json.loads((ROOT/'templates/state.json').read_text())
state.update({'run_id': run_id, 'preset': args.preset, 'loop_name': args.preset, 'goal': args.goal, 'owner': args.owner, 'status':'PARTIAL'})
(out/'state.json').write_text(json.dumps(state, ensure_ascii=False, indent=2)+'\n')
if args.preset != 'custom' and (ROOT/'presets'/f'{args.preset}.md').exists():
    shutil.copyfile(ROOT/'presets'/f'{args.preset}.md', out/'preset.md')
print(json.dumps({'ok': True, 'run_id': run_id, 'out': str(out)}, ensure_ascii=False))
