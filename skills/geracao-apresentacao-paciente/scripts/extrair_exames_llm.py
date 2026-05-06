#!/usr/bin/env python3
"""
Extrator de exames laboratoriais via LLM (OpenAI gpt-4o + Structured Outputs).

Substitui o regex parser frágil por extração semântica com structured output
(response_format=json_schema, strict=True). O LLM é forçado a obedecer ao schema.
"""
import os
import re
import json
import subprocess
from openai import OpenAI


def _load_api_key():
    for p in ["/root/.openclaw/.env.runtime", "/root/.openclaw/.env"]:
        if not os.path.exists(p):
            continue
        with open(p) as f:
            for line in f:
                line = line.strip()
                if line.startswith("OPENAI_API_KEY="):
                    val = line.split("=", 1)[1]
                    if val.startswith("sk-"):
                        return val
    return os.environ.get("OPENAI_API_KEY", "")


_API_KEY = _load_api_key()
MODEL = "gpt-4o"  # alta precisão (custo $0.06/laudo)


# JSON Schema para Structured Outputs (strict=True)
SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "paciente_nome": {"type": "string"},
        "data_coleta": {"type": "string"},
        "lab_origem": {"type": "string"},
        "exames": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "nome_canonico": {
                        "type": "string",
                        "enum": [
                            # Hemograma
                            "Hemácias", "Hemoglobina", "Hematócrito", "VCM", "HCM", "CHCM", "RDW",
                            "Leucócitos", "Plaquetas",
                            "Bastonetes", "Segmentados", "Neutrófilos", "Eosinófilos",
                            "Basófilos", "Monócitos", "Linfócitos",
                            # Glicídico
                            "Glicose", "HbA1c", "Insulina", "HOMA-IR", "HOMA-Beta",
                            "Glicemia Média", "Frutosamina",
                            # Lipídico
                            "Colesterol Total", "HDL", "LDL", "VLDL", "Triglicérides",
                            "Não-HDL", "ApoB", "ApoA", "Lp(a)",
                            # Hepático
                            "TGO", "TGP", "GGT", "Fosfatase Alcalina", "Bilirrubina",
                            # Renal
                            "Ureia", "Creatinina", "Ácido Úrico",
                            # Tireoide
                            "TSH", "T4 Livre", "T3 Livre", "T3 Total", "T4 Total", "Anti-TPO",
                            # Hormonal
                            "Testosterona Total", "Testosterona Livre", "Testo Biodisponível",
                            "Estradiol", "Progesterona", "FSH", "LH", "Prolactina",
                            "SHBG", "DHEA-S",
                            # Inflamatórios
                            "PCR-us", "Homocisteína", "VHS",
                            # Vitaminas / Minerais
                            "Vitamina D", "Vitamina B12", "Ácido Fólico", "Zinco",
                            "Ferro", "Ferritina", "Magnésio", "Cálcio", "Sódio", "Potássio", "PTH",
                            # Adrenal
                            "Cortisol", "Cortisol Basal", "IGF-1",
                        ]
                    },
                    "nome_no_laudo": {"type": "string"},
                    "valor": {"type": "number"},
                    "unidade": {"type": "string"},
                    "ref_min": {"type": ["number", "null"]},
                    "ref_max": {"type": ["number", "null"]},
                    "grupo": {
                        "type": "string",
                        "enum": ["hemograma", "glicidico", "lipidico", "hepatico", "renal",
                                 "tireoide", "hormonal", "inflamatorio", "vitaminas", "adrenal", "outros"]
                    },
                    "status_clinico": {
                        "type": "string",
                        "enum": ["normal", "low", "attn", "alert", "crit"]
                    },
                    "observacao": {"type": ["string", "null"]}
                },
                "required": ["nome_canonico", "nome_no_laudo", "valor", "unidade",
                             "ref_min", "ref_max", "grupo", "status_clinico", "observacao"]
            }
        }
    },
    "required": ["paciente_nome", "data_coleta", "lab_origem", "exames"]
}


SYSTEM_PROMPT = """Você é um analista clínico especializado em laudos laboratoriais brasileiros.

REGRA CANÔNICA: SEMPRE use o SEXO do paciente (M/F) para classificar status_clinico.
Refs de Testosterona, Ferritina, Hemácias, Hemoglobina, TGO, TGP, GGT, Creatinina,
Ácido Úrico, Estradiol, Progesterona, FSH, LH, Prolactina, SHBG, DHEA-S, VHS, Ferro
VARIAM POR SEXO. Nunca classifique sem considerar o sexo informado. (Sabin, DB Recife, Hapvida, Labchecap, Hermes Pardini, Richet, Leme, LPC, Datalab, etc).

REGRAS CRÍTICAS de extração:

1. **Apenas valores reais do paciente** — NÃO confunda com:
   - Valores de referência ("Inferior a 190", "Até 16,0%", "30 a 400")
   - Valores históricos em gráficos
   - Idade, datas, códigos de protocolo, CRM, CNES
   - Cabeçalhos de coluna ("Adultos > 20 anos")

2. **Hemograma diferencial** — Linfócitos, Neutrófilos, Monócitos, Eosinófilos, Basófilos, Bastonetes, Segmentados aparecem com DUAS colunas (% e absoluto/mm³). USE SEMPRE o valor ABSOLUTO em /mm³.

3. **Plaquetas** — se aparece "242 x10³" ou "242 mil/mm³", registre 242000 (multiplique).

4. **Testosterona Total**: Homem 264-916 ng/dL, Mulher 15-70 ng/dL.
   **Testosterona Livre**: Homem 9-47 pg/mL, Mulher 0,3-3,18 pg/mL.

5. **status_clinico** — calcule contra a referência apropriada AO SEXO:
   - normal: dentro da faixa
   - low: abaixo do mínimo (mas <50% baixo)
   - attn: limítrofe
   - alert: acima do máximo (1-50% acima)
   - crit: >50% acima do máximo OU <50% do mínimo

6. **Não invente** valores. Se um exame não tem valor numérico claro, NÃO inclua.

7. **Deduplicação** — se o mesmo exame aparece múltiplas vezes (histórico vs atual), use o MAIS RECENTE.

8. **nome_canonico** deve estar na enum. Se um exame do laudo não bate com nenhum dos nomes da enum, NÃO inclua.

9. **Status do paciente Tiaro** (exemplo): se vem "RESISTÊNCIA À INSULINA" ou similar como nome de exame, ignore — só inclua exames quantificáveis."""


def extrair_texto_pdf(pdf_path):
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", pdf_path, "-"],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode == 0:
            return result.stdout
    except Exception as e:
        print(f"[ERRO] pdftotext: {e}")
    return ""


def filtrar_texto(texto, max_chars=80000):
    """Remove ruído óbvio para reduzir tokens."""
    linhas = texto.splitlines()
    out = []
    skip_substrings = [
        "Hash laudo:", "Assinatura digital", "ASSINATURA DIGITAL",
        "Endereço da Unidade", "Telefone", "CNPJ", "Bibliografia",
    ]
    for line in linhas:
        if any(s in line for s in skip_substrings):
            continue
        # Linhas que são apenas dígitos/separadores e longas (provável gráfico)
        if re.fullmatch(r"[\s\d.,/:_\-]+", line) and len(line) > 60:
            continue
        out.append(line)
    text = "\n".join(out)
    if len(text) > max_chars:
        text = text[:max_chars] + "\n[...truncado...]"
    return text


def extrair_exames_via_llm(pdf_path, paciente_meta=None, model=MODEL):
    """
    Extrai exames de um PDF de laudo.

    REGRA CANÔNICA: paciente_meta DEVE conter 'sexo' ('M' ou 'F').
    Sem isso, retorna erro — porque refs clínicas variam por sexo
    (Testosterona, Ferritina, Hemácias, Hemoglobina, Creatinina, etc).
    """
    if not _API_KEY:
        return {"erro": "OPENAI_API_KEY não configurada"}

    paciente_meta = paciente_meta or {}
    sexo = str(paciente_meta.get("sexo", "")).upper()[:1]
    if sexo not in {"M", "F"}:
        return {
            "erro": "REGRA CANÔNICA: sexo do paciente é OBRIGATÓRIO (M ou F). "
                    "Refs de Testosterona/Ferritina/Hemoglobina/etc variam por sexo.",
            "exames": [],
        }
    idade = paciente_meta.get("idade", "")

    texto = extrair_texto_pdf(pdf_path)
    if not texto:
        return {"erro": "Falha ao extrair texto do PDF", "exames": []}

    texto_filtrado = filtrar_texto(texto)

    sexo_descricao = "MASCULINO" if sexo == "M" else "FEMININO"
    user_msg = (
        f"=== DADOS DO PACIENTE (USE PARA CLASSIFICAR STATUS_CLINICO) ===\n"
        f"Sexo: {sexo_descricao} ({sexo})\n"
        f"Idade: {idade or '?'} anos\n\n"
        f"=== TEXTO DO LAUDO (pdftotext) ===\n"
        f"--- INÍCIO ---\n{texto_filtrado}\n--- FIM ---\n\n"
        f"INSTRUÇÕES:\n"
        f"1. Extraia todos os exames laboratoriais com valores reais do paciente.\n"
        f"2. Para CADA exame, classifique status_clinico contra a referência APROPRIADA AO SEXO {sexo} do paciente.\n"
        f"   Exemplos críticos:\n"
        f"   - Testosterona Total: M=264-916 ng/dL, F=15-70 ng/dL\n"
        f"   - Ferritina: M=30-400 ng/mL, F=13-150 ng/mL\n"
        f"   - Hemoglobina: M=13-16,5 g/dL, F=12-15,8 g/dL\n"
        f"   - Creatinina: M=0,7-1,2 mg/dL, F=0,5-1,0 mg/dL\n"
        f"3. Use APENAS os nomes da enum em nome_canonico."
    )

    client = OpenAI(api_key=_API_KEY)

    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0,  # determinístico
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "extracao_exames",
                    "schema": SCHEMA,
                    "strict": True,
                }
            },
        )
    except Exception as e:
        return {"erro": f"OpenAI API error: {e}"}

    content = response.choices[0].message.content
    if not content:
        return {"erro": "Resposta vazia do LLM"}

    try:
        result = json.loads(content)
        # Adiciona texto bruto pra L10 anti-alucinacao no validador
        result['_texto_pdf'] = texto
        return result
    except json.JSONDecodeError as e:
        return {"erro": f"JSON inválido: {e}", "raw": content[:500]}


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python3 extrair_exames_llm_openai.py <pdf_path> [sexo]")
        sys.exit(1)
    pdf = sys.argv[1]
    sexo = sys.argv[2] if len(sys.argv) > 2 else ""
    resultado = extrair_exames_via_llm(pdf, paciente_meta={"sexo": sexo})
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
