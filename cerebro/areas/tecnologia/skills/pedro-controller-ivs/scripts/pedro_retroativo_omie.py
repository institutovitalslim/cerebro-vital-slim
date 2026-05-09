#!/usr/bin/env python3
"""Pedro — Mutirão retroativo Omie.

Normaliza e valida CSV de extratos/pagamentos/recebimentos para staging.
Não escreve no Omie. Gera relatório para revisão humana.
"""
from __future__ import annotations
import argparse, csv, json, sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

REQUIRED = ["data","descricao","valor","natureza","tipo_pagamento","categoria_omie","conta_corrente_omie","cliente_fornecedor","documento","comprovante","cod_titulo_omie","status_conferencia","observacao"]
NATUREZAS = {"R":"recebimento", "P":"pagamento"}
STATUSES = {"pendente","revisado_maria","aprovado_tiaro","ja_existe_omie","possivel_duplicidade","precisa_categoria","precisa_comprovante","novo_lancamento_sugerido","nao_lancar"}

def money(v):
    v=(v or '').strip().replace('R$','').replace(' ','').replace('.','').replace(',','.') if ',' in (v or '') else (v or '').strip()
    try:
        d=Decimal(v)
        if d < 0: d = abs(d)
        return d
    except InvalidOperation:
        return None

def validate_row(row, idx):
    errors=[]; warnings=[]
    for k in REQUIRED:
        row.setdefault(k, "")
    if not row['data']:
        errors.append('data ausente')
    if not row['descricao']:
        errors.append('descrição ausente')
    val=money(row['valor'])
    if val is None or val == 0:
        errors.append('valor inválido/zero')
    nat=(row['natureza'] or '').upper().strip()
    if nat not in NATUREZAS:
        errors.append('natureza deve ser R ou P')
    status=(row['status_conferencia'] or 'pendente').strip()
    if status not in STATUSES:
        warnings.append(f'status não padrão: {status}')
    if not row['categoria_omie']:
        warnings.append('precisa_categoria')
    if not row['conta_corrente_omie']:
        warnings.append('precisa_conta_corrente')
    if not row['comprovante']:
        warnings.append('precisa_comprovante')
    return errors, warnings, val, nat

def main():
    ap=argparse.ArgumentParser(description='Valida CSV retroativo para staging Omie — sem escrita no Omie')
    ap.add_argument('csv_path')
    ap.add_argument('--out', default=None, help='Diretório de saída')
    args=ap.parse_args()
    src=Path(args.csv_path)
    out=Path(args.out or src.with_suffix('').as_posix() + '_pedro_out')
    out.mkdir(parents=True, exist_ok=True)
    rows=[]; issues=[]; totals={'R':Decimal('0'), 'P':Decimal('0')}
    with src.open(newline='', encoding='utf-8-sig') as f:
        reader=csv.DictReader(f)
        missing=[h for h in REQUIRED if h not in (reader.fieldnames or [])]
        if missing:
            print('ERRO: colunas ausentes: '+', '.join(missing), file=sys.stderr); sys.exit(2)
        for i,row in enumerate(reader, start=2):
            errs,warns,val,nat=validate_row(row,i)
            if val is not None and nat in totals: totals[nat]+=val
            row['_linha']=i; row['_erros']='; '.join(errs); row['_alertas']='; '.join(warns)
            rows.append(row)
            if errs or warns:
                issues.append({'linha':i,'descricao':row.get('descricao'), 'erros':errs, 'alertas':warns})
    # outputs
    with (out/'staging_validado.csv').open('w', newline='', encoding='utf-8') as f:
        fields=REQUIRED+['_linha','_erros','_alertas']
        w=csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows([{k:r.get(k,'') for k in fields} for r in rows])
    report={
        'arquivo_origem': str(src),
        'linhas': len(rows),
        'total_recebimentos': str(totals['R']),
        'total_pagamentos': str(totals['P']),
        'saldo_liquido_movimentado': str(totals['R']-totals['P']),
        'linhas_com_alerta_ou_erro': len(issues),
        'issues': issues[:500],
        'guardrail': 'Este relatório não escreveu no Omie. Revisão Maria/Tiaro obrigatória antes de qualquer lançamento.'
    }
    (out/'relatorio_pedro_retroativo.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    md=["# Relatório Pedro — staging retroativo Omie", "", f"Arquivo: `{src}`", f"Linhas: {len(rows)}", f"Total recebimentos: R$ {totals['R']}", f"Total pagamentos: R$ {totals['P']}", f"Saldo líquido movimentado: R$ {totals['R']-totals['P']}", f"Linhas com alerta/erro: {len(issues)}", "", "## Guardrail", "Nenhuma escrita foi feita no Omie. Revisão Maria/Tiaro obrigatória antes de qualquer lançamento.", "", "## Próximo passo", "Corrigir alertas, preencher categorias/contas/comprovantes e cruzar com Omie read-only para detectar duplicidades."]
    (out/'RELATORIO.md').write_text('\n'.join(md)+'\n', encoding='utf-8')
    print(out/'RELATORIO.md')

if __name__ == '__main__':
    main()
