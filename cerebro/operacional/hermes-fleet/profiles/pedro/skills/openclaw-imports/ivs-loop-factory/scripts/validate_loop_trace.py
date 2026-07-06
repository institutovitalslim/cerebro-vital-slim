#!/usr/bin/env python3
import json, sys
from pathlib import Path

REQUIRED_STATUS={'DONE','DONE_WITH_CONCERNS','PARTIAL','BLOCKED','NEEDS_APPROVAL','DELEGATED'}
REQUIRED_STOP={'success','plateau','blocked','budget_exhausted','human_gate','delegated',None}

def main(path):
    p=Path(path); errors=[]
    state=p/'state.json'; trace=p/'trace.md'
    if not state.exists(): errors.append('missing state.json')
    if not trace.exists(): errors.append('missing trace.md')
    data={}
    if state.exists():
        try: data=json.loads(state.read_text())
        except Exception as e: errors.append(f'invalid state.json: {e}')
    status=data.get('status')
    if status not in REQUIRED_STATUS: errors.append(f'invalid status: {status}')
    stop=data.get('stop_reason')
    if stop not in REQUIRED_STOP: errors.append(f'invalid stop_reason: {stop}')
    if status=='DONE' and not data.get('observations'):
        errors.append('DONE requires observations/evidence in state.json')
    if data.get('approval_required') and status not in {'NEEDS_APPROVAL','DELEGATED','BLOCKED'}:
        errors.append('approval_required true should stop as NEEDS_APPROVAL/DELEGATED/BLOCKED')
    print(json.dumps({'ok': not errors, 'errors': errors, 'path': str(p)}, ensure_ascii=False, indent=2))
    return 1 if errors else 0
if __name__=='__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv)>1 else '.'))
