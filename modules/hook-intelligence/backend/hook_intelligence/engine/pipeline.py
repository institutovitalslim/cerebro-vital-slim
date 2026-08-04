import json
from uuid import NAMESPACE_URL, uuid5

from hook_intelligence import ENGINE_VERSION
from hook_intelligence.domain.models import (
    ComplianceResult,
    ComplianceStatus,
    GenerationRequest,
    Hook,
    HookScores,
    Source,
)
from hook_intelligence.engine.composer import VARIANT_COUNT, compose_pattern
from hook_intelligence.engine.library import HookLibrary
from hook_intelligence.engine.selector import select_patterns

_DEFAULT_SCORES = HookScores(
    clarity=0,
    specificity=0,
    novelty=0,
    retention=0,
    channel_fit=0,
    overall=0,
)


def _request_fingerprint(request: GenerationRequest) -> str:
    return json.dumps(
        request.model_dump(mode="json"),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def generate_deterministic(
    request: GenerationRequest, library: HookLibrary | None = None
) -> tuple[Hook, ...]:
    """Gera hooks locais em ordem reproduzível, sem aleatoriedade ou I/O externo."""

    active_library = HookLibrary.load_default() if library is None else library
    patterns = select_patterns(request, active_library)
    fingerprint = _request_fingerprint(request)
    hooks: list[Hook] = []
    normalized_texts: set[str] = set()

    # Limite explícito: cada padrão pode usar cada variação uma única vez.
    for variant_index in range(VARIANT_COUNT):
        for pattern in patterns:
            try:
                text = compose_pattern(pattern, request, variant_index)
            except ValueError:
                # Templates proibidos ou composições que não cabem são candidatos inelegíveis.
                continue
            normalized = text.casefold()
            if normalized in normalized_texts:
                continue
            normalized_texts.add(normalized)
            identifier = uuid5(
                NAMESPACE_URL,
                f"hook-intelligence:{fingerprint}:{pattern.id}:{variant_index}",
            )
            hooks.append(
                Hook(
                    id=identifier,
                    text=text,
                    library=request.library,
                    pattern_id=pattern.id,
                    mechanisms=[pattern.mechanism],
                    objective=request.objective,
                    channel=request.channel,
                    awareness_stage=request.awareness_stage,
                    audience=request.audience,
                    topic=request.topic,
                    tone=request.tone,
                    scores=_DEFAULT_SCORES.model_copy(deep=True),
                    compliance=ComplianceResult(status=ComplianceStatus.PASS, reasons=[]),
                    explanation=pattern.explanation,
                    source=Source.DETERMINISTIC,
                    engine_version=ENGINE_VERSION,
                )
            )
            if len(hooks) == request.count:
                return tuple(hooks)

    raise ValueError(
        "capacidade determinística insuficiente: "
        f"requested={request.count}, generated={len(hooks)}, "
        f"patterns={len(patterns)}, variants={VARIANT_COUNT}"
    )
