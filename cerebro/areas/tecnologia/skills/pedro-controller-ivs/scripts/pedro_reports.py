#!/usr/bin/env python3
"""Pedro — Reports gerenciais a partir de staging financeiro consolidado.

Entrada esperada: CSV padrão do Pedro, já normalizado/conciliado.
Não escreve no Omie. Gera reports executivos, auditoria, DRE preliminar e receita recuperável.
"""
from __future__ import annotations
import argparse, csv, json, re
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path
from datetime import datetime

REQUIRED = ["data","descricao","valor","natureza","tipo_pagamento","categoria_omie","conta_corrente_omie","cliente_fornecedor","documento","comprovante","cod_titulo_omie","status_conferencia","observacao"]

STATUS_OK = {"revisado_maria", "aprovado_tiaro", "ja_existe_omie"}

def br_money(v: Decimal) -> str:
    s = f"{v:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    return f"R$ {s}"

def parse_money(v):
    raw=(v or '').strip().replace('R$','').replace(' ','')
    if ',' in raw:
        raw=raw.replace('.','').replace(',','.')
    try:
        return abs(Decimal(raw))
    except InvalidOperation:
        return Decimal('0')

def month_key(date_s):
    m=re.search(r'(\d{4})[-/](\d{1,2})', date_s or '')
    if m: return f"{m.group(1)}-{int(m.group(2)):02d}"
    m=re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', date_s or '')
    if m: return f"{m.group(3)}-{int(m.group(2)):02d}"
    return 'sem_data'

def load_rows(path):
    with Path(path).open(newline='', encoding='utf-8-sig') as f:
        reader=csv.DictReader(f)
        missing=[h for h in REQUIRED if h not in (reader.fieldnames or [])]
        if missing: raise SystemExit('Colunas ausentes: '+', '.join(missing))
        rows=[]
        for i,r in enumerate(reader, start=2):
            r['_linha']=i
            r['_valor_decimal']=parse_money(r.get('valor'))
            r['_mes']=month_key(r.get('data'))
            r['_natureza']=(r.get('natureza') or '').upper().strip()
            r['_status']=(r.get('status_conferencia') or 'pendente').strip()
            rows.append(r)
        return rows

def analyze(rows):
    total_r=Decimal('0'); total_p=Decimal('0')
    by_month=defaultdict(lambda: {'R':Decimal('0'),'P':Decimal('0'),'count':0})
    by_cat=defaultdict(lambda: {'R':Decimal('0'),'P':Decimal('0'),'count':0})
    by_account=defaultdict(lambda: {'R':Decimal('0'),'P':Decimal('0'),'count':0})
    issues=[]; recover=[]; duplicates=defaultdict(list)
    for r in rows:
        val=r['_valor_decimal']; nat=r['_natureza']
        if nat=='R': total_r += val
        elif nat=='P': total_p += val
        by_month[r['_mes']][nat if nat in ('R','P') else 'P'] += val
        by_month[r['_mes']]['count'] += 1
        cat=r.get('categoria_omie') or 'sem_categoria'
        acct=r.get('conta_corrente_omie') or 'sem_conta'
        by_cat[cat][nat if nat in ('R','P') else 'P'] += val; by_cat[cat]['count']+=1
        by_account[acct][nat if nat in ('R','P') else 'P'] += val; by_account[acct]['count']+=1
        key=(r.get('data'), r.get('descricao','').strip().lower(), str(val), nat)
        duplicates[key].append(r)
        alerts=[]
        if not r.get('categoria_omie'): alerts.append('sem categoria')
        if not r.get('conta_corrente_omie'): alerts.append('sem conta corrente')
        if not r.get('comprovante'): alerts.append('sem comprovante')
        if r['_status'] not in STATUS_OK: alerts.append('não revisado/aprovado')
        if nat not in ('R','P'): alerts.append('natureza inválida')
        if alerts: issues.append({'linha':r['_linha'],'data':r.get('data'),'descricao':r.get('descricao'),'valor':str(val),'alertas':alerts})
        obs=(r.get('observacao') or '').lower(); st=r['_status'].lower()
        if nat=='R' and any(x in obs+' '+st for x in ['vencido','atras','inadimpl','pendente','receber']):
            recover.append({'linha':r['_linha'],'data':r.get('data'),'descricao':r.get('descricao'),'valor':str(val),'status':r['_status']})
    dup_list=[]
    for k,items in duplicates.items():
        if len(items)>1:
            dup_list.append({'chave':k,'linhas':[x['_linha'] for x in items], 'valor':str(items[0]['_valor_decimal'])})
    return {'totals':{'R':total_r,'P':total_p,'saldo':total_r-total_p}, 'by_month':by_month, 'by_cat':by_cat, 'by_account':by_account, 'issues':issues, 'recover':recover, 'duplicates':dup_list}

def table_amounts(d):
    lines=[]
    for k,v in sorted(d.items()):
        lines.append(f"| {k} | {v['count']} | {br_money(v['R'])} | {br_money(v['P'])} | {br_money(v['R']-v['P'])} |")
    return lines

def write_reports(rows, a, out):
    out=Path(out); out.mkdir(parents=True, exist_ok=True)
    now=datetime.now().strftime('%d/%m/%Y %H:%M')
    # JSON
    serial={
        'gerado_em': now,
        'linhas': len(rows),
        'totais': {k:str(v) for k,v in a['totals'].items()},
        'issues_count': len(a['issues']),
        'duplicidades_count': len(a['duplicates']),
        'receita_recuperavel_count': len(a['recover']),
        'issues': a['issues'][:1000],
        'duplicidades': a['duplicates'][:500],
        'receita_recuperavel': a['recover'][:500],
    }
    (out/'report-data.json').write_text(json.dumps(serial, ensure_ascii=False, indent=2), encoding='utf-8')
    # Executivo
    md=["# Pedro — Report executivo financeiro", "", f"Gerado em: {now}", f"Linhas analisadas: {len(rows)}", "", "## Resumo executivo",
        f"- Recebimentos consolidados: **{br_money(a['totals']['R'])}**.",
        f"- Pagamentos consolidados: **{br_money(a['totals']['P'])}**.",
        f"- Saldo líquido movimentado: **{br_money(a['totals']['saldo'])}**.",
        f"- Alertas de auditoria: **{len(a['issues'])}**.",
        f"- Possíveis duplicidades: **{len(a['duplicates'])}**.",
        "", "## Por mês", "| Mês | Lançamentos | Recebimentos | Pagamentos | Líquido |", "|---|---:|---:|---:|---:|", *table_amounts(a['by_month']),
        "", "## Por categoria", "| Categoria | Lançamentos | Recebimentos | Pagamentos | Líquido |", "|---|---:|---:|---:|---:|", *table_amounts(a['by_cat']),
        "", "## Decisão necessária", "- Maria: revisar alertas de categoria, conta corrente e comprovantes.", "- Tiaro: aprovar regras novas, ajustes sensíveis e qualquer escrita em Omie.",
        "", "## Próximo passo recomendado", "- Rodar conciliação Omie read-only antes de qualquer lançamento definitivo."]
    (out/'REPORT_EXECUTIVO.md').write_text('\n'.join(md)+'\n', encoding='utf-8')
    # Auditoria
    aud=["# Pedro — Report de auditoria", "", f"Gerado em: {now}", "", "## Alertas principais"]
    if a['issues']:
        for x in a['issues'][:200]: aud.append(f"- Linha {x['linha']} · {x['data']} · {x['descricao']} · {br_money(Decimal(x['valor']))}: {', '.join(x['alertas'])}")
    else: aud.append('- Sem alertas estruturais no CSV.')
    aud += ["", "## Possíveis duplicidades"]
    if a['duplicates']:
        for x in a['duplicates'][:100]: aud.append(f"- Linhas {x['linhas']} · valor {br_money(Decimal(x['valor']))} · chave {x['chave']}")
    else: aud.append('- Nenhuma duplicidade simples detectada.')
    (out/'REPORT_AUDITORIA.md').write_text('\n'.join(aud)+'\n', encoding='utf-8')
    # Receita recuperável
    rec=["# Pedro — Radar de receita recuperável", "", f"Gerado em: {now}", "", f"Itens sinalizados: {len(a['recover'])}"]
    total_rec=sum((Decimal(x['valor']) for x in a['recover']), Decimal('0'))
    rec.append(f"Valor potencial sinalizado: **{br_money(total_rec)}**")
    rec += ["", "## Itens"]
    if a['recover']:
        for x in a['recover'][:200]: rec.append(f"- Linha {x['linha']} · {x['data']} · {x['descricao']} · {br_money(Decimal(x['valor']))} · status {x['status']}")
    else: rec.append('- Nenhum item sinalizado por observação/status. Após integração Omie boletos, este relatório ficará mais preciso.')
    (out/'REPORT_RECEITA_RECUPERAVEL.md').write_text('\n'.join(rec)+'\n', encoding='utf-8')
    # Investimentos
    inv=["# Pedro — Análise preliminar de capacidade de investimento", "", f"Gerado em: {now}", "", "## Leitura preliminar", f"- Saldo líquido movimentado no período: **{br_money(a['totals']['saldo'])}**.", "- Este relatório ainda não considera saldo inicial, compromissos futuros, impostos, folha, sazonalidade e reserva mínima.", "", "## Guardrail", "Pedro não recomenda aplicação executável. Apenas estrutura cenários para Tiaro.", "", "## Próximo passo", "Definir reserva mínima de caixa, compromissos fixos mensais e meta de liquidez antes de qualquer análise de investimento."]
    (out/'REPORT_INVESTIMENTOS_PRELIMINAR.md').write_text('\n'.join(inv)+'\n', encoding='utf-8')
    print(out)

def main():
    ap=argparse.ArgumentParser(description='Gera reports Pedro a partir de CSV consolidado')
    ap.add_argument('csv_path')
    ap.add_argument('--out', default=None)
    args=ap.parse_args()
    rows=load_rows(args.csv_path)
    a=analyze(rows)
    out=args.out or (Path(args.csv_path).with_suffix('').as_posix() + '_reports')
    write_reports(rows,a,out)

if __name__=='__main__': main()
