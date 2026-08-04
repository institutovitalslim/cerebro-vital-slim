import re
import string

from hook_intelligence.domain.models import GenerationRequest
from hook_intelligence.engine.library import ALLOWED_SLOTS, Pattern

# Variações editoriais curtas, úteis e finitas. A posição também varia; não se trata
# de trocar apenas a pontuação do mesmo texto.
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


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _expression_pattern(expression: str) -> re.Pattern[str]:
    normalized = _normalize(expression).casefold()
    if not normalized:
        raise ValueError("palavras obrigatórias/proibidas não podem ser vazias")
    return re.compile(rf"(?<!\w){re.escape(normalized)}(?!\w)", re.UNICODE)


def contains_expression(text: str, expression: str) -> bool:
    return _expression_pattern(expression).search(_normalize(text).casefold()) is not None


def contains_forbidden(text: str, forbidden_words: list[str]) -> bool:
    return any(contains_expression(text, word) for word in forbidden_words)


def _validated_slots(pattern: Pattern) -> tuple[str, ...]:
    try:
        parsed = tuple(_FORMATTER.parse(pattern.template))
    except ValueError as error:
        raise ValueError(f"pattern_id={pattern.id}: template inválido: {error}") from error

    slots: list[str] = []
    for _, field, format_spec, conversion in parsed:
        if field is None:
            continue
        if field not in ALLOWED_SLOTS:
            raise ValueError(f"pattern_id={pattern.id}: unknown slot {field}")
        if format_spec or conversion:
            raise ValueError(f"pattern_id={pattern.id}: formatação de slot não permitida")
        slots.append(field)
    if len(slots) != len(set(slots)):
        raise ValueError(f"pattern_id={pattern.id}: slots repetidos")
    if tuple(slots) != pattern.slots:
        raise ValueError(f"pattern_id={pattern.id}: slots declarados não correspondem ao template")
    return tuple(slots)


def _truncate_words(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    words = text.split()
    retained: list[str] = []
    length = 0
    for word in words:
        addition = len(word) + int(bool(retained))
        if length + addition > limit:
            break
        retained.append(word)
        length += addition
    return " ".join(retained).rstrip(" ,;:—-")


def _fit(core: str, suffix: str, max_length: int) -> str:
    suffix = _normalize(suffix)
    separator = "" if not suffix else " "
    room = max_length - len(separator) - len(suffix)
    if room < 3:
        raise ValueError("required_words não cabem em max_length")
    fitted_core = _truncate_words(_normalize(core), room)
    if len(fitted_core) < 3:
        raise ValueError("texto base não cabe em max_length sem cortar palavra")
    result = _normalize(fitted_core + separator + suffix)
    if len(result) > max_length:
        raise ValueError("texto não cabe em max_length")
    return result


def _required_suffix(words: list[str]) -> str:
    normalized = [_normalize(word) for word in words]
    if not normalized:
        return ""
    if any(not word for word in normalized):
        raise ValueError("required_words não podem conter texto vazio")
    return "— com foco em " + " e ".join(normalized)


def compose_pattern(pattern: Pattern, request: GenerationRequest, variant_index: int = 0) -> str:
    """Compõe um padrão com valores literais e limites seguros."""

    _validated_slots(pattern)
    if not 0 <= variant_index < VARIANT_COUNT:
        raise ValueError(f"variant_index deve estar entre 0 e {VARIANT_COUNT - 1}")
    if contains_forbidden(pattern.template, request.forbidden_words):
        raise ValueError(f"pattern_id={pattern.id}: template contém forbidden_words")

    topic = _normalize(request.topic)
    context = _normalize(request.context or "na prática cotidiana")
    required_word = (
        _normalize(request.required_words[0]) if request.required_words else "um critério claro"
    )
    values = {
        "topic": topic,
        "audience": _normalize(request.audience),
        "desired_outcome": f"uma compreensão mais clara de {topic}",
        "context": context,
        "required_word": required_word,
    }
    # str.format processa apenas o template. Chaves dentro dos valores permanecem dados.
    rendered = _normalize(pattern.template.format_map(values))
    prefix, tail = _VARIATIONS[variant_index]
    core = _normalize(prefix + rendered)
    editorial_suffix = tail

    preliminary = _fit(core, editorial_suffix, request.max_length)
    missing = [
        word for word in request.required_words if not contains_expression(preliminary, word)
    ]
    if missing:
        suffix_parts = [part for part in (editorial_suffix, _required_suffix(missing)) if part]
        preliminary = _fit(core, " ".join(suffix_parts), request.max_length)

    if not all(contains_expression(preliminary, word) for word in request.required_words):
        # A palavra podia existir apenas na parte truncada. Reserve todas explicitamente.
        preliminary = _fit(core, _required_suffix(request.required_words), request.max_length)
    if contains_forbidden(preliminary, request.forbidden_words):
        raise ValueError(f"pattern_id={pattern.id}: candidato contém forbidden_words")
    if not 3 <= len(preliminary) <= request.max_length:
        raise ValueError(f"pattern_id={pattern.id}: comprimento final inválido")
    return preliminary
