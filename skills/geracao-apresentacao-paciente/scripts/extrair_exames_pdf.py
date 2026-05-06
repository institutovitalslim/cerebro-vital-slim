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
    # NOVO: Exames com dígito no nome (HbA1c, VitaminaB12 etc) — antes do padrão geral
    re.compile(
        r"^(?P<nome>[A-ZÀ-Ú][A-Za-zÀ-ú0-9]{1,20}(?:\s[A-Za-zÀ-ú0-9]{1,20}){0,2})"
        r"\s{2,}"
        r"(?P<valor>[\d\.,]+(?:\s*[<>]\s*[\d\.,]+)?)"
        r"\s+"
        r"(?P<unidade>[A-Za-zµ/%°]+(?:\/[A-Za-zµ]+)?)"
        r"(?:\s+(?P<referencia>.+?))?$",
        re.UNICODE
    ),
    # Formato tabular padrão (sem dígitos no nome): "Glicose  88  mg/dL  70 a 99"
    re.compile(
        r"^(?P<nome>[A-ZÀ-Ú][A-Za-zÀ-ú\s\-\.\/\(\)]+?)"
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
    # Formato compacto sem dígitos no nome: "Glicose: 88 mg/dL"
    re.compile(
        r"^(?P<nome>[A-ZÀ-Ú][A-Za-zÀ-ú\s\-\.\/\(\)]+?)"
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


def extrair_data_exame(linhas):
    """Extrai a data do exame do conteúdo do PDF."""
    patterns = [
        r'[Cc]oleta[:\s]+(\d{2}/\d{2}/\d{4})',
        r'[Aa]tendimento[:\s]+(\d{2}/\d{2}/\d{4})',
        r'[Dd]ata[:\s]+(?:do\s+)?[Ee]xame[:\s]+(\d{2}/\d{2}/\d{4})',
        r'[Dd]ata[:\s]+(\d{2}/\d{2}/\d{4})',
        r'[Ee]mission[:\s]+(\d{2}/\d{2}/\d{4})',
        r'[Ll]ibera(?:ção|cao)[:\s]+(\d{2}/\d{2}/\d{4})',
    ]
    for linha in linhas[:50]:  # data geralmente nas primeiras linhas
        for pat in patterns:
            import re as _re
            m = _re.search(pat, linha)
            if m:
                return m.group(1)
    return None


# ===========================================================================
# V2 — Whitelist parser, multi-lab. Inicia abaixo.
# ===========================================================================
import unicodedata as _ud2

def _norm(s):
    """Uppercase, sem acentos, espaços colapsados, sem dots/dashes excessivos."""
    if not s:
        return ""
    s = _ud2.normalize("NFD", s)
    s = "".join(c for c in s if _ud2.category(c) != "Mn")
    s = s.upper()
    # Remove pontilhado de preenchimento e dois-pontos
    s = re.sub(r"[\.\:]{2,}", " ", s)
    s = s.replace(":", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


# Catálogo: chave normalizada -> (canon, grupo, unit_default, ref_min, ref_max)
EXAM_CATALOG_V2 = {
    # === Hemograma ===
    "HEMACIAS":              ("Hemácias",         "hemograma",   "milhoes/mm3", 4.50, 6.10),
    "ERITROCITOS":           ("Hemácias",         "hemograma",   "milhoes/mm3", 4.50, 6.10),
    "HEMOGLOBINA":           ("Hemoglobina",      "hemograma",   "g/dL",        13.0, 16.5),
    "HEMATOCRITO":           ("Hematócrito",      "hemograma",   "%",           36.0, 54.0),
    "VCM":                   ("VCM",              "hemograma",   "fl",          80.0, 98.0),
    "VOL GLOBULAR MEDIO":    ("VCM",              "hemograma",   "fl",          80.0, 98.0),
    "VOL GLOB MEDIO":        ("VCM",              "hemograma",   "fl",          80.0, 98.0),
    "HCM":                   ("HCM",              "hemograma",   "pg",          26.8, 32.9),
    "HEM GLOBULAR MEDIA":    ("HCM",              "hemograma",   "pg",          26.8, 32.9),
    "HB GLOB MEDIA":         ("HCM",              "hemograma",   "pg",          26.8, 32.9),
    "CHCM":                  ("CHCM",             "hemograma",   "g/dl",        30.0, 36.5),
    "C H GLOBULAR MEDIA":    ("CHCM",             "hemograma",   "g/dl",        30.0, 36.5),
    "CONC HB GLOB MEDIA":    ("CHCM",             "hemograma",   "g/dl",        30.0, 36.5),
    "RDW":                   ("RDW",              "hemograma",   "%",           11.0, 16.0),
    "LEUCOCITOS":            ("Leucócitos",       "hemograma",   "/mm3",        3600, 11000),
    "CONTAGEM DE LEUCOCITOS":("Leucócitos",       "hemograma",   "/mm3",        3600, 11000),
    "CONTAGEM GLOBAL":       ("Leucócitos",       "hemograma",   "/mm3",        3600, 11000),
    "PLAQUETAS":             ("Plaquetas",        "hemograma",   "/mm3",        130000, 450000),
    "CONTAGEM DE PLAQUETAS": ("Plaquetas",        "hemograma",   "/mm3",        130000, 450000),
    "BASTONETES":            ("Bastonetes",       "hemograma",   "/mm3",        0,    700),
    "BASTOES":               ("Bastonetes",       "hemograma",   "/mm3",        0,    700),
    "SEGMENTADOS":           ("Segmentados",      "hemograma",   "/mm3",        1700, 8000),
    "NEUTROFILOS":           ("Neutrófilos",      "hemograma",   "/mm3",        1800, 7800),
    "NEUTROFILOS SEG":       ("Neutrófilos",      "hemograma",   "/mm3",        1800, 7800),
    "EOSINOFILOS":           ("Eosinófilos",      "hemograma",   "/mm3",        50,   500),
    "BASOFILOS":             ("Basófilos",        "hemograma",   "/mm3",        0,    100),
    "MONOCITOS":             ("Monócitos",        "hemograma",   "/mm3",        100,  1200),
    "LINFOCITOS":            ("Linfócitos",       "hemograma",   "/mm3",        1000, 4800),
    # === Glicídico ===
    "GLICOSE":               ("Glicose",          "glicidico",   "mg/dL",       70,   99),
    "GLICEMIA":              ("Glicose",          "glicidico",   "mg/dL",       70,   99),
    "GLICEMIA DE JEJUM":     ("Glicose",          "glicidico",   "mg/dL",       70,   99),
    "INSULINA":              ("Insulina",         "glicidico",   "mU/mL",       2.6,  24.9),
    "INSULINA BASAL":        ("Insulina",         "glicidico",   "mU/mL",       2.6,  24.9),
    "INSULINEMIA":           ("Insulina",         "glicidico",   "mU/mL",       2.6,  24.9),
    "HEMOGLOBINA GLICADA":   ("HbA1c",            "glicidico",   "%",           None, 5.7),
    "HEMOGLOBINA GLICADA HBA1C": ("HbA1c",        "glicidico",   "%",           None, 5.7),
    "HBA1C":                 ("HbA1c",            "glicidico",   "%",           None, 5.7),
    "HBA1C DOSAGEM":         ("HbA1c",            "glicidico",   "%",           None, 5.7),
    "HOMA IR":               ("HOMA-IR",          "glicidico",   "",            None, 2.7),
    "HOMA-IR":               ("HOMA-IR",          "glicidico",   "",            None, 2.7),
    "HOMA BETA":             ("HOMA-Beta",        "glicidico",   "",            100,  200),
    "GLICEMIA MEDIA ESTIMADA": ("Glicemia Média", "glicidico",   "mg/dL",       None, 117),
    "FRUTOSAMINA":           ("Frutosamina",      "glicidico",   "umol/L",      None, 285),
    # === Lipídico ===
    "COLESTEROL TOTAL":      ("Colesterol Total", "lipidico",    "mg/dL",       None, 190),
    "COLESTEROL":            ("Colesterol Total", "lipidico",    "mg/dL",       None, 190),
    "COLESTEROL HDL":        ("HDL",              "lipidico",    "mg/dL",       40,   None),
    "HDL":                   ("HDL",              "lipidico",    "mg/dL",       40,   None),
    "HDL COLESTEROL":        ("HDL",              "lipidico",    "mg/dL",       40,   None),
    "COLESTEROL LDL":        ("LDL",              "lipidico",    "mg/dL",       None, 130),
    "LDL":                   ("LDL",              "lipidico",    "mg/dL",       None, 130),
    "LDL COLESTEROL":        ("LDL",              "lipidico",    "mg/dL",       None, 130),
    "COLESTEROL VLDL":       ("VLDL",             "lipidico",    "mg/dL",       None, 30),
    "VLDL":                  ("VLDL",             "lipidico",    "mg/dL",       None, 30),
    "TRIGLICERIDES":         ("Triglicérides",    "lipidico",    "mg/dL",       None, 150),
    "TRIGLICERIDEOS":        ("Triglicérides",    "lipidico",    "mg/dL",       None, 150),
    "COLESTEROL NAO HDL":    ("Não-HDL",          "lipidico",    "mg/dL",       None, 130),
    "APOLIPOPROTEINA B":     ("ApoB",             "lipidico",    "mg/dL",       None, 100),
    "APOB":                  ("ApoB",             "lipidico",    "mg/dL",       None, 100),
    "APOLIPOPROTEINA A":     ("ApoA",             "lipidico",    "mg/dL",       79,   169),
    "APOLIPOPROTEINA A-1":   ("ApoA",             "lipidico",    "mg/dL",       79,   169),
    "APOA":                  ("ApoA",             "lipidico",    "mg/dL",       79,   169),
    "LIPOPROTEINA A":        ("Lp(a)",            "lipidico",    "mg/dL",       None, 30),
    # === Hepático ===
    "TGO":                   ("TGO",              "hepatico",    "U/L",         None, 40),
    "AST":                   ("TGO",              "hepatico",    "U/L",         None, 40),
    "TRANSAMINASE OXALACETICA TGO AST": ("TGO",   "hepatico",    "U/L",         None, 40),
    "TGP":                   ("TGP",              "hepatico",    "U/L",         None, 41),
    "ALT":                   ("TGP",              "hepatico",    "U/L",         None, 41),
    "TRANSAMINASE PIRUVICA TGP ALT": ("TGP",      "hepatico",    "U/L",         None, 41),
    "GGT":                   ("GGT",              "hepatico",    "U/L",         None, 60),
    "GAMA GLUTAMIL TRANSFERASE": ("GGT",          "hepatico",    "U/L",         None, 60),
    "GAMA GT":               ("GGT",              "hepatico",    "U/L",         None, 60),
    "FOSFATASE ALCALINA":    ("Fosfatase Alcalina", "hepatico",  "U/L",         40,   130),
    "BILIRRUBINA TOTAL":     ("Bilirrubina",      "hepatico",    "mg/dL",       None, 1.2),
    # === Renal ===
    "UREIA":                 ("Ureia",            "renal",       "mg/dL",       10,   50),
    "CREATININA":            ("Creatinina",       "renal",       "mg/dL",       0.7,  1.2),
    "ACIDO URICO":           ("Ácido Úrico",      "renal",       "mg/dL",       3.4,  7.0),
    # === Tireoide ===
    "TSH":                   ("TSH",              "tireoide",    "uUI/mL",      0.27, 4.20),
    "TSH TIREOESTIMULANTE":  ("TSH",              "tireoide",    "uUI/mL",      0.27, 4.20),
    "T4 LIVRE":              ("T4 Livre",         "tireoide",    "ng/dL",       0.86, 2.49),
    "T4L":                   ("T4 Livre",         "tireoide",    "ng/dL",       0.86, 2.49),
    "T3 LIVRE":              ("T3 Livre",         "tireoide",    "pg/mL",       2.0,  4.4),
    "T3L":                   ("T3 Livre",         "tireoide",    "pg/mL",       2.0,  4.4),
    "T3 HORMONIO TRIIODOTIRONINA": ("T3 Total",   "tireoide",    "ng/dL",       60,   200),
    "T3 TOTAL":              ("T3 Total",         "tireoide",    "ng/dL",       60,   200),
    "T4 TOTAL":              ("T4 Total",         "tireoide",    "ug/dL",       5.1,  14.1),
    "ANTI-TPO":              ("Anti-TPO",         "tireoide",    "UI/mL",       None, 35),
    "ANTI TPO":              ("Anti-TPO",         "tireoide",    "UI/mL",       None, 35),
    # === Hormonal ===
    "TESTOSTERONA TOTAL":    ("Testosterona Total","hormonal",   "ng/dL",       264,  916),
    "TESTOSTERONA LIVRE":    ("Testosterona Livre","hormonal",   "pg/mL",       9,    47),
    "TESTOSTERONA BIODISPONIVEL": ("Testo Biodisponível","hormonal","ng/dL",    None, None),
    "ESTRADIOL":             ("Estradiol",        "hormonal",    "pg/mL",       None, 53),
    "ESTRADIOL E-2 DOSAGEM": ("Estradiol",        "hormonal",    "pg/mL",       None, 53),
    "ESTRADIOL DOSAGEM":     ("Estradiol",        "hormonal",    "pg/mL",       None, 53),
    "PROGESTERONA":          ("Progesterona",     "hormonal",    "ng/mL",       None, None),
    "FSH":                   ("FSH",              "hormonal",    "mUI/mL",      1.5,  12.4),
    "FSH HORMONIO FOLICULO ESTIMULANTE": ("FSH","hormonal",      "mUI/mL",      1.5,  12.4),
    "LH":                    ("LH",               "hormonal",    "mUI/mL",      1.7,  8.6),
    "LH HORMONIO LUTEINIZANTE": ("LH",            "hormonal",    "mUI/mL",      1.7,  8.6),
    "PROLACTINA":            ("Prolactina",       "hormonal",    "ng/mL",       None, 15),
    "SHBG":                  ("SHBG",             "hormonal",    "nmol/L",      16.5, 55.9),
    "DHEA-S":                ("DHEA-S",           "hormonal",    "ug/dL",       None, None),
    "DHEAS":                 ("DHEA-S",           "hormonal",    "ug/dL",       None, None),
    "DHEA SULFATO":          ("DHEA-S",           "hormonal",    "ug/dL",       None, None),
    # === Inflamatórios ===
    "PCR":                   ("PCR-us",           "inflamatorio","mg/L",        None, 3.0),
    "PCR-US":                ("PCR-us",           "inflamatorio","mg/L",        None, 3.0),
    "PCR ULTRA SENSIVEL":    ("PCR-us",           "inflamatorio","mg/L",        None, 3.0),
    "PROTEINA C REATIVA":    ("PCR-us",           "inflamatorio","mg/L",        None, 3.0),
    "HOMOCISTEINA":          ("Homocisteína",     "inflamatorio","umol/L",      None, 12),
    "HOMOCISTEINA DOSAGEM NO SANGUE": ("Homocisteína","inflamatorio","umol/L",  None, 12),
    "VHS":                   ("VHS",              "inflamatorio","mm/h",        None, 15),
    # === Vitaminas / Minerais ===
    "VITAMINA D":            ("Vitamina D",       "vitaminas",   "ng/mL",       30,   None),
    "VITAMINA D3":           ("Vitamina D",       "vitaminas",   "ng/mL",       30,   None),
    "VITAMINA D3 25-HIDROXI":("Vitamina D",       "vitaminas",   "ng/mL",       30,   None),
    "VITAMINA D 25 HIDROXIVITAMINA D3":("Vitamina D","vitaminas","ng/mL",       30,   None),
    "VITAMINA D 25":         ("Vitamina D",       "vitaminas",   "ng/mL",       30,   None),
    "VITAMINA B12":          ("Vitamina B12",     "vitaminas",   "pg/mL",       211,  946),
    "VITAMINA B12 DOSAGEM":  ("Vitamina B12",     "vitaminas",   "pg/mL",       211,  946),
    "ACIDO FOLICO":          ("Ácido Fólico",     "vitaminas",   "ng/mL",       3.0,  None),
    "FOLATO":                ("Ácido Fólico",     "vitaminas",   "ng/mL",       3.0,  None),
    "ZINCO":                 ("Zinco",            "vitaminas",   "ug/dL",       60,   130),
    "FERRO":                 ("Ferro",            "vitaminas",   "ug/dL",       33,   193),
    "FERRO SERICO":          ("Ferro",            "vitaminas",   "ug/dL",       33,   193),
    "FERRITINA":             ("Ferritina",        "vitaminas",   "ng/mL",       30,   400),
    "MAGNESIO":              ("Magnésio",         "vitaminas",   "mg/dL",       1.6,  2.6),
    "CALCIO":                ("Cálcio",           "vitaminas",   "mg/dL",       8.6,  10.2),
    "SODIO":                 ("Sódio",            "vitaminas",   "mEq/L",       136,  146),
    "POTASSIO":              ("Potássio",         "vitaminas",   "mEq/L",       3.5,  5.1),
    "PTH":                   ("PTH",              "vitaminas",   "pg/mL",       15,   65),
    # === Adrenal ===
    "CORTISOL":              ("Cortisol Basal",   "adrenal",     "ug/dL",       6.7,  22.6),
    "CORTISOL 08 HORAS":     ("Cortisol Basal",   "adrenal",     "ug/dL",       6.7,  22.6),
    "CORTISOL 08:00 HORAS":  ("Cortisol Basal",   "adrenal",     "ug/dL",       6.7,  22.6),
    "CORTISOL BASAL":        ("Cortisol Basal",   "adrenal",     "ug/dL",       6.7,  22.6),
    "IGF-1":                 ("IGF-1",            "adrenal",     "ng/mL",       100,  340),
    "IGF1":                  ("IGF-1",            "adrenal",     "ng/mL",       100,  340),
    "SOMATOMEDINA C":        ("IGF-1",            "adrenal",     "ng/mL",       100,  340),
}

# Exames hemograma diferencial: tem dupla coluna % + /mm3
HEMO_DIFERENCIAL = {"Bastonetes", "Segmentados", "Neutrófilos", "Eosinófilos",
                    "Basófilos", "Monócitos", "Linfócitos"}

# Exames cujo valor pode vir multiplicado (ex: Plaquetas "242 x 10³/mm3")
HEMO_MULTIPLICADOR_X1000 = {"Plaquetas", "Leucócitos"}

# Pre-normalize lookup
_CAT_NORM = {_norm(k): v for k, v in EXAM_CATALOG_V2.items()}
# Sorted by length DESC para preferir matches longos (ex: "TESTOSTERONA TOTAL" antes de "TESTOSTERONA")
_CAT_KEYS_BY_LEN = sorted(_CAT_NORM.keys(), key=len, reverse=True)

# Linhas a ignorar (metadata)
_SKIP_PATTERNS = [
    "MÉTODO", "METODO", "MATERIAL:", "MATERIAL :", "MATERIAL ",
    "AMOSTRA:", "HORAS DE JEJUM", "VALOR DE REFERENCIA", "VALOR DE REFERÊNCIA",
    "VALORES DE REFERENCIA", "VALORES DE REFERÊNCIA", "VALORES REFERENCIAIS",
    "LABORATORIO REGISTRADO", "EXAME LIBERADO", "EXAME REVISTO",
    "CNES DO RESPONSAVEL", "CNES DO RESPONSÁVEL", "RESPONSAVEL TECNICO",
    "RESPONSÁVEL TÉCNICO", "ENDERECO", "ENDEREÇO", "UNIDADE :",
    "PAGINA", "PÁGINA", "COLETA:", "LIBERACAO", "LIBERAÇÃO", "LIBERADO",
    "CONVENIO", "CONVÊNIO", "MEDICO ", "MÉDICO ", "SOLICITANTE",
    "ASSINATURA DIGITAL", "QNT DE EXAMES", "ATENDIMENTO",
    "OBS:", "ATENCAO:", "ATENÇÃO:", "FONTE:", "NOTA:", "REFERÊNCIA BIBLIOGRÁFICA",
    "ERITROGRAMA", "LEUCOGRAMA", "HEMOGRAMA",
    "BIBLIOGRAFIA", "HASH LAUDO", "HASH:", "RASTREABILIDADE",
    "DATA NASC:", "DT NASC", "DT. NASC", "DATA DE CADASTRO",
    "EMISSÃO:", "EMISSAO:", "PEDIDO:", "PRESCRIÇÃO HIS",
    "REGISTRO HIS", "CADASTRO:", "PRONTUARIO HIS", "ORIGEM:",
    "CLINICA:", "CLÍNICA:", "QUARTO/LEITO", "EXAMES DE ANALISES",
    "EXAMES DE ANÁLISES", "TIPO ATENDIMENTO", "MATRICULA",
    "EMPRESA/CONVENIO", "EMPRESA/CONVÊNIO", "OBSERVACAO", "OBSERVAÇÃO",
    "RECEM NASCIDOS", "RECÉM NASCIDOS", "GESTANTE", "ADULTOS:",
    "CRIANÇAS", "CRIANCAS", "FACE FOLICULAR", "FASE FOLICULAR",
    "MEIO DO CICLO", "FASE LUTEA", "FASE LÚTEA",
]


def _is_skip(line):
    up = line.upper().strip()
    if not up:
        return True
    if re.fullmatch(r"[\s\d.,/:_\-]+", line):
        return True
    # Se a linha CONTÉM um nome de exame conhecido, NÃO pula
    nt = _norm(line)
    for key in _CAT_KEYS_BY_LEN[:60]:  # checa só os 60 mais longos pra performance
        if len(key) >= 5 and key in nt:
            return False
    for pat in _SKIP_PATTERNS:
        if pat in up:
            return True
    return False


def _parse_br_num(s):
    """Parse '1.234,56' (BR), '1234.56', '1234', '4.95' (US dec) → float."""
    if s is None:
        return None
    s = str(s).strip().replace(" ", "")
    if not s:
        return None
    has_comma = "," in s
    if has_comma:
        # BR: pontos = milhar, vírgula = decimal
        s = s.replace(".", "").replace(",", ".")
        try:
            return float(s)
        except (ValueError, TypeError):
            return None
    # Sem vírgula: análise por número de pontos
    if "." in s:
        parts = s.split(".")
        if len(parts) == 2:
            # Um único ponto:
            #   "4.95"   → decimal (≤3 dígitos depois)
            #   "5.500"  → AMBÍGUO. Heurística: se dígitos depois do ponto == 3 e parte inteira ≤ 999,
            #              prefere milhar BR (ex: "5.500" = 5500). Caso contrário decimal.
            inteira, dec = parts
            if len(dec) == 3 and len(inteira) <= 3 and not inteira.startswith("0"):
                # Possível milhar BR ("5.500"). Mas em alguns labs "1.85" é altura. Decisão:
                # se valor concatenado >= 1000 → milhar.
                joined = int(inteira + dec)
                if joined >= 1000:
                    return float(joined)
            try:
                return float(s)
            except (ValueError, TypeError):
                return None
        else:
            # Múltiplos pontos: tudo milhar
            s = s.replace(".", "")
    try:
        return float(s)
    except (ValueError, TypeError):
        return None


def _fmt_num(n):
    if n is None:
        return ""
    if abs(n - int(n)) < 0.001:
        return str(int(n))
    return f"{n:.2f}".rstrip("0").rstrip(".").replace(".", ",")


def _classify(valor_f, ref_min, ref_max):
    if valor_f is None:
        return "normal"
    if ref_max is not None and valor_f > ref_max:
        if valor_f > ref_max * 1.5:
            return "crit"
        return "alert"
    if ref_min is not None and valor_f < ref_min:
        if valor_f < ref_min * 0.5:
            return "crit"
        return "low"
    return "normal"


def _ref_string(ref_min, ref_max):
    if ref_min is not None and ref_max is not None:
        return f"{_fmt_num(ref_min)} a {_fmt_num(ref_max)}"
    if ref_max is not None:
        return f"<{_fmt_num(ref_max)}"
    if ref_min is not None:
        return f">{_fmt_num(ref_min)}"
    return ""


def _try_match_catalog(text):
    """Procura nome de exame em text (já normalizado). Retorna (cat_key, meta) ou (None, None)."""
    nt = _norm(text)
    if not nt:
        return None, None
    # Match exato
    if nt in _CAT_NORM:
        return nt, _CAT_NORM[nt]
    # Match no início (texto começa com chave)
    for key in _CAT_KEYS_BY_LEN:
        if len(key) < 3:
            continue
        if nt.startswith(key + " ") or nt == key:
            return key, _CAT_NORM[key]
        # também permite key seguida de ":" ou "," ou "."
        if re.match(rf"^{re.escape(key)}([\s:,\.\-]|$)", nt):
            return key, _CAT_NORM[key]
    return None, None



def _strip_name_prefix(line, cat_norm_key):
    """Retorna substring de line APÓS o nome do exame (matched fuzzy).
    Aproximação: avança chars no original mantendo contador de chars normalizados consumidos.
    """
    target_len = len(cat_norm_key)
    consumed = 0
    line_upper = ""
    norm_line = _norm(line)
    if not norm_line.startswith(cat_norm_key):
        return line  # não bate, retorna original
    # Walk char-by-char no original, normalizando incrementalmente
    consumed_chars_in_original = 0
    norm_so_far = ""
    for i, ch in enumerate(line):
        # Normalize char (deixa espaços e letras; remove acentos; uppercase)
        norm_ch = _ud2.normalize("NFD", ch)
        norm_ch = "".join(c for c in norm_ch if _ud2.category(c) != "Mn")
        norm_ch = norm_ch.upper()
        if norm_ch in (".", ":"):
            norm_ch = " "
        # Acumula
        norm_so_far += norm_ch
        # Colapsa espaços
        norm_collapsed = re.sub(r"\s+", " ", norm_so_far).lstrip()
        if len(norm_collapsed) >= target_len:
            # Atingimos o tamanho. Posição final no original: i+1
            return line[i+1:]
    return ""


def _walk_back_for_name(linhas, idx, max_back=20):
    """Da posição idx, anda pra trás procurando linha com exam name."""
    for j in range(idx - 1, max(idx - max_back - 1, -1), -1):
        line = linhas[j].strip()
        if not line:
            continue
        # Tenta match no texto antes do primeiro número
        m_pre = re.split(r"[\d]", line, maxsplit=1)
        candidate = m_pre[0] if m_pre else line
        candidate = candidate.rstrip(":.,;-").strip()
        # Skip linhas curtas tipo "Coletado em" / "Liberado"
        if any(skip in line.upper() for skip in [
            "COLETADO", "LIBERADO", "ASSINATURA", "HASH:", "CNES",
            "EXAME LIBERADO", "MATERIAL:", "MÉTODO", "METODO",
            "HORAS DE JEJUM", "PÁGINA", "PAGINA", "OBSERVAÇÃO",
            "OBSERVACAO", "ATENÇÃO:", "ATENCAO:", "FONTE:",
        ]):
            continue
        if len(candidate) > 80:
            continue
        cat, meta = _try_match_catalog(candidate)
        if meta:
            return cat, meta
    return None, None


def _parse_ref_block(linhas, start, max_lines=8):
    """Busca 'Valor de referência' nas próximas linhas e extrai (min, max)."""
    for j in range(start, min(start + max_lines, len(linhas))):
        line = linhas[j].strip()
        if not line:
            continue
        # "X a Y unidade"  ou "DE X A Y unidade"
        m = re.search(r"(?:DE\s+)?([\d.,]+)\s*[aàAÀ]\s*([\d.,]+)", line)
        if m:
            lo = _parse_br_num(m.group(1))
            hi = _parse_br_num(m.group(2))
            if lo is not None and hi is not None and lo < hi:
                return lo, hi
        m2 = re.search(r"(?:ate|até|<=?|<|inferior)\s*([\d.,]+)", line, re.IGNORECASE)
        if m2:
            hi = _parse_br_num(m2.group(1))
            if hi is not None:
                return None, hi
        m3 = re.search(r"(?:>=?|>|acima de|superior)\s*([\d.,]+)", line, re.IGNORECASE)
        if m3:
            lo = _parse_br_num(m3.group(1))
            if lo is not None:
                return lo, None
    return None, None


_VALUE_TOKEN_RE = re.compile(r"([\d.,]+)\s*([A-Za-z%/³µ³ºª]+(?:[/.²³º]?\w+)*)?")


def _extract_value_unit(line, after_pos=0):
    """Extrai primeiro número + unidade depois de after_pos."""
    sub = line[after_pos:]
    m = _VALUE_TOKEN_RE.search(sub)
    if not m:
        return None, None, None
    valor_f = _parse_br_num(m.group(1))
    if valor_f is None:
        return None, None, None
    unidade = (m.group(2) or "").strip()
    # Limpa unidade: rejeita lixo
    if unidade in {"a", "A", "à", "À", "DE", "de"}:
        unidade = ""
    return m.group(1), valor_f, unidade


def _sanity_ok(valor_f, ref_min_cat, ref_max_cat):
    """Rejeita valores absurdamente fora do range esperado."""
    if valor_f is None:
        return False
    if ref_max_cat is not None and valor_f > ref_max_cat * 100:
        return False
    if ref_min_cat is not None and ref_min_cat > 0 and valor_f < ref_min_cat * 0.001:
        return False
    return True


def parse_exames_linhas_v2(linhas):
    """Parser whitelist multi-format."""
    exames = {}  # canon -> dict (last-wins)

    def _commit(canon, grupo, valor_str, valor_f, unidade, ref_min, ref_max, source="B"):
        # Não permite Modo B sobrescrever Modo A
        if canon in exames and exames[canon].get("_source") == "A" and source == "B":
            return
        status = _classify(valor_f, ref_min, ref_max)
        ref_disp = _ref_string(ref_min, ref_max)
        # Se já temos esse canon e o novo veio de Modo A (mais confiável), sobrescreve.
        # Se já temos e veio de Modo B/C, só insere se ainda não existe.
        # Implementação simples: sempre sobrescreve; ordens de scan privilegiam confiabilidade.
        # Filtra unidades-lixo (palavras que aparecem mas não são unidades)
        unit_blacklist = {"Valores", "anos", "ano", "Feminino", "Masculino", "Homens", "Mulheres",
                          "Homem", "Mulher", "Crianças", "Adultos", "Adulto", "Material",
                          "horas", "Horas", "DOSAGEM", "Dosagem", "Resultado", "RESULTADO",
                          "Ate", "Até", "Acima", "Abaixo", "OH", "HIDROXI", "LIVRE", "TOTAL",
                          "Valor"}
        if unidade and unidade.strip() in unit_blacklist:
            unidade = ""
        exames[canon] = {
            "nome": canon,
            "nome_raw": canon,
            "valor": _fmt_num(valor_f),
            "valor_f": valor_f,
            "unidade": unidade,
            "referencia": ref_disp,
            "status": status,
            "tag_label": status.upper(),
            "tag_class": status,
            "alterado": status != "normal",
            "grupo": grupo,
            "_source": source,
        }

    n = len(linhas)
    for i, line in enumerate(linhas):
        line_strip = line.strip()
        if not line_strip:
            continue

        # === Modo A: "Resultado: VALUE UNIT" → walk-back ===
        m_res = re.search(r"^\s*RESULTADO\s*:\s*(.+)$", line, re.IGNORECASE)
        if m_res:
            tail = m_res.group(1)
            valor_str, valor_f, unidade = _extract_value_unit(tail)
            if valor_f is not None:
                cat, meta = _walk_back_for_name(linhas, i)
                if meta:
                    canon, grupo, unit_def, ref_min_cat, ref_max_cat = meta
                    # Multiplicador x10³ para Plaquetas/Leucócitos
                    if canon in HEMO_MULTIPLICADOR_X1000 and valor_f < 1000:
                        line_lower = line.lower() + " " + tail.lower()
                        if any(mark in line_lower for mark in ["x 10³", "x10³", "x 10^3", "x10^3", "mil/mm",
                                                                "x 10e3", "x10e3", "10³/mm", "10^3/mm"]):
                            valor_f = valor_f * 1000
                    if _sanity_ok(valor_f, ref_min_cat, ref_max_cat):
                        # Tenta ref do PDF (próximas linhas), senão usa catálogo
                        ref_min, ref_max = _parse_ref_block(linhas, i + 1)
                        if ref_min is None and ref_max is None:
                            # Tenta tail (ex: "Resultado: 141 mEq/L  136 a 145 mEq/L")
                            ref_min, ref_max = _parse_ref_block([tail], 0, 1)
                        if ref_min is None and ref_max is None:
                            ref_min, ref_max = ref_min_cat, ref_max_cat
                        unit_final = unidade or unit_def
                        _commit(canon, grupo, valor_str, valor_f, unit_final, ref_min, ref_max, source="A")
                        continue

        # === Modo B/C/D: inline com nome no início da linha ===
        # Tenta achar exam name no início da linha
        cat, meta = _try_match_catalog(line_strip)
        if not meta:
            continue

        canon, grupo, unit_def, ref_min_cat, ref_max_cat = meta
        # Posição depois do nome no original
        cat_len_in_orig = 0
        try:
            # Encontra onde termina o nome na linha original (case-insensitive, accent-insensitive)
            line_norm_full = _norm(line_strip)
            pos = line_norm_full.find(cat)
            if pos == 0:
                # Mapeia tamanho do nome normalizado pra posição no original
                # Aproximação: pega N caracteres iniciais que produzam essa norma
                # Implementação simples: começa do tamanho do cat e procura primeiro número
                cat_len_in_orig = len(cat) + 5  # margem
        except Exception:
            cat_len_in_orig = 0

        # Pula o nome do exame antes de buscar valor (evita pegar "4" de "T4 LIVRE")
        rest_after_name = _strip_name_prefix(line_strip, cat)
        if not rest_after_name.strip():
            continue
        # Rejeita se logo após o nome aparecem palavras de DESCRIÇÃO
        rest_check_lower = rest_after_name.strip().lower()
        descriptive_prefixes = ["adultos", "criancas", "crianças", "homens", "mulheres",
                                "feminino", "masculino", "inferior a", "superior a", "acima de",
                                "abaixo de", "ate ", "até ", "menos que", "mais que",
                                "fase ", "trimestre", "ciclo ", "menstruacao", "gestante", "menopausa",
                                "valores de referência", "valores de referencia"]
        if any(rest_check_lower.startswith(p) for p in descriptive_prefixes):
            continue
        # Coleta TODOS números após o nome
        all_matches = list(re.finditer(r"(?:^|[\s.:,;\-]+)(\d[\d.,]*)", rest_after_name))
        if not all_matches:
            continue
        # Decide qual número usar
        m_val = all_matches[0]
        if canon in HEMO_DIFERENCIAL and len(all_matches) >= 2:
            # Padrão hemograma diferencial: "<NOME> <%> <absoluto> <ref_pct> <ref_abs>"
            # Ex: "LINFÓCITOS  31  3.447  20-50  740 a 5.500"
            # O primeiro é %, segundo é absoluto. Usar absoluto.
            v0 = _parse_br_num(all_matches[0].group(1))
            v1 = _parse_br_num(all_matches[1].group(1))
            if v0 is not None and v1 is not None and v0 < 100 and v1 > v0:
                m_val = all_matches[1]
        # Rejeita se ANTES do número há ">", "<", "≥", "≤"
        before_val = rest_after_name[:m_val.start()]
        if any(sign in before_val for sign in [">", "<", "≥", "≤"]):
            continue
        valor_str_raw = m_val.group(1)
        valor_f = _parse_br_num(valor_str_raw)
        if valor_f is None:
            continue
        # Multiplicador x10³ para Plaquetas/Leucócitos quando lab usa notação compacta
        if canon in HEMO_MULTIPLICADOR_X1000 and valor_f < 1000:
            line_lower = line_strip.lower()
            if any(mark in line_lower for mark in ["x 10³", "x10³", "x 10^3", "x10^3", "mil/mm",
                                                    "x 10e3", "x10e3", "10³/mm", "10^3/mm"]):
                valor_f = valor_f * 1000
        if not _sanity_ok(valor_f, ref_min_cat, ref_max_cat):
            continue

        # Unidade: token logo após o número
        after_val_pos = m_val.end()
        rest = rest_after_name[after_val_pos:].strip()
        unidade = ""
        # Aceita unidades canônicas: mg/dL, g/dL, %, U/L, mU/mL, ng/mL, ug/dL, etc
        m_unit = re.match(r"\s*([%]|[a-zA-Zµ]+(?:[/³²][a-zA-Z\d]+)*)", rest)
        rejected_descriptive = False
        if m_unit:
            tok = m_unit.group(1).strip()
            tok_low = tok.lower()
            descriptive_words = {"anos", "ano", "horas", "hora", "idade", "feminino", "masculino",
                                 "homens", "mulheres", "homem", "mulher", "adultos", "criancas", "crianças",
                                 "valores", "valor", "ate", "até", "inferior", "superior",
                                 "dosagem", "resultado", "ref", "referencia", "referência",
                                 "fase", "ciclo", "menstruacao", "menstruação", "gestante",
                                 "trimestre", "menopausa"}
            if tok_low in descriptive_words:
                rejected_descriptive = True
            elif tok_low not in {"a", "à", "de", "ou", "e", "do", "da", "oh", "hidroxi", "livre", "total"}:
                unidade = tok
        if rejected_descriptive:
            continue  # rejeita match — provavelmente lendo descrição
        unidade_final = unidade or unit_def

        # Refs: tenta extrair da parte depois do valor primeiro
        ref_text = rest_after_name[after_val_pos:]
        ref_min, ref_max = _parse_ref_block([ref_text], 0, 1)
        if ref_min is None and ref_max is None:
            ref_min, ref_max = _parse_ref_block(linhas, i + 1, 4)
        if ref_min is None and ref_max is None:
            ref_min, ref_max = ref_min_cat, ref_max_cat

        _commit(canon, grupo, valor_str_raw, valor_f, unidade_final, ref_min, ref_max)

    return list(exames.values())


# Wrappers backward-compat
def parse_exames_linhas(linhas):
    return parse_exames_linhas_v2(linhas)


def enriquecer_exame(exame_raw):
    return exame_raw

# ===========================================================================
# Fim V2.
# ===========================================================================


SEVERIDADE_ORDEM = {"crit": 0, "alert": 1, "baixo": 1, "low": 1, "attn": 2, "normal": 3, "otimo": 4}

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
        grupo = {
            "id": g_key,
            "nome": titulo,
            "hint": hint,
            "exames": grupos_dict[g_key],
        }
        # Filter "outros" to only lab values with references or known catalog entries
        if g_key == "outros":
            grupo["exames"] = [ex for ex in grupo["exames"] if ex.get("referencia") or ex.get("valor_f") is not None]
        grupos.append(grupo)

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
            "tag_label": ex.get("tag_label", ex["status"].upper()),
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


# Indicadores de laudo laboratorial
LAB_INDICATORS = [
    "coleta:", "data de coleta", "laborat", "hemograma", "eritrograma",
    "leucograma", "valores de referencia", "valores de referencia",
    "vr:", "crbm:", "cnes", "fase analitica",
]
# Indicadores de receita/formula magistral
PRESCRIPTION_INDICATORS = [
    "capsula q.s.p", "comprimido", "posologia",
    "tomar 0", "uso: tomar", "manipulad",
]

def is_lab_report(linhas):
    """
    Retorna True se o PDF parece ser um laudo laboratorial.
    Retorna False se parece ser receita/formula magistral — sera ignorado.
    """
    import unicodedata
    def strip(s):
        return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    texto = strip(" ".join(linhas[:80]).lower())
    lab_score = sum(1 for k in LAB_INDICATORS if strip(k) in texto)
    presc_score = sum(1 for k in PRESCRIPTION_INDICATORS if strip(k) in texto)
    if presc_score >= 2 and lab_score == 0:
        return False
    if lab_score >= 1:
        return True
    return True

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

        if not is_lab_report(linhas):
            print(f"[PDF] {nome_arquivo}: parece ser receita/formula, ignorando.", file=sys.stderr)
            return {"encontrado": False, "erro": "PDF nao e laudo laboratorial (receita/formula detectada)"}

        print(f"[PDF] {len(linhas)} linhas extraidas. Parseando exames...", file=sys.stderr)
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

        data_exame = extrair_data_exame(linhas)
        return {
            "encontrado": True,
            "arquivo": nome_arquivo,
            "data_exame": data_exame,
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
