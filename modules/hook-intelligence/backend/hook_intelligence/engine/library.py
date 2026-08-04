import json
import string
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, NoReturn

from hook_intelligence.domain.models import AwarenessStage, Channel, Objective, Tone

ALLOWED_SLOTS = frozenset({"topic", "audience", "desired_outcome", "context", "required_word"})
LIBRARIES = ("universal", "ivs-health")
TAXONOMY_FILES = {
    "channels": "channels.json",
    "objectives": "objectives.json",
    "awareness": "awareness.json",
    "tones": "tones.json",
}
EXPECTED_ENUMS = {
    "channels": frozenset(item.value for item in Channel),
    "objectives": frozenset(item.value for item in Objective),
    "awareness": frozenset(item.value for item in AwarenessStage),
    "tones": frozenset(item.value for item in Tone),
}
PATTERN_FIELDS = frozenset(
    {
        "id",
        "library",
        "mechanism",
        "objectives",
        "channels",
        "awareness_stages",
        "tones",
        "template",
        "slots",
        "explanation",
        "intensity",
    }
)


@dataclass(frozen=True)
class Pattern:
    id: str
    library: str
    mechanism: str
    objectives: tuple[str, ...]
    channels: tuple[str, ...]
    awareness_stages: tuple[str, ...]
    tones: tuple[str, ...]
    template: str
    slots: tuple[str, ...]
    explanation: str
    intensity: int


class HookLibrary:
    """Biblioteca validada e imutável de padrões originais."""

    def __init__(
        self,
        patterns: tuple[Pattern, ...],
        mechanisms: tuple[str, ...],
        taxonomies: Mapping[str, tuple[str, ...]],
    ) -> None:
        self._all_patterns = patterns
        self._mechanisms = mechanisms
        self._taxonomies = MappingProxyType(dict(taxonomies))
        self._by_id = MappingProxyType({pattern.id: pattern for pattern in patterns})

    @property
    def all_patterns(self) -> tuple[Pattern, ...]:
        return self._all_patterns

    @property
    def mechanisms(self) -> tuple[str, ...]:
        return self._mechanisms

    @property
    def taxonomies(self) -> Mapping[str, tuple[str, ...]]:
        return self._taxonomies

    @classmethod
    def load_default(cls) -> "HookLibrary":
        data_root = Path(__file__).resolve().parents[3] / "data"
        return cls.load(data_root)

    @classmethod
    def load(cls, data_root: str | Path) -> "HookLibrary":
        root = Path(data_root)
        taxonomies = cls._load_taxonomies(root)
        mechanisms = cls._load_mechanisms(root)
        patterns: list[Pattern] = []
        seen_ids: set[str] = set()
        seen_templates: dict[str, str] = {}
        for library in LIBRARIES:
            relative = f"{library}/patterns.json"
            records = cls._read_json(root, relative)
            if not isinstance(records, list):
                cls._invalid(relative, "<arquivo>", "estrutura", "deve ser uma lista")
            for record in records:
                pattern = cls._parse_pattern(
                    record,
                    relative,
                    library,
                    mechanisms,
                    taxonomies,
                )
                if pattern.id in seen_ids:
                    cls._invalid(relative, pattern.id, "id", "ID duplicado globalmente")
                normalized = cls._normalize_template(pattern.template)
                if normalized in seen_templates:
                    other = seen_templates[normalized]
                    cls._invalid(
                        relative,
                        pattern.id,
                        "template",
                        f"template duplicado de {other}",
                    )
                seen_ids.add(pattern.id)
                seen_templates[normalized] = pattern.id
                patterns.append(pattern)
        return cls(tuple(sorted(patterns, key=lambda item: item.id)), mechanisms, taxonomies)

    @classmethod
    def _load_taxonomies(cls, root: Path) -> dict[str, tuple[str, ...]]:
        result: dict[str, tuple[str, ...]] = {}
        for name, filename in TAXONOMY_FILES.items():
            relative = f"taxonomies/{filename}"
            records = cls._read_json(root, relative)
            ids = cls._parse_entries(records, relative)
            expected = EXPECTED_ENUMS[name]
            if set(ids) != expected:
                cls._invalid(
                    relative,
                    "<arquivo>",
                    "id",
                    f"IDs devem corresponder aos enums: {sorted(expected)}",
                )
            result[name] = ids
        return result

    @classmethod
    def _load_mechanisms(cls, root: Path) -> tuple[str, ...]:
        relative = "universal/mechanisms.json"
        ids = cls._parse_entries(cls._read_json(root, relative), relative)
        if len(ids) != 20:
            cls._invalid(relative, "<arquivo>", "id", "deve conter exatamente 20 mecanismos")
        return ids

    @classmethod
    def _parse_entries(cls, records: Any, relative: str) -> tuple[str, ...]:
        if not isinstance(records, list):
            cls._invalid(relative, "<arquivo>", "estrutura", "deve ser uma lista")
        ids: list[str] = []
        for index, record in enumerate(records):
            item_id = (
                record.get("id", f"índice-{index}")
                if isinstance(record, dict)
                else f"índice-{index}"
            )
            if not isinstance(record, dict) or set(record) != {"id", "label", "description"}:
                cls._invalid(relative, item_id, "estrutura", "requer id, label e description")
            for field in ("id", "label", "description"):
                if not isinstance(record[field], str) or not record[field].strip():
                    cls._invalid(relative, item_id, field, "deve ser texto não vazio")
            if item_id in ids:
                cls._invalid(relative, item_id, "id", "ID duplicado")
            ids.append(item_id)
        return tuple(ids)

    @classmethod
    def _parse_pattern(
        cls,
        record: Any,
        relative: str,
        expected_library: str,
        mechanisms: tuple[str, ...],
        taxonomies: Mapping[str, tuple[str, ...]],
    ) -> Pattern:
        item_id = (
            record.get("id", "<desconhecido>") if isinstance(record, dict) else "<desconhecido>"
        )
        if not isinstance(record, dict):
            cls._invalid(relative, item_id, "estrutura", "pattern deve ser um objeto")
        missing = PATTERN_FIELDS - set(record)
        extra = set(record) - PATTERN_FIELDS
        if missing or extra:
            cls._invalid(
                relative,
                item_id,
                "estrutura",
                f"campos ausentes={sorted(missing)} extras={sorted(extra)}",
            )
        if not isinstance(item_id, str) or not item_id.startswith(
            "universal-" if expected_library == "universal" else "ivs-"
        ):
            cls._invalid(relative, str(item_id), "id", "prefixo incompatível com a biblioteca")
        if record["library"] != expected_library:
            cls._invalid(relative, item_id, "library", f"deve ser {expected_library}")
        if record["mechanism"] not in mechanisms:
            cls._invalid(relative, item_id, "mechanism", "mecanismo desconhecido")

        references = {
            "objectives": "objectives",
            "channels": "channels",
            "awareness_stages": "awareness",
            "tones": "tones",
        }
        converted: dict[str, tuple[str, ...]] = {}
        for field, taxonomy in references.items():
            value = record[field]
            if (
                not isinstance(value, list)
                or not value
                or any(not isinstance(item, str) for item in value)
            ):
                cls._invalid(relative, item_id, field, "deve ser lista não vazia de strings")
            if len(value) != len(set(value)):
                cls._invalid(relative, item_id, field, "não permite referências repetidas")
            unknown = set(value) - set(taxonomies[taxonomy])
            if unknown:
                cls._invalid(
                    relative, item_id, field, f"referências desconhecidas: {sorted(unknown)}"
                )
            converted[field] = tuple(value)

        template = record["template"]
        if not isinstance(template, str) or not 20 <= len(template) <= 280:
            cls._invalid(relative, item_id, "template", "comprimento deve estar entre 20 e 280")
        try:
            actual_slots = tuple(
                field_name
                for _, field_name, _, _ in string.Formatter().parse(template)
                if field_name is not None
            )
        except ValueError as error:
            cls._invalid(relative, item_id, "template", f"placeholders inválidos: {error}")
        declared_slots = record["slots"]
        if not isinstance(declared_slots, list) or not declared_slots:
            cls._invalid(relative, item_id, "slots", "deve ser lista não vazia")
        unknown_slots = (set(actual_slots) | set(declared_slots)) - ALLOWED_SLOTS
        if unknown_slots:
            cls._invalid(
                relative, item_id, "slots", f"slots desconhecidos: {sorted(unknown_slots)}"
            )
        if tuple(declared_slots) != actual_slots:
            cls._invalid(
                relative, item_id, "slots", f"declarados {declared_slots}, extraídos {actual_slots}"
            )
        explanation = record["explanation"]
        if not isinstance(explanation, str) or len(explanation) < 40:
            cls._invalid(relative, item_id, "explanation", "comprimento mínimo é 40")
        intensity = record["intensity"]
        if not isinstance(intensity, int) or isinstance(intensity, bool) or not 1 <= intensity <= 3:
            cls._invalid(relative, item_id, "intensity", "deve ser inteiro entre 1 e 3")
        return Pattern(
            id=item_id,
            library=expected_library,
            mechanism=record["mechanism"],
            objectives=converted["objectives"],
            channels=converted["channels"],
            awareness_stages=converted["awareness_stages"],
            tones=converted["tones"],
            template=template,
            slots=actual_slots,
            explanation=explanation,
            intensity=intensity,
        )

    @staticmethod
    def _normalize_template(template: str) -> str:
        return "".join(character for character in template.casefold() if character.isalnum())

    @classmethod
    def _read_json(cls, root: Path, relative: str) -> Any:
        path = root / relative
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            cls._invalid(relative, "<arquivo>", "json", str(error))

    @staticmethod
    def _invalid(relative: str, item_id: str, field: str, detail: str) -> NoReturn:
        raise ValueError(f"{relative} | id={item_id} | campo={field}: {detail}")

    def patterns(self, library: str) -> tuple[Pattern, ...]:
        if library not in LIBRARIES:
            raise ValueError(f"library desconhecida: {library}")
        return tuple(pattern for pattern in self._all_patterns if pattern.library == library)

    def get(self, pattern_id: str) -> Pattern | None:
        return self._by_id.get(pattern_id)

    def filter(
        self,
        *,
        library: str | None = None,
        channel: str | None = None,
        objective: str | None = None,
        awareness_stage: str | None = None,
        tone: str | None = None,
        mechanism: str | None = None,
        max_intensity: int | None = None,
    ) -> tuple[Pattern, ...]:
        return tuple(
            pattern
            for pattern in self._all_patterns
            if (library is None or pattern.library == library)
            and (channel is None or channel in pattern.channels)
            and (objective is None or objective in pattern.objectives)
            and (awareness_stage is None or awareness_stage in pattern.awareness_stages)
            and (tone is None or tone in pattern.tones)
            and (mechanism is None or pattern.mechanism == mechanism)
            and (max_intensity is None or pattern.intensity <= max_intensity)
        )
