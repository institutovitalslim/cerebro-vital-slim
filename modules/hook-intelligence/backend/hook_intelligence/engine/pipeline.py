import json
import unicodedata
from uuid import NAMESPACE_URL, uuid5

from pydantic import ValidationError

from hook_intelligence import ENGINE_VERSION
from hook_intelligence.adapters import DisabledAdapter, adapter_from_env
from hook_intelligence.adapters.base import HookAdapter
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
    contains_expression,
    contains_forbidden,
    normalize_text,
)
from hook_intelligence.engine.deduplicator import deduplicate
from hook_intelligence.engine.library import HookLibrary
from hook_intelligence.engine.scorer import score_text
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


def _rules_library(request: GenerationRequest, active_library: object) -> HookLibrary | None:
    if request.library.value != "ivs-health":
        return None
    return active_library if isinstance(active_library, HookLibrary) else HookLibrary.load_default()


def _valid_adapted_text(text: object, request: GenerationRequest) -> str | None:
    if not isinstance(text, str):
        return None
    normalized = normalize_text(text)
    if not 3 <= len(normalized) <= request.max_length:
        return None
    if not any(character.isalnum() for character in normalized):
        return None
    if any(unicodedata.category(character).startswith("C") for character in normalized):
        return None
    if not all(contains_expression(normalized, word) for word in request.required_words):
        return None
    if contains_forbidden(normalized, request.forbidden_words):
        return None
    return normalized


def generate_with_optional_ai(
    request: GenerationRequest,
    library: HookLibrary | None = None,
    adapter: HookAdapter | None = None,
) -> tuple[Hook, ...]:
    """Só substitui o baseline quando todo o lote adaptado passa nova validação."""

    validated_request = _validated_request(request)
    active_library = HookLibrary.load_default() if library is None else library
    baseline = generate_deterministic(request, active_library)
    if not validated_request.use_ai:
        return baseline

    try:
        active_adapter = adapter_from_env() if adapter is None else adapter
        if isinstance(active_adapter, DisabledAdapter):
            return baseline
        raw = active_adapter.adapt(
            validated_request.topic,
            [hook.text for hook in baseline],
        )
        if not isinstance(raw, list) or len(raw) != len(baseline):
            return baseline
        normalized: list[str] = []
        for value in raw:
            safe = _valid_adapted_text(value, validated_request)
            if safe is None:
                return baseline
            normalized.append(safe)
        if len(deduplicate(normalized, threshold=0.82)) != len(baseline):
            return baseline

        rules_library = _rules_library(validated_request, active_library)
        compliance = [
            evaluate_compliance(text, validated_request.library, rules_library)
            for text in normalized
        ]
        if any(result.status is ComplianceStatus.BLOCK for result in compliance):
            return baseline

        fingerprint = _request_fingerprint(validated_request)
        adapted: list[tuple[int, Hook]] = []
        for index, (text, original, result) in enumerate(
            zip(normalized, baseline, compliance, strict=True)
        ):
            scores = score_text(text, validated_request.channel, validated_request.topic)
            identifier = uuid5(
                NAMESPACE_URL,
                f"hook-intelligence:ai:{fingerprint}:{text}:{index}",
            )
            adapted.append(
                (
                    index,
                    original.model_copy(
                        update={
                            "id": identifier,
                            "text": text,
                            "scores": scores.to_hook_scores(),
                            "compliance": result,
                            "source": Source.AI_ADAPTED,
                        },
                        deep=True,
                    ),
                )
            )
        adapted.sort(key=lambda item: (-item[1].scores.overall, item[0]))
        return tuple(hook for _, hook in adapted)
    except Exception:  # noqa: BLE001 -- fallback integral é o contrato desta fronteira.
        return baseline
