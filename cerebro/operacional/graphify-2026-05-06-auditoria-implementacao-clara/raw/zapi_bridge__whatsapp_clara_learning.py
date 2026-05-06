#!/usr/bin/env python3
# Consolida aprendizado da Clara a partir de conversas WhatsApp atuais e históricas.
# Não grava telefones nem dados brutos no relatório final; usa apenas padrões agregados e insights.
import argparse, json, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

BRIDGE_DIR = Path('/root/.openclaw/workspace/ops/zapi_bridge')
sys.path.insert(0, str(BRIDGE_DIR))
import daily_clara_analysis as base

OUT_REPORTS = Path('/root/.openclaw/reports/clara-learning')
CEREBRO_LOGS = Path('/root/cerebro-vital-slim/cerebro/logs/clara-whatsapp-learning')


def compact_report(mode, period_label, signals, insights):
    lines = [
        f'# Clara WhatsApp Learning — {mode} — {period_label}',
        '',
        f'> Gerado em {datetime.now(timezone.utc).isoformat()}',
        '',
        '## Contadores agregados',
        f'- Mensagens analisadas: **{signals.get("total_messages", 0)}**',
        f'- Leads/conversas únicas: **{signals.get("unique_leads", 0)}**',
        f'- Recebidas: {signals.get("total_inbound", 0)} | Enviadas: {signals.get("total_outbound", 0)}',
        f'- Sinais de agendamento/vitória: **{len(signals.get("wins", []))}**',
        f'- Sinais de queda/objeção: **{len(signals.get("drops", []))}**',
        '',
        '## Aprendizados operacionais para Clara',
        '',
        insights or 'SEM_APRENDIZADOS_NOVOS - sem insight extraído',
        '',
        '## Regras de uso',
        '- Usar como aprendizado operacional, não como regra clínica.',
        '- Não diagnosticar, prescrever nem prometer resultado.',
        '- Não expor dados pessoais de pacientes/leads.',
        '- Promover mudanças estruturais somente via Graphify/RC-25.',
    ]
    return '\n'.join(lines).strip() + '\n'


def run(mode, hours=None, days=None):
    base.setup_gog_env()
    rows = base.fetch_sheet_rows()
    if not rows:
        raise SystemExit('no rows from WhatsApp sheet')
    now = datetime.now(timezone.utc)
    if mode == 'current':
        hours = hours or 6
        since = now - timedelta(hours=hours)
        period = f'últimas {hours}h'
        suffix = 'whatsapp-current'
    else:
        days = days or 180
        since = now - timedelta(days=days)
        period = f'últimos {days} dias'
        suffix = 'whatsapp-historical'
    msgs = base.parse_rows(rows, int(since.timestamp()))
    if msgs:
        convos = base.cluster_conversations(msgs)
        signals = base.extract_signals(msgs, convos)
        insights = base.call_kimi_for_insights(signals, now.strftime('%Y-%m-%d')) or 'SEM_APRENDIZADOS_NOVOS - falha na extração'
    else:
        signals = {'total_messages':0,'total_inbound':0,'total_outbound':0,'unique_leads':0,'openings':[],'wins':[],'drops':[],'inbound_samples':[]}
        insights = 'SEM_APRENDIZADOS_NOVOS - sem mensagens no período'

    OUT_REPORTS.mkdir(parents=True, exist_ok=True)
    CEREBRO_LOGS.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    md = compact_report(mode, period, signals, insights)
    report_path = CEREBRO_LOGS / f'{stamp}-{suffix}.md'
    report_path.write_text(md, encoding='utf-8')
    latest_md = CEREBRO_LOGS / f'latest-{suffix}.md'
    latest_md.write_text(md, encoding='utf-8')

    # JSON sanitizado para o pipeline diário de Graphify/RC-25.
    payload = {
        'ok': True,
        'slot': suffix,
        'fonte': 'WhatsApp IVS via planilha de conversas',
        'modo': mode,
        'periodo': period,
        'cerebro_report': str(report_path),
        'contadores': {
            'total_messages': signals.get('total_messages',0),
            'unique_leads': signals.get('unique_leads',0),
            'total_inbound': signals.get('total_inbound',0),
            'total_outbound': signals.get('total_outbound',0),
            'wins': len(signals.get('wins',[])),
            'drops': len(signals.get('drops',[])),
        },
        'aprendizados': insights,
        'entrega': 'padrões de conversa reais para melhorar agendamento da Clara sem expor PII',
        'buscar': 'objeções, vitórias, quedas, timing de convite para agenda, linguagem premium e follow-up',
    }
    json_path = OUT_REPORTS / f'{stamp}-{suffix}.json'
    latest_json = OUT_REPORTS / f'latest-{suffix}.json'
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    latest_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'ok': True, 'mode': mode, 'period': period, 'messages': signals.get('total_messages',0), 'leads': signals.get('unique_leads',0), 'report': str(report_path), 'latest_json': str(latest_json)}, ensure_ascii=False, indent=2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', choices=['current','historical'], required=True)
    ap.add_argument('--hours', type=int)
    ap.add_argument('--days', type=int)
    args = ap.parse_args()
    run(args.mode, args.hours, args.days)

if __name__ == '__main__':
    main()
