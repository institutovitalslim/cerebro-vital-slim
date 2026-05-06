#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extrai_laudo.py -- Skill de extracao de dados de laudos laboratoriais
Formatos suportados:
  1. CRM/BA 1865  (Trade Center / Itapoan / SSA)  -> mais comum IVS
  2. Sabin Diagnosticos
  3. CRM-LPC / Hermes Pardini (tabela simples)
  4. DB Recife / Instituto Vital Slim
Uso:
  python3 extrai_laudo.py <caminho.pdf> [--json] [--sexo M|F] [--idade N]
"""

import re
import sys
import json
import argparse
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    sys.exit("Instale pdfplumber: pip install pdfplumber")


# ===========================================================================
# Utilitarios
# ===========================================================================

def normaliza(s):
    return re.sub(r'\s+', ' ', s).strip()


def parse_numero(s):
    """
    Converte string de numero brasileiro para float.
    Exemplos:
      "1.816"  -> 1816.0   (separador de milhar)
      "19,20"  -> 19.20
      "3,49"   -> 3.49
      "0,37"   -> 0.37
      "> 90"   -> 90.0
    """
    s = str(s).strip()
    # Remove prefixos comparativos
    s = re.sub(r'^[<><=!]+\s*', '', s)
    # Pega a primeira sequencia numerica com possivel virgula/ponto
    m = re.search(r'([\d]+(?:[.,][\d]+)?)', s)
    if not m:
        return None
    token = m.group(1)
    if ',' in token:
        # Virgula e decimal: "19,20" -> 19.20
        token = token.replace('.', '').replace(',', '.')
    elif '.' in token:
        # Ponto pode ser decimal OU milhar
        # Se exatamente 3 digitos apos o ponto -> milhar (ex: "1.816")
        if re.match(r'^\d+\.\d{3}$', token):
            token = token.replace('.', '')  # 1.816 -> 1816
        # else: ponto decimal normal (ex: "0.37")
    try:
        return float(token)
    except ValueError:
        return None


def classifica(valor, ref_texto, sexo='M', nome=''):
    if valor is None or not ref_texto:
        return '?'
    ref = ref_texto.replace(',', '.')

    # Tenta extrair faixa etaria ou por sexo + range especifico
    # Exemplo: "Masculino: 20 a 49 anos: 18.3 a 54.1 nmol/L"
    # Prioriza: para o sexo do paciente, pega o range com mais casas decimais
    sexo_kw = 'Masculino|Homem|Homens' if sexo == 'M' else 'Feminino|Mulher|Mulheres'
    m_sexo = re.search(
        r'(?:' + sexo_kw + r')[^:\n]*:\s*(?:\d+\s*a\s*\d+\s*anos\s*:\s*)?([\d.]+)\s*a\s*([\d.]+)',
        ref, re.I
    )
    if m_sexo:
        low, high = float(m_sexo.group(1)), float(m_sexo.group(2))
        if valor < low:
            return 'critico_baixo' if (low - valor) / low > 0.2 else 'baixo'
        if valor > high:
            return 'critico_alto' if (valor - high) / high > 0.3 else 'alto'
        return 'ok'

    # range "X.XX a Y.YY" ou "X.XX - Y.YY" com casas decimais (mais preciso, evita faixa etaria)
    m_ranges = list(re.finditer(r'([\d]+\.[\d]+)\s*[aA\-]\s*([\d]+\.[\d]+)', ref))
    if m_ranges:
        # para sexo especifico: pega o range que o valor mais provavelmente pertence
        for mr in m_ranges:
            low, high = float(mr.group(1)), float(mr.group(2))
            # descarta ranges claramente etarios (ex: 0.72 a 11.0 = TSH infantil)
            if low < 0.1 and high < 2.0:
                continue
            if valor < low:
                return 'critico_baixo' if (low - valor) / low > 0.2 else 'baixo'
            if valor > high:
                return 'critico_alto' if (valor - high) / high > 0.3 else 'alto'
            return 'ok'

    # range simples "X a Y" ou "X - Y" sem decimais — so usa se nao parece faixa etaria
    # Tenta com "a" primeiro
    for sep_pat in [r'\s*[aA]\s*', r'\s*-\s*']:
        m = re.search(r'([\d]+(?:\.\d+)?)\s*' + sep_pat.strip() + r'\s*([\d]+(?:\.\d+)?)', ref)
        if m:
            low, high = float(m.group(1)), float(m.group(2))
            # Heuristica: se high < 120 e ambos inteiros pequenos, provavelmente idade
            if low < 15 and high <= 90 and '.' not in m.group(0):
                continue  # provavel faixa etaria, tenta proximo
            if valor < low:
                return 'critico_baixo' if (low - valor) / low > 0.2 else 'baixo'
            if valor > high:
                return 'critico_alto' if (valor - high) / high > 0.3 else 'alto'
            return 'ok'
    # "< X"
    m = re.search(r'[<]\s*([\d.]+)', ref)
    if m:
        high = float(m.group(1))
        if valor > high:
            return 'critico_alto' if (valor - high) / high > 0.5 else 'alto'
        return 'ok'
    # "> X"
    m = re.search(r'[>]\s*([\d.]+)', ref)
    if m:
        low = float(m.group(1))
        if valor < low:
            return 'critico_baixo' if (low - valor) / low > 0.3 else 'baixo'
        return 'ok'
    # SUPERIOR
    m = re.search(r'SUPERIOR\s*(?:OU IGUAL A\s*)?([\d.]+)', ref, re.I)
    if m:
        low = float(m.group(1))
        if valor < low:
            return 'critico_baixo' if (low - valor) / low > 0.3 else 'baixo'
        return 'ok'
    # INFERIOR (A X  OU  OU IGUAL A X)
    m = re.search(r'INFERIOR\s*(?:OU\s+IGUAL\s+A\s*|A\s+)?([\d.]+)', ref, re.I)
    if m:
        high = float(m.group(1))
        if valor > high:
            return 'critico_alto' if (valor - high) / high > 0.5 else 'alto'
        return 'ok'
    # "Inferior a X" minusculo
    m = re.search(r'[Ii]nferior\s+a\s+([\d.]+)', ref, re.I)
    if m:
        high = float(m.group(1))
        if valor > high:
            return 'critico_alto' if (valor - high) / high > 0.5 else 'alto'
        return 'ok'
    return '?'


# ===========================================================================
# Deteccao de formato
# ===========================================================================

def detecta_formato(texto_pag1):
    t = texto_pag1[:2000].upper()
    if 'CRM/BA 1865' in t or 'LABORATORIO REGISTRADO NO CRM/BA' in t:
        return 'CRMBA1865'
    if 'SABIN' in t:
        return 'SABIN'
    if 'CRM-LPC' in t or 'VALORES ENCONTRADOS' in t:
        return 'CRMLPC'
    if 'DB RECIFE' in t or 'INSTITUTO VITAL SLIM' in t:
        return 'DBRECIFE'
    if 'RESULTADO:' in t or 'RESULTADO :' in t:
        return 'CRMBA1865'  # fallback generico
    return 'DESCONHECIDO'


# ===========================================================================
# Extrator CRM/BA 1865  (padrao principal IVS)
# ===========================================================================

SKIP_NAMES = {
    'HOMA BETA', 'GLICEMIA MEDIA ESTIMADA', 'ESTIMATIVA DA TAXA',
    'ASSINATURA DIGITAL', 'EXAME LIBERADO', 'EXAME REVISTO',
    'ESTE EXAME FOI', 'RESULTADO ANTERIOR',
}

# Palavras que nao sao nome de exame mesmo em maiusculas
NOT_EXAM_NAMES = {
    'CALCULADO', 'MATERIAL', 'SANGUE', 'SORO', 'URINA', 'LIQUOR',
    'NORMAL', 'REAGENTE', 'NAO REAGENTE', 'INDETERMINADO',
    'NOTA', 'NOTAS', 'ATENÇÃO', 'ATENCAO', 'REFERENCIA',
}

HEADER_RE = re.compile(
    r'^(?:Nome\s*:|RG\s*:|DN\s*:|Medico\s*:|Conveni|Unidade\s*:|'
    r'Responsavel|Endereco|Laboratorio|Pagina\s*:)',
    re.I | re.UNICODE
)


def extrai_crmba1865(pdf_path, sexo='M', idade=None):
    resultados = []
    paciente = {}
    paginas = []

    with pdfplumber.open(pdf_path) as pdf:
        for pg in pdf.pages:
            paginas.append(pg.extract_text() or '')

    pag1 = paginas[0] if paginas else ''

    # Info paciente
    for pat, chave in [
        (r'Nome\s*:([^\n]+)', 'nome'),
        (r'DN\s*:\s*(\S+)', 'dn'),
        (r'Medico\s*:([^\n]+?)(?:Convenio|Atendimento|\n)', 'medico'),
        (r'Atendimento\s*:\s*([\d/\-]+)', 'data_coleta'),
    ]:
        m = re.search(pat, pag1, re.I)
        if m:
            paciente[chave] = normaliza(m.group(1))

    # Limpa e concatena linhas de todas as paginas
    linhas = []
    sep_re = re.compile(r'^_{20,}$')
    hex_re = re.compile(r'^[0-9A-F]{20,}$')

    for texto in paginas:
        for ln in texto.splitlines():
            ln = ln.strip()
            if not ln:
                continue
            if sep_re.match(ln):
                linhas.append('---SEP---')
                continue
            if HEADER_RE.match(ln):
                continue
            if hex_re.match(ln):
                continue
            linhas.append(ln)

    # Percorre buscando "RESULTADO:"
    n = len(linhas)
    for i, ln in enumerate(linhas):
        m_res = re.match(r'RESULTADO\s*:\s*(.+)', ln, re.I)
        if not m_res:
            continue

        valor_texto = m_res.group(1).strip()

        # Nome do exame: retrocede ate SEP ou inicio
        nome_exame = ''
        j = i - 1
        while j >= 0 and linhas[j] != '---SEP---':
            cand = linhas[j].strip()
            cand_upper = cand.upper()
            # Linha candidata a nome de exame:
            # - comprimento > 3
            # - comeca com letra maiuscula
            # - nao e palavra conhecida de lixo
            # - nao tem ":" nos primeiros 20 chars
            if (len(cand) > 3
                    and re.match(r'^[A-Z\xC0-\xD6\xD8-\xDE]', cand)
                    and cand_upper not in NOT_EXAM_NAMES
                    and not re.match(
                        r'^(Metodo|Material|Coleta|Liberacao|CNES|'
                        r'Exame liberado|Este exame|Liberado eletron|'
                        r'Calculado$)', cand, re.I)
                    and ':' not in cand[:20]):
                nome_exame = cand
                break
            j -= 1

        if not nome_exame:
            continue

        # Pula nomes de lixo
        nome_upper = nome_exame.upper()
        if any(s in nome_upper for s in SKIP_NAMES):
            continue

        # Valor e unidade
        valor_num = parse_numero(valor_texto)
        # Extrai unidade: primeiro token nao-numerico apos o numero
        m_unit = re.search(r'[<>]?\s*[\d.,]+(?:/[\d.,]+)?\s+([a-zA-Z%/µμ\.\d]+(?:/[a-zA-Z\d\.µ]+)*)', valor_texto)
        if m_unit:
            unidade = m_unit.group(1).rstrip('*').rstrip(')').rstrip('(').strip()
        else:
            unidade = ''

        # Referencia: avanca ate encontrar ref ou SEP
        ref_partes = []
        k = i + 1
        coletando = False
        while k < n and k < i + 20:
            rl = linhas[k].strip()
            if rl == '---SEP---':
                break
            # Pula linhas tecnicas que nao sao referencia
            if re.match(
                r'^(?:Coleta|Liberacao|ASSINATURA|CNES|EXAME LIB|LIBERADO|'
                r'ESTE EXAME|Aten.o para|Nota:|Notas:|Referencia:|'
                r'Conversao de|Referencia:)',
                rl, re.I
            ):
                k += 1
                continue
            # Linha de inicio de ref
            if re.match(r'^Valor de refer', rl, re.I):
                coletando = True
                ref_partes.append(rl)
                k += 1
                continue
            if coletando:
                # Coleta linhas de referencia: valores, faixas etarias, sexo, etc.
                # Para quando encontra linha de historico (so numeros e datas)
                # ou linha claramente nao-referencial
                if re.match(r'^\d{2}/\d{2}/\d{2}', rl):  # data do historico
                    break
                if re.match(r'^[A-Z]{3}\s*\d+', rl):  # hash digital
                    break
                ref_partes.append(rl)
            k += 1

        ref_texto = normaliza(' '.join(ref_partes))
        status = classifica(valor_num, ref_texto, sexo, nome_upper)

        nome_norm = normaliza(nome_exame)

        # Evita duplicata do mesmo exame em unidades diferentes
        # (ex: Testosterona Livre em nmol/L e pg/mL na mesma pagina)
        # Mantém o resultado com mais digitos (mais preciso / unidade preferencial)
        existente = next((r for r in resultados if r['exame'] == nome_norm), None)
        if existente:
            # Se o novo valor esta em pg/mL e o existente em nmol/L (ou vice-versa),
            # manter pg/mL pois e mais interpretável clinicamente
            unit_pref = {'pg/mL', 'ng/dL', 'mUI/mL', 'µUI/mL', 'ng/mL', 'mg/dL', 'mg/L', 'µg/dL'}
            if unidade in unit_pref and existente.get('unidade') not in unit_pref:
                resultados.remove(existente)
            else:
                i += 1
                continue  # descarta o duplicado menos preferencial

        resultados.append({
            'exame': nome_norm,
            'valor_texto': normaliza(valor_texto),
            'valor': valor_num,
            'unidade': unidade,
            'referencia': ref_texto[:250],
            'status': status,
        })

    # Calcula HOMA-IR se nao foi extraido
    if not any('HOMA' in r['exame'].upper() for r in resultados):
        ins = next((r for r in resultados if 'INSULINA' in r['exame'].upper()), None)
        gli = next((r for r in resultados if r['exame'].upper() == 'GLICOSE'), None)
        if ins and gli and ins['valor'] and gli['valor']:
            homa = round((gli['valor'] * ins['valor']) / 405, 2)
            homa_s = 'critico_alto' if homa > 4.0 else ('alto' if homa > 2.7 else 'ok')
            resultados.append({
                'exame': 'HOMA-IR (CALCULADO)',
                'valor_texto': str(homa),
                'valor': homa,
                'unidade': '',
                'referencia': 'Normal ate 2.7',
                'status': homa_s,
            })

    # === Pos-processamento: correcoes para exames com referencias complexas ===
    for r in resultados:
        nome = r['exame'].upper()
        v = r['valor']
        if v is None:
            continue
        # Vitamina D: >100 e toxicidade, 30-100 e otimo, <20 e deficiente
        if 'VITAMINA D' in nome:
            if v > 100:
                r['status'] = 'alto'
            elif v >= 30:
                r['status'] = 'ok'
            elif v >= 20:
                r['status'] = 'ok'  # desejavel
            else:
                r['status'] = 'baixo'
        # IGF-1 / Somatomedina: adultos aprox 80-350 ng/mL
        elif 'SOMATOMEDINA' in nome or 'IGF' in nome:
            if 80 <= v <= 350:
                r['status'] = 'ok'
            elif v < 80:
                r['status'] = 'baixo'
            else:
                r['status'] = 'alto'
        # Zinco adultos: 60-130 ug/dL
        elif 'ZINCO' in nome:
            if 60 <= v <= 130:
                r['status'] = 'ok'
            elif v < 60:
                r['status'] = 'baixo'
            else:
                r['status'] = 'alto'
        # Magnésio adultos: 1.6-2.6 mg/dL
        elif 'MAGN' in nome:
            if 1.6 <= v <= 2.6:
                r['status'] = 'ok'
            elif v < 1.6:
                r['status'] = 'critico_baixo' if v < 1.2 else 'baixo'
            else:
                r['status'] = 'alto'
        # Progesterona masculino: 0 a 0.149 ng/mL (alta = raro, pode ser feminino)
        elif 'PROGESTERONA' in nome and sexo == 'M':
            if v <= 0.2:
                r['status'] = 'ok'
            elif v <= 1.0:
                r['status'] = 'alto'
            else:
                r['status'] = 'critico_alto'

    return paciente, resultados


# ===========================================================================
# Extrator CRM-LPC (tabela)
# ===========================================================================

def extrai_crmlpc(pdf_path, sexo='M', idade=None):
    resultados = []
    paciente = {}

    with pdfplumber.open(pdf_path) as pdf:
        textos = [pg.extract_text() or '' for pg in pdf.pages]

    pag1 = textos[0]
    m = re.search(r'Paciente\.+:\s*(.+?)(?:Sexo|$)', pag1, re.I)
    if m:
        paciente['nome'] = normaliza(m.group(1))

    texto_total = '\n'.join(textos)
    linhas = [l.strip() for l in texto_total.splitlines() if l.strip()]

    SKIP_LPC = {'ERITROGRAMA', 'LEUCOGRAMA', 'VALORES ENCONTRADOS', 'VALORES DE REFERENCIA'}

    for ln in linhas:
        if re.match(r'Paciente\.|Codigo\.|Cadastro\.|_{10,}', ln):
            continue
        # padrão: NOME valor ref
        m = re.match(
            r'^([A-ZÁÉÍÓÚÇÃ][A-ZÁÉÍÓÚÇÃ\s\-\(\)]+?)\s+'
            r'(<?[>]?\s*[\d,\.]+\s*(?:[a-zA-Zµ%/\.\d]+)?)\s+'
            r'(.{5,60})?$',
            ln
        )
        if not m:
            continue
        nome = normaliza(m.group(1))
        v_txt = m.group(2).strip()
        ref = (m.group(3) or '').strip()

        if nome.upper() in SKIP_LPC or len(nome) < 3:
            continue

        v_num = parse_numero(v_txt)
        status = classifica(v_num, ref, sexo, nome.upper())

        resultados.append({
            'exame': nome,
            'valor_texto': v_txt,
            'valor': v_num,
            'unidade': '',
            'referencia': ref,
            'status': status,
        })

    return paciente, resultados


# ===========================================================================
# Extrator Sabin
# ===========================================================================

def extrai_sabin(pdf_path, sexo='M', idade=None):
    # Sabin tem estrutura muito variada — usa o extrator generico CRMBA1865
    # com ajuste de deteccao de nome de exame
    return extrai_crmba1865(pdf_path, sexo, idade)


# ===========================================================================
# Grupos tematicos
# ===========================================================================

GRUPOS = {
    'Hemograma': [
        'HEMACIAS', 'HEMÁCIAS', 'HEMOGLOBINA', 'HEMATOCRITO', 'VCM', 'HCM', 'CHCM', 'RDW',
        'LEUCOCITOS', 'LEUCÓCITOS', 'SEGMENTADOS', 'NEUTROFILOS', 'NEUTRÓFILOS',
        'LINFOCITOS', 'LINFÓCITOS', 'MONOCITOS', 'MONÓCITOS', 'EOSINOFILOS',
        'BASOFILOS', 'PLAQUETAS', 'VPM', 'MPV', 'BASTONETES',
    ],
    'Glicemia / Insulina': [
        'GLICOSE', 'INSULINA', 'HEMOGLOBINA GLICADA', 'HBA1C', 'HOMA',
    ],
    'Lipidograma': [
        'TRIGLICERIDES', 'TRIGLICÉRIDES', 'COLESTEROL', 'APOLIPOPROTEINA', 'APOLIPOPROTEÍNA',
    ],
    'Inflamacao / Coagulacao': [
        'PROTEINA C REATIVA', 'PROTEÍNA C REATIVA', 'PCR', 'HOMOCISTEINA', 'HOMOCISTEÍNA',
        'FIBRINOGENIO', 'FIBRINOGÊNIO', 'VHS', 'DESIDROGENASE', 'LDH',
    ],
    'Figado / Rins': [
        'UREIA', 'UREIA', 'CREATININA', 'ACIDO URICO', 'ÁCIDO ÚRICO',
        'TGO', 'TGP', 'TRANSAMINASE', 'GAMA GLUTAMIL', 'GGT',
        'FOSFATASE ALCALINA', 'BILIRRUBINA', 'TAXA DE FILTRAC',
    ],
    'Minerais': [
        'SODIO', 'SÓDIO', 'POTASSIO', 'POTÁSSIO', 'MAGNESIO', 'MAGNÉSIO',
        'CALCIO', 'CÁLCIO', 'FOSFORO', 'FÓSFORO', 'ZINCO',
        'FERRO SERICO', 'FERRO SÉRICO', 'FERRITINA', 'TRANSFERRINA',
    ],
    'Vitaminas': [
        'VITAMINA D', 'VITAMINA B12', 'VITAMINA C', 'VITAMINA B1',
        'ACIDO FOLICO', 'ÁCIDO FÓLICO', 'PARATORMONIO', 'PARATORMÔNIO', 'PTH',
    ],
    'Tireoide': [
        'TSH', 'T4 LIVRE', 'T3 HORMONIO', 'T3 LIVRE', 'T4 TOTAL', 'TIREOESTIMULANTE',
        'TRIIODOTIRONINA',
    ],
    'Hormonios': [
        'TESTOSTERONA', 'ESTRADIOL', 'PROGESTERONA', 'PROLACTINA',
        'LH -', 'LH -', 'LH', 'FSH', 'CORTISOL', 'SHBG', 'GLOBULINA LIGADORA',
        'DHEA', 'DHT', 'DIHIDROTESTOSTERONA', 'IGF', 'ANDROSTENEDIONA',
    ],
    'Outros': [],
}


def agrupa(resultados):
    out = {g: [] for g in GRUPOS}
    for r in resultados:
        nome = r['exame'].upper()
        alocado = False
        for grupo, kws in GRUPOS.items():
            if grupo == 'Outros':
                continue
            for kw in kws:
                if kw in nome:
                    out[grupo].append(r)
                    alocado = True
                    break
            if alocado:
                break
        if not alocado:
            out['Outros'].append(r)
    return out


# ===========================================================================
# Saida formatada
# ===========================================================================

STATUS_LABEL = {
    'ok': 'OK',
    'alto': 'ALTO',
    'baixo': 'BAIXO',
    'critico_alto': '** CRITICO ALTO **',
    'critico_baixo': '** CRITICO BAIXO **',
    '?': '',
}


def imprime(paciente, resultados):
    print('\n' + '=' * 70)
    print('  PACIENTE : ' + paciente.get('nome', 'N/A'))
    print('  MEDICO   : ' + paciente.get('medico', 'N/A'))
    print('  COLETA   : ' + paciente.get('data_coleta', 'N/A'))
    print('  FORMATO  : ' + paciente.get('formato_detectado', 'N/A'))
    print('=' * 70)

    grupos = agrupa(resultados)
    for grupo, itens in grupos.items():
        if not itens:
            continue
        print('\n--- ' + grupo + ' ' + '-' * (60 - len(grupo)))
        for r in itens:
            s = STATUS_LABEL.get(r['status'], r['status'])
            # Mostra valor numerico formatado se disponivel, caso contrario valor_texto
            if r['valor'] is not None:
                v_display = str(r['valor'])
            else:
                v_display = r['valor_texto'][:12]
            u = r.get('unidade', '')[:10]
            linha = '  {:<45} {:>12} {:<12} {}'.format(
                r['exame'][:45],
                v_display[:12],
                u,
                s,
            )
            print(linha)

    alterados = [r for r in resultados if r['status'] not in ('ok', '?')]
    if alterados:
        print('\n=== ALTERADOS ({}) ==='.format(len(alterados)))
        for r in alterados:
            s = STATUS_LABEL.get(r['status'], r['status'])
            v = str(r['valor']) if r['valor'] is not None else r['valor_texto'][:12]
            print('  {:45} {:>12} {:<10} -> {}'.format(
                r['exame'][:45],
                v[:12],
                r.get('unidade', '')[:10],
                s,
            ))
    print()


# ===========================================================================
# Ponto de entrada
# ===========================================================================

def extrai(pdf_path, sexo='M', idade=None, verbose=True):
    p = Path(pdf_path)
    if not p.exists():
        raise FileNotFoundError('PDF nao encontrado: ' + str(pdf_path))

    with pdfplumber.open(str(p)) as pdf:
        pag1 = pdf.pages[0].extract_text() or ''

    fmt = detecta_formato(pag1)
    if verbose:
        print('[extrai_laudo] Formato: ' + fmt + ' | Arquivo: ' + p.name)

    if fmt == 'CRMLPC':
        paciente, resultados = extrai_crmlpc(str(p), sexo, idade)
    elif fmt == 'SABIN':
        paciente, resultados = extrai_sabin(str(p), sexo, idade)
    else:
        paciente, resultados = extrai_crmba1865(str(p), sexo, idade)

    paciente['formato_detectado'] = fmt
    grupos = agrupa(resultados)
    return paciente, resultados, grupos


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='Extrai laudos laboratoriais')
    ap.add_argument('pdf', help='Caminho do PDF')
    ap.add_argument('--json', action='store_true', help='Saida em JSON')
    ap.add_argument('--sexo', default='M', choices=['M', 'F'])
    ap.add_argument('--idade', type=int, default=None)
    args = ap.parse_args()

    paciente, resultados, grupos = extrai(args.pdf, args.sexo, args.idade)

    if args.json:
        out = {
            'paciente': paciente,
            'total_exames': len(resultados),
            'exames': resultados,
        }
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        imprime(paciente, resultados)
