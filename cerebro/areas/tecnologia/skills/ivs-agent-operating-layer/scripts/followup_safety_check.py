#!/usr/bin/env python3
"""Follow-up Seguro IVS — preflight for Clara/Maria WhatsApp active sends.

Default is safe: local validation + dry-run only. Real send requires both --real
and --i-understand-real-whatsapp-send, and should only be used after explicit
Tiaro/equipe authorization.
"""
import argparse
import json
import re
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

BASE = Path('/root/.openclaw/workspace/ops/zapi_bridge')
ADMIN_SEND_URL = 'http://127.0.0.1:8787/admin/send'


def normalize_phone(raw: str) -> str:
    return re.sub(r'\D+', '', raw or '')


def load_json(path: Path, default):
    try:
        if not path.exists():
            return default
        data = json.loads(path.read_text(encoding='utf-8'))
        return data if isinstance(data, dict) else default
    except Exception:
        return default


def exclusion_for(phone: str):
    state = load_json(BASE / 'clara_exclusions.json', {'phones': {}})
    entry = (state.get('phones') or {}).get(phone)
    if not isinstance(entry, dict):
        return None
    reason = str(entry.get('reason') or 'excluded_phone')
    source = str(entry.get('source') or '')
    if reason.startswith('lead_exception') or source == 'tiaro_lead_exception':
        return {'blocked': False, 'explicit_exception': True, 'entry': entry}
    return {'blocked': True, 'explicit_exception': False, 'entry': entry}


def lead_entry(phone: str):
    state = load_json(BASE / 'clara_leads_state.json', {'leads': {}})
    entry = (state.get('leads') or {}).get(phone)
    return entry if isinstance(entry, dict) else None


def post_admin_send(phone: str, message: str, dry_run: bool):
    payload = json.dumps({'phone': phone, 'message': message, 'dry_run': dry_run}, ensure_ascii=False).encode('utf-8')
    req = Request(ADMIN_SEND_URL, data=payload, headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urlopen(req, timeout=10) as resp:
            body = resp.read().decode('utf-8', errors='replace')
            return resp.status, json.loads(body) if body else {}
    except HTTPError as exc:
        body = exc.read().decode('utf-8', errors='replace')
        try:
            parsed = json.loads(body)
        except Exception:
            parsed = {'raw': body[:500]}
        return exc.code, parsed
    except URLError as exc:
        return 0, {'ok': False, 'error': str(exc)}


def main():
    ap = argparse.ArgumentParser(description='Preflight seguro para follow-up ativo da Clara via Z-API')
    ap.add_argument('--phone', required=True)
    ap.add_argument('--message', required=True)
    ap.add_argument('--real', action='store_true', help='solicita envio real; bloqueado sem confirmação explícita')
    ap.add_argument('--i-understand-real-whatsapp-send', action='store_true')
    ap.add_argument('--local-only', action='store_true', help='não chama /admin/send; apenas valida arquivos locais')
    args = ap.parse_args()

    phone = normalize_phone(args.phone)
    message = (args.message or '').strip()
    if not phone:
        print(json.dumps({'ok': False, 'error': 'missing_phone'}, ensure_ascii=False, indent=2)); return 2
    if not message:
        print(json.dumps({'ok': False, 'error': 'missing_message'}, ensure_ascii=False, indent=2)); return 2

    ex = exclusion_for(phone)
    lead = lead_entry(phone)
    decision = 'dry_run_allowed'
    blocked = False
    reasons = []
    if ex and ex.get('blocked'):
        blocked = True
        decision = 'blocked_by_exclusion'
        reasons.append(str((ex.get('entry') or {}).get('reason') or 'excluded_phone'))
    if args.real and not args.i_understand_real_whatsapp_send:
        blocked = True
        decision = 'real_send_missing_explicit_confirmation'
        reasons.append('missing_i_understand_real_whatsapp_send')

    http_status = None
    http_body = None
    if not args.local_only and not (args.real and blocked):
        # If blocked by exclusion, still call /admin/send dry_run to confirm server-side block.
        dry_run = not args.real
        http_status, http_body = post_admin_send(phone, message, dry_run=dry_run)
        if http_status == 409:
            blocked = True
            decision = 'blocked_by_admin_send'
            reasons.append(str((http_body or {}).get('reason') or 'admin_send_block'))

    result = {
        'ok': not blocked,
        'mode': 'real_send' if args.real else 'dry_run',
        'decision': decision,
        'phone': phone,
        'message_preview': message[:160],
        'lead': lead,
        'exclusion': ex,
        'blocked': blocked,
        'reasons': sorted(set(reasons)),
        'admin_send_status': http_status,
        'admin_send_body': http_body,
        'guardrail': 'Paciente/do_not_reply bloqueia por padrão. Envio real exige autorização explícita.'
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if blocked else 0


if __name__ == '__main__':
    sys.exit(main())
