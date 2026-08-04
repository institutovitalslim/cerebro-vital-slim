#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extrator CANÔNICO de ANTROPOMETRIA (ficha de papel fotografada) — Instituto Vital Slim.

Contexto
--------
No dia da consulta (T1) a equipe preenche à MÃO a ficha "MEDIDAS CORPORAIS"
(papel timbrado da Dra.) e fotografa em JPEG/PNG (às vezes digitaliza em PDF).
Até hoje esse arquivo era lido "no olho" pelo agente de visão, ad-hoc, sem
schema, sem faixa de plausibilidade e sem trilha de revisão — o próximo ponto
de improviso do pipeline de apresentação. Este script fecha esse buraco.

Espelha o padrão do extrator canônico de bioimpedância
(`extrair_bioimpedancia_llm.py`): gpt-4o vision + Structured Outputs (schema
`strict`) + imagem inline em base64, PDF convertido por `pdftoppm`.

Diferença essencial: dígito manuscrito erra fácil (1 vs 7, 3 vs 8). Por isso
TODO valor passa por VALIDAÇÃO DE FAIXA FISIOLÓGICA e por limiar de confiança
antes de entrar no JSON. Nada entra silenciosamente:

  - `status="ilegivel"`        -> valor null, confianca 0, vai p/ revisao_manual
  - `status="em_branco"`       -> campo não existe/não preenchido na ficha -> campos_ausentes
  - valor fora da faixa        -> NÃO entra em `antropometria`; vai p/ revisao_manual (bloqueante)
  - confianca < limiar         -> entra em `antropometria` com requer_confirmacao=true
                                  E aparece em revisao_manual (aviso)
  - incoerência entre campos   -> revisao_manual (PA sistólica <= diastólica, IMC implausível, RCQ absurda)

Saída (formato consumido pelo entrypoint canônico)
--------------------------------------------------
{
  "antropometria":  {"<campo>": {"valor":..., "unidade":..., "confianca":..., ...}},
  "revisao_manual": [{"campo","label","valor_bruto","unidade","confianca","motivo","severidade"}],
  "campos_ausentes":[...],
  "derivados":      {"imc":..., "rcq":..., "pressao_arterial":"SSSxDDD mmHg"},
  "flat":           {...},   # conveniência: mesmas chaves usadas hoje em state/*-antropometria.json
  "resumo":         {...},
  "fonte": "<arquivo>", "extraido_em": "<iso>", "modelo": "...", "schema_version": "..."
}

Uso
---
  python3 extrair_antropometria.py --imagem ficha.jpeg --out antropometria.json
  python3 extrair_antropometria.py --imagem ficha.pdf  --out a.json --paciente-sexo M
  python3 extrair_antropometria.py --imagem f.jpg --out a.json --falhar-se-revisao
  python3 extrair_antropometria.py --dry-run --out mock.json     # sem rede, dados FICTÍCIOS marcados
  python3 extrair_antropometria.py --self-test                   # testes de faixa embutidos

PII: a ficha traz nome e CPF impressos. O extrator lê `nome_ficha` APENAS para
conferência de identidade (o entrypoint compara com o paciente esperado) e
NUNCA extrai CPF. A imagem só é anexada em base64 (`_imagem_b64`) com
`--embed-imagem` explícito — o default é NÃO embutir, porque essa foto exibiria
dados pessoais dentro do HTML entregue ao paciente.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
import tempfile
from collections import OrderedDict
from datetime import datetime, timedelta, timezone

SCHEMA_VERSION = "antropometria/1.0"
MODEL_PADRAO = "gpt-4o"          # vision necessário (mesmo modelo do extrator de bioimpedância)
LIMIAR_CONFIANCA_PADRAO = 0.60
BRT = timezone(timedelta(hours=-3))

# ---------------------------------------------------------------------------
# 1. CAMPOS DA FICHA + FAIXAS FISIOLÓGICAS PLAUSÍVEIS
#    (faixa = PLAUSIBILIDADE, não normalidade clínica: 150x100 mmHg é
#     hipertensão mas é plausível e DEVE passar; 999 cm de cintura não é.)
# ---------------------------------------------------------------------------
CAMPOS = OrderedDict([
    # --- impressos na ficha "MEDIDAS CORPORAIS" ---
    ("peso_kg",                   {"label": "Peso",                "ficha": "PESO",                "unidade": "kg",   "min": 25.0,  "max": 350.0, "flat": "peso_kg"}),
    ("altura_cm",                 {"label": "Altura",              "ficha": "ALTURA",              "unidade": "cm",   "min": 100.0, "max": 250.0, "flat": "altura_cm"}),
    ("cintura_cm",                {"label": "Cintura",             "ficha": "CINTURA",             "unidade": "cm",   "min": 40.0,  "max": 250.0, "flat": "cintura_cm"}),
    ("pescoco_cm",                {"label": "Pescoço",             "ficha": "PESCOÇO",             "unidade": "cm",   "min": 20.0,  "max": 70.0,  "flat": "pescoco_cm"}),
    ("peito_cm",                  {"label": "Peito",               "ficha": "PEITO",               "unidade": "cm",   "min": 50.0,  "max": 200.0, "flat": "peito_cm"}),
    ("abdomen_cm",                {"label": "Abdômen",             "ficha": "ABDÔMEN",             "unidade": "cm",   "min": 40.0,  "max": 250.0, "flat": "abdomen_cm"}),
    ("braco_direito_cm",          {"label": "Braço direito",       "ficha": "BRAÇO DIREITO",       "unidade": "cm",   "min": 15.0,  "max": 80.0,  "flat": "braco_direito_cm"}),
    ("quadril_cm",                {"label": "Quadril",             "ficha": "QUADRIL",             "unidade": "cm",   "min": 50.0,  "max": 250.0, "flat": "quadril_cm"}),
    ("perna_direita_cm",          {"label": "Perna direita",       "ficha": "PERNA DIREITA",       "unidade": "cm",   "min": 25.0,  "max": 120.0, "flat": "perna_direita_cm"}),
    ("spo2_pct",                  {"label": "SpO₂",                "ficha": "SPO2",                "unidade": "%",    "min": 50.0,  "max": 100.0, "flat": "spo2_pct"}),
    ("frequencia_cardiaca_bpm",   {"label": "Frequência cardíaca", "ficha": "FREQUÊNCIA CARDÍACA", "unidade": "bpm",  "min": 30.0,  "max": 220.0, "flat": "frequencia_cardiaca_bpm"}),
    ("pressao_sistolica_mmhg",    {"label": "PA sistólica",        "ficha": "PRESSÃO ARTERIAL",    "unidade": "mmHg", "min": 60.0,  "max": 260.0}),
    ("pressao_diastolica_mmhg",   {"label": "PA diastólica",       "ficha": "PRESSÃO ARTERIAL",    "unidade": "mmHg", "min": 30.0,  "max": 160.0}),
    # --- variantes que aparecem em fichas de outras unidades / retornos ---
    ("braco_esquerdo_cm",         {"label": "Braço esquerdo",      "ficha": "BRAÇO ESQUERDO",      "unidade": "cm",   "min": 15.0,  "max": 80.0}),
    ("antebraco_direito_cm",      {"label": "Antebraço direito",   "ficha": "ANTEBRAÇO",           "unidade": "cm",   "min": 12.0,  "max": 60.0}),
    ("coxa_direita_cm",           {"label": "Coxa direita",        "ficha": "COXA",                "unidade": "cm",   "min": 25.0,  "max": 120.0}),
    ("perna_esquerda_cm",         {"label": "Perna esquerda",      "ficha": "PERNA ESQUERDA",      "unidade": "cm",   "min": 25.0,  "max": 120.0}),
    ("panturrilha_direita_cm",    {"label": "Panturrilha direita", "ficha": "PANTURRILHA",         "unidade": "cm",   "min": 20.0,  "max": 70.0}),
    # --- dobras cutâneas (adipômetro), quando a ficha tiver ---
    ("dobra_tricipital_mm",       {"label": "Dobra tricipital",    "ficha": "DOBRA TRICIPITAL",    "unidade": "mm",   "min": 2.0,   "max": 80.0}),
    ("dobra_bicipital_mm",        {"label": "Dobra bicipital",     "ficha": "DOBRA BICIPITAL",     "unidade": "mm",   "min": 2.0,   "max": 80.0}),
    ("dobra_subescapular_mm",     {"label": "Dobra subescapular",  "ficha": "DOBRA SUBESCAPULAR",  "unidade": "mm",   "min": 2.0,   "max": 80.0}),
    ("dobra_suprailiaca_mm",      {"label": "Dobra suprailíaca",   "ficha": "DOBRA SUPRAILÍACA",   "unidade": "mm",   "min": 2.0,   "max": 80.0}),
    ("dobra_abdominal_mm",        {"label": "Dobra abdominal",     "ficha": "DOBRA ABDOMINAL",     "unidade": "mm",   "min": 2.0,   "max": 80.0}),
    ("dobra_coxa_mm",             {"label": "Dobra da coxa",       "ficha": "DOBRA COXA",          "unidade": "mm",   "min": 2.0,   "max": 80.0}),
    ("dobra_panturrilha_mm",      {"label": "Dobra panturrilha",   "ficha": "DOBRA PANTURRILHA",   "unidade": "mm",   "min": 2.0,   "max": 80.0}),
])

# Campos textuais (não numéricos) lidos da ficha.
CAMPOS_TEXTO = OrderedDict([
    ("data_medicao",           {"label": "Data da medição",       "ficha": "Data e hora",  "flat": "data"}),
    ("nome_ficha",             {"label": "Nome na ficha",         "ficha": "Nome",         "pii": True}),
    ("anotacoes_manuscritas",  {"label": "Anotações manuscritas", "ficha": "(texto livre)"}),
])

MOTIVOS = {
    "ilegivel":            "campo ilegível na foto (rasura, borrão, corte, foco) — conferir na ficha física",
    "fora_da_faixa":       "valor fora da faixa fisiológica plausível — provável erro de leitura de dígito manuscrito",
    "confianca_baixa":     "leitura com confiança abaixo do limiar — confirmar dígito na ficha física",
    "pa_incoerente":       "pressão arterial incoerente (sistólica <= diastólica)",
    "imc_implausivel":     "IMC derivado de peso/altura fora do plausível — peso ou altura lido errado",
    "rcq_implausivel":     "relação cintura/quadril fora do plausível — cintura ou quadril lido errado",
    "unidade_divergente":  "unidade lida na ficha diverge da unidade canônica do campo",
}

# ---------------------------------------------------------------------------
# 2. SCHEMA STRICT (OpenAI Structured Outputs)
#    Obs.: modo strict NÃO aceita minimum/maximum — a validação de faixa é
#    feita em Python (é exatamente o que queremos: determinística e auditável).
# ---------------------------------------------------------------------------
def _campo_numerico_schema(spec: dict) -> dict:
    return {
        "type": "object",
        "description": f"{spec['label']} (rótulo na ficha: {spec['ficha']}), unidade canônica {spec['unidade']}",
        "properties": {
            "status": {
                "type": "string",
                "enum": ["lido", "em_branco", "ilegivel"],
                "description": "lido = valor legível; em_branco = rótulo ausente da ficha ou sem nada escrito; ilegivel = escrito mas não dá pra ler com segurança",
            },
            "valor": {"type": ["number", "null"], "description": "valor numérico com ponto decimal; null se status != 'lido'"},
            "unidade_lida": {"type": ["string", "null"], "description": "unidade escrita ao lado do número, se houver (ex: 'Kg', 'cm', 'bpm', 'mmHg'); null se não escrita"},
            "confianca": {"type": "number", "description": "0.0 a 1.0 — quão certo você está do dígito manuscrito. Dígito ambíguo (1/7, 3/8, 5/6) deve baixar a confiança."},
            "observacao": {"type": ["string", "null"], "description": "curta; ex.: 'rasurado', 'dois números sobrepostos', 'valor riscado e reescrito'"},
        },
        "required": ["status", "valor", "unidade_lida", "confianca", "observacao"],
        "additionalProperties": False,
    }


def _campo_texto_schema(spec: dict) -> dict:
    return {
        "type": "object",
        "description": f"{spec['label']} (rótulo na ficha: {spec['ficha']})",
        "properties": {
            "status": {"type": "string", "enum": ["lido", "em_branco", "ilegivel"]},
            "valor": {"type": ["string", "null"]},
            "confianca": {"type": "number"},
            "observacao": {"type": ["string", "null"]},
        },
        "required": ["status", "valor", "confianca", "observacao"],
        "additionalProperties": False,
    }


def montar_schema() -> dict:
    medidas_props = {k: _campo_numerico_schema(v) for k, v in CAMPOS.items()}
    texto_props = {k: _campo_texto_schema(v) for k, v in CAMPOS_TEXTO.items()}
    return {
        "type": "object",
        "properties": {
            "medidas": {
                "type": "object",
                "properties": medidas_props,
                "required": list(medidas_props.keys()),
                "additionalProperties": False,
            },
            **texto_props,
        },
        "required": ["medidas", *texto_props.keys()],
        "additionalProperties": False,
    }


SYSTEM_PROMPT = """Você é um extrator estruturado de FICHAS DE ANTROPOMETRIA manuscritas do Instituto Vital Slim.

A imagem é a FOTO de uma ficha de papel timbrada ("Dra. Daniely Freitas" / "MEDIDAS CORPORAIS"):
os RÓTULOS são impressos e os VALORES foram escritos à mão, à caneta, ao lado de cada rótulo.
A foto pode estar torta, com sombra, reflexo ou perspectiva.

Regras absolutas:
1. NUNCA invente um valor. Se o número não estiver claramente legível, use status="ilegivel", valor=null, confianca=0.
2. Se o rótulo não existe na ficha, ou existe mas está sem nada escrito, use status="em_branco", valor=null, confianca=0.
3. Valor numérico com PONTO decimal (110.6, não "110,6"). Nunca inclua a unidade dentro de "valor".
4. Registre em "unidade_lida" a unidade escrita à mão ao lado do número, se houver (ex: "Kg", "cm", "bpm", "mmHg", "%").
5. PRESSÃO ARTERIAL é escrita como "SISTÓLICA x DIASTÓLICA" (ex.: "120 x 80 mmHg"): devolva os dois números
   separados, em pressao_sistolica_mmhg e pressao_diastolica_mmhg.
6. ALTURA: se estiver escrita em metros (1,67), converta para CENTÍMETROS (167). PESO sempre em kg.
7. "confianca" é honesta e granular: dígito manuscrito ambíguo (1 vs 7, 3 vs 8, 5 vs 6, 0 vs 6) ou número
   sobreposto/rasurado deve receber confiança BAIXA (< 0.6), mesmo que você tenha um palpite.
8. "anotacoes_manuscritas": qualquer texto escrito à mão que NÃO pertence a um campo rotulado
   (observações clínicas soltas no fim da ficha). Transcreva literalmente; não interprete.
9. "nome_ficha": apenas o nome impresso/escrito do paciente, para conferência de identidade.
   NÃO extraia CPF, telefone, endereço, token ou código de desbloqueio — ignore esses dados.
10. "data_medicao": a data (e hora, se houver) da avaliação, no formato como está escrito na ficha.

Responda APENAS o JSON do schema."""


# ---------------------------------------------------------------------------
# 3. ENTRADA: imagem/PDF -> base64
# ---------------------------------------------------------------------------
def _pdf_para_jpeg_b64(pdf_path: str, pagina: int = 1, dpi: int = 200) -> str:
    """Converte uma página do PDF em JPEG base64 (mesmo caminho do extrator de bioimpedância)."""
    with tempfile.TemporaryDirectory() as tmp:
        prefixo = os.path.join(tmp, "page")
        subprocess.run(
            ["pdftoppm", "-r", str(dpi), "-jpeg", "-f", str(pagina), "-l", str(pagina), pdf_path, prefixo],
            check=True, capture_output=True,
        )
        for sufixo in (f"-{pagina}.jpg", f"-{pagina:02d}.jpg", f"-{pagina:03d}.jpg"):
            caminho = prefixo + sufixo
            if os.path.exists(caminho):
                with open(caminho, "rb") as f:
                    return base64.b64encode(f.read()).decode("ascii")
        raise RuntimeError(f"pdftoppm não gerou imagem da página {pagina} de {pdf_path}")


def _reduzir_se_gigante(raw: bytes, limite_bytes: int = 4_000_000) -> bytes:
    """Foto de celular pode passar de 10 MB. Reduz com Pillow se disponível; senão devolve como está."""
    if len(raw) <= limite_bytes:
        return raw
    try:
        import io
        from PIL import Image  # type: ignore
        img = Image.open(io.BytesIO(raw))
        img.thumbnail((2400, 2400))
        buf = io.BytesIO()
        img.convert("RGB").save(buf, format="JPEG", quality=88)
        return buf.getvalue()
    except Exception:
        return raw


def imagem_para_b64(caminho: str, pagina: int = 1) -> tuple:
    """Devolve (base64, mime). Aceita .jpg/.jpeg/.png/.webp/.pdf."""
    if not os.path.exists(caminho):
        raise FileNotFoundError(f"arquivo não encontrado: {caminho}")
    ext = os.path.splitext(caminho)[1].lower()
    if ext == ".pdf":
        return _pdf_para_jpeg_b64(caminho, pagina=pagina), "image/jpeg"
    if ext not in (".jpg", ".jpeg", ".png", ".webp"):
        raise ValueError(f"extensão não suportada: {ext} (use jpg, jpeg, png, webp ou pdf)")
    with open(caminho, "rb") as f:
        raw = _reduzir_se_gigante(f.read())
    mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}[ext.lstrip(".")]
    if len(raw) > 0 and mime == "image/png" and raw[:2] == b"\xff\xd8":
        mime = "image/jpeg"  # thumbnail reencodou em JPEG
    return base64.b64encode(raw).decode("ascii"), mime


# ---------------------------------------------------------------------------
# 4. CHAMADA DE VISÃO (gpt-4o + Structured Outputs strict)
# ---------------------------------------------------------------------------
def _load_api_key() -> str:
    """Mesma ordem de precedência do extrator canônico de bioimpedância."""
    for p in ["/root/.openclaw/secure/openai.env", "/root/.openclaw/.env.runtime", "/root/.openclaw/.env"]:
        if not os.path.exists(p):
            continue
        try:
            with open(p) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("OPENAI_API_KEY="):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if val.startswith("sk-"):
                            return val
        except OSError:
            continue
    return os.environ.get("OPENAI_API_KEY", "")


def chamar_visao(img_b64: str, mime: str, paciente_meta: dict = None, model: str = MODEL_PADRAO) -> dict:
    """Chama gpt-4o vision com imagem inline e schema strict. Devolve o payload BRUTO do modelo."""
    api_key = _load_api_key()
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY não configurada (procurado em /root/.openclaw/secure/openai.env, "
            ".env.runtime, .env e no ambiente). Use --dry-run para exercitar o pipeline sem visão."
        )
    try:
        from openai import OpenAI  # import tardio: --help/--self-test/--dry-run não dependem do pacote
    except ImportError as e:
        raise RuntimeError(f"pacote openai indisponível ({e}). Use --dry-run ou instale: pip install openai")

    meta = paciente_meta or {}
    ctx = ", ".join(f"{k}={v}" for k, v in meta.items() if v)
    user_msg = "Extraia TODOS os campos desta ficha de antropometria manuscrita."
    if ctx:
        user_msg += f" Contexto do paciente (apenas para desambiguar leitura, NÃO para preencher campo em branco): {ctx}."

    client = OpenAI(api_key=api_key)
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": [
                {"type": "text", "text": user_msg},
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{img_b64}", "detail": "high"}},
            ]},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "antropometria", "schema": montar_schema(), "strict": True},
        },
        temperature=0.0,
    )
    return json.loads(resp.choices[0].message.content)


# ---------------------------------------------------------------------------
# 5. VALIDAÇÃO (faixa fisiológica + confiança + coerência entre campos)
# ---------------------------------------------------------------------------
def _rev(campo: str, spec: dict, valor, confianca, motivo_key: str, severidade: str, detalhe: str = "") -> dict:
    return {
        "campo": campo,
        "label": spec.get("label", campo),
        "rotulo_ficha": spec.get("ficha"),
        "valor_bruto": valor,
        "unidade": spec.get("unidade"),
        "confianca": confianca,
        "motivo": MOTIVOS.get(motivo_key, motivo_key),
        "motivo_codigo": motivo_key,
        "severidade": severidade,   # "bloqueante" = NÃO entra em antropometria | "aviso" = entra marcado
        "detalhe": detalhe or None,
    }


_UNIDADES_EQUIV = {
    "kg": {"kg", "quilos", "k"},
    "cm": {"cm", "centimetros", "centímetros"},
    "%": {"%", "pct", "por cento"},
    "bpm": {"bpm", "batimentos", "b/min"},
    "mm": {"mm", "milimetros", "milímetros"},
    "mmhg": {"mmhg", "mm hg"},
}


def _unidade_bate(canonica: str, lida) -> bool:
    if not lida:
        return True
    equivalentes = _UNIDADES_EQUIV.get(canonica.lower(), {canonica.lower()})
    return str(lida).strip().lower() in equivalentes


def validar_payload(bruto: dict, limiar: float = LIMIAR_CONFIANCA_PADRAO) -> dict:
    """Aplica faixas fisiológicas, limiar de confiança e checagens cruzadas.

    Devolve (antropometria, revisao_manual, campos_ausentes, textos, derivados).
    """
    antropometria: "OrderedDict[str, dict]" = OrderedDict()
    revisao: list = []
    ausentes: list = []
    medidas = (bruto or {}).get("medidas") or {}

    for campo, spec in CAMPOS.items():
        item = medidas.get(campo) or {}
        status = item.get("status") or ("lido" if item.get("valor") is not None else "em_branco")
        valor = item.get("valor")
        conf = item.get("confianca")
        conf = float(conf) if isinstance(conf, (int, float)) else 0.0
        conf = max(0.0, min(1.0, conf))
        obs = item.get("observacao")
        unidade_lida = item.get("unidade_lida")

        if status == "em_branco":
            ausentes.append(campo)
            continue

        if status == "ilegivel" or valor is None:
            revisao.append(_rev(campo, spec, None, 0.0, "ilegivel", "bloqueante", obs or ""))
            continue

        try:
            valor = float(valor)
        except (TypeError, ValueError):
            revisao.append(_rev(campo, spec, item.get("valor"), 0.0, "ilegivel", "bloqueante", "valor não numérico"))
            continue

        # ---- FAIXA FISIOLÓGICA (bloqueante) ----
        if not (spec["min"] <= valor <= spec["max"]):
            revisao.append(_rev(
                campo, spec, valor, conf, "fora_da_faixa", "bloqueante",
                f"faixa aceita: {spec['min']:g}–{spec['max']:g} {spec['unidade']}",
            ))
            continue

        registro = {
            "valor": round(valor, 2),
            "unidade": spec["unidade"],
            "confianca": round(conf, 2),
            "label": spec["label"],
            "requer_confirmacao": False,
            "observacao": obs,
        }

        # ---- CONFIANÇA (aviso: entra, mas marcado e listado) ----
        if conf < limiar:
            registro["requer_confirmacao"] = True
            revisao.append(_rev(campo, spec, valor, conf, "confianca_baixa", "aviso",
                                f"limiar {limiar:.2f}"))

        # ---- UNIDADE divergente (aviso) ----
        if not _unidade_bate(spec["unidade"], unidade_lida):
            registro["requer_confirmacao"] = True
            revisao.append(_rev(campo, spec, valor, conf, "unidade_divergente", "aviso",
                                f"unidade lida na ficha: {unidade_lida!r}"))

        antropometria[campo] = registro

    # ---------------- checagens cruzadas ----------------
    derivados = {}

    def _v(c):
        r = antropometria.get(c)
        return r["valor"] if r else None

    sis, dia = _v("pressao_sistolica_mmhg"), _v("pressao_diastolica_mmhg")
    if sis is not None and dia is not None:
        if sis <= dia:
            for c in ("pressao_sistolica_mmhg", "pressao_diastolica_mmhg"):
                spec = CAMPOS[c]
                revisao.append(_rev(c, spec, _v(c), antropometria[c]["confianca"], "pa_incoerente",
                                    "bloqueante", f"lido {sis:g} x {dia:g} mmHg"))
                antropometria.pop(c, None)
        else:
            derivados["pressao_arterial"] = f"{sis:g}x{dia:g} mmHg"

    peso, altura = _v("peso_kg"), _v("altura_cm")
    if peso and altura:
        imc = peso / ((altura / 100.0) ** 2)
        if 10.0 <= imc <= 80.0:
            derivados["imc"] = round(imc, 1)
        else:
            for c in ("peso_kg", "altura_cm"):
                spec = CAMPOS[c]
                if c in antropometria:
                    antropometria[c]["requer_confirmacao"] = True
                    revisao.append(_rev(c, spec, _v(c), antropometria[c]["confianca"], "imc_implausivel",
                                        "aviso", f"IMC derivado = {imc:.1f} (plausível 10–80)"))
            derivados["imc"] = None

    cintura, quadril = _v("cintura_cm"), _v("quadril_cm")
    if cintura and quadril:
        rcq = cintura / quadril
        if 0.5 <= rcq <= 1.6:
            derivados["rcq"] = round(rcq, 2)
        else:
            for c in ("cintura_cm", "quadril_cm"):
                spec = CAMPOS[c]
                if c in antropometria:
                    antropometria[c]["requer_confirmacao"] = True
                    revisao.append(_rev(c, spec, _v(c), antropometria[c]["confianca"], "rcq_implausivel",
                                        "aviso", f"RCQ derivada = {rcq:.2f} (plausível 0,50–1,60)"))
            derivados["rcq"] = None

    # ---------------- campos textuais ----------------
    textos = OrderedDict()
    for campo, spec in CAMPOS_TEXTO.items():
        item = (bruto or {}).get(campo) or {}
        status = item.get("status") or ("lido" if item.get("valor") else "em_branco")
        valor = item.get("valor")
        conf = item.get("confianca")
        conf = float(conf) if isinstance(conf, (int, float)) else 0.0
        if status == "em_branco" or not valor:
            ausentes.append(campo)
            continue
        if status == "ilegivel":
            revisao.append(_rev(campo, spec, None, 0.0, "ilegivel", "bloqueante", item.get("observacao") or ""))
            continue
        textos[campo] = {
            "valor": str(valor).strip(),
            "unidade": None,
            "confianca": round(max(0.0, min(1.0, conf)), 2),
            "label": spec["label"],
            "requer_confirmacao": conf < LIMIAR_CONFIANCA_PADRAO,
            "observacao": item.get("observacao"),
        }

    return {
        "antropometria": antropometria,
        "textos": textos,
        "revisao_manual": revisao,
        "campos_ausentes": ausentes,
        "derivados": derivados,
    }


def montar_flat(antropometria: dict, textos: dict, derivados: dict) -> dict:
    """Projeção plana — mesmas chaves já usadas em state/*-antropometria.json e no render.

    Só entram campos que PASSARAM na validação (nada fora de faixa, nada ilegível).
    """
    flat = OrderedDict()
    for campo, spec in CAMPOS.items():
        chave = spec.get("flat")
        if chave and campo in antropometria:
            flat[chave] = antropometria[campo]["valor"]
    for campo, spec in CAMPOS_TEXTO.items():
        chave = spec.get("flat")
        if chave and campo in textos:
            flat[chave] = textos[campo]["valor"]
    if derivados.get("pressao_arterial"):
        flat["pressao_arterial"] = derivados["pressao_arterial"]
    return flat


# ---------------------------------------------------------------------------
# 6. ORQUESTRAÇÃO
# ---------------------------------------------------------------------------
def montar_saida(bruto: dict, fonte: str, limiar: float, modelo: str,
                 img_b64: str = None, mime: str = None, mock: bool = False) -> dict:
    val = validar_payload(bruto, limiar=limiar)
    antro, textos = val["antropometria"], val["textos"]
    saida = OrderedDict()
    saida["antropometria"] = OrderedDict(list(antro.items()) + list(textos.items()))
    saida["revisao_manual"] = val["revisao_manual"]
    saida["campos_ausentes"] = val["campos_ausentes"]
    saida["derivados"] = val["derivados"]
    saida["flat"] = montar_flat(antro, textos, val["derivados"])
    saida["resumo"] = {
        "campos_extraidos": len(saida["antropometria"]),
        "campos_revisao_manual": len(val["revisao_manual"]),
        "campos_revisao_bloqueantes": sum(1 for r in val["revisao_manual"] if r["severidade"] == "bloqueante"),
        "campos_ausentes": len(val["campos_ausentes"]),
        "campos_requer_confirmacao": sum(1 for r in saida["antropometria"].values() if r.get("requer_confirmacao")),
        "limiar_confianca": limiar,
    }
    saida["fonte"] = os.path.abspath(fonte) if fonte else None
    saida["extraido_em"] = datetime.now(BRT).isoformat(timespec="seconds")
    saida["modelo"] = modelo
    saida["schema_version"] = SCHEMA_VERSION
    if mock:
        saida["_mock"] = True
        saida["_dados_ficticios"] = True
        saida["_uso_clinico_proibido"] = True
    if img_b64:
        saida["_imagem_b64"] = img_b64
        saida["_imagem_mime"] = mime
    return saida


def extrair_antropometria(caminho: str, paciente_meta: dict = None,
                          limiar: float = LIMIAR_CONFIANCA_PADRAO,
                          model: str = MODEL_PADRAO, pagina: int = 1,
                          embed_imagem: bool = False) -> dict:
    """API importável — espelha extrair_bioimpedancia(). Levanta em caso de falha de visão."""
    img_b64, mime = imagem_para_b64(caminho, pagina=pagina)
    bruto = chamar_visao(img_b64, mime, paciente_meta=paciente_meta, model=model)
    return montar_saida(bruto, caminho, limiar, model,
                        img_b64=img_b64 if embed_imagem else None, mime=mime)


def detectar_ficha_antropometria(arquivos: list) -> dict:
    """Encontra a ficha de antropometria numa lista de arquivos (Drive ou disco).

    Espelha detectar_pdf_bioimpedancia(): casa por nome, mais recente primeiro
    (a lista já vem ordenada por modifiedTime DESC em buscar_exames_drive.py).
    """
    chaves = ("antropometri", "medidas corporais", "medidas-corporais", "medidas_corporais", "ficha de medidas")
    for p in arquivos or []:
        nome = str(p.get("nome", p) if isinstance(p, dict) else p).lower()
        if any(k in nome for k in chaves) and "nf" not in nome:
            return p
    return None


# ---------------------------------------------------------------------------
# 7. MOCK (--dry-run) — valores SENTINELA, jamais clínicos
# ---------------------------------------------------------------------------
def _mock_campo(status="lido", valor=None, conf=0.95, unidade=None, obs=None):
    return {"status": status, "valor": valor, "unidade_lida": unidade, "confianca": conf, "observacao": obs}


def payload_mock() -> dict:
    """Payload sintético que exercita TODOS os caminhos de validação.

    Valores são SENTINELAS redondos e um deles é deliberadamente absurdo — não
    representam nenhum paciente. A saída sai marcada com _dados_ficticios=True.
    """
    medidas = {c: _mock_campo(status="em_branco", conf=0.0) for c in CAMPOS}
    medidas["peso_kg"] = _mock_campo(valor=100.0, unidade="Kg")
    medidas["altura_cm"] = _mock_campo(valor=170.0, unidade="cm")
    medidas["cintura_cm"] = _mock_campo(valor=999.0, unidade="cm")          # fora da faixa -> bloqueante
    medidas["quadril_cm"] = _mock_campo(valor=100.0, unidade="cm")
    medidas["abdomen_cm"] = _mock_campo(valor=100.0, conf=0.30)             # confiança baixa -> aviso
    medidas["pescoco_cm"] = _mock_campo(status="ilegivel", conf=0.0, obs="borrão de caneta")
    medidas["spo2_pct"] = _mock_campo(valor=98.0, unidade="%")
    medidas["frequencia_cardiaca_bpm"] = _mock_campo(valor=70.0, unidade="bpm")
    medidas["pressao_sistolica_mmhg"] = _mock_campo(valor=120.0, unidade="mmHg")
    medidas["pressao_diastolica_mmhg"] = _mock_campo(valor=80.0, unidade="mmHg")
    return {
        "medidas": medidas,
        "data_medicao": {"status": "lido", "valor": "01/01/2000", "confianca": 0.99, "observacao": "MOCK"},
        "nome_ficha": {"status": "lido", "valor": "PACIENTE FICTICIO DE TESTE", "confianca": 0.99, "observacao": "MOCK"},
        "anotacoes_manuscritas": {"status": "em_branco", "valor": None, "confianca": 0.0, "observacao": None},
    }


# ---------------------------------------------------------------------------
# 8. SELF-TEST (sem rede) — evidência de que a validação bloqueia de verdade
# ---------------------------------------------------------------------------
def self_test() -> int:
    falhas = []

    def check(nome, cond, detalhe=""):
        print(f"  [{'PASS' if cond else 'FALHA'}] {nome}{(' — ' + detalhe) if detalhe and not cond else ''}")
        if not cond:
            falhas.append(nome)

    print("SELF-TEST extrair_antropometria.py")

    # T1 — valor absurdo vai p/ revisao_manual (bloqueante) e NÃO entra em antropometria
    r = validar_payload({"medidas": {"cintura_cm": _mock_campo(valor=999.0)}})
    check("T1 fora-de-faixa não entra em antropometria", "cintura_cm" not in r["antropometria"])
    rev = [x for x in r["revisao_manual"] if x["campo"] == "cintura_cm"]
    check("T1 fora-de-faixa vira revisao_manual bloqueante",
          len(rev) == 1 and rev[0]["motivo_codigo"] == "fora_da_faixa" and rev[0]["severidade"] == "bloqueante")

    # T1b — o limite superior exato ainda é aceito (faixa inclusiva)
    r = validar_payload({"medidas": {"cintura_cm": _mock_campo(valor=CAMPOS["cintura_cm"]["max"])}})
    check("T1b limite superior da faixa é aceito", "cintura_cm" in r["antropometria"])

    # T1c — valor plausível mas clinicamente alterado NÃO é barrado (PA 150x100, SpO2 92)
    r = validar_payload({"medidas": {
        "pressao_sistolica_mmhg": _mock_campo(valor=150.0),
        "pressao_diastolica_mmhg": _mock_campo(valor=100.0),
        "spo2_pct": _mock_campo(valor=92.0)}})
    check("T1c valor alterado mas plausível passa (não é triagem clínica)",
          len(r["antropometria"]) == 3 and r["derivados"].get("pressao_arterial") == "150x100 mmHg")

    # T2 — ilegível: valor null, confianca 0, motivo
    r = validar_payload({"medidas": {"pescoco_cm": _mock_campo(status="ilegivel", conf=0.0)}})
    rev = [x for x in r["revisao_manual"] if x["campo"] == "pescoco_cm"]
    check("T2 ilegível -> null + confianca 0 + motivo",
          "pescoco_cm" not in r["antropometria"] and len(rev) == 1
          and rev[0]["valor_bruto"] is None and rev[0]["confianca"] == 0.0
          and rev[0]["motivo_codigo"] == "ilegivel")

    # T3 — em branco vai p/ campos_ausentes, não polui revisao_manual
    r = validar_payload({"medidas": {"dobra_coxa_mm": _mock_campo(status="em_branco", conf=0.0)}})
    check("T3 em_branco -> campos_ausentes (sem ruído em revisao_manual)",
          "dobra_coxa_mm" in r["campos_ausentes"] and not r["revisao_manual"])

    # T4 — confiança baixa: entra marcado E é listado (nunca silencioso)
    r = validar_payload({"medidas": {"abdomen_cm": _mock_campo(valor=100.0, conf=0.30)}}, limiar=0.60)
    rev = [x for x in r["revisao_manual"] if x["motivo_codigo"] == "confianca_baixa"]
    check("T4 confiança baixa -> entra com requer_confirmacao + revisao_manual (aviso)",
          r["antropometria"].get("abdomen_cm", {}).get("requer_confirmacao") is True
          and len(rev) == 1 and rev[0]["severidade"] == "aviso")

    # T5 — PA incoerente (sistólica <= diastólica) derruba os dois campos
    r = validar_payload({"medidas": {
        "pressao_sistolica_mmhg": _mock_campo(valor=80.0),
        "pressao_diastolica_mmhg": _mock_campo(valor=120.0)}})
    check("T5 PA incoerente -> ambos p/ revisao_manual",
          not r["antropometria"]
          and len([x for x in r["revisao_manual"] if x["motivo_codigo"] == "pa_incoerente"]) == 2)

    # T6 — IMC implausível marca peso e altura
    r = validar_payload({"medidas": {"peso_kg": _mock_campo(valor=30.0), "altura_cm": _mock_campo(valor=200.0)}})
    check("T6 IMC implausível -> aviso em peso e altura",
          r["derivados"].get("imc") is None
          and len([x for x in r["revisao_manual"] if x["motivo_codigo"] == "imc_implausivel"]) == 2)

    # T7 — unidade divergente vira aviso
    r = validar_payload({"medidas": {"peso_kg": _mock_campo(valor=100.0, unidade="cm")}})
    check("T7 unidade divergente -> aviso",
          len([x for x in r["revisao_manual"] if x["motivo_codigo"] == "unidade_divergente"]) == 1)

    # T8 — flat só carrega o que passou na validação
    saida = montar_saida(payload_mock(), "mock", LIMIAR_CONFIANCA_PADRAO, "mock", mock=True)
    check("T8 flat exclui campo fora de faixa", "cintura_cm" not in saida["flat"])
    check("T8 flat traz PA formatada", saida["flat"].get("pressao_arterial") == "120x80 mmHg")
    check("T8 mock sai marcado como fictício", saida.get("_dados_ficticios") is True)
    check("T8 saída tem as 4 chaves do contrato",
          all(k in saida for k in ("antropometria", "revisao_manual", "fonte", "extraido_em")))

    # T9 — schema strict bem formado (todas as props em required, additionalProperties False)
    sch = montar_schema()
    med = sch["properties"]["medidas"]
    check("T9 schema strict: medidas com todas as props em required",
          set(med["properties"]) == set(med["required"]) and med["additionalProperties"] is False)
    check("T9 schema strict: raiz fechada",
          set(sch["properties"]) == set(sch["required"]) and sch["additionalProperties"] is False)

    # T10 — nenhum campo do schema fica sem faixa fisiológica
    check("T10 todo campo numérico tem faixa min/max",
          all(isinstance(s.get("min"), float) and isinstance(s.get("max"), float) and s["min"] < s["max"]
              for s in CAMPOS.values()))

    print(f"\n{len(falhas)} falha(s)." if falhas else "\nTodos os testes passaram.")
    return 1 if falhas else 0


# ---------------------------------------------------------------------------
# 9. CLI
# ---------------------------------------------------------------------------
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="extrair_antropometria.py",
        description="Extrator canônico de antropometria (ficha de papel manuscrita) via gpt-4o vision + schema strict, com validação de faixa fisiológica.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""exemplos:
  extrair_antropometria.py --imagem ficha.jpeg --out antropometria.json
  extrair_antropometria.py --imagem ficha.pdf --pagina 1 --out a.json --paciente-sexo M
  extrair_antropometria.py --imagem f.jpg --out a.json --falhar-se-revisao   # exit 2 se houver bloqueante
  extrair_antropometria.py --dry-run --out mock.json                          # sem rede, dados FICTÍCIOS
  extrair_antropometria.py --self-test                                        # testes de validação embutidos

exit codes: 0 ok | 1 erro | 2 revisão manual bloqueante (só com --falhar-se-revisao)""")
    ap.add_argument("--imagem", help="ficha de antropometria: .jpg, .jpeg, .png, .webp ou .pdf")
    ap.add_argument("--out", help="arquivo JSON de saída (default: stdout)")
    ap.add_argument("--paciente-sexo", choices=["M", "F"], help="sexo do paciente (contexto de leitura)")
    ap.add_argument("--paciente-idade", help="idade do paciente (contexto de leitura)")
    ap.add_argument("--paciente-nome", help="nome esperado — confere contra o nome impresso na ficha")
    ap.add_argument("--pagina", type=int, default=1, help="página do PDF (default: 1)")
    ap.add_argument("--limiar-confianca", type=float, default=LIMIAR_CONFIANCA_PADRAO,
                    help=f"abaixo disso o campo é marcado p/ conferência (default: {LIMIAR_CONFIANCA_PADRAO})")
    ap.add_argument("--model", default=MODEL_PADRAO, help=f"modelo de visão (default: {MODEL_PADRAO})")
    ap.add_argument("--embed-imagem", action="store_true",
                    help="anexa a foto em base64 (_imagem_b64). OFF por padrão: a ficha contém dados pessoais")
    ap.add_argument("--falhar-se-revisao", action="store_true",
                    help="exit 2 se houver campo bloqueante em revisao_manual")
    ap.add_argument("--dry-run", action="store_true", help="não chama visão; usa payload MOCK marcado como fictício")
    ap.add_argument("--mock-json", help="usa payload bruto de visão vindo de arquivo (teste determinístico)")
    ap.add_argument("--self-test", action="store_true", help="roda os testes de validação embutidos e sai")
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()

    if not args.imagem and not (args.dry_run or args.mock_json):
        ap.error("--imagem é obrigatório (ou use --dry-run / --mock-json / --self-test)")

    img_b64 = mime = None
    mock = False
    try:
        if args.mock_json:
            with open(args.mock_json, encoding="utf-8") as f:
                bruto = json.load(f)
            modelo = f"mock-json:{os.path.basename(args.mock_json)}"
        elif args.dry_run:
            bruto = payload_mock()
            modelo = "dry-run (sem visão)"
            mock = True
        else:
            img_b64, mime = imagem_para_b64(args.imagem, pagina=args.pagina)
            meta = {k: v for k, v in (("sexo", args.paciente_sexo), ("idade", args.paciente_idade)) if v}
            bruto = chamar_visao(img_b64, mime, paciente_meta=meta, model=args.model)
            modelo = args.model
    except Exception as e:
        print(f"ERRO: {type(e).__name__}: {e}", file=sys.stderr)
        return 1

    saida = montar_saida(bruto, args.imagem or (args.mock_json or "dry-run"),
                         args.limiar_confianca, modelo,
                         img_b64=img_b64 if args.embed_imagem else None, mime=mime, mock=mock)

    # conferência de identidade (não bloqueia: só sinaliza)
    if args.paciente_nome:
        lido = (saida["antropometria"].get("nome_ficha") or {}).get("valor") or ""
        def _norm(s):
            return " ".join(str(s).lower().replace(".", " ").split())
        a, b = _norm(args.paciente_nome), _norm(lido)
        bate = bool(b) and (a in b or b in a or (a.split()[:1] == b.split()[:1] and a.split()[-1:] == b.split()[-1:]))
        saida["conferencia_identidade"] = {"esperado_informado": True, "confere": bate}
        if not bate:
            saida["revisao_manual"].append({
                "campo": "nome_ficha", "label": "Nome na ficha", "rotulo_ficha": "Nome",
                "valor_bruto": None, "unidade": None, "confianca": None,
                "motivo": "nome da ficha não confere com o paciente esperado — possível ficha trocada",
                "motivo_codigo": "identidade_divergente", "severidade": "bloqueante", "detalhe": None,
            })
            saida["resumo"]["campos_revisao_manual"] = len(saida["revisao_manual"])
            saida["resumo"]["campos_revisao_bloqueantes"] += 1

    texto = json.dumps(saida, ensure_ascii=False, indent=2)
    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(texto + "\n")
        r = saida["resumo"]
        print(f"OK  {args.out}")
        print(f"    extraidos={r['campos_extraidos']}  revisao_manual={r['campos_revisao_manual']} "
              f"(bloqueantes={r['campos_revisao_bloqueantes']})  ausentes={r['campos_ausentes']} "
              f"  requer_confirmacao={r['campos_requer_confirmacao']}")
    else:
        print(texto)

    if args.falhar_se_revisao and saida["resumo"]["campos_revisao_bloqueantes"] > 0:
        print("REVISAO MANUAL BLOQUEANTE — não seguir para o render sem conferir a ficha física.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
