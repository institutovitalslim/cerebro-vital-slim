#!/usr/bin/env python3
import argparse, json, subprocess, time
from pathlib import Path
BASE=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer')
GEN=BASE/'scripts/generate_agent_os_cockpit.py'
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out',default='/root/deliverables/cockpit-vivo-ivs-agent-os.html'); ap.add_argument('--refresh-seconds',type=int,default=60); args=ap.parse_args()
    data_path=Path('/root/deliverables/cockpit-unico-ivs-agent-os.json')
    html_path=Path('/root/deliverables/cockpit-unico-ivs-agent-os.html')
    subprocess.check_output(['python3',str(GEN),'--out',str(html_path),'--json-out',str(data_path)], text=True, stderr=subprocess.STDOUT)
    d=json.loads(data_path.read_text())
    html=f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta http-equiv="refresh" content="{args.refresh_seconds}"><meta name="viewport" content="width=device-width,initial-scale=1"><title>IVS Agent OS — Cockpit Vivo</title><style>body{{font-family:Inter,Arial,sans-serif;background:#0b1020;color:#eef;margin:0;padding:24px}}.card{{background:#141b34;border:1px solid #2c385f;border-radius:16px;padding:18px;margin:12px 0}}.ok{{color:#67e8a5}}.warn{{color:#facc15}}pre{{white-space:pre-wrap;background:#090d1a;padding:12px;border-radius:10px;overflow:auto}}a{{color:#93c5fd}}</style></head><body><h1>IVS Agent OS — Cockpit Vivo</h1><p>Auto-refresh: {args.refresh_seconds}s · Gerado em {int(time.time())}</p><div class="card"><h2>Status: <span class="{'ok' if d.get('status')=='OK' else 'warn'}">{d.get('status')}</span></h2><p>OK: {d.get('ok')}</p><p><a href="cockpit-unico-ivs-agent-os.html">Abrir cockpit detalhado</a></p></div><div class="card"><h2>Fontes</h2><pre>{json.dumps(d.get('sources'),ensure_ascii=False,indent=2)}</pre></div><div class="card"><h2>Resumo bruto</h2><pre>{json.dumps({'status':d.get('status'),'ok':d.get('ok'),'generated_at':d.get('generated_at')},ensure_ascii=False,indent=2)}</pre></div></body></html>'''
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(html,encoding='utf-8')
    print(json.dumps({'ok':True,'out':str(out),'source_json':str(data_path),'refresh_seconds':args.refresh_seconds,'status':d.get('status')},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
