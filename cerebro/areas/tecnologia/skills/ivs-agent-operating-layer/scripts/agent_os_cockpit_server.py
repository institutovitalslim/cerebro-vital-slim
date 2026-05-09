#!/usr/bin/env python3
"""Local protected HTTP server for IVS Agent OS deliverables.
Binds to 127.0.0.1 by default. Token required via ?token= or X-IVS-Agent-OS-Token.
Never exposes secrets; serves only allowlisted deliverables.
"""
import argparse, os, secrets, json, mimetypes, subprocess
from pathlib import Path
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
BASE=Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer')
DEL=Path('/root/deliverables')
TOKEN_FILE=BASE/'server/cockpit-token.txt'
ALLOW={
 '/':'cockpit-vivo-ivs-agent-os.html',
 '/live':'cockpit-vivo-ivs-agent-os.html',
 '/cockpit':'cockpit-unico-ivs-agent-os.html',
 '/runs':'cockpit-workflow-runs-ivs.html',
 '/trends':'agent-os-trends.html',
 '/approval':'approval-console-ivs-agent-os.html',
 '/runbook':'runbook-ivs-agent-os.md',
 '/status.json':'cockpit-unico-ivs-agent-os.json',
 '/alerts.json':'agent-os-critical-alerts-latest.json',
}
def ensure_token():
    TOKEN_FILE.parent.mkdir(parents=True,exist_ok=True)
    if not TOKEN_FILE.exists():
        TOKEN_FILE.write_text(secrets.token_urlsafe(32), encoding='utf-8')
        os.chmod(TOKEN_FILE,0o600)
    return TOKEN_FILE.read_text(encoding='utf-8').strip()
def refresh():
    subprocess.check_output(['python3',str(BASE/'scripts/agent_os_cli.py'),'refresh-all'], text=True, stderr=subprocess.STDOUT, timeout=120)
class H(BaseHTTPRequestHandler):
    token=''
    def _auth(self):
        qs=parse_qs(urlparse(self.path).query)
        supplied=(qs.get('token') or [''])[0] or self.headers.get('X-IVS-Agent-OS-Token','')
        return supplied and secrets.compare_digest(supplied, self.token)
    def do_GET(self):
        if not self._auth():
            self.send_response(403); self.send_header('content-type','application/json'); self.end_headers(); self.wfile.write(b'{"ok":false,"error":"forbidden"}'); return
        path=urlparse(self.path).path
        if path=='/refresh':
            try: refresh(); body=json.dumps({'ok':True,'refreshed':True}).encode()
            except Exception as e: body=json.dumps({'ok':False,'error':str(e)[:300]}).encode()
            self.send_response(200); self.send_header('content-type','application/json'); self.end_headers(); self.wfile.write(body); return
        name=ALLOW.get(path)
        if not name:
            self.send_response(404); self.end_headers(); return
        fp=(DEL/name).resolve()
        if not str(fp).startswith(str(DEL.resolve())) or not fp.exists():
            self.send_response(404); self.end_headers(); return
        data=fp.read_bytes(); ctype=mimetypes.guess_type(str(fp))[0] or ('text/markdown' if fp.suffix=='.md' else 'application/octet-stream')
        self.send_response(200); self.send_header('content-type',ctype+'; charset=utf-8' if ctype.startswith('text/') or ctype=='application/json' else ctype); self.send_header('cache-control','no-store'); self.end_headers(); self.wfile.write(data)
    def log_message(self, fmt, *args):
        print('cockpit_server', self.address_string(), fmt%args)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--host',default='127.0.0.1'); ap.add_argument('--port',type=int,default=8791); ap.add_argument('--print-token',action='store_true'); args=ap.parse_args()
    H.token=ensure_token()
    if args.print_token:
        print(json.dumps({'ok':True,'url':f'http://{args.host}:{args.port}/?token={H.token}','token_file':str(TOKEN_FILE)},ensure_ascii=False,indent=2)); return
    print(json.dumps({'ok':True,'bind':f'{args.host}:{args.port}','token_file':str(TOKEN_FILE),'mode':'local_protected'},ensure_ascii=False))
    ThreadingHTTPServer((args.host,args.port),H).serve_forever()
if __name__=='__main__': main()
