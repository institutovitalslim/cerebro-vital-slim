import json
import re
import string
from collections.abc import Mapping
from dataclasses import dataclass
from itertools import pairwise
from pathlib import Path
from types import MappingProxyType
from typing import Any, NoReturn

from hook_intelligence.domain.models import AwarenessStage, Channel, Objective, Tone

ALLOWED_SLOTS = frozenset({"topic", "audience", "desired_outcome", "context", "required_word"})
LIBRARIES = ("universal", "ivs-health")
# Limites defensivos para regras locais. A Task 6 deve truncar ou rejeitar entradas maiores
# antes de chamar o scanner; o helper também faz essa validação para não depender do caller.
CLAIM_SCAN_MAX_CHARS = 4000
CLAIM_REGEX_MAX_CHARS = 500
REGEX_CONDITIONAL_MARKER = "(?" + "("
EXACT_MECHANISM_IDS = frozenset(
    {
        "curiosity_gap",
        "pattern_interrupt",
        "expectation_contrast",
        "identification",
        "common_mistake",
        "myth_vs_evidence",
        "specificity",
        "authority",
        "status_identity",
        "before_after_tension",
        "avoidable_loss",
        "future_desire",
        "inverted_objection",
        "demonstration",
        "discovery",
        "incomplete_list",
        "editorial_question",
        "open_story",
        "grounded_contrarian",
        "mechanism_reveal",
    }
)
CLAIM_CATEGORY_IDS = frozenset(
    {
        "cure",
        "guarantee",
        "diagnosis",
        "prescription",
        "false_urgency",
        "stigma",
        "unsourced_number",
        "absolute_superiority",
    }
)
PATTERN_ID_RE = re.compile(r"^(universal|ivs)-[a-z0-9]+(?:-[a-z0-9]+)*$")
AUXILIARY_ID_RE = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")
# Tunado nos 60 padrões: 0,82 captura paráfrases quase literais sem confundir estruturas afins.
NEAR_DUPLICATE_DICE_THRESHOLD = 0.82
# Mais longo que templates, o texto editorial admite algum vocabulário comum; 0,72 ainda
# identifica explicações produzidas pela mesma fórmula nos 60 registros revisados.
EXPLANATION_NEAR_DUPLICATE_DICE_THRESHOLD = 0.72
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
        audiences: tuple[Mapping[str, str], ...],
        topics: tuple[Mapping[str, str], ...],
        forbidden_claims: Mapping[str, Any],
        compiled_claim_patterns: tuple[tuple[str, str, re.Pattern[str]], ...],
    ) -> None:
        self._all_patterns = patterns
        self._mechanisms = mechanisms
        self._taxonomies = MappingProxyType(dict(taxonomies))
        self._audiences = audiences
        self._topics = topics
        self._forbidden_claims = forbidden_claims
        self._compiled_claim_patterns = compiled_claim_patterns
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

    @property
    def audiences(self) -> tuple[Mapping[str, str], ...]:
        return self._audiences

    @property
    def topics(self) -> tuple[Mapping[str, str], ...]:
        return self._topics

    @property
    def forbidden_claims(self) -> Mapping[str, Any]:
        return self._forbidden_claims

    @classmethod
    def load_default(cls) -> "HookLibrary":
        return cls.load(Path(__file__).resolve().parents[3] / "data")

    @classmethod
    def load(cls, data_root: str | Path) -> "HookLibrary":
        root = Path(data_root)
        taxonomies = cls._load_taxonomies(root)
        mechanisms = cls._load_mechanisms(root)
        audiences = cls._load_auxiliary_entries(root, "ivs-health/audiences.json", 8)
        topics = cls._load_auxiliary_entries(root, "ivs-health/topics.json", 12)
        forbidden_claims, compiled_claim_patterns = cls._load_forbidden_claims(root)
        patterns: list[Pattern] = []
        seen_ids: set[str] = set()
        seen_templates: dict[str, str] = {}
        seen_template_texts: dict[str, str] = {}
        seen_explanations: dict[str, str] = {}
        seen_explanation_texts: dict[str, str] = {}
        for library in LIBRARIES:
            relative = f"{library}/patterns.json"
            records = cls._read_json(root, relative)
            if not isinstance(records, list):
                cls._invalid(relative, "<arquivo>", "estrutura", "deve ser uma lista")
            for record in records:
                pattern = cls._parse_pattern(record, relative, library, mechanisms, taxonomies)
                if pattern.id in seen_ids:
                    cls._invalid(relative, pattern.id, "id", "ID duplicado globalmente")
                normalized = cls._normalize(pattern.template)
                if normalized in seen_templates:
                    cls._invalid(
                        relative,
                        pattern.id,
                        "template",
                        f"template duplicado de {seen_templates[normalized]}",
                    )
                for other_id, other_text in seen_template_texts.items():
                    score = cls._bigram_dice(pattern.template, other_text)
                    if score >= NEAR_DUPLICATE_DICE_THRESHOLD:
                        cls._invalid(
                            relative,
                            pattern.id,
                            "template",
                            f"template muito similar a {other_id} (Dice={score:.2f})",
                        )
                normalized_explanation = cls._normalize(pattern.explanation)
                if normalized_explanation in seen_explanations:
                    cls._invalid(
                        relative,
                        pattern.id,
                        "explanation",
                        f"explicação duplicada de {seen_explanations[normalized_explanation]}",
                    )
                for other_id, other_text in seen_explanation_texts.items():
                    score = cls._bigram_dice(pattern.explanation, other_text)
                    if score >= EXPLANATION_NEAR_DUPLICATE_DICE_THRESHOLD:
                        cls._invalid(
                            relative,
                            pattern.id,
                            "explanation",
                            f"explicação muito similar a {other_id} (Dice={score:.2f})",
                        )
                seen_ids.add(pattern.id)
                seen_templates[normalized] = pattern.id
                seen_template_texts[pattern.id] = pattern.template
                seen_explanations[normalized_explanation] = pattern.id
                seen_explanation_texts[pattern.id] = pattern.explanation
                patterns.append(pattern)
        cls._validate_coverage(patterns)
        return cls(
            tuple(sorted(patterns, key=lambda item: item.id)),
            mechanisms,
            taxonomies,
            audiences,
            topics,
            forbidden_claims,
            compiled_claim_patterns,
        )

    @classmethod
    def _load_taxonomies(cls, root: Path) -> dict[str, tuple[str, ...]]:
        result = {}
        for name, filename in TAXONOMY_FILES.items():
            relative = f"taxonomies/{filename}"
            ids = cls._parse_entries(cls._read_json(root, relative), relative)
            if set(ids) != EXPECTED_ENUMS[name]:
                cls._invalid(
                    relative,
                    "<arquivo>",
                    "id",
                    f"IDs devem corresponder aos enums: {sorted(EXPECTED_ENUMS[name])}",
                )
            result[name] = ids
        return result

    @classmethod
    def _load_mechanisms(cls, root: Path) -> tuple[str, ...]:
        relative = "universal/mechanisms.json"
        ids = cls._parse_entries(cls._read_json(root, relative), relative)
        if set(ids) != EXACT_MECHANISM_IDS:
            cls._invalid(
                relative,
                "<arquivo>",
                "id",
                f"IDs devem ser exatamente {sorted(EXACT_MECHANISM_IDS)}",
            )
        return ids

    @classmethod
    def _parse_entries(cls, records: Any, relative: str) -> tuple[str, ...]:
        if not isinstance(records, list):
            cls._invalid(relative, "<arquivo>", "estrutura", "deve ser uma lista")
        ids = []
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
    def _load_auxiliary_entries(
        cls, root: Path, relative: str, minimum: int
    ) -> tuple[Mapping[str, str], ...]:
        records = cls._read_json(root, relative)
        ids = cls._parse_entries(records, relative)
        if len(ids) < minimum:
            cls._invalid(relative, "<arquivo>", "estrutura", f"requer ao menos {minimum} itens")
        for record in records:
            if not AUXILIARY_ID_RE.fullmatch(record["id"]):
                cls._invalid(relative, record["id"], "id", "deve ser slug não vazio")
        return tuple(MappingProxyType(dict(record)) for record in records)

    @classmethod
    def _load_forbidden_claims(
        cls, root: Path
    ) -> tuple[Mapping[str, Any], tuple[tuple[str, str, re.Pattern[str]], ...]]:
        relative = "ivs-health/forbidden-claims.json"
        payload = cls._read_json(root, relative)
        if not isinstance(payload, dict) or set(payload) != {"version", "categories"}:
            cls._invalid(relative, "<arquivo>", "estrutura", "requer version e categories")
        if not isinstance(payload["version"], str) or not payload["version"].strip():
            cls._invalid(relative, "<arquivo>", "version", "deve ser texto não vazio")
        categories = payload["categories"]
        if not isinstance(categories, list):
            cls._invalid(relative, "<arquivo>", "categories", "deve ser uma lista")
        immutable = []
        compiled: list[tuple[str, str, re.Pattern[str]]] = []
        fields = {"id", "label", "description", "examples", "patterns"}
        ids: list[str] = []
        for index, category in enumerate(categories):
            item_id: Any = (
                category.get("id", f"índice-{index}")
                if isinstance(category, dict)
                else f"índice-{index}"
            )
            if not isinstance(category, dict):
                cls._invalid(relative, str(item_id), "estrutura", "categoria deve ser um objeto")
            if set(category) != fields:
                cls._invalid(relative, str(item_id), "estrutura", f"requer {sorted(fields)}")
            for field in ("id", "label", "description"):
                if not isinstance(category[field], str) or not category[field].strip():
                    cls._invalid(relative, str(item_id), field, "deve ser texto não vazio")
            item_id = category["id"]
            ids.append(item_id)
            converted = dict(category)
            for field in ("examples", "patterns"):
                values = category[field]
                if (
                    not isinstance(values, list)
                    or not values
                    or any(not isinstance(value, str) or not value.strip() for value in values)
                ):
                    cls._invalid(relative, item_id, field, "deve ser lista não vazia de textos")
                converted[field] = tuple(values)
            for expression in converted["patterns"]:
                cls._validate_claim_regex(relative, item_id, expression)
                try:
                    regex = re.compile(expression, re.IGNORECASE)
                except re.error as error:
                    cls._invalid(relative, item_id, "regex", str(error))
                compiled.append((item_id, expression, regex))
            immutable.append(MappingProxyType(converted))
        if set(ids) != CLAIM_CATEGORY_IDS or len(ids) != len(CLAIM_CATEGORY_IDS):
            cls._invalid(
                relative,
                "<arquivo>",
                "categorias",
                f"IDs devem ser exatamente {sorted(CLAIM_CATEGORY_IDS)}",
            )
        payload_proxy = MappingProxyType(
            {"version": payload["version"], "categories": tuple(immutable)}
        )
        return payload_proxy, tuple(compiled)

    @classmethod
    def _validate_claim_regex(cls, relative: str, item_id: str, expression: str) -> None:
        """Aceita um subset conservador sem executar a expressão não confiável.

        O subset limita tamanho e rejeita quantificação de grupos, backreferences,
        extensões de grupo (salvo ``(?:...)``) e wildcards ilimitados. As regras são
        deliberadamente mais estritas que o motor ``re`` para manter tempo de busca
        previsível.
        """

        reason = None
        if len(expression) > CLAIM_REGEX_MAX_CHARS:
            reason = f"excede {CLAIM_REGEX_MAX_CHARS} caracteres"
        elif "(?P=" in expression or re.search(r"\\[1-9]|\\g<|\\k<", expression):
            reason = "backreference não permitida"
        elif "(?<=" in expression or "(?<!" in expression:
            reason = "lookbehind não permitido"
        elif REGEX_CONDITIONAL_MARKER in expression:
            reason = "condicional não permitido"
        elif re.search(r"\(\?(?!:)", expression):
            reason = "extensão de grupo não permitida; apenas (?:...) é aceito"
        elif re.search(r"(?<!\\)\.(?:\*|\+)", expression):
            reason = "wildcard ilimitado não permitido"
        elif re.search(r"(?<!\\)\)\s*[*+?{]", expression):
            reason = "quantificador aplicado a grupo não permitido"
        if reason is not None:
            cls._invalid(relative, item_id, "pattern", f"{expression}: {reason}")

    @classmethod
    def _validate_coverage(cls, patterns: list[Pattern]) -> None:
        universal = [item for item in patterns if item.library == "universal"]
        ivs = [item for item in patterns if item.library == "ivs-health"]
        if len(universal) < 40:
            cls._invalid("universal/patterns.json", "<arquivo>", "contagem", "requer ao menos 40")
        if len(ivs) < 20:
            cls._invalid("ivs-health/patterns.json", "<arquivo>", "contagem", "requer ao menos 20")
        covered = {item.mechanism for item in universal}
        if covered != EXACT_MECHANISM_IDS:
            cls._invalid(
                "universal/patterns.json",
                "<arquivo>",
                "mechanism",
                f"deve cobrir todos os mecanismos; ausentes={sorted(EXACT_MECHANISM_IDS - covered)}",
            )
        if len({item.mechanism for item in ivs}) < 10:
            cls._invalid(
                "ivs-health/patterns.json",
                "<arquivo>",
                "mechanism",
                "requer ao menos 10 mecanismos distintos",
            )

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
        missing, extra = PATTERN_FIELDS - set(record), set(record) - PATTERN_FIELDS
        if missing or extra:
            cls._invalid(
                relative,
                item_id,
                "estrutura",
                f"campos ausentes={sorted(missing)} extras={sorted(extra)}",
            )
        expected_prefix = "universal" if expected_library == "universal" else "ivs"
        match = PATTERN_ID_RE.fullmatch(item_id) if isinstance(item_id, str) else None
        if not match or match.group(1) != expected_prefix:
            cls._invalid(relative, str(item_id), "id", "formato ou prefixo incompatível")
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
        converted = {}
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
                field for _, field, _, _ in string.Formatter().parse(template) if field is not None
            )
        except ValueError as error:
            cls._invalid(relative, item_id, "template", f"placeholders inválidos: {error}")
        declared_slots = record["slots"]
        if (
            not isinstance(declared_slots, list)
            or not declared_slots
            or any(not isinstance(slot, str) for slot in declared_slots)
        ):
            cls._invalid(relative, item_id, "slots", "deve ser lista não vazia de strings")
        if len(actual_slots) != len(set(actual_slots)) or len(declared_slots) != len(
            set(declared_slots)
        ):
            cls._invalid(relative, item_id, "slots", "não permite slots repetidos")
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
        if not isinstance(explanation, str) or len(explanation.strip()) < 180:
            cls._invalid(relative, item_id, "explanation", "comprimento mínimo é 180")
        if "..." in explanation or "…" in explanation:
            cls._invalid(relative, item_id, "explanation", "não permite reticências")
        sentence_count = len(re.findall(r"[.!?](?:\s|$)", explanation))
        if not 2 <= sentence_count <= 3:
            cls._invalid(relative, item_id, "explanation", "requer duas ou três frases")
        intensity = record["intensity"]
        if not isinstance(intensity, int) or isinstance(intensity, bool) or not 1 <= intensity <= 3:
            cls._invalid(relative, item_id, "intensity", "deve ser inteiro entre 1 e 3")
        return Pattern(
            item_id,
            expected_library,
            record["mechanism"],
            converted["objectives"],
            converted["channels"],
            converted["awareness_stages"],
            converted["tones"],
            template,
            actual_slots,
            explanation,
            intensity,
        )

    @staticmethod
    def _normalize(text: str) -> str:
        return "".join(character for character in text.casefold() if character.isalnum())

    @staticmethod
    def _bigram_dice(left: str, right: str) -> float:
        def bigrams(text: str) -> set[tuple[str, str]]:
            tokens = re.findall(r"[\w{}]+", text.casefold())
            return set(pairwise(tokens))

        left_pairs, right_pairs = bigrams(left), bigrams(right)
        if not left_pairs or not right_pairs:
            return 0.0
        return 2 * len(left_pairs & right_pairs) / (len(left_pairs) + len(right_pairs))

    @classmethod
    def _read_json(cls, root: Path, relative: str) -> Any:
        try:
            return json.loads((root / relative).read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
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
        known_filters = {
            "library": (library, LIBRARIES),
            "channel": (channel, self._taxonomies["channels"]),
            "objective": (objective, self._taxonomies["objectives"]),
            "awareness_stage": (awareness_stage, self._taxonomies["awareness"]),
            "tone": (tone, self._taxonomies["tones"]),
            "mechanism": (mechanism, self._mechanisms),
        }
        for name, (value, allowed) in known_filters.items():
            if value is not None and value not in allowed:
                raise ValueError(f"{name} desconhecido: {value}; permitidos={sorted(allowed)}")
        if max_intensity is not None and (
            not isinstance(max_intensity, int)
            or isinstance(max_intensity, bool)
            or not 1 <= max_intensity <= 3
        ):
            raise ValueError("max_intensity deve ser inteiro entre 1 e 3")
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

    def scan_forbidden_claims(self, text: str) -> tuple[tuple[str, str], ...]:
        """Retorna ``(categoria, pattern)`` em ordem determinística para texto limitado.

        Somente regex validadas e compiladas durante o carregamento são executadas.
        """

        if not isinstance(text, str):
            raise TypeError("texto do scan deve ser str")
        if len(text) > CLAIM_SCAN_MAX_CHARS:
            raise ValueError(f"texto do scan excede {CLAIM_SCAN_MAX_CHARS} caracteres")
        return tuple(
            (category, expression)
            for category, expression, regex in self._compiled_claim_patterns
            if regex.search(text) is not None
        )
