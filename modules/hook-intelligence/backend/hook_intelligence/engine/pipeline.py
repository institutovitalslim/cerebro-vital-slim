import json
from uuid import NAMESPACE_URL, uuid5

from pydantic import ValidationError

from hook_intelligence import ENGINE_VERSION
from hook_intelligence.domain.models import (
    ComplianceStatus,
    GenerationRequest,
    Hook,
    HookScores,
    Source,
)
from hook_intelligence.engine.compliance import evaluate_compliance
from hook_intelligence.engine.composer import (
    VARIANT_COUNT,
    CandidateConstraintError,
    canonical_key,
    compose_pattern,
    normalize_text,
)
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


def _deduplicate_expressions(values: list[str], field: str) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = normalize_text(value)
        if not item:
            raise ValueError(f"request inválida: {field} não pode conter item vazio")
        key = item.casefold()
        if key not in seen:
            seen.add(key)
            normalized.append(item)
    return normalized


def _validated_request(request: GenerationRequest) -> GenerationRequest:
    """Reconstrói e canoniza a request, inclusive cópias Pydantic sem validação."""

    if not isinstance(request, GenerationRequest):
        # A fronteira pública converte tipos inválidos em ValueError contextual por contrato.
        raise ValueError("request deve ser uma GenerationRequest válida")  # noqa: TRY004
    raw = request.model_dump(mode="python", round_trip=True, warnings=False)
    try:
        # ``strict`` é essencial: model_copy(update=...) pode introduzir tipos inválidos.
        GenerationRequest.model_validate(raw, strict=True)
    except ValidationError as error:
        raise ValueError(f"GenerationRequest inválida: {error}") from error

    topic = normalize_text(raw["topic"])
    audience = normalize_text(raw["audience"])
    if not topic:
        raise ValueError("request inválida: topic não pode ser vazio/whitespace-only")
    if not audience:
        raise ValueError("request inválida: audience não pode ser vazio/whitespace-only")

    raw["topic"] = topic
    raw["audience"] = audience
    if raw["context"] is not None:
        raw["context"] = normalize_text(raw["context"])
    if raw["mechanism"] is not None:
        raw["mechanism"] = normalize_text(raw["mechanism"])
    raw["required_words"] = _deduplicate_expressions(raw["required_words"], "required_words")
    raw["forbidden_words"] = _deduplicate_expressions(raw["forbidden_words"], "forbidden_words")

    required = {canonical_key(item) for item in raw["required_words"]}
    forbidden = {canonical_key(item) for item in raw["forbidden_words"]}
    overlap = required & forbidden
    if overlap:
        conflict = min(overlap)
        raise ValueError(
            f"request inválida: contradição entre required_words e forbidden_words: {conflict!r}"
        )
    try:
        return GenerationRequest.model_validate(raw, strict=True)
    except ValidationError as error:
        raise ValueError(f"GenerationRequest normalizada inválida: {error}") from error


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

    validated_request = _validated_request(request)
    active_library = HookLibrary.load_default() if library is None else library
    if validated_request.library.value == "ivs-health":
        rules_library = (
            active_library
            if isinstance(active_library, HookLibrary)
            else HookLibrary.load_default()
        )
    else:
        rules_library = None
    patterns = select_patterns(validated_request, active_library)
    fingerprint = _request_fingerprint(validated_request)
    hooks: list[Hook] = []
    normalized_texts: set[str] = set()
    blocked = 0

    # Limite explícito: cada padrão pode usar cada variação uma única vez.
    for variant_index in range(VARIANT_COUNT):
        for pattern in patterns:
            try:
                text = compose_pattern(pattern, validated_request, variant_index)
            except CandidateConstraintError:
                # Apenas candidatos que violam constraints são inelegíveis.
                continue
            normalized = canonical_key(text)
            if normalized in normalized_texts:
                continue
            normalized_texts.add(normalized)
            compliance = evaluate_compliance(text, validated_request.library, rules_library)
            if compliance.status is ComplianceStatus.BLOCK:
                blocked += 1
                continue
            identifier = uuid5(
                NAMESPACE_URL,
                f"hook-intelligence:{fingerprint}:{pattern.id}:{variant_index}",
            )
            hooks.append(
                Hook(
                    id=identifier,
                    text=text,
                    library=validated_request.library,
                    pattern_id=pattern.id,
                    mechanisms=[pattern.mechanism],
                    objective=validated_request.objective,
                    channel=validated_request.channel,
                    awareness_stage=validated_request.awareness_stage,
                    audience=validated_request.audience,
                    topic=validated_request.topic,
                    tone=validated_request.tone,
                    scores=_DEFAULT_SCORES.model_copy(deep=True),
                    compliance=compliance,
                    explanation=pattern.explanation,
                    source=Source.DETERMINISTIC,
                    engine_version=ENGINE_VERSION,
                )
            )
            if len(hooks) == validated_request.count:
                return tuple(hooks)

    raise ValueError(
        "capacidade determinística insuficiente: "
        f"requested={validated_request.count}, generated={len(hooks)}, "
        f"blocked={blocked}, "
        f"patterns={len(patterns)}, variants={VARIANT_COUNT}, "
        f"max_length={validated_request.max_length}"
    )
