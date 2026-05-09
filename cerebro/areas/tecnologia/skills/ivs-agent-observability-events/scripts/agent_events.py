#!/usr/bin/env python3
import argparse, json, os, re, time
from pathlib import Path
ROOT=Path('/root/.openclaw')
ZLOG=ROOT/'workspace/ops/zapi_bridge/zapi_clara_bridge.log'
WF=ROOT/'workspace/skills/ivs-agent-operating-layer/workflows'
DELIV=Path('/root/deliverables')
PHONE=re.compile(r'55\d{8,13}|\b\d{10,13}\b')

def red(s): return PHONE.sub(lambda m: m.group(0)[:4]+'***'+m.group(0)[-2:], str(s))[:500]
def event(src, kind, sev, msg, **kw):
    d={'ts':int(time.time()),'source':src,'kind':kind,'severity':sev,'message':red(msg)}; d.update(kw); return d

def zapi_events(limit=40):
    out=[]
    if not ZLOG.exists(): return out
    lines=ZLOG.read_text(encoding='utf-8',errors='ignore').splitlines()[-limit:]
    for ln in lines:
        sev='OK'
        if 'blocked' in ln or 'failed' in ln or 'error' in ln.lower(): sev='MEDIUM'
        if 'global_pause' in ln or 'auto_paused' in ln: sev='HIGH'
        if any(k in ln for k in ['admin_send','blocked','ignored phone','lead_allowed','global_pause','auto_paused']):
            out.append(event('clara-zapi','log',sev,ln))
    return out

def workflow_events():
    out=[]
    if WF.exists():
        for p in sorted(WF.glob('*.json')):
            try: d=json.loads(p.read_text(encoding='utf-8'))
            except Exception as e: out.append(event('workflow-registry','invalid_json','HIGH',f'{p.name}: {e}')); continue
            out.append(event('workflow-registry','workflow','OK',d.get('name') or p.stem, id=d.get('id'), owner=d.get('owner')))
    return out

def deliverable_events(limit=20):
    out=[]
    if not DELIV.exists(): return out
    files=sorted([p for p in DELIV.iterdir() if p.is_file()], key=lambda p:p.stat().st_mtime, reverse=True)[:limit]
    for p in files:
        out.append(event('deliverables','file','OK',p.name, path=str(p), mtime=int(p.stat().st_mtime), size=p.stat().st_size))
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--json',action='store_true'); ap.add_argument('--md-out'); args=ap.parse_args()
    events=zapi_events()+workflow_events()+deliverable_events()
    totals={}
    for e in events: totals[e['severity']]=totals.get(e['severity'],0)+1
    report={'ok':not any(e['severity']=='HIGH' for e in events),'generated_at':int(time.time()),'mode':'read_only_redacted_events','totals':{'events':len(events),**totals},'events':events[-200:]}
    if args.md_out:
        lines=['# IVS Agent Observability Events','',f"Eventos: {len(events)}",'', '## Feed']
        lines += [f"- [{e['severity']}] {e['source']} · {e['kind']} · {e['message']}" for e in events[-120:]] or ['- Sem eventos.']
        Path(args.md_out).parent.mkdir(parents=True, exist_ok=True); Path(args.md_out).write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
