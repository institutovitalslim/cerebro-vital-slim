#!/usr/bin/env python3
import json, os, subprocess, sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path
from urllib.parse import quote_plus

ROOT = Path('/root/cerebro-vital-slim')
STATE = ROOT / 'ops/quarkclinic_confirmations/state/pending_confirmations.json'
LOGDIR = ROOT / 'ops/quarkclinic_confirmations/logs'
QC = '/root/.openclaw/workspace/snapshot/openclaw-home/workspace/skills/quarkclinic-api/scripts/quarkclinic_api.py'
ENV = '/root/.openclaw/workspace/ops/zapi_bridge/zapi_bridge.env'
TZ = ZoneInfo('America/Bahia')


def sh(cmd):
    return subprocess.check_output(cmd, text=True)


def load_env(path):
    env = {}
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def normalize_phone(raw):
    digits = ''.join(ch for ch in str(raw or '') if ch.isdigit())
    if not digits:
        return ''
    if digits.startswith('55'):
        return digits
    if len(digits) >= 10:
        return '55' + digits
    return digits


def main():
    now = datetime.now(TZ)
    target = (now + timedelta(days=1)).date()
    target_str = target.strftime('%d-%m-%Y')
    out = sh(['python3', QC, 'agendamentos', 'list', '--de', target_str, '--ate', target_str, '--json'])
    data = json.loads(out)
    items = data if isinstance(data, list) else data.get('items') or data.get('results') or []

    env = load_env(ENV)
    base = env.get('ZAPI_BASE_URL') or f"https://api.z-api.io/instances/{env['ZAPI_INSTANCE_ID']}/token/{env['ZAPI_TOKEN']}"
    client = env['ZAPI_CLIENT_TOKEN']

    pending = {'generatedAt': now.isoformat(), 'date': target_str, 'items': []}
    sent = []
    for appt in items:
        status = str(appt.get('status') or '').lower()
        if 'cancel' in status:
            continue
        dt = appt.get('dataHoraInicio') or appt.get('data_inicio') or appt.get('dataHora') or ''
        if not dt:
            continue
        try:
            hhmm = dt[11:16]
        except Exception:
            continue
        if hhmm >= '12:00':
            continue
        paciente = appt.get('paciente') or {}
        nome = paciente.get('nome') or appt.get('pacienteNome') or 'paciente'
        phone = normalize_phone((paciente.get('telefone') or paciente.get('celular') or appt.get('telefone') or appt.get('whatsapp') or ''))
        if not phone:
            continue
        ag_id = appt.get('id') or appt.get('agendamentoId')
        msg = (
            f"Oi, {nome.split()[0]}! 😊 Passando para confirmar sua consulta de amanhã às {hhmm} no Instituto Vital Slim.\n\n"
            "Pode me responder com uma destas opções:\n"
            "1) Confirmo\n"
            "2) Preciso remarcar\n"
            "3) Não vou conseguir\n\n"
            "Fico à disposição."
        )
        payload = json.dumps({'phone': phone, 'message': msg})
        cmd = [
            'curl','-sS','-X','POST', f'{base}/send-text',
            '-H', f'Client-Token: {client}',
            '-H', 'Content-Type: application/json',
            '-d', payload
        ]
        raw = subprocess.check_output(cmd, text=True)
        resp = json.loads(raw)
        if not resp.get('messageId'):
            raise RuntimeError(f'Falha envio para {phone}: {raw}')
        item = {
            'phone': phone,
            'nome': nome,
            'agendamentoId': ag_id,
            'dataHoraInicio': dt,
            'messageId': resp.get('messageId'),
            'status': 'sent'
        }
        pending['items'].append(item)
        sent.append(item)

    STATE.write_text(json.dumps(pending, ensure_ascii=False, indent=2))
    LOGDIR.mkdir(parents=True, exist_ok=True)
    (LOGDIR / f'send_{target_str}.json').write_text(json.dumps({'sent': sent}, ensure_ascii=False, indent=2))
    print(json.dumps({'date': target_str, 'sentCount': len(sent)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
