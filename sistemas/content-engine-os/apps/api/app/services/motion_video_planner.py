from __future__ import annotations

from copy import deepcopy
from typing import Any

CONTENT_FORMATS: list[dict[str, Any]] = [
    {
        "key": "mito_que_prende",
        "name": "Mito que prende",
        "description": "Derruba uma crença popular que mantém a paciente presa na culpa.",
        "best_for": ["educacao", "autoridade", "objecao"],
        "objection_targets": ["o problema sou eu", "ja_tentei_de_tudo"],
        "default_structure": ["mito", "por que parece verdade", "mecanismo real", "virada", "metodo", "proximo passo"],
        "motion_notes": "Mixed media com o mito se desmontando em camadas metabólicas abstratas.",
        "prompt_bias": "Use contraste entre crença comum e mecanismo fisiológico, sem humilhar a paciente.",
        "compliance_notes": "Não prometer resultado; apresentar mecanismo como educação, não diagnóstico.",
    },
    {
        "key": "sinal_escondido",
        "name": "Sinal escondido",
        "description": "Mostra um sintoma/sinal que a paciente normalizou.",
        "best_for": ["identificacao", "educacao"],
        "objection_targets": ["isso e normal da idade"],
        "default_structure": ["sinal", "normalizacao", "mecanismo", "contexto", "avaliacao", "cta"],
        "motion_notes": "Clinical mechanism map com sinais pequenos virando mapa clínico.",
        "prompt_bias": "Evite diagnosticar; use linguagem de possibilidade e avaliação.",
        "compliance_notes": "Não afirmar doença; sugerir investigação profissional.",
    },
    {
        "key": "comparacao_de_caminhos",
        "name": "Comparação de caminhos",
        "description": "Compara tentativa solta com método acompanhado.",
        "best_for": ["conversao", "objecao"],
        "objection_targets": ["ja_tentei_de_tudo"],
        "default_structure": ["caminho A", "limite A", "caminho B", "criterio", "beneficio", "cta"],
        "motion_notes": "Split-screen editorial com dois caminhos visuais sem antes/depois.",
        "prompt_bias": "Mostrar diferença de processo, não superioridade garantida.",
        "compliance_notes": "Sem comparação de resultados ou promessa temporal.",
    },
    {
        "key": "antes_da_decisao",
        "name": "Antes da decisão",
        "description": "Critérios antes de dieta, remédio, consulta ou procedimento.",
        "best_for": ["educacao", "remarketing"],
        "objection_targets": ["vou tentar mais uma dieta"],
        "default_structure": ["decisao", "risco de pular etapa", "criterio 1", "criterio 2", "criterio 3", "cta"],
        "motion_notes": "Checklist visual premium com cartões clínicos sem texto bruto legível.",
        "prompt_bias": "Orientar decisão segura e informada.",
        "compliance_notes": "Não substituir consulta; orientar avaliação individualizada.",
    },
    {
        "key": "erro_comum",
        "name": "Erro comum",
        "description": "Erro cotidiano que sabota percepção ou progresso.",
        "best_for": ["retencao", "educacao"],
        "objection_targets": ["culpa", "autocobranca"],
        "default_structure": ["erro", "por que acontece", "consequencia", "correcao", "metodo", "cta"],
        "motion_notes": "Paper cutout problem/solution com objeto-metáfora se reorganizando.",
        "prompt_bias": "Nomear o erro sem acusar a paciente.",
        "compliance_notes": "Sem culpabilização e sem aconselhamento prescritivo individual.",
    },
    {
        "key": "checklist_rapido",
        "name": "Checklist rápido",
        "description": "Lista curta para autoidentificação e salvamento.",
        "best_for": ["salvavel", "engajamento"],
        "objection_targets": ["nao_sei_se_e_para_mim"],
        "default_structure": ["pergunta", "item 1", "item 2", "item 3", "interpretacao", "cta"],
        "motion_notes": "Cards animados e ícones clínicos abstratos.",
        "prompt_bias": "Dar clareza sem fechar diagnóstico.",
        "compliance_notes": "Checklist não é laudo; incluir ressalva educativa.",
    },
    {
        "key": "mini_aula_visual",
        "name": "Mini-aula visual",
        "description": "Explicação simples de mecanismo/metabolismo/rotina.",
        "best_for": ["autoridade", "educacao"],
        "objection_targets": ["nao_entendo_o_que_acontece"],
        "default_structure": ["pergunta", "mecanismo 1", "mecanismo 2", "exemplo", "virada", "cta"],
        "motion_notes": "Clinical Mechanism Map com diagramas metabólicos abstratos.",
        "prompt_bias": "Ensinar com metáfora visual, sem excesso técnico.",
        "compliance_notes": "Claims devem ser genéricos e revisáveis por compliance.",
    },
    {
        "key": "bastidor_medico_seguro",
        "name": "Bastidor médico seguro",
        "description": "Mostra processo/avaliação/rotina sem expor paciente.",
        "best_for": ["autoridade", "confiança"],
        "objection_targets": ["medo_de_julgamento"],
        "default_structure": ["bastidor", "criterio", "cuidado", "seguranca", "diferencial", "cta"],
        "motion_notes": "Luxury Explainer com mesa clínica abstrata e documentos sem PII.",
        "prompt_bias": "Reforçar cuidado e processo, sem revelar dados reais.",
        "compliance_notes": "Zero PII, zero prontuário real, zero exposição de paciente.",
    },
    {
        "key": "historia_espelho",
        "name": "História espelho",
        "description": "Narrativa emocional abstrata de identificação.",
        "best_for": ["identificacao", "retencao"],
        "objection_targets": ["vergonha", "isolamento"],
        "default_structure": ["cena", "tensao", "pensamento", "virada", "novo significado", "cta"],
        "motion_notes": "Paper Diorama Documentary com personagem anônima/silhueta.",
        "prompt_bias": "Gerar identificação sem paciente real ou exposição sensível.",
        "compliance_notes": "Não usar antes/depois nem dramatização de sofrimento extremo.",
    },
    {
        "key": "reframe_de_culpa",
        "name": "Reframe de culpa",
        "description": "Troca culpa por contexto, método e avaliação.",
        "best_for": ["objecao", "conversao"],
        "objection_targets": ["eu_falhei"],
        "default_structure": ["culpa", "contexto", "mecanismo", "o que muda", "metodo", "cta"],
        "motion_notes": "Mixed media emocional com peso simbólico virando mapa de contexto.",
        "prompt_bias": "Tirar culpa sem prometer solução simples.",
        "compliance_notes": "Evitar linguagem determinista ou terapêutica indevida.",
    },
    {
        "key": "faq_direto",
        "name": "FAQ direto",
        "description": "Responde uma dúvida frequente com clareza curta.",
        "best_for": ["remarketing", "conversao"],
        "objection_targets": ["preco", "tempo", "distancia", "convenio"],
        "default_structure": ["pergunta", "resposta curta", "nuance", "criterio", "proximo passo", "cta"],
        "motion_notes": "Clean editorial Q&A com cartões sem texto bruto no clipe.",
        "prompt_bias": "Responder sem soar defensivo ou vendedor demais.",
        "compliance_notes": "Preço/agenda devem respeitar regras comerciais vigentes.",
    },
    {
        "key": "prova_de_metodo",
        "name": "Prova de método",
        "description": "Mostra critérios, processo e acompanhamento.",
        "best_for": ["autoridade", "conversao"],
        "objection_targets": ["e_so_mais_promessa"],
        "default_structure": ["promessa comum", "criterio", "processo", "acompanhamento", "diferencial", "cta"],
        "motion_notes": "Luxury/Clinical Map com engrenagens de método.",
        "prompt_bias": "Provar processo sem prometer resultado individual.",
        "compliance_notes": "Sem números de resultado se não houver base e autorização.",
    },
    {
        "key": "dois_tipos_de_paciente",
        "name": "Dois tipos de paciente",
        "description": "Contrasta perfis/decisões sem humilhar.",
        "best_for": ["educacao", "objecao"],
        "objection_targets": ["nao_sou_disciplinada"],
        "default_structure": ["perfil A", "limite", "perfil B", "decisao", "aprendizado", "cta"],
        "motion_notes": "Split comparison com silhuetas abstratas.",
        "prompt_bias": "Contraste com respeito; sem inferiorizar.",
        "compliance_notes": "Evitar estigma corporal e julgamento moral.",
    },
    {
        "key": "verdade_desconfortavel",
        "name": "Verdade desconfortável",
        "description": "Frase forte seguida de explicação cuidadosa.",
        "best_for": ["retencao", "autoridade"],
        "objection_targets": ["negacao", "adiamento"],
        "default_structure": ["verdade", "por que incomoda", "mecanismo", "excecao", "caminho", "cta"],
        "motion_notes": "Cinematic paper diorama com reveal central.",
        "prompt_bias": "Impacto sem sensacionalismo.",
        "compliance_notes": "Frase forte precisa de nuance clínica.",
    },
    {
        "key": "sequencia_de_stories",
        "name": "Sequência de stories",
        "description": "Sequência interativa derivada para enquete/caixinha/CTA.",
        "best_for": ["stories", "engajamento"],
        "objection_targets": ["baixa_resposta"],
        "default_structure": ["story 1 pergunta", "story 2 identificação", "story 3 explicação", "story 4 CTA"],
        "motion_notes": "Story cards motion em 9:16, cortes rápidos e stickers seguros.",
        "prompt_bias": "Interatividade manual, sem automação de DM.",
        "compliance_notes": "Sem promessa e sem captura sensível automática.",
    },
    {
        "key": "ugc_pov_contextual",
        "name": "UGC/POV contextual",
        "description": "Situação real simulada sem usar paciente real.",
        "best_for": ["identificacao", "alcance"],
        "objection_targets": ["identificacao_baixa"],
        "default_structure": ["POV", "tensao", "frase interna", "reframe", "metodo", "cta"],
        "motion_notes": "Simulated POV abstract, sem rosto real, com objetos cotidianos.",
        "prompt_bias": "Parecer vivido sem fingir depoimento real.",
        "compliance_notes": "Não criar testimonial falso nem resultado fabricado.",
    },
    {
        "key": "demonstracao_de_tecnologia",
        "name": "Demonstração de tecnologia",
        "description": "Explica equipamento/procedimento sem promessa.",
        "best_for": ["autoridade", "educacao"],
        "objection_targets": ["medo_do_desconhecido"],
        "default_structure": ["equipamento", "funcao", "o que mede/faz", "limite", "seguranca", "cta"],
        "motion_notes": "Clinical device explainer com diagrama técnico limpo.",
        "prompt_bias": "Mostrar função e critérios, não milagre tecnológico.",
        "compliance_notes": "Sem promessa terapêutica; respeitar indicação profissional.",
    },
    {
        "key": "oferta_contextual",
        "name": "Oferta contextual",
        "description": "Apresenta consulta/programa como próximo passo lógico.",
        "best_for": ["conversao", "remarketing"],
        "objection_targets": ["preco_sem_valor_percebido"],
        "default_structure": ["problema", "custo de adiar", "método", "para quem", "convite", "cta"],
        "motion_notes": "Luxury Explainer com convite premium discreto.",
        "prompt_bias": "Converter pelo valor do processo, não por urgência falsa.",
        "compliance_notes": "Sem escassez enganosa ou promessa de resultado.",
    },
    {
        "key": "reacao_etica",
        "name": "Reação ética",
        "description": "Reage a mito/tendência sem atacar pessoa.",
        "best_for": ["autoridade", "tendencia"],
        "objection_targets": ["crenca_popular_forte"],
        "default_structure": ["tendencia", "o que parece", "risco", "visao IVS", "criterio", "cta"],
        "motion_notes": "Commentary collage com recortes genéricos, sem copiar criativo externo.",
        "prompt_bias": "Criticar ideia, não pessoa ou concorrente.",
        "compliance_notes": "Não atacar profissional, marca ou paciente; evitar linguagem pública sensível.",
    },
    {
        "key": "resumo_salvavel",
        "name": "Resumo salvável",
        "description": "Síntese de alta utilidade para salvar/compartilhar.",
        "best_for": ["salvavel", "educacao"],
        "objection_targets": ["esquecimento", "falta_de_clareza"],
        "default_structure": ["tema", "ponto 1", "ponto 2", "ponto 3", "síntese", "cta"],
        "motion_notes": "Clean animated cards com hierarquia clara e legenda final.",
        "prompt_bias": "Simplificar sem banalizar.",
        "compliance_notes": "Evitar checklist diagnóstico; conteúdo educativo.",
    },
]

SCREEN_FORMATS: dict[str, dict[str, Any]] = {
    "reels": {"label": "Reels / Shorts / TikTok", "aspect_ratio": "9:16", "recommended": True},
    "youtube": {"label": "YouTube horizontal", "aspect_ratio": "16:9", "recommended": False},
    "feed_4_5": {"label": "Feed vertical", "aspect_ratio": "4:5", "recommended": False},
    "square": {"label": "Feed quadrado", "aspect_ratio": "1:1", "recommended": False},
}

MOTION_PRESETS: dict[str, dict[str, str]] = {
    "ivs_mixed_media_medico_premium": {
        "label": "IVS Mixed Media Médico-Premium",
        "description": "Colagem editorial, papel, halftone, mapas metabólicos, linhas douradas e fundo creme/café.",
    },
    "ivs_paper_diorama_documentary": {
        "label": "IVS Paper Diorama Documentary",
        "description": "Diorama de papel, jornal envelhecido, luz cinematográfica e câmera macro investigativa.",
    },
    "ivs_clinical_mechanism_map": {
        "label": "IVS Clinical Mechanism Map",
        "description": "Mapas metabólicos abstratos, hormônios, músculo, sono, tireoide e exames em visual limpo.",
    },
    "ivs_luxury_explainer": {
        "label": "IVS Luxury Explainer",
        "description": "Fundo café/preto, linhas douradas, movimento lento premium e linguagem institucional.",
    },
}

DURATION_PRESETS = [
    {"key": "reel_rapido", "label": "Reel rápido", "duration_seconds": 30, "blocks_count": 3},
    {"key": "reel_padrao", "label": "Reel padrão", "duration_seconds": 60, "blocks_count": 6},
    {"key": "short_autoridade", "label": "Short autoridade", "duration_seconds": 90, "blocks_count": 9},
    {"key": "mini_doc", "label": "Mini-doc", "duration_seconds": 180, "blocks_count": 18},
]


def get_content_format(key: str) -> dict[str, Any]:
    for item in CONTENT_FORMATS:
        if item["key"] == key:
            return item
    raise ValueError(f"content_format desconhecido: {key}")


def motion_video_options() -> dict[str, Any]:
    return {
        "content_formats": deepcopy(CONTENT_FORMATS),
        "screen_formats": deepcopy(SCREEN_FORMATS),
        "motion_presets": deepcopy(MOTION_PRESETS),
        "duration_presets": deepcopy(DURATION_PRESETS),
        "content_strategies": ["loop_previsao", "jornada_ivs", "retencao_loops", "erro_mecanismo_metodo", "mito_realidade_conduta"],
        "voiceovers": ["documental_feminina_pt_br", "documental_masculina_pt_br", "premium_institucional_pt_br", "sem_voz"],
        "generation_modes": ["plan_only", "approved_for_paid_generation"],
    }


def _block_count(payload: dict[str, Any]) -> int:
    if payload.get("blocks_count"):
        return max(1, min(18, int(payload["blocks_count"])))
    duration = int(payload.get("duration_seconds") or 60)
    return max(1, min(18, round(duration / 10)))


def _narration_for_block(index: int, fmt: dict[str, Any], topic: str, objection: str) -> str:
    structure = fmt.get("default_structure") or []
    step = structure[(index - 1) % len(structure)] if structure else f"ponto {index}"
    templates = {
        1: f"Se {topic.lower()} parece uma questão de força de vontade, talvez a história esteja começando pelo lugar errado.",
        2: f"O ponto invisível é que {step} muda a forma como a paciente interpreta o próprio corpo.",
        3: f"Quando a objeção é {objection.replace('_', ' ')}, o conteúdo precisa mostrar mecanismo, não julgamento.",
        4: f"A imagem central deve transformar {step} em algo simples: processo, contexto e acompanhamento clínico.",
        5: f"O Instituto Vital Slim entra como guia, organizando sinais, exames, rotina e decisão segura.",
        6: "O próximo passo não é promessa rápida; é avaliação individual para entender o que precisa ser ajustado.",
    }
    return templates.get(index, f"Bloco {index}: desenvolver {step} com uma ideia visual clara, sem promessa, sem diagnóstico e sem paciente real.")


def _visual_prompt(index: int, narration: str, scene: str, motion: str, audio: str, negative: str, preset: dict[str, str]) -> str:
    return f"""Block {index}
STYLE REFERENCE:
Match the attached IVS editorial medical motion-graphics key exactly — {preset['description']} Premium medical editorial tone, non-photorealistic, no live-action.

NARRATION:
\"{narration}\"

SCENE:
{scene}

MOTION:
{motion}

AUDIO:
{audio}

NEGATIVE:
{negative}
""".strip()


def build_motion_video_plan(payload: dict[str, Any]) -> dict[str, Any]:
    topic = (payload.get("topic") or "Tema IVS sem título").strip()
    objective = payload.get("objective") or "educacao_autoridade"
    objection = payload.get("objection") or "nao_informada"
    content_format_key = payload.get("content_format") or "mini_aula_visual"
    fmt = get_content_format(content_format_key)
    screen_key = payload.get("screen_format") or "reels"
    screen = SCREEN_FORMATS.get(screen_key, SCREEN_FORMATS["reels"])
    preset_key = payload.get("visual_preset") or "ivs_mixed_media_medico_premium"
    preset = MOTION_PRESETS.get(preset_key, MOTION_PRESETS["ivs_mixed_media_medico_premium"])
    blocks_count = _block_count(payload)
    duration_seconds = int(payload.get("duration_seconds") or blocks_count * 10)
    strategy = payload.get("content_strategy") or "loop_previsao"
    source_examples_summary = payload.get("source_examples_summary") or "Sem exemplos externos selecionados; usar biblioteca IVS-first de formatos."

    negative = (
        "readable text, words, numbers, watermark, logo, patient identity, before-and-after imagery, "
        "promise of result, photorealism, live-action footage, talking characters, lip-sync, color drift, sensationalism"
    )
    blocks: list[dict[str, Any]] = []
    for index in range(1, blocks_count + 1):
        narration = _narration_for_block(index, fmt, topic, objection)
        scene = f"Representar visualmente '{fmt['name']}' para o tema '{topic}' com objeto-metáfora único, sem texto legível no clipe bruto."
        motion = f"Movimento elegante em bloco de 10s: entrada de recortes, mapa/linha dourada, micro-reveal aos 3s e transição limpa para o bloco {index + 1 if index < blocks_count else 'final'}."
        audio = "Ambient bed documental discreto, paper whoosh, pulso suave e sem fala no clipe bruto."
        blocks.append({
            "block_index": index,
            "narration_text": narration,
            "scene": scene,
            "motion": motion,
            "audio": audio,
            "negative_prompt": negative,
            "visual_prompt": _visual_prompt(index, narration, scene, motion, audio, negative, preset),
            "duration_sec": 10,
            "status": "planned",
        })

    return {
        "title": f"Motion Video — {topic}",
        "topic": topic,
        "thesis": payload.get("thesis") or f"{fmt['name']} aplicado ao tema '{topic}' para quebrar a objeção sem promessa médica.",
        "objective": objective,
        "objection": objection,
        "content_format": content_format_key,
        "content_format_name": fmt["name"],
        "content_format_application": fmt["prompt_bias"],
        "source_examples_abstraction": source_examples_summary,
        "content_strategy": strategy,
        "screen_format": screen_key,
        "aspect_ratio": screen["aspect_ratio"],
        "duration_seconds": duration_seconds,
        "blocks_count": blocks_count,
        "visual_preset": preset_key,
        "visual_preset_label": preset["label"],
        "hook_question": f"E se {topic.lower()} não for o problema que você achava?",
        "through_line_object": payload.get("through_line_object") or "um mapa metabólico de papel que se reorganiza a cada bloco",
        "payoff": "O caminho seguro é entender mecanismo, contexto e decisão clínica individualizada.",
        "blocks": blocks,
        "caption": f"{topic}\n\nConteúdo educativo. Avaliação individual é o que transforma dúvida em plano seguro.",
        "cta": payload.get("cta") or "Comente AVALIAÇÃO para entender o próximo passo.",
        "compliance_notes": [
            "Sem paciente real, PII, antes/depois ou promessa de resultado.",
            "Usar exemplos externos apenas para abstrair mecanismo, nunca copiar.",
            "Conteúdo educativo não substitui avaliação médica individual.",
        ],
        "quality_scores_estimados": {
            "format_fit_score": 78,
            "example_abstraction_score": 75,
            "objection_break_score": 74,
            "retention_score": 76,
            "compliance_score": 88,
            "ivs_avatar_score": 80,
        },
        "estimated_credits": {"mode": "dry_run", "clips": blocks_count, "voice": blocks_count, "assemble": 1},
        "approval_status": "plan_only",
        "generation_mode": "plan_only",
        "patient_send_ready": False,
    }
