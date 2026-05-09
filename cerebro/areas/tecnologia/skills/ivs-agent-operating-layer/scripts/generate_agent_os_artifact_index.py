#!/usr/bin/env python3
import argparse, json, time, mimetypes
from pathlib import Path
DEL=Path('/root/deliverables')
PREFIXES=('cockpit-','agent-os-','approval-console-','runbook-','workflow-registry-','ivs-agent-')
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--json-out',default='/root/deliverables/agent-os-artifact-index.json'); ap.add_argument('--md-out',default='/root/deliverables/agent-os-artifact-index.md'); args=ap.parse_args()
    items=[]
    for p in sorted(DEL.iterdir() if DEL.exists() else [], key=lambda x:x.name):
        if not p.is_file(): continue
        if not p.name.startswith(PREFIXES): continue
        st=p.stat(); items.append({'name':p.name,'path':str(p),'size':st.st_size,'mtime':int(st.st_mtime),'mime':mimetypes.guess_type(str(p))[0] or 'application/octet-stream'})
    report={'ok':True,'generated_at':int(time.time()),'totals':{'artifacts':len(items)},'artifacts':items}
    Path(args.json_out).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    lines=['# Índice de Artefatos IVS Agent OS','',f"Gerado em: `{report['generated_at']}`",'',f"Total: **{len(items)}**",'']
    for i in items: lines.append(f"- `{i['path']}` — {i['size']} bytes — {i['mime']}")
    Path(args.md_out).write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
