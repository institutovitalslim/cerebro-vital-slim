#!/usr/bin/env python3
"""Clara Safety Monitor — read-only operational audit for IVS.

Never sends WhatsApp messages. Never pauses/unpauses Clara. It reads local bridge
state and optionally checks local health/status endpoints.
"""
import argparse
import json
import time
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from typing import Any, Dict, Tuple

DEFAULT_BASE = Path('/root/.openclaw/workspace/ops/zapi_bridge')


def load_json(path: Path, default: Dict[str, Any]) -> Tuple[Dict[str, Any], str | None]:
    try:
        if not path.exists():
            return default, f'missing:{path}'
        data = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(data, dict):
            return default, f'invalid_root:{path}'
        return data, None
    except Exception as exc:
        return default, f'read_error:{path}:{exc}'


def http_json(url: str, timeout: float = 2.0) -> Dict[str, Any]:
    req = Request(url, method='GET')
    try:
        with urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode('utf-8', errors='replace')
            try:
                parsed = json.loads(body)
            except Exception:
                parsed = {'raw': body[:500]}
            return {'ok': 200 <= resp.status < 300, 'status': resp.status, 'body': parsed}
    except HTTPError as exc:
        return {'ok': False, 'status': exc.code, 'body': exc.read().decode('utf-8', errors='replace')[:500]}
    except URLError as exc:
        return {'ok': False, 'error': str(exc)}
    except Exception as exc:
        return {'ok': False, 'error': str(exc)}


def classify_exclusions(exclusions: Dict[str, Any]) -> Dict[str, Any]:
    phones = exclusions.get('phones') if isinstance(exclusions.get('phones'), dict) else {}
    by_reason: Dict[str, int] = {}
    lead_exceptions = []
    do_not_reply = []
    patient_bridge_known = []
    for phone, entry in phones.items():
        if not isinstance(entry, dict):
            continue
        reason = str(entry.get('reason') or 'unknown')
        source = str(entry.get('source') or '')
        by_reason[reason] = by_reason.get(reason, 0) + 1
        item = {'phone': phone, 'name': entry.get('name'), 'reason': reason, 'source': source}
        if reason.startswith('lead_exception') or source == 'tiaro_lead_exception':
            lead_exceptions.append(item)
        if reason == 'patient_do_not_reply':
            do_not_reply.append(item)
        if reason == 'patient_bridge_known':
            patient_bridge_known.append(item)
    return {
        'total': len(phones),
        'by_reason': dict(sorted(by_reason.items())),
        'lead_exceptions_count': len(lead_exceptions),
        'lead_exceptions_sample': lead_exceptions[:20],
        'patient_do_not_reply_count': len(do_not_reply),
        'patient_do_not_reply_sample': do_not_reply[:20],
        'patient_bridge_known_count': len(patient_bridge_known),
    }


def lead_exclusion_collisions(exclusions: Dict[str, Any], leads: Dict[str, Any]) -> Dict[str, Any]:
    phones = exclusions.get('phones') if isinstance(exclusions.get('phones'), dict) else {}
    lead_map = leads.get('leads') if isinstance(leads.get('leads'), dict) else {}
    blocked_active = []
    explicit_exceptions = []
    suspicious = []
    for phone, lead_entry in lead_map.items():
        if not isinstance(lead_entry, dict) or not lead_entry.get('active'):
            continue
        ex = phones.get(phone)
        if not isinstance(ex, dict):
            continue
        reason = str(ex.get('reason') or '')
        source = str(ex.get('source') or '')
        item = {
            'phone': phone,
            'lead_source': lead_entry.get('source'),
            'exclusion_reason': reason,
            'exclusion_source': source,
            'name': ex.get('name'),
        }
        if reason.startswith('lead_exception') or source == 'tiaro_lead_exception':
            explicit_exceptions.append(item)
        else:
            blocked_active.append(item)
            if reason in ('patient_do_not_reply', 'patient_bridge_known'):
                suspicious.append(item)
    return {
        'active_leads_with_blocking_exclusion_count': len(blocked_active),
        'active_leads_with_blocking_exclusion_sample': blocked_active[:30],
        'explicit_lead_exceptions_count': len(explicit_exceptions),
        'explicit_lead_exceptions_sample': explicit_exceptions[:30],
        'patient_like_active_lead_collision_count': len(suspicious),
        'patient_like_active_lead_collision_sample': suspicious[:30],
    }


def manual_overrides(control: Dict[str, Any]) -> Dict[str, Any]:
    overrides = control.get('manual_overrides') if isinstance(control.get('manual_overrides'), dict) else {}
    now = time.time()
    active = []
    expired = []
    for phone, entry in overrides.items():
        if not isinstance(entry, dict):
            continue
        until = entry.get('until')
        item = {'phone': phone, 'until': until, 'note': entry.get('note'), 'owner': entry.get('owner'), 'set_at': entry.get('set_at')}
        try:
            if until is None or float(until) > now:
                active.append(item)
            else:
                expired.append(item)
        except Exception:
            active.append(item)
    return {'active_count': len(active), 'active_sample': active[:30], 'expired_count': len(expired), 'expired_sample': expired[:30]}


def main() -> int:
    parser = argparse.ArgumentParser(description='Read-only Clara/Z-API safety monitor')
    parser.add_argument('--base', default=str(DEFAULT_BASE))
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--no-http', action='store_true')
    args = parser.parse_args()

    base = Path(args.base)
    exclusions, err_ex = load_json(base / 'clara_exclusions.json', {'phones': {}})
    leads, err_leads = load_json(base / 'clara_leads_state.json', {'leads': {}})
    control, err_control = load_json(base / 'clara_control_state.json', {})
    event_state, err_event = load_json(base / 'clara_event_state.json', {'events': {}})

    health = None if args.no_http else http_json('http://127.0.0.1:8787/healthz')
    status = None if args.no_http else http_json('http://127.0.0.1:8787/admin/status')

    findings = []
    if health and not health.get('ok'):
        findings.append({'severity': 'HIGH', 'code': 'bridge_health_unavailable', 'detail': health})
    if control.get('paused') is True:
        findings.append({'severity': 'INFO', 'code': 'clara_global_pause_active', 'detail': {'paused_reason': control.get('paused_reason'), 'paused_by': control.get('paused_by'), 'paused_until': control.get('paused_until')}})
    collisions = lead_exclusion_collisions(exclusions, leads)
    if collisions['patient_like_active_lead_collision_count']:
        findings.append({'severity': 'MEDIUM', 'code': 'active_leads_blocked_as_patient_like', 'detail': {'count': collisions['patient_like_active_lead_collision_count']}})

    report = {
        'ok': True,
        'generated_at': int(time.time()),
        'mode': 'read_only_no_send_no_pause',
        'paths': {'base': str(base)},
        'read_errors': [e for e in [err_ex, err_leads, err_control, err_event] if e],
        'bridge_health': health,
        'bridge_admin_status': status,
        'exclusions': classify_exclusions(exclusions),
        'leads': {'total': len(leads.get('leads') or {}), 'active_total': sum(1 for v in (leads.get('leads') or {}).values() if isinstance(v, dict) and v.get('active'))},
        'events': {'total': len(event_state.get('events') or {})},
        'manual_overrides': manual_overrides(control),
        'collisions': collisions,
        'findings': findings,
        'next_actions': [
            'Revisar colisões active_leads_blocked_as_patient_like antes de liberar qualquer exceção.',
            'Manter patient_do_not_reply e patient_bridge_known bloqueados por padrão.',
            'Usar /admin/send apenas com dry_run:true em testes.',
        ],
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Clara Safety Monitor — {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(report['generated_at']))} UTC")
        print(f"Modo: {report['mode']}")
        print(f"Bridge health: {health}")
        print(f"Exclusões: {report['exclusions']['total']} | patient_do_not_reply: {report['exclusions']['patient_do_not_reply_count']} | patient_bridge_known: {report['exclusions']['patient_bridge_known_count']}")
        print(f"Leads ativos: {report['leads']['active_total']} | colisões paciente-like: {collisions['patient_like_active_lead_collision_count']}")
        print(f"Overrides manuais ativos: {report['manual_overrides']['active_count']}")
        for f in findings:
            print(f"- {f['severity']} {f['code']}: {f.get('detail')}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
