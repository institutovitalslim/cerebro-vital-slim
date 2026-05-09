#!/usr/bin/env python3
"""Service manager for local protected IVS Agent OS cockpit server.
Binds only localhost via the underlying server. Token is never printed unless explicitly using server --print-token.
"""
import argparse, json, os, signal, subprocess, time
from pathlib import Path
BASE=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer')
SERVER=BASE/'scripts/agent_os_cockpit_server.py'
STATE=BASE/'server/cockpit-service-state.json'
LOG=BASE/'server/cockpit-server.log'
HOST='127.0.0.1'; PORT=8791

def load():
    try: return json.loads(STATE.read_text(encoding='utf-8'))
    except Exception: return {}
def save(d):
    STATE.parent.mkdir(parents=True,exist_ok=True); STATE.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def alive(pid):
    if not pid: return False
    try: os.kill(int(pid),0); return True
    except Exception: return False
def status():
    st=load(); pid=st.get('pid'); ok=alive(pid)
    return {'ok':ok,'pid':pid if ok else None,'url':f'http://{HOST}:{PORT}/','state_file':str(STATE),'log':str(LOG),'mode':'localhost_protected_service'}
def start():
    st=status()
    if st['ok']: return {**st,'action':'already_running'}
    LOG.parent.mkdir(parents=True,exist_ok=True)
    lf=open(LOG,'ab')
    p=subprocess.Popen(['python3',str(SERVER),'--host',HOST,'--port',str(PORT)], stdout=lf, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, close_fds=True)
    time.sleep(1)
    d={'pid':p.pid,'host':HOST,'port':PORT,'started_at':int(time.time())}; save(d)
    st=status(); st['action']='started'; return st
def stop():
    st=load(); pid=st.get('pid')
    if not alive(pid): return {'ok':True,'action':'not_running'}
    os.kill(int(pid), signal.SIGTERM); time.sleep(1)
    if alive(pid): os.kill(int(pid), signal.SIGKILL); time.sleep(.5)
    return {'ok':not alive(pid),'action':'stopped','pid':pid}
def restart():
    a=stop(); b=start(); return {'ok':b.get('ok'), 'stop':a, 'start':b}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('action',choices=['status','start','stop','restart']); args=ap.parse_args()
    res={'status':status,'start':start,'stop':stop,'restart':restart}[args.action](); print(json.dumps(res,ensure_ascii=False,indent=2)); raise SystemExit(0 if res.get('ok') or args.action=='stop' else 2)
if __name__=='__main__': main()
