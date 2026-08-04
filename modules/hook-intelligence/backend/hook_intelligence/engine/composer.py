import re
import string
import unicodedata
from typing import NoReturn

from hook_intelligence.domain.models import GenerationRequest
from hook_intelligence.engine.library import ALLOWED_SLOTS, Pattern

# Variações editoriais curtas, úteis e finitas. Caudas são sempre adicionadas inteiras.
_VARIATIONS = (
    ("", ""),
    ("", " — um ponto para observar"),
    ("", " — vale analisar com calma"),
    ("Em foco: ", ""),
    ("Para refletir: ", ""),
    ("Um recorte útil: ", ""),
    ("Na prática: ", ""),
    ("Ponto de partida: ", ""),
    ("", " — considere o contexto"),
    ("Leitura inicial: ", ""),
    ("Questão central: ", ""),
    ("Antes de decidir: ", ""),
)
VARIANT_COUNT = len(_VARIATIONS)
_FORMATTER = string.Formatter()
_DANGLING_PT_BR = frozenset(
    {
        "a",
        "ao",
        "aos",
        "as",
        "com",
        "da",
        "das",
        "de",
        "do",
        "dos",
        "e",
        "em",
        "na",
        "nas",
        "no",
        "nos",
        "o",
        "os",
        "ou",
        "para",
        "pela",
        "pelas",
        "pelo",
        "pelos",
        "por",
        "que",
        "quando",
        "se",
        "sem",
        "um",
        "uma",
        "uns",
        "umas",
    }
)


class PatternCompositionError(ValueError):
    """O padrão é estruturalmente inválido e não deve ser silenciosamente ignorado."""


class CandidateConstraintError(ValueError):
    """A composição é válida, mas este candidato não satisfaz os limites da request."""


def normalize_text(text: str) -> str:
    """Normaliza Unicode e espaços na ordem canônica usada pelo motor."""

    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text)).strip()


def canonical_key(text: str) -> str:
    return normalize_text(text).casefold()


def _expression_pattern(expression: str) -> re.Pattern[str]:
    normalized = canonical_key(expression)
    if not normalized:
        raise CandidateConstraintError("palavras obrigatórias/proibidas não podem ser vazias")
    return re.compile(rf"(?<!\w){re.escape(normalized)}(?!\w)", re.UNICODE)


def contains_expression(text: str, expression: str) -> bool:
    return _expression_pattern(expression).search(canonical_key(text)) is not None


def contains_forbidden(text: str, forbidden_words: list[str]) -> bool:
    return any(contains_expression(text, word) for word in forbidden_words)


def _composition_error(pattern: Pattern, detail: str, cause: Exception | None = None) -> NoReturn:
    error = PatternCompositionError(f"pattern_id={pattern.id}: {detail}")
    if cause is None:
        raise error
    raise error from cause


def _validated_slots(pattern: Pattern) -> tuple[str, ...]:
    try:
        parsed = tuple(_FORMATTER.parse(pattern.template))
    except (TypeError, ValueError) as error:
        _composition_error(pattern, f"template inválido: {error}", error)

    slots: list[str] = []
    for _, field, format_spec, conversion in parsed:
        if field is None:
            continue
        if not field or field not in ALLOWED_SLOTS:
            _composition_error(pattern, f"unknown slot {field!r}")
        if format_spec:
            _composition_error(pattern, f"format_spec não permitido no slot {field}")
        if conversion:
            _composition_error(pattern, f"conversion não permitida no slot {field}")
        slots.append(field)
    if len(slots) != len(set(slots)):
        _composition_error(pattern, "slots repetidos no template")
    if tuple(slots) != pattern.slots:
        _composition_error(
            pattern,
            f"slots declarados {pattern.slots!r} divergem do template {tuple(slots)!r}",
        )
    return tuple(slots)


def _required_suffix(words: list[str]) -> str:
    if not words:
        return ""
    return "— com foco em " + " e ".join(words)


def _fits(*parts: str, max_length: int) -> str | None:
    result = normalize_text(" ".join(part for part in parts if part))
    return result if len(result) <= max_length else None


def _has_dangling_ending(text: str) -> bool:
    words = re.findall(r"\w+", canonical_key(text), re.UNICODE)
    return bool(words) and words[-1] in _DANGLING_PT_BR


def compose_pattern(pattern: Pattern, request: GenerationRequest, variant_index: int = 0) -> str:
    """Compõe um padrão sem cortar templates, caudas ou palavras obrigatórias."""

    _validated_slots(pattern)
    if not 0 <= variant_index < VARIANT_COUNT:
        raise ValueError(f"variant_index deve estar entre 0 e {VARIANT_COUNT - 1}")
    if contains_forbidden(pattern.template, request.forbidden_words):
        raise CandidateConstraintError(f"pattern_id={pattern.id}: template contém forbidden_words")

    topic = normalize_text(request.topic)
    context = normalize_text(request.context or "na prática cotidiana")
    required_word = request.required_words[0] if request.required_words else "um critério claro"
    values = {
        "topic": topic,
        "audience": normalize_text(request.audience),
        "desired_outcome": f"uma compreensão mais clara de {topic}",
        "context": context,
        "required_word": normalize_text(required_word),
    }
    try:
        rendered = normalize_text(pattern.template.format_map(values))
    except (KeyError, TypeError, ValueError, AttributeError, IndexError) as error:
        _composition_error(pattern, f"falha ao formatar template: {error}", error)

    prefix, tail = _VARIATIONS[variant_index]
    core = normalize_text(prefix + rendered)
    if len(core) > request.max_length:
        raise CandidateConstraintError(
            f"pattern_id={pattern.id}: texto base não cabe integralmente em max_length"
        )

    # A cauda editorial é opcional e só entra inteira. Nunca reduzimos o núcleo para acomodá-la.
    preliminary = _fits(core, tail, max_length=request.max_length) or core
    missing = [
        word for word in request.required_words if not contains_expression(preliminary, word)
    ]
    if missing:
        required_suffix = _required_suffix(missing)
        # Primeiro preserva a cauda; se não couber, descarta apenas a cauda editorial opcional.
        with_required = _fits(core, tail, required_suffix, max_length=request.max_length)
        if with_required is None:
            with_required = _fits(core, required_suffix, max_length=request.max_length)
        if with_required is None:
            raise CandidateConstraintError(
                f"pattern_id={pattern.id}: required_words não cabem integralmente em max_length"
            )
        preliminary = with_required

    if not all(contains_expression(preliminary, word) for word in request.required_words):
        raise CandidateConstraintError(f"pattern_id={pattern.id}: required_words ausentes")
    if contains_forbidden(preliminary, request.forbidden_words):
        raise CandidateConstraintError(f"pattern_id={pattern.id}: candidato contém forbidden_words")
    if _has_dangling_ending(preliminary):
        raise CandidateConstraintError(f"pattern_id={pattern.id}: candidato com final pendente")
    if not 3 <= len(preliminary) <= request.max_length:
        raise CandidateConstraintError(f"pattern_id={pattern.id}: comprimento final inválido")
    return preliminary
