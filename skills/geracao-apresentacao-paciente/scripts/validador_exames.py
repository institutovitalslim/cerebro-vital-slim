#!/usr/bin/env python3
"""
Validador v3 — Camada robusta de validação de exames laboratoriais.

CAMADAS:
  L0 Pre-check     — sexo do paciente obrigatório (RC-01)
  L1 Schema        — campos obrigatórios e tipos
  L2 Catálogo      — nome canônico em refs_canonicas.json
  L3 Plausibilidade — valor no range fisiológico absoluto
  L4 Sex+age       — ref aplicável encontrada
  L5 Cross-check Friedewald — LDL ≈ Total - HDL - VLDL
  L6 Status recalc — recalcula com refs canônicas
  L7 Unidade       — unidade do laudo compatível com canônica
  L8 Cross-checks fisiológicos — Wintrobe, HOMA-IR, HbA1c↔Glicemia Média, índices
  L9 Consistência intra-grupo — Glicose vs HbA1c, TGO/TGP ratio, anemia coerente
  L10 Anti-alucinação — valor existe literalmente no texto do PDF
  L11 LLM uncertainty — observação do LLM sinaliza incerteza
"""
import json
import os
import re
import unicodedata
from pathlib import Path

REFS_PATH = Path(__file__).parent.parent / "assets" / "refs_canonicas.json"


def _load_refs():
    with open(REFS_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return {k: v for k, v in data.items() if not k.startswith("_")}


REFS = _load_refs()


# =============================================================================
# L7 — Tabela de equivalência de unidades
# =============================================================================
# Cada linha: forma normalizada → variantes aceitas
# Pre-normalizacao: substitui µ -> u, espacos extras
def _pre_norm_unit(s):
    if not s:
        return ''
    s = s.replace('μ', 'u').replace('µ', 'u')  # caracter unicode mu -> u
    s = s.replace('³', '3').replace('²', '2')  # superscript -> ascii
    s = s.lower().strip()
    s = ' '.join(s.split())  # collapse spaces
    return s

UNIT_EQUIV = {
    'mg/dl':   {'mg/dl', 'mg dl', 'mg.dl', 'mg /dl'},
    'g/dl':    {'g/dl', 'g dl', 'gr/dl'},
    'ng/ml':   {'ng/ml', 'nanog/ml', 'ng ml'},
    'pg/ml':   {'pg/ml', 'pg ml'},
    'ug/dl':   {'ug/dl', 'mcg/dl'},
    'ug/ml':   {'ug/ml', 'mcg/ml'},
    'uui/ml':  {'uui/ml', 'uiu/ml', 'miu/l', 'microui/ml'},
    'mu/ml':   {'mu/ml', 'uu/ml', 'mui/ml', 'miu/ml'},
    'u/l':     {'u/l', 'ui/l', 'iu/l'},
    '%':       {'%'},
    # Unidades absolutas de contagem celular — mil/mm3 == /mm3 quando valor ja convertido
    '/mm3':    {'/mm3', '/mcl', '/ul', 'leuc/mm3', 'mil/mm3', 'mil mm3', 'cels/mm3'},
    'milhoes/mm3': {'milhoes/mm3', 'milhoes mm3', 'milh/mm3', 'milh', '10^6/ul', 'milhoes'},
    'fl':      {'fl'},
    'pg':      {'pg'},
    'umol/l':  {'umol/l', 'micromol/l'},
    'nmol/l':  {'nmol/l'},
    # mEq/L ≡ mmol/L para ions monovalentes (Na+, K+, Cl-)
    'meq/l':   {'meq/l', 'mmol/l'},
    'mm/h':    {'mm/h', 'mm h'},
    '':        {'', ' '},
}

# Inverso: variante → forma normalizada (com pre-norm aplicado)
UNIT_LOOKUP = {}
for canon, variants in UNIT_EQUIV.items():
    for v in variants:
        UNIT_LOOKUP[_pre_norm_unit(v)] = canon


def _normalize_unit(s):
    if s is None:
        return ''
    s = _pre_norm_unit(s)
    if not s:
        return ''
    return UNIT_LOOKUP.get(s, s)


def _units_compativeis(u_laudo, u_canonica):
    """Retorna True se as unidades são equivalentes."""
    if not u_canonica:
        return True  # canônica vazia = adimensional, qualquer coisa serve
    if not u_laudo:
        return True  # laudo sem unidade — não bloqueia, apenas adopta canônica
    return _normalize_unit(u_laudo) == _normalize_unit(u_canonica)


# =============================================================================
# L8 — Cross-checks fisiológicos
# =============================================================================
def _crosscheck_wintrobe(by_canon):
    """Hematócrito ≈ 3 × Hemoglobina (±15%)."""
    if "Hematócrito" not in by_canon or "Hemoglobina" not in by_canon:
        return None
    hct = by_canon["Hematócrito"]["valor_f"]
    hb = by_canon["Hemoglobina"]["valor_f"]
    expected = hb * 3
    delta_pct = abs(hct - expected) / expected * 100
    if delta_pct > 15:
        return f"L8 Wintrobe: Hct={hct}% vs 3×Hb={expected:.1f} (Δ{delta_pct:.0f}%)"
    return None


def _crosscheck_indices_hematologicos(by_canon):
    """VCM = Hct×10/Hemácias, HCM = Hb×10/Hemácias, CHCM = Hb×100/Hct."""
    avisos = []
    if all(k in by_canon for k in ["VCM", "Hematócrito", "Hemácias"]):
        vcm = by_canon["VCM"]["valor_f"]
        hct = by_canon["Hematócrito"]["valor_f"]
        hem = by_canon["Hemácias"]["valor_f"]
        if hem > 0:
            expected = (hct * 10) / hem
            if abs(vcm - expected) / max(expected, 1) > 0.10:
                avisos.append(f"L8 índice VCM: {vcm} vs calc {expected:.1f} (Hct×10/Hemácias)")
    if all(k in by_canon for k in ["HCM", "Hemoglobina", "Hemácias"]):
        hcm = by_canon["HCM"]["valor_f"]
        hb = by_canon["Hemoglobina"]["valor_f"]
        hem = by_canon["Hemácias"]["valor_f"]
        if hem > 0:
            expected = (hb * 10) / hem
            if abs(hcm - expected) / max(expected, 1) > 0.10:
                avisos.append(f"L8 índice HCM: {hcm} vs calc {expected:.1f} (Hb×10/Hemácias)")
    if all(k in by_canon for k in ["CHCM", "Hemoglobina", "Hematócrito"]):
        chcm = by_canon["CHCM"]["valor_f"]
        hb = by_canon["Hemoglobina"]["valor_f"]
        hct = by_canon["Hematócrito"]["valor_f"]
        if hct > 0:
            expected = (hb * 100) / hct
            if abs(chcm - expected) / max(expected, 1) > 0.10:
                avisos.append(f"L8 índice CHCM: {chcm} vs calc {expected:.1f} (Hb×100/Hct)")
    return avisos


def _crosscheck_homa_ir(by_canon):
    """HOMA-IR = (Glicose × Insulina) / 405."""
    if not all(k in by_canon for k in ["HOMA-IR", "Glicose", "Insulina"]):
        return None
    homa = by_canon["HOMA-IR"]["valor_f"]
    glic = by_canon["Glicose"]["valor_f"]
    ins = by_canon["Insulina"]["valor_f"]
    expected = (glic * ins) / 405
    delta_pct = abs(homa - expected) / max(expected, 0.1) * 100
    if delta_pct > 25:
        return f"L8 HOMA-IR: {homa} vs calc {expected:.2f} (Glic×Ins/405) (Δ{delta_pct:.0f}%)"
    return None


def _crosscheck_glicemia_media_hba1c(by_canon):
    """Glicemia Média Estimada ≈ HbA1c × 28.7 - 46.7 (Nathan 2008/ADAG)."""
    if not all(k in by_canon for k in ["HbA1c", "Glicemia Média"]):
        return None
    hba = by_canon["HbA1c"]["valor_f"]
    gme = by_canon["Glicemia Média"]["valor_f"]
    expected = hba * 28.7 - 46.7
    delta_pct = abs(gme - expected) / max(expected, 1) * 100
    if delta_pct > 15:
        return f"L8 GME↔HbA1c: GME={gme} vs calc {expected:.0f} mg/dL (Δ{delta_pct:.0f}%)"
    return None


# =============================================================================
# L9 — Consistência intra-grupo
# =============================================================================
def _consistencia_glicemica(by_canon):
    """Glicose normal mas HbA1c alta (ou vice-versa) → suspeita."""
    avisos = []
    if "Glicose" in by_canon and "HbA1c" in by_canon:
        glic = by_canon["Glicose"]
        hba = by_canon["HbA1c"]
        # Glicose normal mas HbA1c alta crit
        if glic["status_final"] == "normal" and hba["status_final"] == "crit":
            avisos.append(f"L9 incoerência glicídica: Glicose normal ({glic['valor_f']}) "
                          f"mas HbA1c crítica ({hba['valor_f']}%) — verificar")
        # HbA1c normal mas Glicose alta
        if hba["status_final"] == "normal" and glic["status_final"] in ("alert", "crit") and glic["valor_f"] >= 126:
            avisos.append(f"L9 incoerência glicídica: HbA1c normal mas Glicose ≥126 mg/dL")
    return avisos


def _consistencia_hepatica(by_canon):
    """TGO/TGP ratio: >3 sugere álcool ou erro; >2 com TGP normal sugere muscular."""
    if "TGO" in by_canon and "TGP" in by_canon:
        tgo = by_canon["TGO"]["valor_f"]
        tgp = by_canon["TGP"]["valor_f"]
        if tgp > 0:
            ratio = tgo / tgp
            if ratio > 3:
                return [f"L9 ratio TGO/TGP={ratio:.1f} (>3 sugere álcool/cirrose ou erro)"]
    return []


def _consistencia_anemia(by_canon):
    """Anemia coerente: Hb baixa + Hct baixo + Hemácias baixas (ou ferritina baixa para ferropriva)."""
    avisos = []
    if all(k in by_canon for k in ["Hemoglobina", "Hematócrito", "Hemácias"]):
        hb = by_canon["Hemoglobina"]
        hct = by_canon["Hematócrito"]
        hem = by_canon["Hemácias"]
        # Se 1 dos 3 está low/crit mas os outros 2 normais → suspeita
        statuses = [hb["status_final"], hct["status_final"], hem["status_final"]]
        anemicos = sum(1 for s in statuses if s in ("low", "crit"))
        if anemicos == 1:
            avisos.append("L9 anemia incoerente: 1 dos 3 (Hb/Hct/Hemácias) baixo isolado")
    return avisos


# =============================================================================
# L10 — Anti-alucinação: valor existe no texto original
# =============================================================================
def _valor_no_texto(valor_f, texto_pdf, tolerancia_pct=2):
    """Verifica se o valor (ou ±2%) aparece no texto do PDF."""
    if not texto_pdf:
        return True  # sem texto pra checar, pula
    # Formata valor BR (vírgula) e US (ponto)
    fmts = set()
    if abs(valor_f - int(valor_f)) < 0.001:
        fmts.add(str(int(valor_f)))
    fmts.add(f"{valor_f:.1f}".rstrip("0").rstrip("."))
    fmts.add(f"{valor_f:.2f}".rstrip("0").rstrip("."))
    # Versões BR (vírgula)
    fmts |= {f.replace(".", ",") for f in fmts}
    # Tolerância: gera variantes com +/- 1-2%
    for fmt in list(fmts):
        if fmt in texto_pdf:
            return True
    # Fallback: busca por número proximo
    matches = re.findall(r"([\d]+[.,]?\d*)", texto_pdf)
    for m in matches:
        try:
            v = float(m.replace(",", "."))
            if abs(v - valor_f) / max(abs(valor_f), 0.001) < tolerancia_pct / 100:
                return True
        except ValueError:
            continue
    return False


# =============================================================================
# Helpers
# =============================================================================
def _classify(valor, ref_min, ref_max):
    if valor is None:
        return "normal"
    if ref_max is not None and valor > ref_max:
        return "crit" if valor > ref_max * 1.5 else "alert"
    if ref_min is not None and valor < ref_min:
        return "crit" if valor < ref_min * 0.5 else "low"
    return "normal"


def _ref_string(ref_min, ref_max):
    def _fmt(n):
        if n is None: return ""
        if abs(n - int(n)) < 0.001: return str(int(n))
        return f"{n:.2f}".rstrip("0").rstrip(".").replace(".", ",")
    if ref_min is not None and ref_max is not None:
        return f"{_fmt(ref_min)} a {_fmt(ref_max)}"
    if ref_max is not None:
        return f"<{_fmt(ref_max)}"
    if ref_min is not None:
        return f">{_fmt(ref_min)}"
    return ""


def _fmt(n):
    if n is None: return "—"
    if abs(n - int(n)) < 0.001: return str(int(n))
    return f"{n:.2f}".rstrip("0").rstrip(".").replace(".", ",")


def _find_ref_for(canon, sexo, idade):
    if canon not in REFS:
        return None, None, None, None
    entry = REFS[canon]
    sexo = (sexo or "").upper()[:1]
    if sexo not in {"M", "F"}:
        return None, None, None, None
    try:
        idade_int = int(idade) if idade not in (None, "", "?") else 35
    except (ValueError, TypeError):
        idade_int = 35
    candidates = [r for r in entry["ranges"] if r["sexo"] == sexo
                  and r["idade_min"] <= idade_int <= r["idade_max"]]
    if not candidates:
        same_sex = [r for r in entry["ranges"] if r["sexo"] == sexo]
        if not same_sex:
            return None, None, None, entry.get("unit", "")
        candidates = sorted(same_sex,
                            key=lambda r: min(abs(idade_int - r["idade_min"]),
                                              abs(idade_int - r["idade_max"])))[:1]
    r = candidates[0]
    return r.get("ref_min"), r.get("ref_max"), r.get("fonte", ""), entry.get("unit", "")


# =============================================================================
# Validação por exame (L0-L7, L10, L11)
# =============================================================================
def _validate_one(exame, paciente_meta, texto_pdf=None):
    """Valida um exame. Retorna (passou, motivo, exame_corrigido)."""
    # === L0: Sexo obrigatório ===
    sexo_raw = (paciente_meta or {}).get("sexo", "")
    if not sexo_raw:
        return False, "L0 RC-01: sexo do paciente ausente", exame
    sexo = str(sexo_raw).upper()[:1]
    if sexo not in {"M", "F"}:
        return False, f"L0 RC-01: sexo inválido '{sexo_raw}' (use M ou F)", exame

    idade = (paciente_meta or {}).get("idade")

    # === L1: Schema ===
    required = ["nome_canonico", "valor", "grupo"]
    for f in required:
        if f not in exame or exame[f] is None or exame[f] == "":
            return False, f"L1 schema: campo {f} ausente", exame
    try:
        valor = float(exame["valor"])
    except (ValueError, TypeError):
        return False, f"L1 schema: valor não numérico ({exame.get('valor')})", exame

    # === L2: Catálogo ===
    canon = exame["nome_canonico"]
    if canon not in REFS:
        return False, f"L2 catálogo: '{canon}' não está em refs_canonicas.json", exame
    entry = REFS[canon]

    # === L3: Plausibilidade ===
    abs_min = entry.get("abs_min", 0)
    abs_max = entry.get("abs_max", 1e12)
    if valor < abs_min or valor > abs_max:
        return False, (f"L3 plausibilidade: {canon}={valor} fora do range absoluto "
                       f"[{abs_min}, {abs_max}]"), exame

    # === L4: Sex+age ===
    ref_min, ref_max, fonte, unit_canonica = _find_ref_for(canon, sexo, idade)
    if ref_min is None and ref_max is None:
        return False, f"L4 sex+age: nenhuma ref para {canon} sexo={sexo} idade={idade}", exame

    # === L7: Unidade compatível ===
    unidade_laudo = exame.get("unidade", "") or ""
    if unidade_laudo and unit_canonica and not _units_compativeis(unidade_laudo, unit_canonica):
        return False, (f"L7 unidade: laudo='{unidade_laudo}' incompatível com canônica='{unit_canonica}' "
                       f"para {canon}"), exame

    # === L10: Valor existe no texto do PDF (anti-alucinação) ===
    # Pula para hemograma diferencial (valores absolutos calculados a partir de %)
    HEMO_DIF_SKIP = {'Linfócitos', 'Neutrófilos', 'Monócitos', 'Eosinófilos',
                     'Basófilos', 'Bastonetes', 'Segmentados', 'Plaquetas',
                     'Leucócitos'}
    if texto_pdf and canon not in HEMO_DIF_SKIP and not _valor_no_texto(valor, texto_pdf):
        return False, (f"L10 anti-alucinação: valor {valor} de {canon} NÃO aparece no texto do PDF "
                       f"(possível invenção do LLM)"), exame

    # === L11: Observação do LLM sinaliza incerteza ===
    obs = exame.get("observacao") or ""
    obs_lower = obs.lower()
    flags_incerteza = ["incerto", "ambíguo", "ambiguo", "não claro", "nao claro",
                        "duvida", "dúvida", "verificar", "talvez", "possivelmente",
                        "approximate", "approx"]
    if obs and any(f in obs_lower for f in flags_incerteza):
        return False, f"L11 LLM uncertainty: '{obs[:80]}'", exame

    # === L6: Status recalc ===
    status_final = _classify(valor, ref_min, ref_max)

    exame_corrigido = dict(exame)
    exame_corrigido["valor_f"] = valor
    exame_corrigido["ref_min_final"] = ref_min
    exame_corrigido["ref_max_final"] = ref_max
    exame_corrigido["status_final"] = status_final
    exame_corrigido["unidade_canonica"] = unit_canonica
    exame_corrigido["validacao"] = {
        "passou": True,
        "ref_origem": "canonica_sexo_idade",
        "ref_fonte": fonte,
        "sexo_aplicado": sexo,
        "idade_aplicada": idade,
        "status_llm_original": exame.get("status_clinico"),
        "divergencia_status": exame.get("status_clinico") != status_final,
        "unidade_laudo": unidade_laudo,
        "unidade_canonica": unit_canonica,
        "obs_llm": obs,
    }
    return True, "OK", exame_corrigido


# =============================================================================
# Validação cruzada (L5, L8, L9)
# =============================================================================
def _cross_check_friedewald(exames_validos):
    """L5 LDL Friedewald."""
    by_canon = {e["nome_canonico"]: e for e in exames_validos}
    if all(k in by_canon for k in ["Colesterol Total", "HDL", "LDL"]):
        total = by_canon["Colesterol Total"]["valor_f"]
        hdl = by_canon["HDL"]["valor_f"]
        ldl = by_canon["LDL"]["valor_f"]
        vldl = by_canon.get("VLDL", {}).get("valor_f")
        trig = by_canon.get("Triglicérides", {}).get("valor_f")
        if vldl is not None:
            ldl_calc = total - hdl - vldl
        elif trig is not None and trig < 400:
            ldl_calc = total - hdl - (trig / 5)
        else:
            return []
        delta_pct = abs(ldl - ldl_calc) / max(ldl_calc, 1) * 100
        if delta_pct > 25:
            return [(by_canon["LDL"], f"L5 Friedewald: LDL={ldl} vs Total-HDL-VLDL={ldl_calc:.1f} (Δ{delta_pct:.0f}%)")]
    return []


def _cross_checks_l8(exames_validos):
    """L8 cross-checks fisiológicos."""
    by_canon = {e["nome_canonico"]: e for e in exames_validos}
    avisos = []
    for fn in (_crosscheck_wintrobe, _crosscheck_homa_ir, _crosscheck_glicemia_media_hba1c):
        r = fn(by_canon)
        if r:
            avisos.append(r)
    avisos.extend(_crosscheck_indices_hematologicos(by_canon))
    return avisos


def _consistencias_l9(exames_validos):
    """L9 consistência intra-grupo."""
    by_canon = {e["nome_canonico"]: e for e in exames_validos}
    avisos = []
    avisos.extend(_consistencia_glicemica(by_canon))
    avisos.extend(_consistencia_hepatica(by_canon))
    avisos.extend(_consistencia_anemia(by_canon))
    return avisos


# =============================================================================
# Função principal
# =============================================================================
def validar_exames(extracao_llm: dict, paciente_meta: dict = None, texto_pdf: str = None):
    """
    Valida output do LLM extractor com 11 camadas robustas.

    Args:
        extracao_llm: dict com {paciente_nome, exames: [...], ...}
        paciente_meta: dict com {sexo: 'M'|'F', idade: int, ...}
        texto_pdf: texto bruto do PDF (opcional, ativa L10 anti-alucinação)

    Returns:
        dict com {validados, revisao_manual, cross_check_warnings, ...}
    """
    if not extracao_llm or "exames" not in extracao_llm:
        return {"validados": [], "revisao_manual": [], "erro": "Sem exames"}

    sexo_raw = (paciente_meta or {}).get("sexo", "")
    if not sexo_raw or str(sexo_raw).upper()[:1] not in {"M", "F"}:
        return {
            "validados": [],
            "revisao_manual": [{"exame": ex, "motivo": "L0 RC-01: sexo obrigatório"}
                               for ex in extracao_llm.get("exames", [])],
            "erro": "REGRA CANÔNICA RC-01 violada: sexo obrigatório",
            "paciente_nome": extracao_llm.get("paciente_nome", ""),
        }

    exames = extracao_llm.get("exames", [])
    validados = []
    revisao = []

    for ex in exames:
        passou, motivo, ex_corrigido = _validate_one(ex, paciente_meta, texto_pdf)
        if passou:
            validados.append(ex_corrigido)
        else:
            revisao.append({"exame": ex, "motivo": motivo})

    # Cross-checks (L5, L8, L9) — só warnings, não invalidam
    warnings = []
    for ex_obj, motivo in _cross_check_friedewald(validados):
        warnings.append({"exame": ex_obj, "motivo": motivo})
    for w in _cross_checks_l8(validados):
        warnings.append({"motivo": w})
    for w in _consistencias_l9(validados):
        warnings.append({"motivo": w})

    return {
        "validados": validados,
        "revisao_manual": revisao,
        "cross_check_warnings": warnings,
        "paciente_nome": extracao_llm.get("paciente_nome", ""),
        "data_coleta": extracao_llm.get("data_coleta", ""),
        "lab_origem": extracao_llm.get("lab_origem", ""),
        "paciente_sexo": str(sexo_raw).upper()[:1],
        "paciente_idade": (paciente_meta or {}).get("idade"),
        "refs_versao": "refs_canonicas.json v1.0",
        "validador_versao": "v3 (11 camadas)",
        "anti_alucinacao_ativa": texto_pdf is not None,
    }


def adaptar_para_v9(extracao_validada: dict):
    out = []
    for ex in extracao_validada.get("validados", []):
        ref_str = _ref_string(ex.get("ref_min_final"), ex.get("ref_max_final")) or "—"
        out.append({
            "nome": ex["nome_canonico"],
            "valor": _fmt(ex["valor_f"]),
            "unit": ex.get("unidade", "") or ex.get("unidade_canonica", ""),
            "ref": ref_str,
            "status": ex.get("status_final", "normal"),
        })
    return out


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python3 validador_exames.py <extracao_json> [sexo] [idade] [texto_pdf]")
        sys.exit(1)
    with open(sys.argv[1]) as f:
        ex = json.load(f)
    sexo = sys.argv[2] if len(sys.argv) > 2 else "M"
    idade = int(sys.argv[3]) if len(sys.argv) > 3 else 35
    texto = open(sys.argv[4]).read() if len(sys.argv) > 4 else None
    res = validar_exames(ex, {"sexo": sexo, "idade": idade}, texto_pdf=texto)
    print(json.dumps(res, indent=2, ensure_ascii=False))
