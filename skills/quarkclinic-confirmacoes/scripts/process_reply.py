#!/usr/bin/env python3
import json, os, re, subprocess, sys
from pathlib import Path
from urllib.parse import quote_plus

ROOT = Path('/root/cerebro-vital-slim')
STATE = ROOT / 'ops/quarkclinic_confirmations/state/pending_confirmations.json'
ENV = '/root/.openclaw/workspace/ops/zapi_bridge/zapi_bridge.env'


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
    if digits.startswith('55'):
        return digits
    if len(digits) >= 10:
        return '55' + digits
    return digits


def classify(text):
    t = (text or '').strip().lower()
    if any(x in t for x in ['confirmo', 'confirmada', 'confirmado', 'ok', 'certo', 'estarei', 'vou sim', 'sim']):
        return 'confirm'
    if any(x in t for x in ['remar', 'reagend', 'outro horário', 'outro horario']):
        return 'reschedule'
    if any(x in t for x in ['não vou', 'nao vou', 'cancel', 'não consigo', 'nao consigo', 'desmarcar']):
        return 'cancel'
    return 'unknown'


def main():
    if len(sys.argv) < 3:
        raise SystemExit('uso: process_reply.py <phone> <text>')
    phone = normalize_phone(sys.argv[1])
    text = sys.argv[2]
    if not STATE.exists():
        print(json.dumps({'matched': False, 'reason': 'state_missing'}))
        return
    state = json.loads(STATE.read_text())
    items = state.get('items', [])
    candidates = [x for x in items if x.get('phone') == phone and x.get('status') == 'sent']
    if not candidates:
        print(json.dumps({'matched': False, 'reason': 'no_pending_for_phone'}))
        return
    item = sorted(candidates, key=lambda x: x.get('dataHoraInicio',''))[0]
    decision = classify(text)
    ag_id = item['agendamentoId']
    env = load_env(ENV)
    base = env.get('ZAPI_BASE_URL') or f"https://api.z-api.io/instances/{env['ZAPI_INSTANCE_ID']}/token/{env['ZAPI_TOKEN']}"
    client = env['ZAPI_CLIENT_TOKEN']

    client = '/root/.openclaw/workspace/snapshot/openclaw-home/workspace/skills/quarkclinic-api/scripts/quarkclinic_api.py'

    if decision == 'confirm':
        cmd = ['python3', client, 'PATCH', f'/v1/agendamentos/{ag_id}/confirmar', '--write-ok']
        raw = subprocess.check_output(cmd, text=True)
        item['status'] = 'confirmed'
        reply = 'Perfeito 😊 Sua consulta ficou confirmada. Qualquer coisa, estou por aqui.'
    elif decision == 'cancel':
        cmd = ['python3', client, 'PATCH', f'/v1/agendamentos/{ag_id}/cancelar', '--query', f'motivo={quote_plus("Cancelado pelo paciente via WhatsApp")}', '--write-ok']
        raw = subprocess.check_output(cmd, text=True)
        item['status'] = 'cancelled'
        reply = 'Tudo bem 😊 Seu atendimento foi cancelado por aqui. Se quiser, eu posso te ajudar a remarcar.'
    elif decision == 'reschedule':
        item['status'] = 'needs_reschedule'
        raw = '{}'
        reply = 'Claro 😊 Eu posso te ajudar a remarcar. Me diz, por favor, qual período costuma ser melhor pra vc: manhã ou tarde?'
    else:
        print(json.dumps({'matched': True, 'decision': 'unknown', 'updated': False}))
        return

    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2))
    payload = json.dumps({'phone': phone, 'message': reply})
    send = subprocess.check_output(['curl','-sS','-X','POST',f'{base}/send-text','-H',f'Client-Token: {client}','-H','Content-Type: application/json','-d',payload], text=True)
    print(json.dumps({'matched': True, 'decision': decision, 'agendamentoId': ag_id, 'quarkclinic': raw, 'reply': send}, ensure_ascii=False))

if __name__ == '__main__':
    main()
