# -*- coding: utf-8 -*-
"""
creative_compliance.py — Validação VISUAL de criativos contra a política de publicidade do Meta Ads (IVS).

Centraliza, dentro do content-engine-os, a checagem de cada imagem/frame de vídeo ANTES de usar num criativo.
REGRA DO TIARO: a visão roda no **Codex GPT-5.5 via OAuth** (codex_llm.vision_chat) — NUNCA OpenRouter.

Uso (CLI): python3 creative_compliance.py <imagem> "<conceito>"
Uso (lib): from creative_compliance import assess_visual_creative
"""
from __future__ import annotations
import os, sys, json, base64, re, glob

GUARDRAILS_GLOB = "/root/cerebro-vital-slim/cerebro/areas/marketing/sub-areas/trafego-pago/meta-ads-guardrails-criativos-ivs-*.md"
ENV_PATHS = ["/root/cerebro-vital-slim/sistemas/content-engine-os/.env",
             "/root/cerebro-vital-slim/sistemas/content-engine-os/apps/api/.env"]
# rótulo apenas (a rota real é o codex-gateway / GPT-5.5 OAuth)
VISION_MODEL = "gpt-5.5 (codex)"

# JSON Schema do verdict (best-effort via --output-schema do codex; há fallback de parse)
COMPLIANCE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["approved", "violations", "has_text", "text_language", "matches_concept", "score", "reason"],
    "properties": {
        "approved": {"type": "boolean"},
        "violations": {"type": "array", "items": {"type": "string"}},
        "has_text": {"type": "boolean"},
        "text_language": {"type": ["string", "null"]},
        "matches_concept": {"type": "boolean"},
        "score": {"type": "integer"},
        "reason": {"type": "string"},
    },
}


def load_guardrails() -> str:
    files = sorted(glob.glob(GUARDRAILS_GLOB))
    if not files:
        return ""
    return open(files[-1], encoding="utf-8").read()


def _api_key() -> str | None:
    """Mantido por compat de import (broll_director/virality_library). Não mais usado na visão."""
    k = os.environ.get("OPENROUTER_API_KEY")
    if k:
        return k.strip()
    for p in ENV_PATHS:
        try:
            for line in open(p, encoding="utf-8"):
                if line.startswith("OPENROUTER_API_KEY="):
                    return line.split("=", 1)[1].strip()
        except Exception:
            pass
    return None


def _encode_image(image_path: str, max_side: int = 1024) -> tuple[str, str]:
    """Reduz/comprime a imagem (max_side, JPEG) p/ caber bem na visão."""
    try:
        from PIL import Image
        import io
        im = Image.open(image_path).convert("RGB")
        w, h = im.size
        scale = min(1.0, max_side / max(w, h))
        if scale < 1.0:
            im = im.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=85)
        return base64.b64encode(buf.getvalue()).decode(), "image/jpeg"
    except Exception:
        ext = "png" if image_path.lower().endswith("png") else "jpeg"
        return base64.b64encode(open(image_path, "rb").read()).decode(), f"image/{ext}"


def assess_visual_creative(image_path: str, concept: str, model: str = VISION_MODEL, allow_text: bool = False) -> dict:
    """Retorna verdict JSON: approved, violations[], has_text, text_language, matches_concept, score, reason.
    allow_text=True: permite texto LEGÍVEL em português aprovado (ex.: nome do programa) — ainda barra inglês/claims/medidas."""
    try:
        b64, mime = _encode_image(image_path)
    except Exception as e:
        return {"approved": False, "error": f"read_fail:{e}"}
    data_url = f"data:{mime};base64,{b64}"

    system = (
        "Voce e um auditor RIGOROSO de compliance de publicidade do Meta Ads para uma clinica medica "
        "(Instituto Vital Slim). Avalie a IMAGEM contra a politica oficial abaixo. Regra-mae: na duvida, REPROVE.\n\n"
        + load_guardrails() +
        "\n\nREPROVE (approved=false) OBRIGATORIAMENTE se a imagem contiver QUALQUER um destes:\n"
        "- medicacao, comprimido, capsula, pilula, ampola, seringa, injecao, frasco de remedio\n"
        "- balanca (pesar), fita metrica\n"
        "- antes e depois corporal, barriga exposta, close de gordura/cintura, nudez, lingerie, biquini\n"
        "- ambiente de CLINICA, consultorio, recepcao medica, sala de exames, hospital ou qualquer interior "
        "clinico/medico (so a clinica REAL do Instituto Vital Slim poderia aparecer; ambiente clinico generico/de "
        "terceiros e PROIBIDO)\n"
        "- TEXTO LEGIVEL: palavras/frases/numeros de medida/claims legiveis sobrepostos ou em destaque "
        "(has_text=true). ATENCAO: texto INCIDENTAL e ILEGIVEL/borrado ao fundo (ex.: UI de tela de celular/"
        "notebook desfocada, rotulo ilegivel) NAO conta como has_text e e tolerado. So marque has_text=true se "
        "houver PALAVRA LEGIVEL.\n"
        "- texto LEGIVEL em ingles ou a sigla 'IVS'\n"
        "Tambem REPROVE se a imagem NAO ilustrar o conceito pedido (matches_concept=false => approved=false).\n"
        "Responda SOMENTE com JSON valido, sem markdown:\n"
        '{"approved":bool,"violations":[str],"has_text":bool,"text_language":str|null,'
        '"matches_concept":bool,"score":int,"reason":str}'
    )
    if allow_text:
        system += ("\n\nEXCECAO DE TEXTO (allow_text): e PERMITIDO o texto legivel em PORTUGUES escrito num papel/"
                   "receituario com o nome do programa (ex.: 'Programa de Acompanhamento'). NESTE caso has_text pode "
                   "ser true SEM reprovar, DESDE QUE: o texto esteja em portugues correto, sem ingles, sem claims/"
                   "promessas, sem medidas (kg/cm/%), sem nome de medicamento, sem a sigla 'IVS'. Qualquer texto fora "
                   "disso continua reprovando.")
    user_text = (f'Conceito que a imagem DEVE ilustrar: "{concept}". '
                 "A imagem casa com esse conceito E e 100% compliant com a politica Meta (incluindo SEM nenhum texto)?")

    from codex_llm import vision_chat
    content, last_err = None, None
    for use_schema in (True, False):  # tenta com schema; se falhar, sem schema (robustez)
        try:
            content = vision_chat(system, user_text, images=[data_url],
                                  output_schema=COMPLIANCE_SCHEMA if use_schema else None,
                                  timeout=200)
            if content:
                break
        except Exception as e:
            last_err = str(e)[:200]
            content = None
    if not content:
        return {"approved": False, "error": last_err or "codex_vision_failed"}

    m = re.search(r"\{.*\}", content, re.S)
    try:
        verdict = json.loads(m.group(0)) if m else None
    except Exception:
        verdict = None
    if verdict is None:
        return {"approved": False, "reason": "parse_fail", "raw": content[:300]}

    # trava-dura local (defense-in-depth)
    fail = bool(verdict.get("violations")) or verdict.get("matches_concept") is False
    if not allow_text and verdict.get("has_text"):
        fail = True
    if allow_text and (verdict.get("text_language") or "").lower().startswith("en"):
        fail = True  # texto em ingles nunca passa, mesmo com allow_text
    if fail:
        verdict["approved"] = False
    verdict["model"] = VISION_MODEL
    return verdict


if __name__ == "__main__":
    img, concept = sys.argv[1], sys.argv[2]
    print(json.dumps(assess_visual_creative(img, concept), ensure_ascii=False, indent=2))
