from hashlib import sha256

from hook_intelligence.domain.models import GenerationRequest
from hook_intelligence.engine.library import HookLibrary, Pattern


def stable_rank(seed: str, pattern_id: str) -> str:
    """Retorna a ordenação estável especificada pelo contrato do motor."""

    return sha256(f"{seed}:{pattern_id}".encode()).hexdigest()


def select_patterns(request: GenerationRequest, library: HookLibrary) -> tuple[Pattern, ...]:
    """Aplica filtros rígidos e ranqueia preferências sem excluir fallbacks."""

    candidates = tuple(
        pattern
        for pattern in library.all_patterns
        if pattern.library == request.library.value
        and (request.mechanism is None or pattern.mechanism == request.mechanism)
        and pattern.intensity <= request.intensity
    )
    if not candidates:
        raise ValueError(
            "pool rígido vazio: "
            f"library={request.library.value}, mechanism={request.mechanism}, "
            f"intensity={request.intensity}"
        )

    channel = request.channel.value
    objective = request.objective.value
    awareness = request.awareness_stage.value
    tone = request.tone.value
    seed = request.topic + request.audience

    def preference_key(pattern: Pattern) -> tuple[int, int, int, int, int, str, str]:
        objective_match = int(objective in pattern.objectives)
        channel_match = int(channel in pattern.channels)
        return (
            -(objective_match + channel_match),
            -objective_match,
            -channel_match,
            -int(awareness in pattern.awareness_stages),
            -int(tone in pattern.tones),
            stable_rank(seed, pattern.id),
            pattern.id,
        )

    return tuple(sorted(candidates, key=preference_key))
