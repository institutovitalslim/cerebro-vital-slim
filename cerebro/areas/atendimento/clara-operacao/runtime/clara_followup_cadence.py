#!/usr/bin/env python3
"""Motor de cadência de follow-up da Clara.

Objetivo: enviar follow-ups comerciais D+1/D+2/D+3 para leads que tiveram
primeiro contato respondido pela Clara e ficaram sem resposta do lead.

Seguro por padrão:
- dry-run por padrão; só envia com --execute + --approval-id;
- usa /admin/send da bridge, herdando gates de segurança, RC-12, RC-34, RC-44,
  runtime enforcement e action gate;
- não usa nome do lead;
- não oferece agenda no follow-up frio;
- deduplica variantes de telefone;
- registra ledger local redigido.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

BASE = Path('/root/.openclaw/workspace/ops/zapi_bridge')
ENV_FILE = BASE / 'zapi_bridge.env'
LEADS_FILE = BASE / 'clara_leads_state.json'
STATE_FILE = BASE / 'clara_followup_cadence_state.json'
LEDGER_FILE = BASE / 'clara_followup_cadence_ledger.jsonl'
REPORT_FILE = BASE / 'clara_followup_cadence_latest.json'
BRIDGE_URL = 'http://127.0.0.1:8787/admin/send'

# Cadência conservadora. 23h permite rodar no mesmo turno do dia seguinte.
DEFAULT_INTERVALS_HOURS = [23, 47, 71]
QUIET_START_HOUR = 8
QUIET_END_HOUR = 22
MAX_PER_RUN = 20
MIN_REPLY_COUNT = 1
AUDIT_DIR = BASE / 'audit'


def normalize_decision_text(value: str) -> str:
    text = (value or '').strip().lower()
    table = str.maketrans({
        'á': 'a', 'à': 'a', 'â': 'a', 'ã': 'a',
        'é': 'e', 'ê': 'e',
        'í': 'i',
        'ó': 'o', 'ô': 'o', 'õ': 'o',
        'ú': 'u',
        'ç': 'c',
    })
    return re.sub(r'\s+', ' ', text.translate(table)).strip()


def contains_financial_no_fit_decline(text: str) -> bool:
    norm = normalize_decision_text(text)
    if not norm:
        return False
    if 'dentro d minhas condicoes' in norm or 'dentro das minhas condicoes' in norm or 'cabe nas minhas condicoes' in norm:
        return False
    patterns = (
        r'\bnao tenho (?:condicoes|condicao|dinheiro|como pagar|orcamento)\b',
        r'\bsem (?:condicoes|condicao|dinheiro|orcamento)\b',
        r'\bsem condicoes financeiras\b',
        r'\bnao consigo pagar\b',
        r'\bnao posso pagar\b',
        r'\bfora do meu orcamento\b',
    )
    return any(re.search(pattern, norm) for pattern in patterns)


def phone_variants(phone: str) -> list[str]:
    normalized = normalize_phone(phone) or ''
    variants = []
    for candidate in (re.sub(r'\D+', '', phone or ''), normalized):
        if candidate and candidate not in variants:
            variants.append(candidate)
    if len(normalized) == 13 and normalized.startswith('55') and normalized[4] == '9':
        v = normalized[:4] + normalized[5:]
        if v not in variants:
            variants.append(v)
    if len(normalized) == 12 and normalized.startswith('55'):
        subscriber = normalized[4:]
        if subscriber and subscriber[0] in '6789':
            v = normalized[:4] + '9' + subscriber
            if v not in variants:
                variants.append(v)
    return variants


def recent_audit_has_financial_no_fit_decline(phone: str, max_files: int = 60) -> bool:
    variants = set(phone_variants(phone))
    if not variants:
        return False
    try:
        files = sorted(AUDIT_DIR.glob('zapi_webhook_events_*.jsonl'), key=lambda p: p.stat().st_mtime)[-max_files:]
    except Exception:
        files = []
    for file_path in files:
        try:
            with file_path.open('r', encoding='utf-8') as fh:
                for line in fh:
                    try:
                        item = json.loads(line)
                    except Exception:
                        continue
                    item_phone = normalize_phone(str(item.get('phone') or '')) or re.sub(r'\D+', '', str(item.get('phone') or ''))
                    if item_phone not in variants or bool(item.get('from_me')) or bool(item.get('fromMe')):
                        continue
                    text = str(item.get('text') or '')
                    if not text and isinstance(item.get('payload'), dict):
                        raw_text = item['payload'].get('text')
                        if isinstance(raw_text, dict):
                            text = str(raw_text.get('message') or raw_text.get('body') or '')
                        elif isinstance(raw_text, str):
                            text = raw_text
                    if contains_financial_no_fit_decline(text):
                        return True
        except Exception:
            continue
    return False


def mark_not_qualified_financial(phone: str, name: str = 'Lead sem perfil financeiro') -> None:
    state = load_json(BASE / 'clara_exclusions.json', {'phones': {}})
    phones = state.setdefault('phones', {})
    now = int(time.time())
    for variant in phone_variants(phone):
        phones[variant] = {
            'name': name,
            'reason': 'not_qualified_financial_no_fit',
            'source': 'followup_cadence_audit_financial_decline',
            'updated_at': now,
        }
    state['updated_at'] = now
    write_json(BASE / 'clara_exclusions.json', state)


def now_iso(ts: Optional[float] = None) -> str:
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(ts or time.time()))


def load_json(path: Path, default: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        pass
    return default


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def load_env(path: Path) -> Dict[str, str]:
    env: Dict[str, str] = {}
    if not path.exists():
        return env
    for raw in path.read_text(encoding='utf-8', errors='ignore').splitlines():
        line = raw.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def phone_hash(phone: str) -> str:
    digits = re.sub(r'\D+', '', phone or '')
    return hashlib.sha256(digits.encode()).hexdigest()[:16]


def normalize_phone(value: str) -> Optional[str]:
    if not value or '@' in value:
        return None
    digits = re.sub(r'\D+', '', value)
    if not digits:
        return None
    # Evita IDs LID longos e chaves estranhas.
    if len(digits) > 14:
        return None
    if len(digits) in (10, 11):
        digits = '55' + digits
    if not digits.startswith('55'):
        return None
    if len(digits) < 12 or len(digits) > 13:
        return None
    return digits


def canonical_phone(phone: str) -> str:
    """Remove variação com/sem nono dígito para dedupe aproximado.

    Mantém o número real para envio, mas agrupa variantes comuns: 55 + DDD + 9 + 8 dígitos
    e 55 + DDD + 8 dígitos.
    """
    digits = normalize_phone(phone) or phone
    if len(digits) == 13 and digits.startswith('55') and digits[4] == '9':
        return digits[:4] + digits[5:]
    return digits


# Pools de variações por passo da cadência (D+1, D+2, D+3...).
# Regra Tiaro (2026-06-22): nunca repetir a mesma mensagem para o mesmo lead.
# Cada passo tem várias redações equivalentes; a seleção evita variações já
# enviadas àquele telefone (memória persistente em sent_variants).
FOLLOWUP_POOLS = [
    # Passo 1 — retomada leve, 1 pergunta de abertura
    [
        ("Oi! Passando para retomar seu contato com o Instituto Vital Slim. "
         "Para eu te orientar melhor, me conta um pouco: o que mais te fez buscar ajuda agora?"),
        ("Oi! Fiquei de te ajudar por aqui e não quis te deixar sem retorno. "
         "Só para eu entender seu momento: o que mais está te incomodando hoje?"),
        ("Oi! Voltando aqui com calma. Para eu te orientar do jeito certo, "
         "me conta rapidinho: o que te trouxe até a gente?"),
        ("Oi! Retomando nosso contato. Em poucas palavras, qual é hoje a sua maior preocupação "
         "com a sua saúde ou com o seu corpo?"),
    ],
    # Passo 2 — reforço de valor + 1 pergunta de problema
    [
        ("Só retomando por aqui com calma: muitas vezes o primeiro passo é entender o que está "
         "travando o resultado. Hoje o que pesa mais para você: peso, exames, energia ou rotina?"),
        ("Voltando ao nosso papo: cada caso costuma ter uma causa diferente por trás. "
         "No seu dia a dia, o que mais atrapalha: a fome, a energia, o sono ou manter constância?"),
        ("Passando de novo, sem pressa. Para eu te ajudar melhor, me diz: "
         "o que tem sido mais difícil para você, começar ou manter o resultado?"),
        ("Retomo aqui porque faz sentido olhar isso com cuidado. "
         "Hoje, o que mais te incomoda: o corpo, a disposição ou como você tem se sentido?"),
    ],
    # Passo 3 — encerramento elegante, microcompromisso de baixo atrito
    [
        ("Vou fazer uma última retomada para não te incomodar. Se ainda fizer sentido entender o "
         "caminho inicial, me responde com ‘quero entender’ que eu te explico de forma simples."),
        ("Não quero insistir além da conta, então deixo seu atendimento em aberto por aqui. "
         "Se quiser retomar quando fizer sentido, é só me chamar que eu te ajudo no próximo passo."),
        ("Vou deixar por aqui para te dar espaço. Se em algum momento você quiser entender como "
         "funciona a avaliação, me manda um ‘oi’ que eu retomo de onde paramos."),
        ("Por hoje paro por aqui para não ser inconveniente. Quando você decidir cuidar disso, "
         "me escreve que eu te oriento com calma sobre o melhor começo."),
    ],
]


def pick_followup_message(step: int, phone_state: Dict[str, Any], seed_key: str) -> Tuple[str, int]:
    """Escolhe uma variação do passo que o lead ainda não recebeu.

    - step: passo 1-based da cadência.
    - phone_state: estado persistente do telefone (sent_variants por passo).
    - seed_key: chave estável (hash do telefone + ciclo) para escolha determinística.
    Retorna (mensagem, indice_da_variacao).
    """
    pool_idx = min(step - 1, len(FOLLOWUP_POOLS) - 1)
    pool = FOLLOWUP_POOLS[pool_idx]
    sent_map = phone_state.setdefault('sent_variants', {})
    used = list(sent_map.get(str(step)) or [])
    available = [i for i in range(len(pool)) if i not in used]
    if not available:
        # Todas já usadas neste passo: reinicia o ciclo de variações deste passo.
        used = []
        available = list(range(len(pool)))
    # Escolha determinística porém espalhada: hash da seed + passo.
    h = int(hashlib.sha256(f"{seed_key}:{step}:{len(used)}".encode('utf-8')).hexdigest(), 16)
    choice = available[h % len(available)]
    sent_map[str(step)] = used + [choice]
    return pool[choice], choice


@dataclass
class Candidate:
    phone: str
    key: str
    due_step: int
    due_at: float
    first_seen_at: float
    last_inbound_at: float
    last_reply_at: float
    reply_count: int
    reason: str


def in_business_hours(ts: Optional[float] = None) -> bool:
    # Servidor está em UTC; Bahia/BRT = UTC-3.
    lt = time.gmtime((ts or time.time()) - 3 * 3600)
    hour = lt.tm_hour
    return QUIET_START_HOUR <= hour < QUIET_END_HOUR


def current_cycle_id(entry: Dict[str, Any]) -> str:
    return str(int(float(entry.get('last_inbound_at') or entry.get('first_seen_at') or 0)))


def select_candidates(leads_state: Dict[str, Any], cadence_state: Dict[str, Any], *, now: float, intervals_hours: List[int], max_per_run: int) -> Tuple[List[Candidate], Dict[str, int]]:
    leads = leads_state.get('leads') or {}
    stats = {
        'raw_entries': 0, 'invalid_phone': 0, 'deduped_variant': 0, 'not_replied_by_clara': 0,
        'pending_lead_message': 0, 'cadence_complete': 0, 'not_due': 0, 'selected': 0,
        'blocked_not_qualified': 0, 'blocked_financial_no_fit_audit': 0,
    }
    selected_by_canon: Dict[str, Candidate] = {}
    for raw_phone, entry in leads.items():
        stats['raw_entries'] += 1
        if not isinstance(entry, dict):
            continue
        phone = normalize_phone(str(raw_phone))
        if not phone:
            stats['invalid_phone'] += 1
            continue
        canon = canonical_phone(phone)
        if entry.get('followup_blocked') or entry.get('not_qualified') or str(entry.get('status') or '').upper() == 'NQ':
            stats['blocked_not_qualified'] += 1
            continue
        if recent_audit_has_financial_no_fit_decline(phone):
            mark_not_qualified_financial(phone)
            entry['followup_blocked'] = True
            entry['not_qualified'] = True
            entry['not_qualified_reason'] = 'financial_no_fit'
            entry['updated_at'] = int(now)
            stats['blocked_financial_no_fit_audit'] += 1
            continue
        first_seen = float(entry.get('first_seen_at') or 0)
        last_in = float(entry.get('last_inbound_at') or first_seen or 0)
        last_reply = float(entry.get('last_reply_at') or 0)
        reply_count = int(entry.get('reply_count') or 0)
        if reply_count < MIN_REPLY_COUNT or last_reply <= 0:
            stats['not_replied_by_clara'] += 1
            continue
        # Se o lead mandou algo depois da última resposta da Clara, não é follow-up: é resposta pendente.
        if last_in > last_reply + 60:
            stats['pending_lead_message'] += 1
            continue
        cycle = current_cycle_id(entry)
        cstate = cadence_state.setdefault('phones', {}).setdefault(phone_hash(canon), {})
        if cstate.get('cycle_id') != cycle:
            cstate.clear()
            cstate['cycle_id'] = cycle
            cstate['sent_steps'] = []
        sent_steps = set(int(x) for x in cstate.get('sent_steps') or [])
        next_step = None
        due_at = None
        # D+1/D+2/D+3 contados a partir da última resposta da Clara no ciclo.
        for idx, h in enumerate(intervals_hours, start=1):
            if idx in sent_steps:
                continue
            candidate_due = last_reply + h * 3600
            next_step, due_at = idx, candidate_due
            break
        if next_step is None:
            stats['cadence_complete'] += 1
            continue
        if now < float(due_at):
            stats['not_due'] += 1
            continue
        cand = Candidate(
            phone=phone, key=phone_hash(canon), due_step=int(next_step), due_at=float(due_at),
            first_seen_at=first_seen, last_inbound_at=last_in, last_reply_at=last_reply,
            reply_count=reply_count, reason=f'D+{next_step}_due_after_clara_reply',
        )
        old = selected_by_canon.get(canon)
        if old:
            stats['deduped_variant'] += 1
            # Prefere o registro com mais interações/reply_count.
            if cand.reply_count <= old.reply_count:
                continue
        selected_by_canon[canon] = cand
    candidates = sorted(selected_by_canon.values(), key=lambda c: (c.due_at, c.last_reply_at))[:max_per_run]
    stats['selected'] = len(candidates)
    return candidates, stats


def append_ledger(entry: Dict[str, Any]) -> None:
    LEDGER_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER_FILE.open('a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')


def call_admin_send(phone: str, message: str, *, dry_run: bool, approval_id: Optional[str], secret: str, timeout: int = 60) -> Tuple[int, Dict[str, Any]]:
    payload: Dict[str, Any] = {
        'phone': phone,
        'message': message,
        'dry_run': dry_run,
        # Follow-up frio deliberadamente sem nome e sem agenda; contexto não validado.
        'name_confirmed': False,
        'context_validated': False,
        'reason': 'clara_followup_cadence_engine',
    }
    if approval_id:
        payload['approval_id'] = approval_id
        payload['approval_evidence'] = 'Tiaro autorizou criação/execução do motor de cadência de follow-up da Clara.'
    data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(BRIDGE_URL, data=data, method='POST')
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    if secret:
        req.add_header('X-Bridge-Secret', secret)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode('utf-8', errors='replace')
            return resp.status, json.loads(body or '{}')
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        try:
            parsed = json.loads(body or '{}')
        except Exception:
            parsed = {'raw': body[:1000]}
        return e.code, parsed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--execute', action='store_true', help='Envia de verdade. Sem isto roda dry-run.')
    ap.add_argument('--approval-id', default='', help='Obrigatório para --execute quando action gate está ativo.')
    ap.add_argument('--max-per-run', type=int, default=MAX_PER_RUN)
    ap.add_argument('--ignore-business-hours', action='store_true')
    ap.add_argument('--interval-hours', default=','.join(map(str, DEFAULT_INTERVALS_HOURS)))
    ap.add_argument('--state-file', default=str(STATE_FILE))
    ap.add_argument('--leads-file', default=str(LEADS_FILE))
    args = ap.parse_args()

    now = time.time()
    intervals = [int(x.strip()) for x in args.interval_hours.split(',') if x.strip()]
    dry_run = not args.execute
    if args.execute and not args.approval_id:
        print(json.dumps({'ok': False, 'error': 'approval_id_required_for_execute'}, ensure_ascii=False, indent=2))
        return 2
    if args.execute and not args.ignore_business_hours and not in_business_hours(now):
        report = {'ok': True, 'mode': 'execute', 'skipped': 'outside_business_hours', 'at': now_iso(now)}
        write_json(REPORT_FILE, report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    env = load_env(ENV_FILE)
    secret = env.get('BRIDGE_SHARED_SECRET', '')
    leads_state = load_json(Path(args.leads_file), {'leads': {}})
    cadence_state = load_json(Path(args.state_file), {'phones': {}, 'runs': []})
    candidates, stats = select_candidates(leads_state, cadence_state, now=now, intervals_hours=intervals, max_per_run=args.max_per_run)

    results: List[Dict[str, Any]] = []
    for cand in candidates:
        pst = cadence_state.setdefault('phones', {}).setdefault(cand.key, {})
        # Seed determinística por lead+ciclo: garante variação e não repete texto.
        seed_key = f"{cand.key}:{int(cand.last_inbound_at or 0)}"
        msg, variant_idx = pick_followup_message(cand.due_step, pst, seed_key)
        status, body = call_admin_send(cand.phone, msg, dry_run=dry_run, approval_id=args.approval_id or None, secret=secret)
        ok = bool(body.get('ok')) and 200 <= status < 300
        result = {
            'phone_hash': cand.key,
            'phone_last4': cand.phone[-4:],
            'step': cand.due_step,
            'variant': variant_idx,
            'due_at': now_iso(cand.due_at),
            'last_reply_at': now_iso(cand.last_reply_at),
            'dry_run': dry_run,
            'http_status': status,
            'ok': ok,
            'bridge_result': {k: v for k, v in body.items() if k not in ('zapiBody',)},
        }
        results.append(result)
        append_ledger({'at': now_iso(), **result})
        if ok and not dry_run:
            sent_steps = list(dict.fromkeys([*(pst.get('sent_steps') or []), cand.due_step]))
            pst.update({
                'cycle_id': str(int(cand.last_inbound_at or 0)),
                'sent_steps': sent_steps,
                'last_sent_at': now,
                'last_sent_at_iso': now_iso(now),
                'last_step': cand.due_step,
                'last_variant': variant_idx,
            })
        else:
            # Em dry-run ou falha, não marca a variação como consumida.
            sm = pst.get('sent_variants') or {}
            used = list(sm.get(str(cand.due_step)) or [])
            if used and used[-1] == variant_idx:
                used.pop()
                sm[str(cand.due_step)] = used
            pst['sent_variants'] = sm

    run_entry = {
        'at': now_iso(now),
        'mode': 'execute' if args.execute else 'dry_run',
        'business_hours': in_business_hours(now),
        'interval_hours': intervals,
        'stats': stats,
        'results': results,
    }
    runs = cadence_state.setdefault('runs', [])
    runs.append({k: v for k, v in run_entry.items() if k != 'results'} | {'result_count': len(results)})
    cadence_state['runs'] = runs[-100:]
    write_json(Path(args.leads_file), leads_state)
    write_json(Path(args.state_file), cadence_state)
    write_json(REPORT_FILE, run_entry)
    print(json.dumps(run_entry, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
