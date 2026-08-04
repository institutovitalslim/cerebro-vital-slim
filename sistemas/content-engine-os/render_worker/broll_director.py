# -*- coding: utf-8 -*-
"""
broll_director.py — DIRETOR CRIATIVO do reel (content-engine-os / render_worker).

Fluxo: gera um ROTEIRO/STORYBOARD completo (por sentido de frase) para APROVACAO do Tiaro
ANTES de gerar qualquer imagem/video. Cada cena traz: quem (Dra ou b-roll), tipo (video/imagem),
descricao LITERAL do visual, prompt de geracao (compliant), motion e a TRANSICAO de entrada.

Regras fixas:
- GANCHO (1a frase/abertura) = SEMPRE a medica (apresentadora), NUNCA b-roll.
- Conceitos LITERAIS e obviamente ligados a frase (sem metafora abstrata).
- Compliance Meta lido da diretriz (sem medicacao/balanca/fita/antes-depois/clinica-de-terceiros/texto/ingles).
- Mulheres 40+ COM SOBREPESO, vestidas, dignas.
- Reprovado no gate -> gera outro (nunca cai pra Dra) [tratado no pipeline via direct_one].

Uso CLI: python3 broll_director.py <data.json> <roteiro_out.json>
"""
from __future__ import annotations
import os, sys, json, re
import urllib.request
from creative_compliance import load_guardrails, _api_key, VISION_MODEL

PUNCT_END = (".", "!", "?")
# vocabulario de transicoes implementadas no Remotion
TRANSITIONS = ["corte", "zoom_in", "zoom_out", "whip_pan", "slide_esq", "slide_dir", "fade", "flash", "blur"]


def segment_phrases(words: list[dict], max_words: int = 6, max_dur: float = 3.2) -> list[dict]:
    phrases, cur, t0 = [], [], None
    for w in words:
        if not cur:
            t0 = w["start"]
        cur.append(w)
        txt = w["text"]
        if txt.endswith(PUNCT_END) or (txt.endswith((",", ";", ":")) and len(cur) >= 3) \
           or len(cur) >= max_words or (w["end"] - t0) >= max_dur:
            phrases.append({"text": " ".join(x["text"] for x in cur), "start": cur[0]["start"], "end": cur[-1]["end"]})
            cur = []
    if cur:
        phrases.append({"text": " ".join(x["text"] for x in cur), "start": cur[0]["start"], "end": cur[-1]["end"]})
    return phrases


def _chat(messages, model=VISION_MODEL, max_tokens=4500, temperature=0.4):
    # REGRA DO TIARO: nunca OpenRouter; sempre Codex GPT-5.5 via gateway OAuth.
    from codex_llm import chat
    system = "\n\n".join(m["content"] for m in messages if m.get("role") == "system")
    user = "\n\n".join(m["content"] for m in messages if m.get("role") == "user")
    return chat(system, user)


def _virality_bp() -> str:
    """Boas práticas de viralização acumuladas (biblioteca auto-atualizada) — consultadas SEMPRE antes de gerar."""
    try:
        from virality_library import guidance
        g = guidance()
        return ("\n\n== BIBLIOTECA DE BOAS PRATICAS DE VIRALIZACAO (consultar SEMPRE; aprende do Virality Predictor) ==\n"
                + g + "\n") if g else ""
    except Exception:
        return ""


def _director_system() -> str:
    return (
        "Voce e DIRETOR CRIATIVO de reels do Instituto Vital Slim (clinica medica feminina, mulheres 40+ com "
        "sobrepeso). Monte o ROTEIRO visual cena a cena para o reel, para o Tiaro APROVAR antes de gerar.\n"
        + _virality_bp() + "\n"
        + load_guardrails() +
        "\n\n== REGRAS DE DIRECAO ==\n"
        "1) GANCHO: a 1a frase / abertura do reel e SEMPRE a MEDICA em cena (apresentadora), NUNCA b-roll.\n"
        "2) Falas pessoais diretas a espectadora e o CTA final ficam na MEDICA (who='dra').\n"
        "3) B-roll deve ser LITERAL e OBVIAMENTE ligado a frase. PROIBIDO metafora abstrata que precisa ser "
        "explicada (NAO use: quebra-cabeca, porta aberta, chaves, macas soltas, mao em vaso de planta, bolha de "
        "sabao, post-its soltos — foram reprovados pelo Tiaro).\n"
        "4) Mapeamentos OBRIGATORIOS quando a frase pedir:\n"
        "   - mente / metabolismo / 'corpo por dentro' => VIDEO 3D do INTERIOR do corpo humano comecando pelo "
        "CEREBRO e indo ao metabolismo/orgaos (anatomia cientifica realista, sem texto).\n"
        "   - 'metodo estudado/aprovado/ciencia/pesquisa' => cena INEQUIVOCA de pesquisa/ciencia SEM aparencia "
        "clinica: pesquisadores 40+ em ROUPAS SOCIAIS NEUTRAS (NAO jaleco/avental branco: jaleco e lido como clinica "
        "e REPROVA no gate) num centro de pesquisa/escritorio moderno, analisando um PAINEL DIGITAL grande com "
        "MOLECULAS 3D + curvas de dados/graficos e um simbolo de validacao (check verde). PROIBIDO: jaleco/avental "
        "branco, reuniao corporativa generica sem dados na tela, pessoas so sentadas a uma mesa, livros velhos, "
        "ambiente de clinica/consultorio/hospital, medicacao/ampola/seringa, texto legivel.\n"
        "   - 'foco individual/exclusivo/sobre voce' => UMA mulher 40+ recebendo atencao/cuidado individual e "
        "personalizado (sem ambiente de clinica de terceiros).\n"
        "   - 'alimento proibido' => comida tentadora com gesto de recusa. 'dieta milagrosa/modinha' => simbolo de "
        "promessa furada de dieta (sem medicacao/balanca/fita).\n"
        "5) COMPLIANCE (elimine na ORIGEM): medicacao/capsula/ampola/seringa; balanca; fita metrica; antes-depois; "
        "barriga/corpo exposto; nudez; QUALQUER texto/letra/numero; ingles; 'IVS'; ambiente de clinica/consultorio/"
        "recepcao/hospital de terceiros. Mulheres = 40+ COM SOBREPESO, vestidas, dignas.\n"
        "6) TRANSICOES: para CADA cena escolha a transicao de ENTRADA (transition_in) do conjunto: "
        f"{TRANSITIONS}. VARIE bastante (nao use so zoom). Use transicao forte (whip_pan/flash/zoom_in) nas viradas "
        "de impacto e suaves (fade/blur/corte) nas continuacoes.\n"
        "7) JUIZ DE COMPLIANCE ESTRITO (GPT-5.5): um auditor de visao valida cada imagem e REPROVA quando a cena nao "
        "e VISUALMENTE INEQUIVOCA quanto ao conceito (ex.: 'reuniao' != 'pesquisa cientifica'). Logo TODO image_prompt "
        "deve cravar elementos visuais CONCRETOS e especificos (cenario + objetos-chave + acao) que tornem o conceito "
        "obvio a primeira vista; nunca cena generica/ambigua.\n\n"
        "Para cada frase devolva: who ('dra'|'broll'); visual_type ('dra'|'video'|'imagem'); concept (PT, descricao "
        "clara do que aparece); image_prompt (INGLES tecnico p/ gerador, SEMPRE terminando com 'no text, no words, "
        "no letters, photorealistic, cinematic, vertical 9:16, enquadramento ao nivel dos olhos e sujeito centralizado, SEM plano de cima/overhead/top-down, SEM enquadramento horizontal aberto'; vazio se who='dra'); motion_prompt (movimento do "
        "video; vazio se imagem/dra); transition_in (1 do conjunto); why (PT, por que casa + por que compliant).\n"
        "Responda SOMENTE JSON: {\"plan\":[{\"idx\":int,\"who\":str,\"visual_type\":str,\"concept\":str,"
        "\"image_prompt\":str,\"motion_prompt\":str,\"transition_in\":str,\"why\":str}]}"
    )


def _extract_json(content: str):
    c = content.strip()
    if "```" in c:
        c = re.sub(r"```[a-zA-Z]*", "", c).replace("```", "")
    m = re.search(r"\{.*\}", c, re.S)
    if not m:
        return None
    raw = m.group(0)
    for attempt in (raw, re.sub(r",\s*([}\]])", r"\1", raw)):
        try:
            return json.loads(attempt)
        except Exception:
            continue
    return None


def plan_broll(phrases: list[dict], full_text: str, model: str = VISION_MODEL) -> list[dict]:
    numbered = "\n".join(f'{i}: "{p["text"]}"' for i, p in enumerate(phrases))
    user = (f"ROTEIRO COMPLETO (contexto):\n\"{full_text}\"\n\nFRASES (idx: texto):\n{numbered}\n\n"
            "IMPORTANTE: devolva JSON 100% valido. NAO use aspas duplas dentro dos textos (use aspas simples). "
            "Sem comentarios, sem markdown.")
    parsed = None
    last = ""
    for _ in range(3):
        last = _chat([{"role": "system", "content": _director_system()}, {"role": "user", "content": user}],
                     temperature=0, max_tokens=12000)
        parsed = _extract_json(last)
        if parsed and isinstance(parsed.get("plan"), list) and parsed["plan"]:
            break
    if not (parsed and parsed.get("plan")):
        try:
            open("/tmp/roteiro_raw.txt", "w", encoding="utf-8").write(last)
        except Exception:
            pass
    plan = (parsed or {}).get("plan", []) if parsed else []
    by_idx = {int(p["idx"]): p for p in plan}
    out = []
    for i, ph in enumerate(phrases):
        p = by_idx.get(i, {"who": "dra"})
        who = p.get("who", "dra")
        # trava: gancho sempre Dra
        if i == 0:
            who = "dra"
        out.append({**ph, "idx": i, "who": who,
                    "visual_type": ("dra" if who == "dra" else p.get("visual_type", "video")),
                    "concept": p.get("concept", "Medica em cena (apresentadora)") if who == "broll" else "Medica em cena",
                    "image_prompt": p.get("image_prompt", "") if who == "broll" else "",
                    "motion_prompt": p.get("motion_prompt", "") if who == "broll" else "",
                    "transition_in": p.get("transition_in", "corte") if p.get("transition_in") in TRANSITIONS else "corte",
                    "why": p.get("why", "")})
    return out


def direct_one(phrase_text: str, full_text: str, avoid: list[str], reason: str = "", model: str = VISION_MODEL) -> dict:
    system = (_director_system() +
              "\n\nAgora gere UM conceito de b-roll ALTERNATIVO e DIFERENTE dos ja tentados, LITERAL e compliant, "
              "para a frase indicada. Responda SOMENTE JSON: "
              '{"concept":str,"image_prompt":str,"motion_prompt":str,"transition_in":str,"why":str}')
    user = (f'Roteiro: "{full_text}"\n\nFrase: "{phrase_text}"\n'
            f'JA TENTADOS (NAO repita): {avoid}\nMotivo da reprovacao (evite): {reason}')
    content = _chat([{"role": "system", "content": system}, {"role": "user", "content": user}])
    m = re.search(r"\{.*\}", content, re.S)
    return json.loads(m.group(0)) if m else {"concept": "", "image_prompt": "", "motion_prompt": ""}


if __name__ == "__main__":
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    words = data["words"]
    full = " ".join(w["text"] for w in words)
    plan = plan_broll(segment_phrases(words), full)
    json.dump(plan, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    nb = sum(1 for p in plan if p["who"] == "broll")
    print(f"frases={len(plan)} | b-roll={nb} | dra={len(plan)-nb}\n")
    for p in plan:
        tag = "DRA " if p["who"] == "dra" else f"{p['visual_type'][:3].upper()} "
        print(f'[{p["start"]:5.1f}-{p["end"]:5.1f}] ({p["transition_in"]:9}) {tag}| "{p["text"]}"')
        if p["who"] == "broll":
            print(f'              -> {p["concept"]}')
