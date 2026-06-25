#!/usr/bin/env python3
"""Daily Clara/Z-API audit with delta detection.

Read-only. Generates an exception-first operational report and stores a compact
snapshot to detect changes between runs.
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

SKILL_DIR = Path('/root/.openclaw/workspace/skills/ivs-agent-operating-layer')
MONITOR = SKILL_DIR / 'scripts' / 'clara_safety_monitor.py'
DEFAULT_STATE = Path('/root/.openclaw/workspace/ops/zapi_bridge/clara_safety_audit_state.json')
DEFAULT_OUT = Path('/root/deliverables/clara-daily-audit-latest.md')
CONTEXT_COMPRESSOR = Path('/root/cerebro-vital-slim/tools/ivs-context-compressor/ivs_context_compressor.py')


def run_monitor() -> Dict[str, Any]:
    raw = subprocess.check_output([sys.executable, str(MONITOR), '--json'], text=True)
    return json.loads(raw)


def load_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return default


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def compact_snapshot(report: Dict[str, Any]) -> Dict[str, Any]:
    admin_body = (report.get('bridge_admin_status') or {}).get('body') or {}
    collisions = report.get('collisions') or {}
    manual = report.get('manual_overrides') or {}
    exclusions = report.get('exclusions') or {}
    return {
        'generated_at': report.get('generated_at'),
        'bridge_health_ok': (report.get('bridge_health') or {}).get('ok') is True,
        'paused': admin_body.get('paused') is True,
        'paused_reason': admin_body.get('paused_reason'),
        'patient_like_collision_count': collisions.get('patient_like_active_lead_collision_count') or 0,
        'collision_phones': sorted([str(x.get('phone')) for x in collisions.get('patient_like_active_lead_collision_sample') or [] if x.get('phone')]),
        'manual_override_active_count': manual.get('active_count') or 0,
        'manual_override_phones': sorted([str(x.get('phone')) for x in manual.get('active_sample') or [] if x.get('phone')]),
        'exclusions_total': exclusions.get('total') or 0,
        'patient_do_not_reply_count': exclusions.get('patient_do_not_reply_count') or 0,
        'patient_bridge_known_count': exclusions.get('patient_bridge_known_count') or 0,
        'findings_codes': sorted([str(f.get('code')) for f in report.get('findings') or [] if f.get('code')]),
    }


def diff(prev: Dict[str, Any], cur: Dict[str, Any]) -> List[str]:
    if not prev:
        return ['Primeira execução: baseline criado.']
    lines: List[str] = []
    checks = [
        ('bridge_health_ok', 'Saúde do bridge'),
        ('paused', 'Pausa global Clara'),
        ('patient_like_collision_count', 'Colisões lead + paciente-like'),
        ('manual_override_active_count', 'Overrides manuais ativos'),
        ('exclusions_total', 'Exclusões totais'),
        ('patient_do_not_reply_count', 'patient_do_not_reply'),
        ('patient_bridge_known_count', 'patient_bridge_known'),
    ]
    for key, label in checks:
        if prev.get(key) != cur.get(key):
            lines.append(f'{label}: {prev.get(key)} → {cur.get(key)}')
    prev_collisions = set(prev.get('collision_phones') or [])
    cur_collisions = set(cur.get('collision_phones') or [])
    new_collisions = sorted(cur_collisions - prev_collisions)
    resolved_collisions = sorted(prev_collisions - cur_collisions)
    if new_collisions:
        lines.append('Novas colisões: ' + ', '.join(new_collisions[:20]))
    if resolved_collisions:
        lines.append('Colisões resolvidas: ' + ', '.join(resolved_collisions[:20]))
    prev_overrides = set(prev.get('manual_override_phones') or [])
    cur_overrides = set(cur.get('manual_override_phones') or [])
    if cur_overrides - prev_overrides:
        lines.append('Novos overrides manuais: ' + ', '.join(sorted(cur_overrides - prev_overrides)[:20]))
    if prev_overrides - cur_overrides:
        lines.append('Overrides encerrados: ' + ', '.join(sorted(prev_overrides - cur_overrides)[:20]))
    return lines or ['Sem mudanças relevantes desde a última execução.']


def severity(report: Dict[str, Any], changes: List[str]) -> str:
    health_ok = (report.get('bridge_health') or {}).get('ok') is True
    admin_body = (report.get('bridge_admin_status') or {}).get('body') or {}
    if not health_ok:
        return 'ALTA'
    if admin_body.get('paused') is True:
        return 'MÉDIA'
    for c in changes:
        if c.startswith('Novas colisões') or c.startswith('Overrides') or c.startswith('Novos overrides'):
            return 'MÉDIA'
    findings = report.get('findings') or []
    if any(str(f.get('severity')).upper() in ('HIGH', 'CRITICAL') for f in findings):
        return 'ALTA'
    if any(str(f.get('severity')).upper() == 'MEDIUM' for f in findings):
        return 'BAIXA'
    return 'OK'


def render_md(report: Dict[str, Any], cur: Dict[str, Any], changes: List[str], sev: str) -> str:
    ts = time.strftime('%d/%m/%Y %H:%M UTC', time.gmtime(report.get('generated_at') or time.time()))
    admin_body = (report.get('bridge_admin_status') or {}).get('body') or {}
    lines = [
        '# Auditoria diária Clara/Z-API — IVS',
        '',
        f'- Gerado em: {ts}',
        f'- Severidade operacional: **{sev}**',
        f'- Modo: read-only; sem envio WhatsApp; sem pausa/despausa.',
        '',
        '## Indicadores',
        f'- Bridge saudável: {cur.get("bridge_health_ok")}',
        f'- Clara pausada: {cur.get("paused")} ({admin_body.get("paused_reason") or "sem motivo"})',
        f'- Exclusões totais: {cur.get("exclusions_total")}',
        f'- patient_do_not_reply: {cur.get("patient_do_not_reply_count")}',
        f'- patient_bridge_known: {cur.get("patient_bridge_known_count")}',
        f'- Colisões lead + paciente-like: {cur.get("patient_like_collision_count")}',
        f'- Overrides manuais ativos: {cur.get("manual_override_active_count")}',
        '',
        '## Mudanças desde a última execução',
    ]
    lines.extend([f'- {c}' for c in changes])
    lines += ['', '## Próxima ação operacional']
    if sev == 'ALTA':
        lines.append('- Verificar bridge/logs imediatamente antes de qualquer follow-up ativo.')
    elif sev == 'MÉDIA':
        lines.append('- Revisar exceções/overrides antes de liberar qualquer envio ativo.')
    else:
        lines.append('- Sem ação imediata. Manter monitoramento conservador.')
    lines += ['', '## Regra mantida', '- Paciente, `do_not_reply` e `patient_bridge_known` seguem bloqueados por padrão.']
    return '\n'.join(lines) + '\n'


def compress_context(path: Path, kind: str = 'clara-log') -> Dict[str, Any]:
    """Optional read-only post-processing with IVS Context Compressor.

    Failure here must never fail the daily audit: this is an observability aid,
    not a production dependency in Clara's path.
    """
    if not CONTEXT_COMPRESSOR.exists():
        return {'ok': False, 'error': f'compressor not found: {CONTEXT_COMPRESSOR}'}
    try:
        raw = subprocess.check_output(
            [
                sys.executable,
                str(CONTEXT_COMPRESSOR),
                '--input',
                str(path),
                '--type',
                kind,
                '--format',
                'json',
            ],
            text=True,
            stderr=subprocess.STDOUT,
        )
        payload = json.loads(raw)
        return {
            'ok': bool(payload.get('ok')),
            'sha256': payload.get('sha256'),
            'outputs': payload.get('outputs'),
            'evidence': payload.get('evidence'),
            'critical_line_count': (payload.get('summary') or {}).get('critical_line_count'),
            'redactions': (payload.get('summary') or {}).get('redactions'),
        }
    except Exception as exc:
        return {'ok': False, 'error': str(exc)[:500]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--state', default=str(DEFAULT_STATE))
    ap.add_argument('--out', default=str(DEFAULT_OUT))
    ap.add_argument('--no-save', action='store_true')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--compress-context', action='store_true', help='Run IVS Context Compressor on the generated report (read-only, optional).')
    args = ap.parse_args()

    report = run_monitor()
    cur = compact_snapshot(report)
    state_path = Path(args.state)
    prev = load_json(state_path, {})
    changes = diff(prev.get('snapshot') if isinstance(prev, dict) else {}, cur)
    sev = severity(report, changes)
    md = render_md(report, cur, changes, sev)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding='utf-8')
    compressed_context = compress_context(out) if args.compress_context else None
    if not args.no_save:
        save_json(state_path, {'snapshot': cur, 'last_report': str(out), 'updated_at': int(time.time())})
    result = {'ok': True, 'severity': sev, 'changes': changes, 'snapshot': cur, 'report': str(out), 'state': str(state_path), 'saved': not args.no_save}
    if compressed_context is not None:
        result['compressed_context'] = compressed_context
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(md)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
