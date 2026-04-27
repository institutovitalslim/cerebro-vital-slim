#!/usr/bin/env python3
"""
Extrai e classifica resultados de exames laboratoriais de PDFs do Google Drive.

Uso:
    python3 extrair_exames_pdf.py <drive_file_id> [--nome "arquivo.pdf"]

Saida: JSON estruturado com grupos de exames, status e hero_alerts para a apresentacao HTML.
"""

import sys
import os
import re
import json
import subprocess
import tempfile
import unicodedata
from pathlib import Path

GOG_ACCOUNT = "medicalcontabilidade@gmail.com"
GOG_ENV = {"GOG_ACCOUNT": GOG_ACCOUNT, "HOME": "/root", "GOG_KEYRING_PASSWORD": "Tf100314@!"}

# ---------------------------------------------------------------------------
# Mapeamento: nome canonico -> grupo, hint clinico, referencia padrao
# ---------------------------------------------------------------------------

EXAM_CATALOG = {
    # --- Metabolico ---
    "Glicose":               ("metabolico", "mg/dL", None, None),
    "HbA1c":                 ("metabolico", "%",     None, 5.7),
    "Insulina Basal":        ("metabolico", "mU/mL", 2.6,  24.9),
    "HOMA-IR":               ("metabolico", "",      None, 2.7),
    "Frutosamina":           ("metabolico", "umol/L",None, 285.0),
    # --- Lipidico ---
    "Colesterol Total":      ("lipidico",   "mg/dL", None, 190.0),
    "HDL":                   ("lipidico",   "mg/dL", 40.0, None),
    "LDL":                   ("lipidico",   "mg/dL", None, 130.0),
    "VLDL":                  ("lipidico",   "mg/dL", None, 30.0),
    "Triglicerideos":        ("lipidico",   "mg/dL", None, 150.0),
    "Apolipoproteina B":     ("lipidico",   "g/L",   None, 1.0),
    "Lipoproteina a":        ("lipidico",   "mg/dL", None, 30.0),
    # --- Hormonal ---
    "TSH":                   ("hormonal",   "uUI/mL",0.27, 4.20),
    "T4 Livre":              ("hormonal",   "ng/dL", 0.86, 2.49),
    "T3 Livre":              ("hormonal",   "pg/mL", 2.5,  3.9),
    "T3 Total":              ("hormonal",   "ng/dL", 60.0, 200.0),
    "T4 Total":              ("hormonal",   "ug/dL", 5.1,  14.1),
    "LH":                    ("hormonal",   "mUI/mL",1.7,  8.6),
    "FSH":                   ("hormonal",   "mUI/mL",1.5,  12.4),
    "Testosterona Total":    ("hormonal",   "ng/dL", 249.0,836.0),
    "Testosterona Livre":    ("hormonal",   "pg/mL", 34.0, 245.0),
    "Testosterona Biodisponivel": ("hormonal","ng/dL",103.0,420.0),
    "Estradiol":             ("hormonal",   "pg/mL", None, None),
    "Progesterona":          ("hormonal",   "ng/mL", None, None),
    "DHEA-S":                ("hormonal",   "ug/dL", 80.0, 560.0),
    "Cortisol":              ("hormonal",   "ug/dL", 6.2,  19.4),
    "Prolactina":            ("hormonal",   "ng/mL", 4.1,  18.4),
    "GH":                    ("hormonal",   "ng/mL", None, 3.0),
    "IGF-1":                 ("hormonal",   "ng/mL", None, None),
    "SHBG":                  ("hormonal",   "nmol/L",13.3, 89.5),
    "Insulina":              ("hormonal",   "mU/mL", 2.6,  24.9),
    # --- Hepatico ---
    "TGO":                   ("hepatico",   "U/L",   None, 40.0),
    "TGP":                   ("hepatico",   "U/L",   None, 41.0),
    "GGT":                   ("hepatico",   "U/L",   None, 61.0),
    "Fosfatase Alcalina":    ("hepatico",   "U/L",   None, 117.0),
    "Albumina":              ("hepatico",   "g/dL",  3.5,  5.0),
    "Proteinas Totais":      ("hepatico",   "g/dL",  6.4,  8.3),
    "Bilirrubina Total":     ("hepatico",   "mg/dL", None, 1.2),
    "Bilirrubina Direta":    ("hepatico",   "mg/dL", None, 0.3),
    "Bilirrubina Indireta":  ("hepatico",   "mg/dL", None, 1.0),
    # --- Renal ---
    "Creatinina":            ("renal",      "mg/dL", 0.7,  1.2),
    "Ureia":                 ("renal",      "mg/dL", 15.0, 45.0),
    "Acido Urico":           ("renal",      "mg/dL", None, 7.2),
    "TFG":                   ("renal",      "mL/min",60.0, None),
    "Microalbuminuria":      ("renal",      "mg/L",  None, 30.0),
    # --- Hemograma ---
    "Hemoglobina":           ("hemograma",  "g/dL",  13.5, 17.5),
    "Hematocrito":           ("hemograma",  "%",     41.0, 53.0),
    "Eritrocitos":           ("hemograma",  "M/uL",  4.5,  5.9),
    "VCM":                   ("hemograma",  "fL",    80.0, 100.0),
    "HCM":                   ("hemograma",  "pg",    27.0, 33.0),
    "CHCM":                  ("hemograma",  "g/dL",  32.0, 36.0),
    "RDW":                   ("hemograma",  "%",     None, 15.0),
    "Leucocitos":            ("hemograma",  "/uL",   4000.0,10000.0),
    "Neutrofilos":           ("hemograma",  "%",     45.0, 70.0),
    "Linfocitos":            ("hemograma",  "%",     20.0, 40.0),
    "Monocitos":             ("hemograma",  "%",     2.0,  10.0),
    "Eosinofilos":           ("hemograma",  "%",     None, 5.0),
    "Basofilos":             ("hemograma",  "%",     None, 1.0),
    "Plaquetas":             ("hemograma",  "/uL",   150000.0,450000.0),
    "VPM":                   ("hemograma",  "fL",    7.5,  12.5),
    # --- Vitaminas e Minerais ---
    "Vitamina D":            ("vitaminas",  "ng/mL", 30.0, None),
    "Vitamina B12":          ("vitaminas",  "pg/mL", 211.0,946.0),
    "Acido Folico":          ("vitaminas",  "ng/mL", 4.6,  None),
    "Ferro Serico":          ("vitaminas",  "ug/dL", 59.0, 158.0),
    "Ferritina":             ("vitaminas",  "ng/mL", 30.0, 400.0),
    "Zinco":                 ("vitaminas",  "ug/dL", 70.0, 120.0),
    "Magnesio":              ("vitaminas",  "mg/dL", 1.6,  2.6),
    "Calcio":                ("vitaminas",  "mg/dL", 8.5,  10.2),
    "Fosforo":               ("vitaminas",  "mg/dL", 2.5,  4.5),
    "Sodio":                 ("vitaminas",  "mEq/L", 136.0,146.0),
    "Potassio":              ("vitaminas",  "mEq/L", 3.5,  5.0),
    # --- Inflamacao ---
    "PCR":                   ("inflamacao", "mg/L",  None, 5.0),
    "PCR Ultrassensivel":    ("inflamacao", "mg/L",  None, 3.0),
    "VHS":                   ("inflamacao", "mm/h",  None, 15.0),
    "Fibrinogenio":          ("inflamacao", "mg/dL", 150.0,400.0),
    # --- Tireoidite ---
    "Anti-TPO":              ("autoimune",  "UI/mL", None, 35.0),
    "Anti-TG":               ("autoimune",  "UI/mL", None, 40.0),
    "PSA Total":             ("oncologico", "ng/mL", None, 4.0),
    "PSA Livre":             ("oncologico", "ng/mL", None, None),
}

GROUP_META = {
    "metabolico":  ("Perfil metabólico e glicêmico",    "A célula que não escuta a insulina é o ponto central do plano."),
    "lipidico":    ("Perfil lipídico",                  "Gordura circulante — risco cardiovascular e inflamatório."),
    "hormonal":    ("Hormônios",                        "Eixo endócrino: tireoide, gonadal e adrenal."),
    "hepatico":    ("Fígado e função hepática",         "O fígado é o laboratório central do metabolismo."),
    "renal":       ("Função renal",                     "Filtração e excreção — marcadores de carga metabólica."),
    "hemograma":   ("Hemograma",                        "Saúde do sangue e capacidade de transporte de oxigênio."),
    "vitaminas":   ("Vitaminas e minerais",             "Micronutrientes essenciais para energia e imunidade."),
    "inflamacao":  ("Inflamação sistêmica",             "Inflamação silenciosa compromete todos os sistemas."),
    "autoimune":   ("Autoimunidade",                    "Autoanticorpos tiroideos e resposta imune."),
    "oncologico":  ("Marcadores oncológicos",           "Rastreamento preventivo."),
    "outros":      ("Outros exames",                    ""),
}

PRIORITY_GROUPS = ["metabolico", "hormonal", "lipidico", "inflamacao",
                   "vitaminas", "hepatico", "renal", "hemograma",
                   "autoimune", "oncologico", "outros"]

# Aliases para normalizar nomes variados entre labs
NAME_ALIASES = {
    "glicose": "Glicose",
    "glicemia": "Glicose",
    "glicose em jejum": "Glicose",
    "hemoglobina glicada": "HbA1c",
    "hemoglobina a1c": "HbA1c",
    "hba1c": "HbA1c",
    "insulina basal": "Insulina Basal",
    "insulina": "Insulina Basal",
    "homa": "HOMA-IR",
    "homa ir": "HOMA-IR",
    "homa-ir": "HOMA-IR",
    "colesterol total": "Colesterol Total",
    "hdl colesterol": "HDL",
    "hdl-colesterol": "HDL",
    "ldl colesterol": "LDL",
    "ldl-colesterol": "LDL",
    "vldl": "VLDL",
    "triglicerideos": "Triglicerideos",
    "triglicerídeos": "Triglicerideos",
    "triglicérides": "Triglicerideos",
    "tsh": "TSH",
    "t4 livre": "T4 Livre",
    "tiroxina livre": "T4 Livre",
    "t3 livre": "T3 Livre",
    "triiodotironina livre": "T3 Livre",
    "t3 total": "T3 Total",
    "t4 total": "T4 Total",
    "lh": "LH",
    "fsh": "FSH",
    "testosterona total": "Testosterona Total",
    "testosterona livre": "Testosterona Livre",
    "testosterona biodisponivel": "Testosterona Biodisponivel",
    "testosterona biodisponível": "Testosterona Biodisponivel",
    "estradiol": "Estradiol",
    "progesterona": "Progesterona",
    "dhea-s": "DHEA-S",
    "dheas": "DHEA-S",
    "dehidroepiandrosterona": "DHEA-S",
    "cortisol": "Cortisol",
    "prolactina": "Prolactina",
    "gh": "GH",
    "igf-1": "IGF-1",
    "igf 1": "IGF-1",
    "shbg": "SHBG",
    "tgo": "TGO",
    "ast": "TGO",
    "tgp": "TGP",
    "alt": "TGP",
    "ggt": "GGT",
    "gamaglutamiltransferase": "GGT",
    "gama glutamil": "GGT",
    "fosfatase alcalina": "Fosfatase Alcalina",
    "albumina": "Albumina",
    "proteinas totais": "Proteinas Totais",
    "proteínas totais": "Proteinas Totais",
    "bilirrubina total": "Bilirrubina Total",
    "bilirrubina direta": "Bilirrubina Direta",
    "bilirrubina indireta": "Bilirrubina Indireta",
    "creatinina": "Creatinina",
    "ureia": "Ureia",
    "uréia": "Ureia",
    "acido urico": "Acido Urico",
    "ácido úrico": "Acido Urico",
    "tfg": "TFG",
    "taxa de filtracao glomerular": "TFG",
    "microalbuminuria": "Microalbuminuria",
    "hemoglobina": "Hemoglobina",
    "hematocrito": "Hematocrito",
    "hematócrito": "Hematocrito",
    "eritrocitos": "Eritrocitos",
    "eritrócitos": "Eritrocitos",
    "vcm": "VCM",
    "hcm": "HCM",
    "chcm": "CHCM",
    "rdw": "RDW",
    "leucocitos": "Leucocitos",
    "leucócitos": "Leucocitos",
    "neutrofilos": "Neutrofilos",
    "neutrófilos": "Neutrofilos",
    "segmentados": "Neutrofilos",
    "linfocitos": "Linfocitos",
    "linfócitos": "Linfocitos",
    "monocitos": "Monocitos",
    "monócitos": "Monocitos",
    "eosinofilos": "Eosinofilos",
    "eosinófilos": "Eosinofilos",
    "basofilos": "Basofilos",
    "basófilos": "Basofilos",
    "plaquetas": "Plaquetas",
    "vpm": "VPM",
    "vitamina d": "Vitamina D",
    "vitamina d3": "Vitamina D",
    "25 oh vitamina d": "Vitamina D",
    "25-oh vitamina d": "Vitamina D",
    "vitamina b12": "Vitamina B12",
    "cobalamina": "Vitamina B12",
    "acido folico": "Acido Folico",
    "ácido fólico": "Acido Folico",
    "ferro serico": "Ferro Serico",
    "ferro sérico": "Ferro Serico",
    "ferro": "Ferro Serico",
    "ferritina": "Ferritina",
    "zinco": "Zinco",
    "magnesio": "Magnesio",
    "magnésio": "Magnesio",
    "calcio": "Calcio",
    "cálcio": "Calcio",
    "fosforo": "Fosforo",
    "fósforo": "Fosforo",
    "sodio": "Sodio",
    "sódio": "Sodio",
    "potassio": "Potassio",
    "potássio": "Potassio",
    "pcr": "PCR",
    "proteina c reativa": "PCR",
    "proteína c reativa": "PCR",
    "pcr ultrassensivel": "PCR Ultrassensivel",
    "pcr us": "PCR Ultrassensivel",
    "vhs": "VHS",
    "velocidade de hemossedimentacao": "VHS",
    "fibrinogenio": "Fibrinogenio",
    "fibrinogênio": "Fibrinogenio",
    "anti-tpo": "Anti-TPO",
    "anticorpo anti-tireoperoxidase": "Anti-TPO",
    "anti-tg": "Anti-TG",
    "anticorpo antitireoglobulina": "Anti-TG",
    "psa total": "PSA Total",
    "psa livre": "PSA Livre",
    "antigeno prostatico especifico": "PSA Total",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")


def normalizar_nome(nome):
    """Normaliza nome de exame para lookup no catalog."""
    n = strip_accents(nome.lower().strip())
    n = re.sub(r"\s+", " ", n)
    n = re.sub(r"[^a-z0-9 \-]", "", n)
    return n


def parse_float_br(s):
    """Converte '1.234,56' ou '1234.56' para float."""
    if not s:
        return None
    s = s.strip().replace(" ", "")
    # Formato brasileiro: ponto como milhar, vírgula como decimal
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def parse_referencia(ref_str):
    """
    Extrai (min, max) de strings de referência.
    Exemplos: '70 a 99', '< 190', '> 40', '0,27 a 4,20', '<= 2,7'
    Retorna (min_val, max_val) ou (None, None).
    """
    if not ref_str:
        return None, None
    ref = ref_str.strip()

    # Padrão "X a Y" ou "X - Y"
    m = re.search(r"([\d\.,]+)\s*(?:a|até|-)\s*([\d\.,]+)", ref, re.IGNORECASE)
    if m:
        return parse_float_br(m.group(1)), parse_float_br(m.group(2))

    # Padrão "< X" ou "<= X" ou "ate X"
    m = re.search(r"(?:<=?|<|até|ate)\s*([\d\.,]+)", ref, re.IGNORECASE)
    if m:
        return None, parse_float_br(m.group(1))

    # Padrão "> X" ou ">= X"
    m = re.search(r"(?:>=?|>|acima de|maior que)\s*([\d\.,]+)", ref, re.IGNORECASE)
    if m:
        return parse_float_br(m.group(1)), None

    return None, None


def classificar_valor(valor_f, ref_min, ref_max):
    """
    Classifica valor numérico contra referência.
    Retorna (status, tag_label, tag_class, alterado).
    status: 'normal' | 'otimo' | 'attn' | 'alert' | 'crit' | 'baixo'
    """
    if valor_f is None:
        return "normal", "Normal", "", False

    # Abaixo do mínimo
    if ref_min is not None and valor_f < ref_min:
        desvio = (ref_min - valor_f) / ref_min if ref_min != 0 else 0
        if desvio < 0.10:
            return "attn", "Baixo", "tag-attn", True
        elif desvio < 0.30:
            return "alert", "Baixo", "tag-alert", True
        else:
            return "crit", "Muito Baixo", "tag-crit", True

    # Acima do máximo
    if ref_max is not None and valor_f > ref_max:
        desvio = (valor_f - ref_max) / ref_max if ref_max != 0 else 0
        if desvio < 0.10:
            return "attn", "Elevado", "tag-attn", True
        elif desvio < 0.40:
            return "alert", "Alto", "tag-alert", True
        else:
            return "crit", "Muito Alto", "tag-crit", True

    # Dentro da referência — verificar se é "ótimo"
    if ref_min is not None and ref_max is not None:
        meio = (ref_min + ref_max) / 2
        # "Ótimo" = valor dentro dos 30% centrais da referência, ou muito bom
        margem = (ref_max - ref_min) * 0.20
        if ref_min + margem <= valor_f <= ref_max - margem:
            return "otimo", "Ótimo", "tag-optimal", False

    return "normal", "Normal", "", False


def formatar_valor(valor_str):
    """Formata valor para exibição (preserva casas decimais relevantes)."""
    if not valor_str:
        return valor_str
    # Remove zeros à direita desnecessários, mas mantém precisão
    try:
        f = parse_float_br(valor_str)
        if f is None:
            return valor_str
        # Formata com vírgula brasileira
        if f == int(f):
            return str(int(f))
        else:
            return f"{f:.2f}".replace(".", ",").rstrip("0").rstrip(",")
    except Exception:
        return valor_str


# ---------------------------------------------------------------------------
# Download PDF do Drive
# ---------------------------------------------------------------------------

def baixar_pdf(file_id, output_path):
    """Baixa PDF do Google Drive via gog."""
    cmd = ["/usr/local/bin/gog", "drive", "download", file_id, "--out", output_path]
    result = subprocess.run(cmd, capture_output=True, text=True, env=GOG_ENV)
    if result.returncode != 0:
        print(f"ERRO gog drive download: {result.stderr}", file=sys.stderr)
        return False
    return os.path.exists(output_path)


# ---------------------------------------------------------------------------
# Extração de texto do PDF
# ---------------------------------------------------------------------------

def extrair_texto_pdfplumber(pdf_path):
    """Extrai texto de todas as páginas via pdfplumber."""
    try:
        import pdfplumber
        linhas = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                texto = page.extract_text()
                if texto:
                    linhas.extend(texto.splitlines())
        return linhas
    except Exception as e:
        print(f"ERRO pdfplumber: {e}", file=sys.stderr)
        return []


def extrair_texto_pdftotext(pdf_path):
    """Fallback: usa pdftotext do sistema."""
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", pdf_path, "-"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return result.stdout.splitlines()
    except Exception as e:
        print(f"ERRO pdftotext: {e}", file=sys.stderr)
    return []


def extrair_linhas_pdf(pdf_path):
    """Extrai linhas de texto do PDF usando melhor método disponível."""
    linhas = extrair_texto_pdfplumber(pdf_path)
    if not linhas:
        linhas = extrair_texto_pdftotext(pdf_path)
    # Limpa linhas vazias e muito curtas
    return [l.strip() for l in linhas if len(l.strip()) > 2]


# ---------------------------------------------------------------------------
# Parser de exames do texto extraído
# ---------------------------------------------------------------------------

# Padrões de extração de resultados de exames
# Tenta capturar: (nome_exame) ... (valor numerico) ... (unidade) ... (referencia)
PATTERNS = [
    # Formato tabular: "Glicose  88  mg/dL  70 a 99"
    re.compile(
        r"^(?P<nome>[A-ZÀ-Ú][A-Za-zÀ-ú0-9\s\-\.\/\(\)]+?)"
        r"\s{2,}"
        r"(?P<valor>[\d\.,]+(?:\s*[<>]\s*[\d\.,]+)?)"
        r"\s+"
        r"(?P<unidade>[A-Za-zµ/%°]+(?:\/[A-Za-zµ]+)?)"
        r"(?:\s+(?P<referencia>.+?))?$",
        re.UNICODE
    ),
    # Formato com dois pontos: "Resultado: 88"  + "Unidade: mg/dL"
    re.compile(
        r"(?:Resultado|Result):\s*(?P<valor>[\d\.,<>]+)\s*(?P<unidade>[A-Za-zµ/%°\/]+)?",
        re.IGNORECASE
    ),
    # Formato compacto: "Glicose: 88 mg/dL" ou "TSH 1,60 µUI/mL"
    re.compile(
        r"^(?P<nome>[A-ZÀ-Ú][A-Za-zÀ-ú0-9\s\-\.\/\(\)]+?)"
        r"[:\s]+"
        r"(?P<valor>[\d\.,]+)"
        r"\s*"
        r"(?P<unidade>[A-Za-zµ/%°]+(?:\/[A-Za-zµA-Z]+)?)?"
        r"(?:\s+(?:VR|Ref|Referência|Referencia|VP|VR)[:.]?\s*(?P<referencia>.+?))?$",
        re.UNICODE
    ),
]

REF_PATTERNS = [
    # "Valores de referência: 70 a 99 mg/dL"
    re.compile(
        r"(?:valores?\s+de\s+refer[eê]ncia|vr|ref\.?|referência)[\s:]*"
        r"(?P<referencia>[\d\.,\s<>=aAàáté\-\/]+)"
        r"(?:\s+[A-Za-zµ/%]+)?",
        re.IGNORECASE
    ),
]


def parse_exames_linhas(linhas):
    """
    Parseia linhas de texto do PDF e tenta extrair exames.
    Retorna lista de dicts {nome_raw, valor_str, unidade, referencia_str}.
    """
    exames_raw = []
    nome_atual = None
    valor_atual = None
    unidade_atual = None
    referencia_atual = None

    i = 0
    while i < len(linhas):
        linha = linhas[i].strip()

        # Detecta linha de nome de exame (começa com letra maiúscula, sem números sozinhos)
        # Seguida por resultado na mesma linha ou na próxima

        # Tentativa 1: linha completa com nome + valor + unidade + referência
        match_completo = None
        for pat in PATTERNS:
            m = pat.match(linha)
            if m and m.group("valor") if "valor" in pat.groupindex else None:
                match_completo = m
                break

        if match_completo and "nome" in match_completo.groupdict() and match_completo.group("nome"):
            nome_raw = match_completo.group("nome").strip()
            valor_str = match_completo.group("valor").strip() if match_completo.group("valor") else None
            unidade = (match_completo.group("unidade") or "").strip()
            ref = (match_completo.group("referencia") or "").strip()

            if valor_str and re.search(r"\d", valor_str):
                exames_raw.append({
                    "nome_raw": nome_raw,
                    "valor_str": valor_str,
                    "unidade": unidade,
                    "referencia_str": ref,
                })
        else:
            # Tentativa 2: Multi-linha — detecta padrão "Resultado:" em linha seguinte
            if i + 1 < len(linhas):
                proxima = linhas[i + 1].strip()
                m_val = re.match(
                    r"(?:resultado|result)[:\s]*(?P<valor>[\d\.,<>]+)\s*(?P<unidade>[A-Za-zµ/%°\/]+)?",
                    proxima, re.IGNORECASE
                )
                if m_val:
                    nome_raw = linha
                    valor_str = m_val.group("valor")
                    unidade = (m_val.group("unidade") or "").strip()
                    # Busca referência nas próximas 3 linhas
                    ref = ""
                    for j in range(i + 2, min(i + 5, len(linhas))):
                        for rp in REF_PATTERNS:
                            mr = rp.search(linhas[j])
                            if mr:
                                ref = mr.group("referencia").strip()
                                break
                        if ref:
                            break
                    if re.match(r"^[A-ZÀ-Ú]", nome_raw) and re.search(r"\d", valor_str):
                        exames_raw.append({
                            "nome_raw": nome_raw,
                            "valor_str": valor_str,
                            "unidade": unidade,
                            "referencia_str": ref,
                        })
                    i += 2
                    continue

        i += 1

    return exames_raw


# ---------------------------------------------------------------------------
# Normalização e classificação
# ---------------------------------------------------------------------------

def resolver_nome(nome_raw):
    """Mapeia nome bruto para nome canônico do catálogo."""
    norm = normalizar_nome(nome_raw)
    if norm in NAME_ALIASES:
        return NAME_ALIASES[norm]
    # Tentativa parcial: verifica se algum alias está contido na string
    for alias, canonical in NAME_ALIASES.items():
        if alias in norm or norm in alias:
            return canonical
    # Retorna nome formatado (capitalizado) como fallback
    return nome_raw.strip().title()


def enriquecer_exame(exame_raw):
    """
    Recebe {nome_raw, valor_str, unidade, referencia_str},
    retorna dict completo com status e grupo.
    """
    nome_canon = resolver_nome(exame_raw["nome_raw"])
    catalog_entry = EXAM_CATALOG.get(nome_canon)

    grupo = "outros"
    unidade = exame_raw["unidade"] or ""
    ref_str = exame_raw["referencia_str"] or ""

    if catalog_entry:
        grupo = catalog_entry[0]
        if not unidade:
            unidade = catalog_entry[1]
        cat_min = catalog_entry[2]
        cat_max = catalog_entry[3]
    else:
        cat_min, cat_max = None, None

    # Usa referência extraída do PDF se disponível, senão usa catálogo
    if ref_str:
        ref_min, ref_max = parse_referencia(ref_str)
        # Prefere referência do catálogo se extraída for muito genérica
        if ref_min is None and ref_max is None:
            ref_min, ref_max = cat_min, cat_max
    else:
        ref_min, ref_max = cat_min, cat_max

    # Formata string de referência para exibição
    if ref_str:
        ref_display = ref_str.strip()
    elif ref_min is not None and ref_max is not None:
        ref_display = f"{ref_min} a {ref_max}"
    elif ref_max is not None:
        ref_display = f"< {ref_max}"
    elif ref_min is not None:
        ref_display = f"> {ref_min}"
    else:
        ref_display = ""

    valor_f = parse_float_br(exame_raw["valor_str"])
    status, tag_label, tag_class, alterado = classificar_valor(valor_f, ref_min, ref_max)

    return {
        "nome": nome_canon,
        "nome_raw": exame_raw["nome_raw"],
        "valor": formatar_valor(exame_raw["valor_str"]),
        "valor_f": valor_f,
        "unidade": unidade,
        "referencia": ref_display,
        "status": status,
        "tag_label": tag_label,
        "tag_class": tag_class,
        "alterado": alterado,
        "grupo": grupo,
    }


# ---------------------------------------------------------------------------
# Agrupa exames e seleciona hero alerts
# ---------------------------------------------------------------------------

SEVERIDADE_ORDEM = {"crit": 0, "alert": 1, "baixo": 1, "attn": 2, "normal": 3, "otimo": 4}

HERO_EXPLICACOES = {
    "HOMA-IR": "Resistência à insulina — célula não responde ao sinal de insulina.",
    "HbA1c": "Média de glicose nos últimos 3 meses.",
    "Glicose": "Glicemia em jejum — metabolismo do açúcar.",
    "TSH": "Regulador central da tireoide.",
    "Vitamina D": "Hormônio-vitamina: imunidade, músculo, humor.",
    "Vitamina B12": "Essencial para nervos e DNA.",
    "Colesterol Total": "Carga lipídica total — risco cardiovascular.",
    "LDL": "Colesterol 'ruim' — placa aterosclerótica.",
    "PCR": "Marcador de inflamação sistêmica.",
    "PCR Ultrassensivel": "Inflamação de baixo grau — risco cardiovascular.",
    "Testosterona Total": "Hormônio anabólico e metabólico central.",
    "LH": "Hormônio que estimula produção de testosterona.",
    "FSH": "Estimula espermatogênese / função ovariana.",
    "Hemoglobina": "Capacidade de transporte de oxigênio.",
    "Ferritina": "Reserva de ferro — energia e imunidade.",
    "TGP": "Marcador de lesão hepática.",
    "Creatinina": "Filtração renal.",
    "TFG": "Taxa de filtração glomerular — saúde dos rins.",
    "Acido Urico": "Relacionado a gota e inflamação.",
    "Triglicerideos": "Gordura no sangue — relacionado a insulina.",
    "Prolactina": "Hiperprolactinemia afeta libido e fertilidade.",
    "Cortisol": "Hormônio do estresse — afeta peso e sono.",
}


def agrupar_exames(exames_enriquecidos):
    """Organiza exames em grupos e seleciona os 4 hero alerts."""
    # Deduplica por nome canônico (mantém o mais recente / primeiro)
    vistos = {}
    for ex in exames_enriquecidos:
        if ex["nome"] not in vistos:
            vistos[ex["nome"]] = ex

    exames = list(vistos.values())

    # Agrupa por categoria
    grupos_dict = {}
    for ex in exames:
        g = ex["grupo"]
        if g not in grupos_dict:
            grupos_dict[g] = []
        grupos_dict[g].append(ex)

    # Monta lista de grupos na ordem de prioridade
    grupos = []
    for g_key in PRIORITY_GROUPS:
        if g_key not in grupos_dict:
            continue
        titulo, hint = GROUP_META.get(g_key, (g_key.capitalize(), ""))
        grupos.append({
            "id": g_key,
            "nome": titulo,
            "hint": hint,
            "exames": grupos_dict[g_key],
        })

    # Seleciona os 4 hero alerts (os mais alterados, com prioridade para crit/alert)
    alterados = [ex for ex in exames if ex["alterado"]]
    alterados.sort(key=lambda x: (SEVERIDADE_ORDEM.get(x["status"], 5), x["nome"]))
    hero_alerts = []
    for ex in alterados[:4]:
        hero_alerts.append({
            "nome": ex["nome"],
            "valor": ex["valor"],
            "unidade": ex["unidade"],
            "referencia": ex["referencia"],
            "status": ex["status"],
            "tag_class": ex["tag_class"],
            "explicacao": HERO_EXPLICACOES.get(ex["nome"], f"{ex['nome']} fora da referência."),
        })

    # Stats gerais
    total = len(exames)
    criticos = sum(1 for ex in exames if ex["status"] == "crit")
    alertas = sum(1 for ex in exames if ex["status"] in ("alert", "baixo"))
    atencao = sum(1 for ex in exames if ex["status"] == "attn")
    normais = sum(1 for ex in exames if ex["status"] in ("normal", "otimo"))

    return {
        "grupos": grupos,
        "hero_alerts": hero_alerts,
        "stats": {
            "total": total,
            "criticos": criticos,
            "alertas": alertas,
            "atencao": atencao,
            "normais": normais,
        },
    }


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------

def extrair_e_analisar(file_id, nome_arquivo="exame.pdf"):
    """Pipeline completo: download -> extração -> parse -> classificação."""
    tmpdir = tempfile.mkdtemp(prefix="exames_")
    pdf_path = os.path.join(tmpdir, nome_arquivo)

    try:
        print(f"[PDF] Baixando {nome_arquivo} ({file_id})...", file=sys.stderr)
        ok = baixar_pdf(file_id, pdf_path)
        if not ok:
            return {"encontrado": False, "erro": "Falha ao baixar PDF do Drive"}

        print(f"[PDF] Extraindo texto...", file=sys.stderr)
        linhas = extrair_linhas_pdf(pdf_path)
        if not linhas:
            return {"encontrado": False, "erro": "PDF sem texto extraível (pode ser imagem)"}

        print(f"[PDF] {len(linhas)} linhas extraídas. Parseando exames...", file=sys.stderr)
        exames_raw = parse_exames_linhas(linhas)
        print(f"[PDF] {len(exames_raw)} exames identificados.", file=sys.stderr)

        if not exames_raw:
            return {
                "encontrado": True,
                "arquivo": nome_arquivo,
                "aviso": "Nenhum valor de exame identificado no PDF.",
                "grupos": [],
                "hero_alerts": [],
                "stats": {"total": 0, "criticos": 0, "alertas": 0, "atencao": 0, "normais": 0},
            }

        exames_enriquecidos = [enriquecer_exame(ex) for ex in exames_raw]
        resultado = agrupar_exames(exames_enriquecidos)

        return {
            "encontrado": True,
            "arquivo": nome_arquivo,
            **resultado,
        }

    finally:
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 extrair_exames_pdf.py <drive_file_id> [--nome arquivo.pdf]")
        sys.exit(1)

    file_id = sys.argv[1]
    nome = "exame.pdf"
    if "--nome" in sys.argv:
        idx = sys.argv.index("--nome")
        if idx + 1 < len(sys.argv):
            nome = sys.argv[idx + 1]

    resultado = extrair_e_analisar(file_id, nome)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
