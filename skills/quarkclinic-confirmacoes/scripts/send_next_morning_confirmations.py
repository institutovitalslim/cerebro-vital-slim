#!/usr/bin/env python3
import argparse, json, os, subprocess, sys
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


def describe_target_day(now_date, target_date):
    if target_date == now_date:
        return 'hoje'
    if target_date == now_date + timedelta(days=1):
        return 'amanhã'
    return f"no dia {target_date.strftime('%d/%m')}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['next-morning', 'same-day-afternoon'], default='next-morning')
    args = parser.parse_args()

    now = datetime.now(TZ)
    if args.mode == 'same-day-afternoon':
        target = now.date()
        turno = 'afternoon'
    else:
        target = (now + timedelta(days=1)).date()
        turno = 'morning'
    target_str = target.strftime('%d-%m-%Y')
    target_day_text = describe_target_day(now.date(), target)
    out = sh(['python3', QC, 'GET', '/v1/agendamentos', '--query', f'data_agendamento_inicio={target_str}', '--query', f'data_agendamento_fim={target_str}'])
    data = json.loads(out)
    resp = data.get('response') or {}
    items = resp.get('response') if isinstance(resp, dict) else (data.get('items') or data.get('results') or [])

    env = load_env(ENV)
    base = env.get('ZAPI_BASE_URL') or f"https://api.z-api.io/instances/{env['ZAPI_INSTANCE_ID']}/token/{env['ZAPI_TOKEN']}"
    client = env['ZAPI_CLIENT_TOKEN']

    pending = {'generatedAt': now.isoformat(), 'date': target_str, 'items': []}
    sent = []
    for appt in items:
        status = str(appt.get('status') or appt.get('statusMarcacao') or '').lower()
        if 'cancel' in status:
            continue
        dt = appt.get('dataHoraInicio') or appt.get('data_inicio') or appt.get('dataHora') or (f"{appt.get('dataAgendamento','')}T{appt.get('horaAgendamento','')}" if appt.get('dataAgendamento') and appt.get('horaAgendamento') else '')
        if not dt:
            continue
        try:
            hhmm = dt[11:16]
        except Exception:
            continue
        if turno == 'morning' and hhmm >= '12:00':
            continue
        if turno == 'afternoon' and hhmm < '12:00':
            continue
        paciente = appt.get('paciente') or {}
        nome = paciente.get('nome') or appt.get('pacienteNome') or appt.get('nomePaciente') or 'paciente'
        phone = normalize_phone((paciente.get('telefone') or paciente.get('celular') or appt.get('telefoneComDDI') or appt.get('telefone') or appt.get('whatsapp') or ''))
        if not phone:
            continue
        ag_id = appt.get('id') or appt.get('agendamentoId')
        procedimento = appt.get('procedimento') or {}
        procedimento_nome = (procedimento.get('nome') or appt.get('procedimentoNome') or 'atendimento').strip()
        primeiro_nome = nome.split()[0].title()
        msg = (
            f"Oi, {primeiro_nome}! Tudo bem? 😊\n\n"
            f"Estou passando para confirmar seu atendimento de {procedimento_nome} {target_day_text}, às {hhmm}, aqui no Instituto Vital Slim.\n\n"
            "Se estiver tudo certo, pode me responder com *Confirmo*.\n"
            "Se precisar, você também pode me dizer *Quero remarcar* ou *Não vou conseguir*."
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
        item['turno'] = turno
        pending['items'].append(item)
        sent.append(item)

    STATE.write_text(json.dumps(pending, ensure_ascii=False, indent=2))
    LOGDIR.mkdir(parents=True, exist_ok=True)
    (LOGDIR / f'send_{target_str}.json').write_text(json.dumps({'sent': sent}, ensure_ascii=False, indent=2))
    print(json.dumps({'date': target_str, 'mode': args.mode, 'sentCount': len(sent)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
