from __future__ import annotations

from copy import deepcopy
from typing import Any
from urllib.parse import urlparse

VISUAL_HOOKS: list[dict[str, Any]] = [
    {
        "key": "text_slide_in",
        "category": "graphic_text_overlay",
        "name": "Text Slide In",
        "description": "Texto curto entra na tela para nomear dor, mito ou contraste nos primeiros segundos.",
        "ivs_use": "Abrir clareza imediata sem depender do áudio: 'Não é falta de disciplina' ou '3 sinais de estratégia solta'.",
        "best_for": ["quebra_de_mito", "checklist_rapido", "faq_direto"],
        "shot_bias": "Comece com objeto/rosto/gesto limpo e texto premium entrando em 0-2s; uma frase, uma quebra de objeção.",
        "guardrails": ["sem excesso de texto", "sem promessa de resultado", "sem estética Canva genérica"],
    },
    {
        "key": "match_cut",
        "category": "pattern_interrupt_visual_switching",
        "name": "Match Cut",
        "description": "Corte casado transforma uma cena/objeto em outro para criar virada de percepção.",
        "ivs_use": "Mostrar tentativa solta virando avaliação organizada: prato, agenda ou roupa se transformam em checklist/método.",
        "best_for": ["comparacao_de_caminhos", "antes_da_decisao", "metodo_ivs"],
        "shot_bias": "Planeje dois planos com forma parecida: caos cotidiano → critério de avaliação; o corte precisa revelar a tese.",
        "guardrails": ["sem truque vazio", "sem antes/depois corporal", "sem comparação de resultado"],
    },
    {
        "key": "jump_switch",
        "category": "subject_motion",
        "name": "Jump Switch",
        "description": "Sujeito ou objeto muda de posição/estado para criar micro-surpresa e ritmo.",
        "ivs_use": "Dra. Daniely ou objetos mudam entre mito, exame e plano; movimento conduz a explicação sem informalidade excessiva.",
        "best_for": ["bastidor_medico_seguro", "metodo_ivs", "jornada_da_paciente"],
        "shot_bias": "Use 3 posições/estados bem definidos: mito → investigação → caminho seguro, com cortes limpos.",
        "guardrails": ["sem dança/trend barulhenta", "sem exposição de paciente", "sem tom amador"],
    },
    {
        "key": "speed_ramp",
        "category": "visual_effect_transitions",
        "name": "Speed Ramp Effect",
        "description": "Aceleração/desaceleração destaca caos, processo ou virada de entendimento.",
        "ivs_use": "Acelerar tentativas soltas e desacelerar no momento de avaliação, método ou tecnologia explicada.",
        "best_for": ["explicacao_de_tecnologia", "prova_de_metodo", "bastidor_medico_seguro"],
        "shot_bias": "Ritmo rápido para confusão/rotina; pausa elegante no payoff/mecanismo; transição limpa e premium.",
        "guardrails": ["sem overediting", "sem estética influencer genérica", "sem prometer transformação"],
    },
    {
        "key": "unusual_image",
        "category": "visual_selection",
        "name": "Unusual Image",
        "description": "Imagem ou objeto pouco óbvio abre curiosidade e materializa uma emoção/objeção.",
        "ivs_use": "Rouparia/cabide, espelho embaçado, agenda lotada, prato incompleto ou exame genérico viram metáfora segura.",
        "best_for": ["reframe_de_culpa", "historia_espelho", "resumo_salvavel"],
        "shot_bias": "Escolha um objeto-metáfora reconhecível e inesperado; ele deve representar a trava sem body shaming.",
        "guardrails": ["sem imagem corporal sensível", "sem vergonha", "sem claim clínico implícito"],
    },
]


def get_visual_hook(key: str | None) -> dict[str, Any]:
    aliases = {
        "graphic_text_overlay": "text_slide_in",
        "text_overlay": "text_slide_in",
        "pattern_interrupt": "match_cut",
        "visual_switching": "match_cut",
        "subject_motion": "jump_switch",
        "visual_effect": "speed_ramp",
        "transition": "speed_ramp",
        "visual_selection": "unusual_image",
        "imagem_incomum": "unusual_image",
    }
    normalized = (key or "text_slide_in").strip().lower()
    normalized = aliases.get(normalized, normalized)
    for item in VISUAL_HOOKS:
        if item["key"] == normalized:
            return item
    return VISUAL_HOOKS[0]


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

MATRIX_8X8_ROWS = [
    {"key": "dr_marlonbatista", "label": "@dr.marlonbatista", "source_type": "approved_profile"},
    {"key": "dra_camilapaes", "label": "@dra.camilapaes", "source_type": "approved_profile"},
    {"key": "instagram_theme_search", "label": "Busca temática Instagram", "source_type": "search"},
    {"key": "validated_medical_profile", "label": "Perfil médico validado pelo João", "source_type": "approved_profile"},
    {"key": "ivs_active_creatives", "label": "Criativos ativos IVS", "source_type": "owned_media"},
    {"key": "tiaro_submitted_reels", "label": "Reels/cards enviados por Tiaro", "source_type": "operator_submission"},
    {"key": "validated_local_competitor", "label": "Concorrente local validado", "source_type": "competitor"},
    {"key": "external_format_source", "label": "Fonte externa de formato sem claim clínico", "source_type": "external_hypothesis"},
]

MATRIX_8X8_COLUMNS = [
    {"key": "hook_3s", "label": "Hook visual/verbal nos 3 primeiros segundos"},
    {"key": "content_format", "label": "Formato de conteúdo usado"},
    {"key": "objection", "label": "Objeção atacada"},
    {"key": "retention_mechanism", "label": "Mecanismo de retenção"},
    {"key": "proof_authority", "label": "Prova/autoridade usada"},
    {"key": "cta", "label": "CTA/ação pedida"},
    {"key": "compliance_risk", "label": "Compliance/risco"},
    {"key": "ivs_avatar_fit", "label": "Aplicabilidade ao avatar IVS"},
]

WINNER_TYPES = [
    {"key": "attention", "label": "Winner de atenção", "selects_for": "melhor hook/retenção"},
    {"key": "conversion", "label": "Winner de conversão", "selects_for": "melhor quebra de objeção + CTA"},
    {"key": "ivs_fit", "label": "Winner de adaptação IVS", "selects_for": "maior alinhamento avatar + compliance"},
]

EXAMPLE_ARCHETYPES = [
    {
        "slot": "hook_retention",
        "source_type": "format_example_archetype",
        "hook_summary": "Hook de 3 segundos com pergunta que abre loop e segura a resposta para o final.",
        "why_this_example_works": "Cria lacuna de curiosidade sem prometer milagre e facilita adaptação para motion graphics.",
        "retention_mechanism": "open_loop_payoff",
        "winner_candidate_type": "attention",
    },
    {
        "slot": "objection_conversion",
        "source_type": "format_example_archetype",
        "hook_summary": "Quebra a objeção central mostrando processo, contexto e próximo passo seguro.",
        "why_this_example_works": "Transforma resistência em critério de decisão sem pressão comercial agressiva.",
        "retention_mechanism": "objection_reframe",
        "winner_candidate_type": "conversion",
    },
    {
        "slot": "ivs_fit_compliance",
        "source_type": "format_example_archetype",
        "hook_summary": "Adapta o formato para o avatar IVS com tom médico-premium e sem paciente real.",
        "why_this_example_works": "Preserva a mecânica do formato, reduz risco de cópia e mantém compliance clínico.",
        "retention_mechanism": "avatar_mirror_safe",
        "winner_candidate_type": "ivs_fit",
    },
]


def normalize_real_content_format_example(payload: dict[str, Any]) -> dict[str, Any]:
    """Normaliza um vídeo real governado para content_format_examples.

    Não baixa mídia nem copia roteiro: transforma URL/payload em referência de mecanismo
    com guardrails de compliance e revisão humana antes de uso em geração.
    """
    content_format = (payload.get("content_format") or "").strip()
    fmt = get_content_format(content_format)
    raw_url = (payload.get("content_url") or payload.get("url") or "").strip()
    source_type = (payload.get("source_type") or "manual_url").strip()
    source_handle_or_url = (payload.get("source_handle_or_url") or payload.get("source_profile") or raw_url or "manual").strip()
    external_id = (payload.get("external_id") or "").strip()
    clean_url = raw_url

    if raw_url:
        parsed = urlparse(raw_url)
        path_parts = [part for part in parsed.path.split("/") if part]
        if "instagram.com" in parsed.netloc and len(path_parts) >= 2 and path_parts[0] in {"p", "reel", "tv"}:
            shortcode = path_parts[1]
            clean_url = f"https://www.instagram.com/{path_parts[0]}/{shortcode}/"
            external_id = external_id or f"instagram:{shortcode}"
        elif not external_id:
            external_id = f"url:{parsed.netloc}{parsed.path}" if parsed.netloc else f"manual:{fmt['key']}"
    if not external_id:
        external_id = f"manual:{fmt['key']}:{abs(hash(str(payload))) % 100000000}"

    score = int(payload.get("ivs_applicability_score") or 70)
    score = max(0, min(100, score))
    return {
        "content_format": fmt["key"],
        "content_format_name": fmt["name"],
        "source_type": source_type,
        "source_handle_or_url": source_handle_or_url,
        "external_id": external_id,
        "content_url": clean_url or None,
        "thumbnail_url": payload.get("thumbnail_url"),
        "transcript_summary": (payload.get("transcript_summary") or "Referência real cadastrada para análise de mecanismo; transcrição completa não armazenada.").strip(),
        "hook_summary": (payload.get("hook_summary") or "Hook pendente de análise pelo João/Maria.").strip(),
        "why_this_example_works": (payload.get("why_this_example_works") or "Exemplo real precisa ser usado apenas para abstrair mecanismo, ritmo e retenção.").strip(),
        "retention_mechanism": payload.get("retention_mechanism") or "pending_analysis",
        "compliance_risk": payload.get("compliance_risk") or "review_required",
        "ivs_applicability_score": score,
        "winner_candidate_type": payload.get("winner_candidate_type") or "pending",
        "selected_for_generation": False,
        "copy_guardrail": "Referência real: não copiar frase, roteiro, legenda, voz, edição proprietária ou claim clínico; usar somente mecanismo abstrato.",
        "raw_metrics": payload.get("metrics") or {},
        "raw_payload_summary": payload.get("raw_payload_summary") or payload.get("caption_summary") or None,
    }


def build_content_format_examples(format_key: str | None = None) -> list[dict[str, Any]]:
    formats = [get_content_format(format_key)] if format_key else CONTENT_FORMATS
    examples: list[dict[str, Any]] = []
    for fmt in formats:
        for index, archetype in enumerate(EXAMPLE_ARCHETYPES, start=1):
            examples.append({
                "id": f"{fmt['key']}::{archetype['slot']}",
                "content_format": fmt["key"],
                "content_format_name": fmt["name"],
                "source_type": archetype["source_type"],
                "source_handle_or_url": "library://ivs/content-format-examples",
                "external_id": f"{fmt['key']}-{archetype['slot']}",
                "content_url": None,
                "thumbnail_url": None,
                "transcript_summary": f"Arquétipo de vídeo de exemplo para {fmt['name']}: {archetype['hook_summary']}",
                "hook_summary": archetype["hook_summary"],
                "why_this_example_works": archetype["why_this_example_works"],
                "retention_mechanism": archetype["retention_mechanism"],
                "compliance_risk": "low",
                "ivs_applicability_score": 86 + index,
                "winner_candidate_type": archetype["winner_candidate_type"],
                "copy_guardrail": "Usar como referência de mecanismo; não copiar frase, roteiro, legenda ou edição proprietária.",
            })
    return examples


def motion_video_matrix_8x8() -> dict[str, Any]:
    return {
        "rows": deepcopy(MATRIX_8X8_ROWS),
        "columns": deepcopy(MATRIX_8X8_COLUMNS),
        "winner_types": deepcopy(WINNER_TYPES),
        "selection_rule": "Após cada batch 8x8, selecionar 3 winners: atenção, conversão e adaptação IVS.",
        "required_outputs_per_winner": ["3 hooks adaptados", "1 roteiro de Reel", "1 variação para Stories", "1 ângulo de anúncio", "1 hipótese de métrica"],
    }


def example_winners_for_format(format_key: str) -> list[dict[str, Any]]:
    examples = build_content_format_examples(format_key)
    winners: list[dict[str, Any]] = []
    for winner_type in WINNER_TYPES:
        candidate = next((item for item in examples if item["winner_candidate_type"] == winner_type["key"]), examples[0])
        winners.append({
            "winner_type": winner_type["key"],
            "winner_label": winner_type["label"],
            "example_id": candidate["id"],
            "rationale": f"{winner_type['selects_for']}; {candidate['why_this_example_works']}",
            "selected_for_generation": False,
            "outputs_required": ["3 hooks adaptados", "1 roteiro de Reel", "1 variação para Stories", "1 ângulo de anúncio", "1 hipótese de métrica"],
        })
    return winners


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
        "content_format_examples": build_content_format_examples(),
        "visual_hooks": deepcopy(VISUAL_HOOKS),
        "matrix_8x8": motion_video_matrix_8x8(),
        "screen_formats": deepcopy(SCREEN_FORMATS),
        "motion_presets": deepcopy(MOTION_PRESETS),
        "duration_presets": deepcopy(DURATION_PRESETS),
        "content_strategies": ["loop_previsao", "jornada_ivs", "retencao_loops", "erro_mecanismo_metodo", "mito_realidade_conduta"],
        "voiceovers": ["documental_feminina_pt_br", "documental_masculina_pt_br", "premium_institucional_pt_br", "sem_voz"],
        "generation_modes": ["plan_only", "approved_for_paid_generation"],
        "workflow": [
            "Objetivo",
            "Objeção",
            "Formato de conteúdo",
            "Visual Hook",
            "Vídeos de exemplo",
            "Estratégia Narrativa",
            "Roteiro/Copy",
            "Motion Brief",
            "Prompts Higgsfield",
            "Gate compliance",
            "Aprovação de gasto",
        ],
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


def _visual_prompt(index: int, narration: str, scene: str, motion: str, audio: str, negative: str, preset: dict[str, str], visual_hook: dict[str, Any] | None = None) -> str:
    hook = visual_hook or get_visual_hook(None)
    return f"""Block {index}
STYLE REFERENCE:
Match the attached IVS editorial medical motion-graphics key exactly — {preset['description']} Premium medical editorial tone, non-photorealistic, no live-action.

VISUAL HOOK:
{hook['name']} ({hook['category']}) — {hook['shot_bias']} IVS use: {hook['ivs_use']}

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
    visual_hook = get_visual_hook(payload.get("visual_hook") or payload.get("visual_hook_mechanic"))
    source_examples_summary = payload.get("source_examples_summary") or "Sem exemplos externos selecionados; usar biblioteca IVS-first de formatos."
    examples = build_content_format_examples(content_format_key)
    winners = example_winners_for_format(content_format_key)

    negative = (
        "readable text, words, numbers, watermark, logo, patient identity, before-and-after imagery, "
        "promise of result, photorealism, live-action footage, talking characters, lip-sync, color drift, sensationalism"
    )
    blocks: list[dict[str, Any]] = []
    for index in range(1, blocks_count + 1):
        narration = _narration_for_block(index, fmt, topic, objection)
        scene = f"Representar visualmente '{fmt['name']}' para o tema '{topic}' com objeto-metáfora único e visual hook {visual_hook['name']} ({visual_hook['category']}), sem texto legível no clipe bruto."
        motion = f"Movimento elegante em bloco de 10s: {visual_hook['shot_bias']} Entrada de recortes, mapa/linha dourada, micro-reveal aos 3s e transição limpa para o bloco {index + 1 if index < blocks_count else 'final'}."
        audio = "Ambient bed documental discreto, paper whoosh, pulso suave e sem fala no clipe bruto."
        blocks.append({
            "block_index": index,
            "narration_text": narration,
            "scene": scene,
            "motion": motion,
            "audio": audio,
            "negative_prompt": negative,
            "visual_prompt": _visual_prompt(index, narration, scene, motion, audio, negative, preset, visual_hook),
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
        "visual_hook": visual_hook["key"],
        "visual_hook_category": visual_hook["category"],
        "visual_hook_name": visual_hook["name"],
        "visual_hook_application": visual_hook["ivs_use"],
        "visual_hook_gate": {
            "version": "visual_hook_gate_ivs_v1_plan",
            "total": 10,
            "max": 10,
            "checks": {
                "interrupcao_visual_0_2s": True,
                "conexao_com_objecao": True,
                "clareza_sem_audio": True,
                "funcao_narrativa": True,
                "compliance_medico_visual": True,
            },
            "recommendation": "Visual hook planejado com função narrativa e guardrails IVS.",
        },
        "source_examples_abstraction": source_examples_summary,
        "source_examples": examples,
        "batch_winners": winners,
        "matrix_8x8_applied": {
            "rows": len(MATRIX_8X8_ROWS),
            "columns": len(MATRIX_8X8_COLUMNS),
            "winner_types": [item["key"] for item in WINNER_TYPES],
        },
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
