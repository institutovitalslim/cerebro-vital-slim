#!/usr/bin/env python3
"""Snapshot diário Hostinger IVS.
Cria snapshot da VPS principal e valida a criação sem expor segredo.

Validações possíveis pela API Hostinger:
- VPS alvo existe e está running.
- Ação de criação chegou em success.
- Snapshot retornado existe.
- created_at do snapshot é posterior ao início da execução.
- expires_at está no futuro.
- restore_time está presente e coerente.

Observação: a API não permite validar conteúdo interno do snapshot sem restore; validação de qualidade aqui é operacional/API, não restore destrutivo.
"""
import argparse, datetime as dt, json, os, pathlib, re, subprocess, sys, time
from typing import Any, Dict
import requests

VM_ID = int(os.getenv('HOSTINGER_VPS_ID', '1429339'))
EXPECTED_IP = os.getenv('HOSTINGER_EXPECTED_IPV4', '187.77.58.193')
BASE = os.getenv('HOSTINGER_API_BASE', 'https://developers.hostinger.com').rstrip('/')
ENV_PATH = pathlib.Path('/root/.openclaw/.env.runtime')
OP_SERVICE_ENV_PATH = pathlib.Path('/root/.openclaw/.op.service-account.env')
LOG_DIR = pathlib.Path('/root/cerebro-vital-slim/logs/hostinger-snapshots')


def utcnow():
    return dt.datetime.now(dt.timezone.utc)


def iso(d: dt.datetime):
    return d.astimezone(dt.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def parse_ts(s: str):
    return dt.datetime.fromisoformat(s.replace('Z', '+00:00'))


def load_shell_env_file(path: pathlib.Path):
    """Carrega pares KEY=VALUE simples sem imprimir segredos."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        raw = line.strip()
        if not raw or raw.startswith('#') or '=' not in raw:
            continue
        key, value = raw.split('=', 1)
        key = key.strip().removeprefix('export ').strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def load_env_token():
    tok = os.getenv('HOSTINGER_API_TOKEN')
    if tok:
        return tok.strip()
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text().splitlines():
            if line.startswith('HOSTINGER_API_TOKEN='):
                return line.split('=', 1)[1].strip().strip('"').strip("'")
    # Fallback seguro: 1Password service account, sem imprimir segredo.
    # O cron de root não tem sessão interativa do `op`, então carregamos apenas
    # o service-account env governado antes de chamar `op read`.
    load_shell_env_file(OP_SERVICE_ENV_PATH)
    try:
        out = subprocess.check_output(['op', 'read', 'op://openclaw/API Hostinger/notesPlain'], text=True, timeout=20)
        m = re.search(r'chave api:\s*([^\s]+)', out)
        return (m.group(1) if m else out.strip())
    except Exception:
        raise SystemExit('HOSTINGER_API_TOKEN não configurado e 1Password indisponível')


def request(method: str, path: str, token: str, **kwargs):
    headers = {
        'Authorization': 'Bearer ' + token,
        'Accept': 'application/json',
        'User-Agent': 'OpenClaw-IVS-Maria/1.0',
    }
    if 'json' in kwargs:
        headers['Content-Type'] = 'application/json'
    r = requests.request(method, BASE + path, headers=headers, timeout=45, **kwargs)
    try:
        body = r.json()
    except Exception:
        body = {'raw': r.text[:2000]}
    if not r.ok:
        raise RuntimeError(f'{method} {path} falhou: HTTP {r.status_code} {body}')
    return body


def get_vm(token):
    vm = request('GET', f'/api/vps/v1/virtual-machines/{VM_ID}', token)
    return vm


def get_snapshot(token):
    return request('GET', f'/api/vps/v1/virtual-machines/{VM_ID}/snapshot', token)


def wait_action(token, action_id: int, max_seconds=300):
    deadline = time.time() + max_seconds
    last = None
    while time.time() < deadline:
        last = request('GET', f'/api/vps/v1/virtual-machines/{VM_ID}/actions/{action_id}', token)
        if last.get('state') in {'success', 'failed', 'error', 'canceled', 'cancelled'}:
            return last
        time.sleep(10)
    return last or {'state': 'timeout', 'id': action_id}


def validate_snapshot(token, started_at=None, require_fresh=False):
    checks = []
    vm = get_vm(token)
    ips = [x.get('address') for x in vm.get('ipv4', [])]
    checks.append({'name': 'vps_found', 'ok': bool(vm.get('id') == VM_ID), 'detail': vm.get('hostname')})
    checks.append({'name': 'vps_running', 'ok': vm.get('state') == 'running', 'detail': vm.get('state')})
    checks.append({'name': 'expected_ip', 'ok': EXPECTED_IP in ips, 'detail': ips})

    snap = get_snapshot(token)
    created = parse_ts(snap['created_at']) if snap.get('created_at') else None
    expires = parse_ts(snap['expires_at']) if snap.get('expires_at') else None
    now = utcnow()
    checks.append({'name': 'snapshot_exists', 'ok': bool(snap.get('id') and created), 'detail': snap.get('id')})
    checks.append({'name': 'snapshot_not_expired', 'ok': bool(expires and expires > now), 'detail': snap.get('expires_at')})
    checks.append({'name': 'restore_time_present', 'ok': isinstance(snap.get('restore_time'), int) and snap.get('restore_time') > 0, 'detail': snap.get('restore_time')})
    if require_fresh and started_at:
        checks.append({'name': 'snapshot_is_fresh', 'ok': bool(created and created >= started_at - dt.timedelta(seconds=5)), 'detail': snap.get('created_at')})

    ok = all(c['ok'] for c in checks)
    return ok, checks, vm, snap


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--validate-only', action='store_true')
    ap.add_argument('--wait-seconds', type=int, default=420)
    args = ap.parse_args()

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    token = load_env_token()
    started = utcnow()
    result: Dict[str, Any] = {
        'started_at': iso(started),
        'mode': 'validate-only' if args.validate_only else 'create-snapshot',
        'vm_id': VM_ID,
        'expected_ipv4': EXPECTED_IP,
        'base': BASE,
    }

    try:
        if args.validate_only:
            ok, checks, vm, snap = validate_snapshot(token, require_fresh=False)
            result.update({'status': 'success' if ok else 'failed', 'checks': checks, 'snapshot': snap, 'vm': {'id': vm.get('id'), 'hostname': vm.get('hostname'), 'state': vm.get('state')}})
        else:
            try:
                action = request('POST', f'/api/vps/v1/virtual-machines/{VM_ID}/snapshot', token)
                result['action'] = action
                action_id = action.get('id')
                if action_id is None:
                    raise RuntimeError(f'POST snapshot não retornou action id: {action}')
                final_action = wait_action(token, int(action_id), max_seconds=args.wait_seconds)
                result['final_action'] = final_action
                ok, checks, vm, snap = validate_snapshot(token, started_at=started, require_fresh=True)
                action_ok = final_action.get('state') == 'success'
                checks.insert(0, {'name': 'snapshot_create_action_success', 'ok': action_ok, 'detail': final_action.get('state')})
                ok = ok and action_ok
                result.update({'status': 'success' if ok else 'failed', 'checks': checks, 'snapshot': snap, 'vm': {'id': vm.get('id'), 'hostname': vm.get('hostname'), 'state': vm.get('state')}})
            except RuntimeError as e:
                # A Hostinger às vezes responde 403 "VPS has unfinished actions" exatamente
                # quando outra ação de snapshot já foi aceita e ainda está finalizando.
                # Nesse caso, não devemos marcar o cron como falha sem verificar se um
                # snapshot fresco apareceu logo depois do horário de início.
                msg = str(e)
                if 'unfinished actions' not in msg.lower() and 'VPS:2047' not in msg:
                    raise
                result['unfinished_action_error'] = msg
                deadline = time.time() + args.wait_seconds
                last = None
                while time.time() < deadline:
                    ok, checks, vm, snap = validate_snapshot(token, started_at=started, require_fresh=True)
                    last = {'ok': ok, 'checks': checks, 'snapshot': snap, 'vm': vm}
                    if ok:
                        checks.insert(0, {'name': 'snapshot_create_action_or_existing_fresh', 'ok': True, 'detail': 'hostinger_unfinished_action_but_fresh_snapshot_validated'})
                        result.update({'status': 'success', 'checks': checks, 'snapshot': snap, 'vm': {'id': vm.get('id'), 'hostname': vm.get('hostname'), 'state': vm.get('state')}})
                        break
                    time.sleep(20)
                else:
                    if last:
                        checks = last['checks']
                        checks.insert(0, {'name': 'snapshot_create_action_or_existing_fresh', 'ok': False, 'detail': 'unfinished_actions_and_no_fresh_snapshot'})
                        vm = last['vm']; snap = last['snapshot']
                        result.update({'status': 'failed', 'checks': checks, 'snapshot': snap, 'vm': {'id': vm.get('id'), 'hostname': vm.get('hostname'), 'state': vm.get('state')}})
                    else:
                        raise
    except Exception as e:
        result.update({'status': 'failed', 'error': str(e)})

    result['finished_at'] = iso(utcnow())
    prefix = 'validate' if args.validate_only else 'snapshot'
    out = LOG_DIR / f"{prefix}-{utcnow().strftime('%Y%m%d-%H%M%SZ')}.json"
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    out.write_text(payload)

    # latest.json deve continuar sendo prova do último snapshot CRIADO.
    # Validações manuais/read-only usam latest-validate.json para não apagar
    # evidência de criação que Tiaro/Maria precisam auditar depois.
    latest_name = 'latest-validate.json' if args.validate_only else 'latest.json'
    latest = LOG_DIR / latest_name
    latest.write_text(payload)

    print(json.dumps({
        'status': result['status'],
        'mode': result['mode'],
        'vm_id': VM_ID,
        'snapshot_created_at': result.get('snapshot', {}).get('created_at'),
        'snapshot_expires_at': result.get('snapshot', {}).get('expires_at'),
        'log': str(out),
        'latest': str(latest),
        'failed_checks': [c for c in result.get('checks', []) if not c.get('ok')],
    }, ensure_ascii=False, indent=2))
    sys.exit(0 if result['status'] == 'success' else 1)

if __name__ == '__main__':
    main()
