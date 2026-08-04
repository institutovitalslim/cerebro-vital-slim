#!/usr/bin/env python3
"""Ingestão governada de dores/desejos mapeados na internet para o Content Engine OS.

Fonte: scraping de autosuggest Google/Bing em pt-BR executado para o blog científico IVS.
Arquivo de entrada: /opt/ivs/blog-scientific-authority/research/scraped_search_questions_top21.csv

Propriedades:
- idempotente por source/source_ref/origin;
- não publica conteúdo;
- não envia mensagem;
- não toca em paciente/lead individual;
- grava sinais agregados de busca como repertório editorial interno.
"""
from __future__ import annotations

import csv
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

INPUT = Path('/opt/ivs/blog-scientific-authority/research/scraped_search_questions_top21.csv')
ORIGIN = 'web-autosuggest-pain-desire-20260626'
TENANT = 'demo'

DOMAIN_LABELS = {
    'emagrecimento': 'Emagrecimento',
    'reposicao_hormonal': 'Reposição Hormonal',
    'longevidade': 'Longevidade',
    'medicina_preventiva': 'Medicina Preventiva',
}


def psql(sql: str) -> str:
    cmd = ['docker', 'exec', '-i', 'content-engine-postgres', 'psql', '-U', 'content_engine', '-d', 'content_engine', '-At']
    out = subprocess.run(cmd, input=sql, text=True, capture_output=True, check=True)
    return out.stdout.strip()


def sql_quote(value: object) -> str:
    if value is None:
        return 'null'
    return "'" + str(value).replace("'", "''") + "'"


def slug(value: str) -> str:
    value = value.lower().strip()
    value = value.translate(str.maketrans('áàãâäéèêëíìîïóòõôöúùûüçñ', 'aaaaaeeeeiiiiooooouuuucn'))
    value = re.sub(r'[^a-z0-9]+', '-', value).strip('-')
    return value[:90] or 'item'


def classify(row: dict[str, str]) -> tuple[str, str, str, str]:
    q = row['question'].strip()
    domain = row['domain'].split('+')[0].strip()
    category = DOMAIN_LABELS.get(domain, domain.replace('_', ' ').title())
    intent = (row.get('intent') or '').strip() or 'dor'

    if intent == 'dor':
        pain = q
        desire = {
            'emagrecimento': 'emagrecer com segurança, entender a causa e recuperar confiança no corpo',
            'reposicao_hormonal': 'atravessar a menopausa/climatério com segurança, energia e clareza',
            'longevidade': 'ter mais energia, força, autonomia e saúde depois dos 40',
            'medicina_preventiva': 'prevenir riscos e entender sinais antes que virem problema maior',
        }.get(domain, 'entender o problema e encontrar um caminho seguro')
    else:
        pain = {
            'emagrecimento': 'frustração com tentativas anteriores, medo de perder saúde ou recuperar peso',
            'reposicao_hormonal': 'dúvida sobre indicação, segurança e medo de efeitos colaterais',
            'longevidade': 'medo de envelhecer com cansaço, fraqueza e perda de autonomia',
            'medicina_preventiva': 'insegurança sobre quais exames e sinais merecem atenção',
        }.get(domain, 'dúvida recorrente mapeada em buscas públicas')
        desire = q

    objection = {
        'emagrecimento': 'já tentei de tudo / tenho medo de promessa vazia / não quero passar fome',
        'reposicao_hormonal': 'tenho medo de hormônio / não sei se é para mim / vejo informações contraditórias',
        'longevidade': 'não tenho tempo / não sei por onde começar / tenho medo de gastar com suplemento à toa',
        'medicina_preventiva': 'meus exames parecem normais / tenho medo de descobrir algo / não sei o que investigar',
    }.get(domain, 'preciso de orientação confiável antes de decidir')
    return category, pain[:220], desire[:220], objection[:220]


def main() -> int:
    if not INPUT.exists():
        raise SystemExit(f'Arquivo de entrada não encontrado: {INPUT}')
    rows = list(csv.DictReader(INPUT.open(encoding='utf-8')))
    if not rows:
        raise SystemExit('CSV sem linhas')

    # Ensure extension/table exists where older DBs might not have phase 4 loaded.
    psql("""
    create extension if not exists pgcrypto;
    create table if not exists content_pattern_library (
      id uuid primary key default gen_random_uuid(),
      tenant_id uuid not null references tenants(id) on delete cascade,
      pattern_key text not null,
      pattern_type text not null,
      label text not null,
      score numeric(8,2) not null default 0,
      examples jsonb not null default '[]'::jsonb,
      created_at timestamptz not null default now(),
      updated_at timestamptz not null default now(),
      unique (tenant_id, pattern_key)
    );
    """)

    # Idempotent cleanup only for this origin/source.
    psql(f"""
    with t as (select id from tenants where slug={sql_quote(TENANT)} limit 1)
    delete from story_themes st using t where st.tenant_id=t.id and st.source={sql_quote(ORIGIN)};

    with t as (select id from tenants where slug={sql_quote(TENANT)} limit 1)
    delete from manual_themes mt using t where mt.tenant_id=t.id and mt.notes like {sql_quote('%' + ORIGIN + '%')};

    with t as (select id from tenants where slug={sql_quote(TENANT)} limit 1)
    delete from themes th using t where th.tenant_id=t.id and th.source_origin={sql_quote(ORIGIN)};

    with t as (select id from tenants where slug={sql_quote(TENANT)} limit 1)
    delete from opportunities op using t where op.tenant_id=t.id and op.source_type={sql_quote(ORIGIN)};

    with t as (select id from tenants where slug={sql_quote(TENANT)} limit 1)
    delete from content_pattern_library cp using t where cp.tenant_id=t.id and cp.pattern_key like {sql_quote(ORIGIN + ':%')};
    """)

    counts = Counter()
    examples_by_domain: dict[str, list[dict[str, object]]] = defaultdict(list)
    for idx, row in enumerate(rows, 1):
        question = row['question'].strip()
        domain = row['domain'].split('+')[0].strip()
        category, pain, desire, objection = classify(row)
        source_ref = f"{ORIGIN}:{idx:02d}:{slug(question)}"
        score = float(row.get('score') or 0)
        confidence = min(0.98, 0.78 + min(score, 20) / 100)
        meta = {
            'question': question,
            'domain': domain,
            'intent': row.get('intent'),
            'score': score,
            'hits': row.get('hits'),
            'sources': row.get('sources'),
            'seeds': row.get('seeds'),
            'source_ref': source_ref,
        }
        psql(f"""
        with t as (select id from tenants where slug={sql_quote(TENANT)} limit 1)
        insert into story_themes (tenant_id, title, category, pain, desire, objection, awareness_level, source, confidence)
        select t.id, {sql_quote(question[:220])}, {sql_quote(category[:80])}, {sql_quote(pain)}, {sql_quote(desire)}, {sql_quote(objection)},
               {sql_quote('consciente_da_dor' if row.get('intent') == 'dor' else 'solution_aware')}, {sql_quote(ORIGIN)}, {confidence:.2f}
        from t
        on conflict (tenant_id, title) do update set
          category=excluded.category,
          pain=excluded.pain,
          desire=excluded.desire,
          objection=excluded.objection,
          awareness_level=excluded.awareness_level,
          source=excluded.source,
          confidence=excluded.confidence;

        with t as (select id from tenants where slug={sql_quote(TENANT)} limit 1)
        insert into themes (tenant_id, name, category, type, source_origin, source_ref)
        select t.id, {sql_quote(question[:500])}, {sql_quote(category)}, {sql_quote('dor_mapeada' if row.get('intent') == 'dor' else 'desejo_mapeado')}, {sql_quote(ORIGIN)}, {sql_quote(source_ref)}
        from t;

        with t as (select id from tenants where slug={sql_quote(TENANT)} limit 1)
        insert into manual_themes (tenant_id, theme, objective, format_targets, notes)
        select t.id, {sql_quote(question)}, {sql_quote('Transformar dúvida pesquisada na internet em conteúdo educativo, ético e gerador de lead qualificado.')},
               {sql_quote(json.dumps(['blog','reels','carrossel','stories','estatico'], ensure_ascii=False))}::jsonb,
               {sql_quote(ORIGIN + ' | ' + json.dumps(meta, ensure_ascii=False))}
        from t;

        with t as (select id from tenants where slug={sql_quote(TENANT)} limit 1)
        insert into opportunities (tenant_id, title, thesis, angle, score, source_type, status)
        select t.id, {sql_quote(question)}, {sql_quote('Dúvida pública recorrente indica dor/desejo do avatar mestre IVS.')},
               {sql_quote(f'{category}: {pain} → {desire}')}, {max(score, 10):.2f}, {sql_quote(ORIGIN)}, 'new'
        from t;
        """)
        counts[domain] += 1
        examples_by_domain[domain].append(meta)

    for domain, examples in examples_by_domain.items():
        category = DOMAIN_LABELS.get(domain, domain)
        score = sum(float(str(e.get('score') or 0)) for e in examples) / max(len(examples), 1)
        psql(f"""
        with t as (select id from tenants where slug={sql_quote(TENANT)} limit 1)
        insert into content_pattern_library (tenant_id, pattern_key, pattern_type, label, score, examples)
        select t.id, {sql_quote(ORIGIN + ':' + domain)}, 'pain_desire_search_cluster', {sql_quote('Dores e desejos pesquisados — ' + category)}, {score:.2f}, {sql_quote(json.dumps(examples, ensure_ascii=False))}::jsonb
        from t
        on conflict (tenant_id, pattern_key) do update set
          label=excluded.label,
          score=excluded.score,
          examples=excluded.examples,
          updated_at=now();
        """)

    summary_sql = f"""
    with t as (select id from tenants where slug={sql_quote(TENANT)} limit 1)
    select 'story_themes', count(*) from story_themes,t where story_themes.tenant_id=t.id and source={sql_quote(ORIGIN)}
    union all
    select 'themes', count(*) from themes,t where themes.tenant_id=t.id and source_origin={sql_quote(ORIGIN)}
    union all
    select 'manual_themes', count(*) from manual_themes,t where manual_themes.tenant_id=t.id and notes like {sql_quote('%' + ORIGIN + '%')}
    union all
    select 'opportunities', count(*) from opportunities,t where opportunities.tenant_id=t.id and source_type={sql_quote(ORIGIN)}
    union all
    select 'content_pattern_library', count(*) from content_pattern_library,t where content_pattern_library.tenant_id=t.id and pattern_key like {sql_quote(ORIGIN + ':%')};
    """
    summary = psql(summary_sql)
    print(json.dumps({'origin': ORIGIN, 'input_rows': len(rows), 'counts_by_domain': counts, 'db_summary_raw': summary}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
