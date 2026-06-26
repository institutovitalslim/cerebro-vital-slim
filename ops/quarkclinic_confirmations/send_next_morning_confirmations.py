#!/usr/bin/env python3
import argparse, json, subprocess
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path

ROOT = Path('/root/cerebro-vital-slim')
STATE = ROOT / 'ops/quarkclinic_confirmations/state/pending_confirmations.json'
LOGDIR = ROOT / 'ops/quarkclinic_confirmations/logs'
QC = '/root/.openclaw/workspace/snapshot/openclaw-home/workspace/snapshot/openclaw-home/workspace/skills/quarkclinic-api/scripts/quarkclinic_api.py'
ENV = '/root/.openclaw/workspace/ops/zapi_bridge/zapi_bridge.env'
CLARA_LEADS_STATE = Path('/root/.openclaw/workspace/ops/zapi_bridge/clara_leads_state.json')
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


def phone_variants(raw):
    phone = normalize_phone(raw)
    variants = set()
    if not phone:
        return variants
    variants.add(phone)
    if phone.startswith('55') and len(phone) >= 12:
        ddi = phone[:2]
        ddd = phone[2:4]
        rest = phone[4:]
        if len(rest) == 9 and rest.startswith('9'):
            variants.add(ddi + ddd + rest[1:])
        elif len(rest) == 8:
            variants.add(ddi + ddd + '9' + rest)
    return {v for v in variants if v}


def load_clara_leads_state(path=CLARA_LEADS_STATE):
    if not Path(path).exists():
        return {}
    try:
        data = json.loads(Path(path).read_text())
    except Exception:
        return {}
    leads = data.get('leads') if isinstance(data, dict) else None
    return leads if isinstance(leads, dict) else {}


def collect_phone_candidates(appt):
    """Coleta telefones do agendamento e paciente preservando a ordem original do cadastro.

    Regra de negócio: confirmação deve ir para o telefone em que o paciente já fala
    com a clínica. A ordem do cadastro serve apenas como fallback quando nenhum
    candidato tiver histórico na Clara/Z-API.
    """
    paciente = appt.get('paciente') or {}
    ordered_raw = [
        paciente.get('telefone'),
        paciente.get('celular'),
        paciente.get('whatsapp'),
        appt.get('telefoneComDDI'),
        appt.get('telefone'),
        appt.get('celular'),
        appt.get('whatsapp'),
        appt.get('telefonePaciente'),
        appt.get('celularPaciente'),
        appt.get('whatsappPaciente'),
    ]

    def walk(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                lk = str(k).lower()
                if any(tok in lk for tok in ('telefone', 'celular', 'whatsapp', 'phone')):
                    if isinstance(v, (str, int, float)):
                        ordered_raw.append(v)
                    else:
                        walk(v)
                elif isinstance(v, (dict, list, tuple)):
                    walk(v)
        elif isinstance(obj, (list, tuple)):
            for v in obj:
                walk(v)

    walk(appt)

    candidates = []
    seen = set()
    for raw in ordered_raw:
        phone = normalize_phone(raw)
        # Telefones BR com DDI costumam ter 12 ou 13 dígitos. Evita capturar IDs.
        if not phone or len(phone) < 12 or len(phone) > 13:
            continue
        if phone not in seen:
            candidates.append(phone)
            seen.add(phone)
    return candidates


def clara_history_score(phone, leads_state):
    """Pontua evidência de conversa real/relacionamento no WhatsApp da clínica."""
    best_score = 0
    best_key = ''
    best_entry = None
    for variant in phone_variants(phone):
        for key in (variant, f'{variant}@c.us'):
            entry = leads_state.get(key)
            if not isinstance(entry, dict):
                continue
            score = 0
            inbound_count = int(entry.get('inbound_count') or 0)
            reply_count = int(entry.get('reply_count') or 0)
            if inbound_count > 0:
                score += 1000 + min(inbound_count, 100)
            if reply_count > 0:
                score += 200 + min(reply_count, 50)
            if entry.get('last_inbound_at'):
                score += 100
            if entry.get('last_reply_at'):
                score += 80
            if entry.get('active'):
                score += 20
            if score > best_score:
                best_score = score
                best_key = key
                best_entry = entry
    return best_score, best_key, best_entry


def choose_confirmation_phone(appt, leads_state=None):
    """Escolhe telefone de confirmação.

    Prioridade canônica definida por Tiaro em 2026-06-26:
    confirmações de atendimento devem ser enviadas ao telefone em que o paciente
    já fala com a clínica/Clara. Se houver mais de um número no cadastro, não usar
    automaticamente o segundo número; escolher o candidato com histórico Z-API.
    """
    leads_state = leads_state if leads_state is not None else load_clara_leads_state()
    candidates = collect_phone_candidates(appt)
    scored = []
    for idx, phone in enumerate(candidates):
        score, matched_key, entry = clara_history_score(phone, leads_state)
        scored.append({
            'phone': phone,
            'score': score,
            'matched_key': matched_key,
            'inbound_count': int((entry or {}).get('inbound_count') or 0),
            'last_inbound_at': (entry or {}).get('last_inbound_at'),
            'last_reply_at': (entry or {}).get('last_reply_at'),
            'active': bool((entry or {}).get('active')),
            'fallback_order': idx,
        })
    if not scored:
        return '', {'reason': 'no_phone_candidates', 'candidates': []}
    with_history = [s for s in scored if s['score'] > 0]
    if with_history:
        chosen = sorted(with_history, key=lambda s: (s['score'], s.get('last_inbound_at') or 0, -s['fallback_order']), reverse=True)[0]
        reason = 'matched_clara_whatsapp_history'
    else:
        chosen = scored[0]
        reason = 'fallback_quarkclinic_order_no_clara_history'
    return chosen['phone'], {'reason': reason, 'chosen': chosen, 'candidates': scored}


def mask_phone(phone):
    p = normalize_phone(phone)
    if len(p) <= 4:
        return '***'
    return f'{p[:4]}*****{p[-4:]}'


def describe_target_day(now_date, target_date):
    if target_date == now_date:
        return 'hoje'
    if target_date == now_date + timedelta(days=1):
        return 'amanhã'
    return f"no dia {target_date.strftime('%d/%m')}"


def parse_state_date(value):
    for fmt in ('%d-%m-%YT%H:%M', '%Y-%m-%dT%H:%M', '%d-%m-%Y', '%Y-%m-%d'):
        try:
            return datetime.strptime(value, fmt).date()
        except Exception:
            pass
    return None


def load_existing_pending(now_date):
    if not STATE.exists():
        return {}
    try:
        data = json.loads(STATE.read_text())
    except Exception:
        return {}
    keep = {}
    for item in data.get('items', []):
        status = item.get('status')
        item_date = parse_state_date(item.get('dataHoraInicio', ''))
        if status in {'confirmed', 'cancelled'}:
            continue
        if item_date and item_date < now_date - timedelta(days=1):
            continue
        keep[str(item.get('agendamentoId'))] = item
    return keep


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['next-morning', 'same-day-afternoon'], default='next-morning')
    parser.add_argument('--dry-run', action='store_true', help='não envia WhatsApp; apenas calcula destinatários e mensagens')
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
    leads_state = load_clara_leads_state()

    pending_by_id = load_existing_pending(now.date())
    sent = []
    skipped = []
    dry_run_items = []
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
        phone, phone_selection = choose_confirmation_phone(appt, leads_state)
        ag_id = appt.get('id') or appt.get('agendamentoId')
        if not phone:
            skipped.append({'agendamentoId': ag_id, 'nome': nome, 'reason': 'no_phone', 'phoneSelection': phone_selection})
            continue
        procedimento = appt.get('procedimento') or {}
        procedimento_nome = (procedimento.get('nome') or appt.get('procedimentoNome') or 'atendimento').strip()
        primeiro_nome = nome.split()[0].title()
        msg = (
            f"Oi, {primeiro_nome}! Tudo bem? 😊\n\n"
            f"Estou passando para confirmar seu atendimento de {procedimento_nome} {target_day_text}, às {hhmm}, aqui no Instituto Vital Slim.\n\n"
            "Se estiver tudo certo, pode me responder com *Confirmo*.\n"
            "Se precisar, você também pode me dizer *Quero remarcar* ou *Não vou conseguir*."
        )
        if args.dry_run:
            dry_run_items.append({
                'phoneMasked': mask_phone(phone),
                'nome': nome,
                'agendamentoId': ag_id,
                'dataHoraInicio': dt,
                'phoneSelection': phone_selection,
                'messagePreview': msg[:220],
            })
            continue
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
            raise RuntimeError(f'Falha envio para {mask_phone(phone)}: {raw}')
        item = {
            'phone': phone,
            'nome': nome,
            'agendamentoId': ag_id,
            'dataHoraInicio': dt,
            'messageId': resp.get('messageId'),
            'status': 'sent',
            'phoneSelection': phone_selection,
        }
        item['turno'] = turno
        pending_by_id[str(ag_id)] = item
        sent.append(item)

    LOGDIR.mkdir(parents=True, exist_ok=True)
    if args.dry_run:
        out_payload = {'date': target_str, 'mode': args.mode, 'dryRun': True, 'candidateCount': len(dry_run_items), 'items': dry_run_items, 'skipped': skipped}
        (LOGDIR / f'dry_run_{target_str}_{args.mode}.json').write_text(json.dumps(out_payload, ensure_ascii=False, indent=2))
        print(json.dumps({'date': target_str, 'mode': args.mode, 'dryRun': True, 'candidateCount': len(dry_run_items), 'skippedCount': len(skipped)}, ensure_ascii=False))
        return

    pending = {
        'generatedAt': now.isoformat(),
        'lastRunMode': args.mode,
        'lastRunDate': target_str,
        'items': sorted(pending_by_id.values(), key=lambda x: x.get('dataHoraInicio', '')),
    }
    STATE.write_text(json.dumps(pending, ensure_ascii=False, indent=2))
    (LOGDIR / f'send_{target_str}.json').write_text(json.dumps({'sent': sent, 'skipped': skipped}, ensure_ascii=False, indent=2))
    print(json.dumps({'date': target_str, 'mode': args.mode, 'sentCount': len(sent), 'skippedCount': len(skipped)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
