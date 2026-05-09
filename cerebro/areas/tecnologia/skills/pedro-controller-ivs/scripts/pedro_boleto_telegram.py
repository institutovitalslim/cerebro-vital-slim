#!/usr/bin/env python3
"""Pedro — leitura segura de boletos escaneados recebidos pelo Telegram.

Extrai OCR/barcode, monta draft de conta a pagar e NÃO escreve no Omie.
Escrita futura exige validação humana e schema Omie confirmado.
"""
from __future__ import annotations
import argparse, json, re, subprocess, tempfile, os
from pathlib import Path
from decimal import Decimal, InvalidOperation
from datetime import datetime

MONEY_RE = re.compile(r'(?:R\$\s*)?(\d{1,3}(?:\.\d{3})*,\d{2}|\d+[,\.]\d{2})')
DATE_RE = re.compile(r'\b(\d{2}/\d{2}/\d{4})\b')
DIGITABLE_RE = re.compile(r'(?:(?:\d[\.\s-]*){44,48})')
CNPJ_RE = re.compile(r'\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b')

def run(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    except Exception as e:
        class R: returncode=1; stdout=''; stderr=str(e)
        return R()

def ocr_image(path: Path) -> str:
    r = run(['tesseract', str(path), 'stdout', '-l', 'por+eng', '--psm', '6'])
    return (r.stdout or '').strip()

def ocr_pdf(path: Path) -> str:
    with tempfile.TemporaryDirectory() as td:
        prefix=str(Path(td)/'page')
        r=run(['pdftoppm','-png','-r','200',str(path),prefix])
        texts=[]
        for img in sorted(Path(td).glob('page-*.png')):
            texts.append(ocr_image(img))
        return '\n\n'.join(t for t in texts if t)

def read_text(path: Path) -> str:
    if path.suffix.lower() in ['.txt','.md','.ocr']:
        return path.read_text(encoding='utf-8', errors='ignore')
    if path.suffix.lower()=='.pdf': return ocr_pdf(path)
    return ocr_image(path)

def barcode(path: Path) -> list[str]:
    if path.suffix.lower()=='.pdf': return []
    r=run(['zbarimg','--quiet','--raw',str(path)])
    if r.returncode==0 and r.stdout.strip(): return [x.strip() for x in r.stdout.splitlines() if x.strip()]
    return []

def norm_digits(s): return re.sub(r'\D','',s or '')

def parse_money(s):
    raw=(s or '').replace('R$','').strip()
    if ',' in raw: raw=raw.replace('.','').replace(',','.')
    try: return str(Decimal(raw))
    except InvalidOperation: return None

def choose_amount(text):
    # Prefer explicit monetary amounts near labels, avoiding linha digitavel/barcode fragments.
    lines=[l.strip() for l in text.splitlines() if l.strip()]
    priority=[]; fallback=[]
    for l in lines:
        low=l.lower()
        if 'linha digit' in low or 'código de barras' in low or 'codigo de barras' in low:
            continue
        vals=[]
        for m in MONEY_RE.finditer(l):
            val=parse_money(m.group(1))
            if val:
                d=Decimal(val)
                if Decimal('0.01') <= d <= Decimal('1000000'):
                    vals.append(d)
        if not vals:
            continue
        if 'r$' in low or 'valor' in low or 'documento' in low or 'cobrado' in low:
            priority.extend(vals)
        else:
            fallback.extend(vals)
    if priority:
        return str(max(priority))
    return str(max(fallback)) if fallback else None

def choose_due_date(text):
    dates=DATE_RE.findall(text)
    # prefer dates near vencimento
    low=text.lower()
    for d in dates:
        idx=low.find(d)
        window=low[max(0,idx-40):idx+40]
        if 'venc' in window or 'vcto' in window or 'pagamento' in window:
            return d
    return dates[0] if dates else None

def choose_payee(text):
    lines=[l.strip() for l in text.splitlines() if len(l.strip())>3]
    keywords=['beneficiário','beneficiario','cedente','favorecido','fornecedor','pagador']
    for i,l in enumerate(lines):
        low=l.lower()
        if any(k in low for k in keywords) and i+1 < len(lines):
            nxt=lines[i+1]
            if not re.search(r'cpf|cnpj|pagador|sacado', nxt.lower()): return nxt[:120]
    # fallback: first uppercase-ish non-bank line
    for l in lines[:15]:
        if len(l) > 8 and not re.search(r'banco|boleto|recibo|pagador|vencimento|ag[êe]ncia|c[oó]digo', l.lower()):
            return l[:120]
    return None

def extract(path: Path):
    text=read_text(path)
    bars=barcode(path)
    digitables=[]
    for b in bars:
        d=norm_digits(b)
        if len(d) in (44,47,48): digitables.append(d)
    for m in DIGITABLE_RE.finditer(text):
        d=norm_digits(m.group(0))
        if len(d) in (44,47,48): digitables.append(d)
    # unique
    digitables=list(dict.fromkeys(digitables))
    cnpjs=CNPJ_RE.findall(text)
    amount=choose_amount(text)
    due=choose_due_date(text)
    payee=choose_payee(text)
    missing=[]
    if not digitables: missing.append('linha_digitavel_ou_codigo_barras')
    if not amount: missing.append('valor')
    if not due: missing.append('vencimento')
    if not payee: missing.append('fornecedor_beneficiario')
    confidence = 'alta' if len(missing)==0 else ('media' if len(missing)<=2 else 'baixa')
    draft={
        'tipo_documento':'boleto_contas_a_pagar',
        'origem':'telegram_scan_ou_pdf',
        'arquivo':str(path),
        'extraido_em':datetime.now().isoformat(timespec='seconds'),
        'fornecedor_beneficiario':payee,
        'cnpj_detectado': cnpjs[0] if cnpjs else None,
        'vencimento':due,
        'valor':amount,
        'linha_digitavel_ou_codigo_barras': digitables[0] if digitables else None,
        'categoria_omie': None,
        'conta_corrente_omie': None,
        'data_previsao_pagamento': due,
        'descricao_sugerida': f"Boleto {payee or 'fornecedor não identificado'}"[:180],
        'status':'draft_requires_maria_tiaro_approval',
        'confianca_extracao':confidence,
        'campos_pendentes':missing + ['categoria_omie','conta_corrente_omie'],
        'guardrail':'Nenhuma escrita foi feita no Omie. Lançamento em contas a pagar exige aprovação explícita e validação anti-duplicidade.',
        'proposed_omie_contapagar_draft':{
            'endpoint':'financas/contapagar',
            'method':'IncluirContaPagar',
            'schema_status':'needs_live_omie_schema_validation_before_write',
            'payload_conceitual':{
                'fornecedor': payee,
                'data_vencimento': due,
                'valor_documento': amount,
                'codigo_barras': digitables[0] if digitables else None,
                'categoria': None,
                'observacao':'Draft gerado por Pedro a partir de boleto Telegram; revisar antes de lançar.'
            }
        },
        'ocr_text_excerpt': text[:3000]
    }
    return draft

def main():
    ap=argparse.ArgumentParser(description='Extrai boleto escaneado e gera draft seguro para contas a pagar')
    ap.add_argument('arquivo', help='imagem, PDF ou texto OCR do boleto')
    ap.add_argument('--out', default=None)
    args=ap.parse_args()
    path=Path(args.arquivo)
    draft=extract(path)
    out=Path(args.out) if args.out else path.with_suffix('.pedro_boleto_draft.json')
    out.write_text(json.dumps(draft, ensure_ascii=False, indent=2), encoding='utf-8')
    md=out.with_suffix('.md')
    md.write_text(f"""# Pedro — Draft de contas a pagar por boleto Telegram

Arquivo: `{path}`
Confiança: **{draft['confianca_extracao']}**

## Campos extraídos
- Fornecedor/beneficiário: {draft['fornecedor_beneficiario']}
- CNPJ detectado: {draft['cnpj_detectado']}
- Vencimento: {draft['vencimento']}
- Valor: {draft['valor']}
- Linha digitável/código: {draft['linha_digitavel_ou_codigo_barras']}

## Pendências
{chr(10).join('- '+x for x in draft['campos_pendentes'])}

## Guardrail
Nenhuma escrita foi feita no Omie. Antes de lançar em contas a pagar: validar fornecedor, categoria, conta corrente, duplicidade e aprovação Maria/Tiaro.
""", encoding='utf-8')
    print(md)

if __name__=='__main__': main()
