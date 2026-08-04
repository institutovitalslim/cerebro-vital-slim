#!/usr/bin/env python3
"""Story Retention Gate IVS — avaliação local de roteiros curtos.

Uso:
  python3 scripts/story_retention_gate.py --text "..."
  python3 scripts/story_retention_gate.py --file roteiro.json

Entrada pode ser texto puro ou JSON com campos title/hook/script/slides/caption/modular_blocks.
Saída JSON: total 0-18, decisão, critérios 0-2 e diagnóstico `story_ladder` (nível 0-6).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


def contains_any(text: str, needles: tuple[str, ...]) -> bool:
    return any(n in text for n in needles)


def script_text(output: dict[str, Any]) -> str:
    slides = output.get("slides") or []
    if slides and isinstance(slides[0], dict):
        return " ".join(((str(s.get("headline") or "")) + " " + (str(s.get("sub") or ""))) for s in slides)
    if slides:
        return " ".join(str(x) for x in slides)
    tweets = output.get("tweets") or []
    if tweets:
        return " ".join(str(x) for x in tweets)
    script = output.get("script") or output.get("body") or output.get("development") or output.get("text") or ""
    return " ".join(str(x) for x in script) if isinstance(script, list) else str(script)


def normalize_payload(raw: str) -> dict[str, Any]:
    raw = raw.strip()
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return parsed
        return {"script": parsed}
    except Exception:
        return {"script": raw}


STORY_LADDER_NAMES = {
    1: "reporter",
    2: "illusionist",
    3: "champion",
    4: "architect",
    5: "translator",
    6: "maestro",
}


def story_ladder_diagnostic(
    text: str,
    first: str,
    corpo: str,
    sentences: list[str],
    criterios: dict[str, int],
    blocks: dict[str, Any],
) -> dict[str, Any]:
    """Diagnóstico inspirado na Story Ladder aplicada ao contexto IVS.

    Mantém o score 0-18 antigo, mas adiciona um gate narrativo: roteiros de
    Reels não devem ficar só no nível 1 (fatos em ordem). Para aprovação real,
    precisam mirar pelo menos nível 3: dor/objeção específica do avatar.
    """
    checks = {
        "1_reporter_fatos_minimos": len(corpo.strip()) >= 80,
        "2_illusionist_contraste_rehook": criterios.get("contraste", 0) >= 1 or criterios.get("antecipacao", 0) >= 1,
        "3_champion_dor_especifica": criterios.get("emocao", 0) >= 1 or criterios.get("objecao_quebrada", 0) >= 1,
        "4_architect_mini_loop": len(sentences) >= 4 and contains_any(text, ("por que", "porque", "exemplo", "na prática", "então", "agora", "primeiro", "segundo", "próximo passo")),
        "5_translator_clareza_metafora_visual": criterios.get("clareza", 0) >= 1 and criterios.get("absorcao", 0) >= 1,
        "6_maestro_assinatura_ivs": bool(
            blocks.get("assinatura_ivs")
            or contains_any(text, (
                "instituto vital slim",
                "dra. daniely",
                "dra daniely",
                "investigação sem julgamento",
                "investigar sem julgar",
                "ciência com acolhimento",
                "seu corpo precisa de investigação",
                "investigação, não julgamento",
            ))
        ),
    }

    level = 0
    for idx, key in enumerate(checks, start=1):
        if checks[key]:
            level = idx
        else:
            break

    if level < 3:
        recommendation = "Subir para nível 3: explicitar dor, objeção ou arquétipo da mulher que não se reconhece no espelho."
    elif level < 4:
        recommendation = "Subir para nível 4: organizar em mini-loop problema → por que importa → exemplo → próximo passo."
    elif level < 5:
        recommendation = "Subir para nível 5: adicionar metáfora, exemplo visual ou linguagem mais simples."
    elif level < 6:
        recommendation = "Subir para nível 6: inserir assinatura IVS — investigação sem julgamento, ciência com acolhimento premium."
    else:
        recommendation = "Story Ladder completa para teste: manter compliance e validar retenção real."

    return {
        "level": level,
        "name": STORY_LADDER_NAMES.get(level, "below_reporter"),
        "target_min_level": 3,
        "checks": checks,
        "recommendation": recommendation,
    }


def journey_storytelling_gate(text: str, first: str, blocks: dict[str, Any]) -> dict[str, Any]:
    """Gate do Framework Storytelling de Jornada IVS.

    Regra Tiaro 2026-07-17: todo conteúdo futuro deve passar por
    Cena → Tensão → Reframe → Guia → Caminho. A paciente é protagonista;
    Instituto Vital Slim/Dra. Daniely entram como guia, não como herói.
    """
    checks = {
        "cena_concreta": bool(
            blocks.get("cena")
            or blocks.get("scene")
            or contains_any(text, (
                "espelho", "roupa", "armário", "calça", "foto", "evento", "consulta",
                "rotina", "acorda", "jantar", "almoço", "trabalho", "filho", "cansada",
            ))
        ),
        "tensao_emocional": bool(
            blocks.get("tensao")
            or blocks.get("tension")
            or contains_any(text, (
                "não se reconhece", "culpa", "frustra", "vergonha", "medo", "trava",
                "cansa", "dói", "desiste", "perdeu o controle", "tentou de tudo",
            ))
        ),
        "reframe_sem_culpa": bool(
            blocks.get("reframe")
            or contains_any(text, (
                "não é falta de força de vontade", "não é falta de disciplina", "não é culpa",
                "talvez", "o problema não", "antes de tentar", "em vez de", "seu corpo não está falhando",
                "precisa entender", "não é só dieta",
            ))
        ),
        "guia_ivs": bool(
            blocks.get("guia")
            or blocks.get("guide")
            or contains_any(text, (
                "instituto vital slim", "dra. daniely", "dra daniely", "avaliação individualizada",
                "investigação", "investigar", "escuta", "acompanhamento", "plano individualizado",
                "entender sua história", "sem julgamento",
            ))
        ),
        "caminho_seguro_cta": bool(
            blocks.get("caminho")
            or blocks.get("path")
            or contains_any(text, (
                "fale com", "whatsapp", "agende", "avaliação", "próximo passo", "salve",
                "compartilhe", "comente", "veja se faz sentido", "comece entendendo", "acompanhar",
            ))
        ),
    }
    score = sum(2 for ok in checks.values() if ok)
    missing = [k for k, ok in checks.items() if not ok]
    if not missing:
        recommendation = "Framework completo: manter a paciente como protagonista e validar compliance."
    else:
        recommendation = "Adicionar antes de aprovar: " + ", ".join(missing) + "."
    return {
        "version": "storytelling_jornada_ivs_v1",
        "framework": "Cena → Tensão → Reframe → Guia → Caminho",
        "total": score,
        "max": 10,
        "score_pct": round(100 * score / 10, 1),
        "target_min": 6,
        "checks": checks,
        "missing": missing,
        "recommendation": recommendation,
    }


def story_retention_gate(output: dict[str, Any], formato: str = "reels") -> dict[str, Any]:
    title = str(output.get("title") or output.get("hook") or output.get("headline") or "")
    corpo = script_text(output)
    caption = str(output.get("caption") or "")
    raw_blocks = output.get("modular_blocks")
    blocks = raw_blocks if isinstance(raw_blocks, dict) else {}
    text = " ".join([title, corpo, caption, json.dumps(blocks, ensure_ascii=False), formato]).lower()
    first = " ".join([title, corpo]).lower()[:360]
    sentences = [s.strip() for s in re.split(r"[.!?\n]+", " ".join([title, corpo])) if s.strip()]
    avg_len = (sum(len(s) for s in sentences) / len(sentences)) if sentences else 999

    criterios = {
        "contraste": 2 if contains_any(first, ("não é", "não foi", "talvez", "mas", "antes de", "em vez de", "o problema não")) else (1 if contains_any(first, ("por que", "erro", "trav", "sinal")) else 0),
        "valor_em_5s": 2 if contains_any(first, ("por que", "como", "sinal", "investig", "entender", "explica", "causa")) else (1 if len(first) > 90 else 0),
        "densidade": 2 if len(corpo) > 260 and not contains_any(first, ("olá", "oi, eu", "hoje eu vou", "meu nome")) else (1 if len(corpo) > 160 else 0),
        "clareza": 2 if sentences and avg_len <= 120 and not contains_any(text, ("fisiopatologia", "homeostase", "eixo hipotálamo", "farmacodinâmica")) else (1 if avg_len <= 170 else 0),
        "absorcao": 2 if contains_any(text, ("exemplo", "pensa assim", "imagine", "é como", "teste", "sinal", "na prática")) else (1 if contains_any(text, ("rotina", "exame", "bioimped", "sono", "fome", "ansiedade")) else 0),
        "antecipacao": 2 if contains_any(text, ("até o fim", "detalhe", "quase ninguém", "o que ninguém", "antes de", "próximo", "virada")) else (1 if contains_any(text, ("sinal", "segredo", "pergunta")) else 0),
        "emocao": 2 if contains_any(text, ("espelho", "roupa", "calça", "culpa", "frustra", "vergonha", "medo", "cansada", "não se reconhece")) else (1 if contains_any(text, ("mulher", "40", "rotina", "tentou de tudo")) else 0),
        "ritmo_energia": 2 if len(sentences) >= 4 and avg_len <= 95 else (1 if len(sentences) >= 3 and avg_len <= 140 else 0),
        "objecao_quebrada": 2 if bool(blocks.get("objecao_alvo") or blocks.get("quebra_objecao") or contains_any(text, ("já tentei", "medo", "preço", "caro", "sem tempo", "só mais uma dieta", "força de vontade"))) else 0,
    }
    total = sum(criterios.values())
    ladder = story_ladder_diagnostic(text, first, corpo, sentences, criterios, blocks)
    journey = journey_storytelling_gate(text, first, blocks)
    decision = "aprovado_para_teste" if total >= 14 and ladder["level"] >= 3 and journey["total"] >= journey["target_min"] else ("ajustar_antes_de_gravar" if total >= 9 or ladder["level"] >= 2 or journey["total"] >= 4 else "reescrever")
    return {
        "version": "story_retention_gate_ivs_v3_story_ladder_jornada",
        "format": formato,
        "total": total,
        "max": 18,
        "score_pct": round(100 * total / 18, 1),
        "decision": decision,
        "criteria": criterios,
        "story_ladder": ladder,
        "narrative_journey_gate": journey,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="Arquivo .json/.txt/.md com roteiro")
    parser.add_argument("--text", help="Texto do roteiro")
    parser.add_argument("--format", default="reels", choices=["reels", "carrossel", "stories", "estatico"])
    args = parser.parse_args()

    if args.file:
        raw = Path(args.file).read_text(encoding="utf-8")
    elif args.text:
        raw = args.text
    else:
        raw = sys.stdin.read()
    payload = normalize_payload(raw)
    print(json.dumps(story_retention_gate(payload, args.format), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
