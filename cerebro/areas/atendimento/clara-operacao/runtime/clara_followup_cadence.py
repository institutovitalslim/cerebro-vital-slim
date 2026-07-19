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
- registra ledger local redigido;
- antes de escolher qualquer texto, analisa o contexto completo recente da conversa
  para retomar do ponto certo, sem parecer que esqueceu o lead.
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
    """Detecta negativa financeira terminal que bloqueia avanço ativo.

    Regra Tiaro (2026-07-19): se o lead já respondeu que está caro demais,
    fora das condições, sem dinheiro/orçamento ou equivalente, o motor não deve
    tentar avançar follow-up. Inbound futuro continua permitido.
    """
    norm = normalize_decision_text(text)
    if not norm:
        return False
    # Protege frases afirmativas/qualificadoras: "cabe nas minhas condições" não é negativa.
    if 'dentro d minhas condicoes' in norm or 'dentro das minhas condicoes' in norm or 'cabe nas minhas condicoes' in norm:
        return False
    patterns = (
        r'\bnao tenho (?:condicoes|condicao|dinheiro|como pagar|orcamento)\b',
        r'\bsem (?:condicoes|condicao|dinheiro|orcamento)\b',
        r'\bsem condicoes financeiras\b',
        r'\bnao consigo pagar\b',
        r'\bnao posso pagar\b',
        r'\bfora do meu orcamento\b',
        r'\bfoge (?:do|ao) meu orcamento\b',
        r'\b(?:muito|bem) caro(?: pra mim| para mim)?\b',
        r'\bcaro demais(?: pra mim| para mim)?\b',
        r'\b(?:e|esta|ta) caro(?: pra mim| para mim)?\b',
        r'\bnao da(?: pra mim| para mim| agora)?\b',
        r'\bnao cabe (?:no|dentro do|em meu|no meu) orcamento\b',
        r'\binviavel(?: pra mim| para mim)?\b',
        r'\bsem chance(?: pra mim| para mim)?\b',
    )
    return any(re.search(pattern, norm) for pattern in patterns)


def contains_terminal_deferral_decline(text: str) -> bool:
    """Detecta quando o lead pediu espaço e disse que ele mesmo retornará.

    Isso não torna o contato NQ definitivo nem bloqueia inbound futuro. Só bloqueia
    follow-up ativo da Clara para não reabrir conversa encerrada com "vou procurar vocês".
    """
    norm = normalize_decision_text(text)
    if not norm:
        return False
    patterns = (
        r'\b(eu\s+)?vou\s+(?:me|mim)?\s*(?:organizar|resolver|ver|pensar)?.{0,30}\bprocurar\s+(?:vcs|voces|vocês)\b',
        r'\b(?:assim que|quando)\s+(?:eu\s+)?(?:resolver|puder|der|me organizar|mim organizar).{0,50}\b(?:procuro|procurar|entro em contato|retorno)\b',
        r'\b(?:eu\s+)?(?:procuro|procurarei|retorno|entro em contato)\s+(?:vcs|voces|vocês|com voces|com vocês|com vcs)\b',
        r'\b(?:eu\s+)?vou\s+procurar\s+(?:vcs|voces|vocês)\b',
    )
    return any(re.search(pattern, norm) for pattern in patterns)


def contains_open_discovery_question(text: str) -> bool:
    """Detecta quando a última fala da Clara já deixou pergunta de descoberta aberta.

    Se o lead não respondeu depois disso, a cadência não deve mandar outra pergunta
    genérica de retomada. Esse foi o incidente Jamile (2026-07-18): a Clara perguntou
    sobre emagrecimento/problema de saúde e, no D+1, retomou com a mesma pergunta.
    """
    norm = normalize_decision_text(text)
    if not norm or '?' not in (text or ''):
        return False
    patterns = (
        r'\bo que mais\b.{0,80}\b(?:incomod|buscar ajuda|trouxe|preocupacao)\b',
        r'\balem do emagrecimento\b.{0,120}\b(?:problema de saude|incomoda)\b',
        r'\bqual e hoje\b.{0,120}\bmaior preocupacao\b',
        r'\bvoce ja tentou\b.{0,120}\b(?:tratamento|mudanca de rotina|acompanhamento medico)\b',
        r'\besta buscando comecar agora\b.{0,80}\bacompanhamento medico\b',
        r'\bme conta\b.{0,80}\b(?:o que te trouxe|o que fez voce buscar|buscar ajuda agora)\b',
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
    return recent_audit_has_text_match(phone, contains_financial_no_fit_decline, max_files=max_files)


def recent_audit_has_terminal_deferral_decline(phone: str, max_files: int = 60) -> bool:
    return recent_audit_has_text_match(phone, contains_terminal_deferral_decline, max_files=max_files)


def recent_audit_has_text_match(phone: str, matcher, max_files: int = 60) -> bool:
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
                    if matcher(text):
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


def mark_terminal_deferral_followup_block(phone: str, name: str = 'Lead pediu para retornar quando resolver') -> None:
    state = load_json(BASE / 'clara_exclusions.json', {'phones': {}})
    phones = state.setdefault('phones', {})
    now = int(time.time())
    for variant in phone_variants(phone):
        phones[variant] = {
            'name': name,
            'reason': 'lead_requested_no_active_followup_manual_return',
            'source': 'followup_cadence_audit_terminal_deferral',
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



def extract_event_text(item: Dict[str, Any]) -> str:
    text = str(item.get('text') or '')
    if not text and isinstance(item.get('payload'), dict):
        raw_text = item['payload'].get('text')
        if isinstance(raw_text, dict):
            text = str(raw_text.get('message') or raw_text.get('body') or '')
        elif isinstance(raw_text, str):
            text = raw_text
        elif isinstance(item['payload'].get('message'), dict):
            msg = item['payload']['message']
            text = str(msg.get('text') or msg.get('conversation') or '')
    return re.sub(r'\s+', ' ', text).strip()


def event_timestamp(item: Dict[str, Any]) -> float:
    for key in ('timestamp', 'ts', 'created_at', 'at'):
        value = item.get(key)
        if value is None:
            continue
        try:
            value_f = float(value)
            if value_f > 10_000_000_000:  # ms
                value_f /= 1000
            return value_f
        except Exception:
            continue
    return 0.0


def recent_conversation_for_phone(phone: str, max_files: int = 120, max_events: int = 80) -> List[Dict[str, Any]]:
    """Carrega o histórico recente real do lead antes de qualquer follow-up.

    Regra canônica Tiaro (2026-07-19): a primeira tarefa do motor de follow-up é
    analisar o contexto das mensagens para voltar a se conectar com o lead da forma
    certa. Este snapshot fica redigido no relatório (categoria/âncora, sem dump de conversa).
    """
    variants = set(phone_variants(phone))
    if not variants:
        return []
    events: List[Dict[str, Any]] = []
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
                    if item_phone not in variants:
                        continue
                    text = extract_event_text(item)
                    if not text:
                        continue
                    events.append({
                        'ts': event_timestamp(item),
                        'from_me': bool(item.get('from_me')) or bool(item.get('fromMe')),
                        'text': text[:1200],
                    })
        except Exception:
            continue
    events.sort(key=lambda x: x.get('ts') or 0)
    return events[-max_events:]


def analyze_lead_message_context(phone: str, last_reply_preview: str = '') -> Dict[str, Any]:
    """Analisa todo o contexto recente antes de redigir a retomada."""
    events = recent_conversation_for_phone(phone)
    inbound = [e for e in events if not e.get('from_me')]
    outbound = [e for e in events if e.get('from_me')]
    last_inbound_text = inbound[-1]['text'] if inbound else ''
    last_outbound_text = outbound[-1]['text'] if outbound else (last_reply_preview or '')
    joined_inbound = ' '.join(e['text'] for e in inbound[-8:])
    norm_in = normalize_decision_text(joined_inbound)

    if contains_terminal_deferral_decline(last_inbound_text):
        return {'ok': False, 'category': 'terminal_deferral', 'anchor': 'lead pediu para retornar depois', 'event_count': len(events)}
    if contains_financial_no_fit_decline(last_inbound_text):
        return {'ok': False, 'category': 'financial_no_fit', 'anchor': 'lead recusou por condição financeira', 'event_count': len(events)}
    outbound_after_inbound = bool(outbound) and (not inbound or float(outbound[-1].get('ts') or 0) >= float(inbound[-1].get('ts') or 0))
    if contains_open_discovery_question(last_outbound_text) and (outbound_after_inbound or not outbound):
        return {'ok': False, 'category': 'open_discovery_waiting', 'anchor': 'Clara já deixou pergunta de descoberta aberta', 'event_count': len(events)}

    category = 'generic_contextual'
    anchor = 'retomar o ponto anterior com leveza'
    if re.search(r'\b(pre[cç]o|valor|consulta|investimento|pagar|parcel)', norm_in):
        category = 'price_or_investment'
        anchor = 'retomar a dúvida sobre investimento sem pressionar'
    elif re.search(r'\b(agenda|hor[aá]rio|marcar|consulta|vaga|encaixe)', norm_in):
        category = 'schedule_interest'
        anchor = 'retomar o interesse em consulta/agenda sem oferecer hoje ou amanhã'
    elif re.search(r'\b(emagrec|peso|gordura|barriga|corpo|obes)', norm_in):
        category = 'weight_or_body_pain'
        anchor = 'retomar a dor ligada a peso/corpo'
    elif re.search(r'\b(cansad|energia|sono|disposi[cç][aã]o|fraqueza)', norm_in):
        category = 'energy_or_routine_pain'
        anchor = 'retomar a queixa de energia/rotina como descoberta'
    elif re.search(r'\b(exame|horm[oô]nio|tireoide|glicose|colesterol|metab[oó]lic)', norm_in):
        category = 'metabolic_or_exam_pain'
        anchor = 'retomar a preocupação com exames/metabolismo'
    elif last_inbound_text:
        anchor = 'retomar a última fala do lead sem repetir pergunta'

    return {
        'ok': True,
        'category': category,
        'anchor': anchor,
        'event_count': len(events),
        'last_inbound_preview': last_inbound_text[:180],
        'last_outbound_preview': last_outbound_text[:180],
    }


def contextualize_followup_message(base_message: str, context: Dict[str, Any]) -> str:
    """Ajusta a abertura do follow-up à leitura do histórico, sem expor dados sensíveis."""
    category = context.get('category') or 'generic_contextual'
    if category == 'price_or_investment':
        return ("Retomando nosso papo sobre investimento com calma: antes de qualquer decisão, "
                "o mais importante é entender se a avaliação faz sentido para o seu momento. "
                "Me conta só uma coisa: o que mais pesa para você hoje, o valor ou a segurança de saber o caminho certo?")
    if category == 'schedule_interest':
        return ("Retomando de onde paramos sobre a consulta: antes de olhar possibilidade de agenda, "
                "quero entender seu momento para te orientar certo. O que fez você buscar ajuda agora?")
    if category == 'weight_or_body_pain':
        return ("Retomando o ponto que apareceu sobre peso/corpo: muitas vezes não é só força de vontade, "
                "tem rotina, exames e metabolismo envolvidos. Hoje o que mais está te incomodando nisso?")
    if category == 'energy_or_routine_pain':
        return ("Retomando o que você trouxe sobre energia/rotina: isso costuma atrapalhar muito a constância. "
                "No seu dia a dia, o que mais pesa: cansaço, sono, fome ou falta de tempo?")
    if category == 'metabolic_or_exam_pain':
        return ("Retomando sua preocupação com exames/metabolismo: a primeira avaliação serve justamente para "
                "entender a raiz do problema antes de propor qualquer caminho. O que mais te preocupa hoje?")
    return base_message

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
    context_category: str = 'unknown'
    context_anchor: str = ''


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
        'blocked_terminal_deferral_audit': 0, 'blocked_open_discovery_question': 0,
        'context_analyzed': 0, 'context_missing': 0,
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
        if recent_audit_has_terminal_deferral_decline(phone):
            mark_terminal_deferral_followup_block(phone)
            entry['followup_blocked'] = True
            entry['followup_blocked_reason'] = 'lead_requested_manual_return'
            entry['updated_at'] = int(now)
            stats['blocked_terminal_deferral_audit'] += 1
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
        last_reply_preview = str(entry.get('last_reply_preview') or '')
        # Regra canônica Tiaro (2026-07-19): antes de qualquer seleção/envio,
        # analisar o contexto real da conversa para reconectar do jeito certo.
        context = analyze_lead_message_context(phone, last_reply_preview)
        stats['context_analyzed'] += 1
        if not context.get('event_count'):
            stats['context_missing'] += 1
        if not context.get('ok', True):
            entry['followup_blocked'] = True
            entry['followup_blocked_reason'] = str(context.get('category') or 'context_not_safe')
            entry['updated_at'] = int(now)
            if context.get('category') == 'open_discovery_waiting':
                stats['blocked_open_discovery_question'] += 1
            elif context.get('category') == 'terminal_deferral':
                stats['blocked_terminal_deferral_audit'] += 1
            elif context.get('category') == 'financial_no_fit':
                stats['blocked_financial_no_fit_audit'] += 1
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
            context_category=str(context.get('category') or 'unknown'),
            context_anchor=str(context.get('anchor') or ''),
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
        msg = contextualize_followup_message(msg, {'category': cand.context_category, 'anchor': cand.context_anchor})
        status, body = call_admin_send(cand.phone, msg, dry_run=dry_run, approval_id=args.approval_id or None, secret=secret)
        ok = bool(body.get('ok')) and 200 <= status < 300
        result = {
            'phone_hash': cand.key,
            'phone_last4': cand.phone[-4:],
            'step': cand.due_step,
            'variant': variant_idx,
            'context_category': cand.context_category,
            'context_anchor': cand.context_anchor,
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
