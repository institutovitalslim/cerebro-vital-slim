#!/usr/bin/env python3
"""Checklist de regressão do GBrain IVS.

Valida se o sidecar encontra regras/processos canônicos que os agentes usam antes de responder.
Não altera o cérebro. Retorna código 0 quando os cenários mínimos passam.
"""
from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('/root/cerebro-vital-slim')
REPORT_DIR = Path('/root/.local/share/ivs-gbrain/reports')
CANONICAL_LATEST = ROOT / 'cerebro/gbrain/sync/latest-regression.md'
GBRAIN_REPO = ROOT / 'tmp/repo-reverse/gbrain'
ENV = os.environ.copy()
ENV['GBRAIN_HOME'] = '/root/.local/share/ivs-gbrain/home'
ENV['OPENCLAW_WORKSPACE'] = '/root/.local/share/ivs-gbrain/agent-workspace'
ENV['PATH'] = '/tmp/gbrain-ivs-bin:/root/.bun/bin:' + ENV.get('PATH', '')

TESTS = [
    {
        'name': 'Governança GBrain / Graphify RC-25',
        'query': 'GBrain operação canônica IVS Graphify RC-25 fonte de verdade markdown',
        'must_any': ['gbrain', 'graphify', 'rc-25', 'fonte de verdade'],
    },
    {
        'name': 'Resolver por área operacional',
        'query': 'onde arquivar regra operacional atendimento Clara WhatsApp leads resolver GBrain',
        'must_any': ['resolver', 'atendimento', 'clara', 'whatsapp'],
    },
    {
        'name': 'Clara confirmação objetiva',
        'query': 'Clara confirmação agenda Confirmo Quero remarcar Não vou conseguir',
        'must_any': ['confirmo', 'quero remarcar', 'não vou conseguir', 'clara'],
    },
    {
        'name': 'Marketing João / Reels',
        'query': 'João marketing reels tópico 5782 relatório diário tráfego IVS',
        'must_any': ['joão', 'marketing', 'reels', 'relatório'],
    },
    {
        'name': 'Apresentação paciente V10',
        'query': 'apresentação paciente novo V10 Instituto Vital Slim pré-requisitos Quarkclinic exames questionário',
        'must_any': ['apresentação', 'v10', 'quarkclinic', 'exames'],
    },
    {
        'name': 'Financeiro Omie',
        'query': 'Omie boletos financeiro Instituto Vital Slim regra operacional',
        'must_any': ['omie', 'financeiro'],
    },
]


def run_search(query: str) -> dict:
    proc = subprocess.run(
        ['gbrain-ivs', 'search', query],
        cwd=str(GBRAIN_REPO),
        env=ENV,
        text=True,
        capture_output=True,
        timeout=60,
    )
    return {'returncode': proc.returncode, 'stdout': proc.stdout, 'stderr': proc.stderr}


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).isoformat()
    results = []
    for test in TESTS:
        res = run_search(test['query'])
        hay = (res['stdout'] + '\n' + res['stderr']).lower()
        passed = res['returncode'] == 0 and any(token.lower() in hay for token in test['must_any'])
        results.append({**test, 'passed': passed, 'returncode': res['returncode'], 'output_preview': hay[:1200]})

    ok = all(r['passed'] for r in results)
    payload = {'ok': ok, 'generated_at': generated_at, 'results': results}
    stamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    json_path = REPORT_DIR / f'gbrain-ivs-regression-{stamp}.json'
    md_path = REPORT_DIR / f'gbrain-ivs-regression-{stamp}.md'
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')

    lines = ['# GBrain IVS — Regressão de Agentes', '', f'Gerado em: `{generated_at}`', '', f'Status geral: **{"OK" if ok else "FALHA"}**', '']
    for r in results:
        lines.append(f"- {'OK' if r['passed'] else 'FALHA'} — **{r['name']}**")
    lines += [
        '',
        '## Uso operacional',
        'Este checklist valida se o GBrain encontra informação suficiente para o reflexo dos agentes: consultar GBrain, abrir fonte canônica e só então responder sobre regra/processo/histórico.',
    ]
    md = '\n'.join(lines).strip() + '\n'
    md_path.write_text(md, encoding='utf-8')
    CANONICAL_LATEST.parent.mkdir(parents=True, exist_ok=True)
    CANONICAL_LATEST.write_text(md, encoding='utf-8')
    (REPORT_DIR / 'latest-regression.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    (REPORT_DIR / 'latest-regression.md').write_text(md, encoding='utf-8')
    print(json.dumps({'ok': ok, 'report': str(md_path), 'canonical_latest': str(CANONICAL_LATEST), 'passed': sum(1 for r in results if r['passed']), 'total': len(results)}, ensure_ascii=False, indent=2))
    return 0 if ok else 2


if __name__ == '__main__':
    raise SystemExit(main())
