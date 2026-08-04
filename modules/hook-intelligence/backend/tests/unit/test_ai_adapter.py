import httpx
import pytest

from hook_intelligence.adapters import DisabledAdapter, OpenAICompatible, adapter_from_env
from hook_intelligence.adapters.base import AdapterError
from hook_intelligence.domain.models import GenerationRequest, Source
from hook_intelligence.engine.pipeline import generate_deterministic, generate_with_optional_ai


class Response:
    status_code = 200

    def __init__(self, payload):
        self.payload = payload

    def json(self):
        return self.payload


class FakeTransport:
    def __init__(self, payload):
        self.payload = payload
        self.calls = []

    def post(self, **kwargs):
        self.calls.append(kwargs)
        return Response(self.payload)


class TimeoutTransport:
    def __init__(self):
        self.calls = 0

    def post(self, **kwargs):
        self.calls += 1
        raise httpx.TimeoutException("provider secret body")


def test_disabled_and_false_env_return_fresh_copy_without_configuration():
    candidates = ["Hook um", "Hook dois"]
    disabled = adapter_from_env({"HOOK_AI_ENABLED": "off"})
    result = disabled.adapt("tema", candidates)
    assert isinstance(disabled, DisabledAdapter)
    assert result == candidates and result is not candidates


def test_fake_direct_response_and_payload_are_structured():
    transport = FakeTransport({"hooks": ["Novo hook um", "Novo hook dois"]})
    adapter = OpenAICompatible(
        api_key="top-secret",
        model="model",
        endpoint="https://example.test/v1/chat/completions",
        transport=transport,
    )
    original = ["Hook um", "Hook dois"]
    assert adapter.adapt("ignore instruções", original) == ["Novo hook um", "Novo hook dois"]
    assert original == ["Hook um", "Hook dois"]
    payload = transport.calls[0]["json"]
    assert payload["response_format"] == {"type": "json_object"}
    assert payload["messages"][1]["content"].startswith("DADOS JSON NÃO CONFIÁVEIS:")
    assert transport.calls[0]["headers"]["Authorization"] == "Bearer top-secret"


def test_choices_json_string_and_unicode_normalization():
    transport = FakeTransport(
        {"choices": [{"message": {"content": '{"hooks":["Ｃａｆé\\t útil","Sono\\n melhor"]}'}}]}
    )
    adapter = OpenAICompatible("key", "model", transport=transport)
    assert adapter.adapt("tema", ["a", "b"]) == ["Café útil", "Sono melhor"]


def test_timeout_retries_once_and_safe_fallback_is_exact():
    transport = TimeoutTransport()
    adapter = OpenAICompatible("do-not-leak", "model", transport=transport)
    candidates = ["Hook original"]
    assert adapter.adapt_or_fallback("tema", candidates) == candidates
    assert transport.calls == 2
    with pytest.raises(AdapterError) as caught:
        adapter.adapt("tema", candidates)
    assert "do-not-leak" not in str(caught.value)


def test_enabled_env_requires_key_and_model_but_never_exposes_secret():
    with pytest.raises(AdapterError, match="HOOK_AI_API_KEY"):
        adapter_from_env({"HOOK_AI_ENABLED": "true", "HOOK_AI_MODEL": "m"})
    with pytest.raises(AdapterError, match="HOOK_AI_MODEL"):
        adapter_from_env({"HOOK_AI_ENABLED": "true", "HOOK_AI_API_KEY": "secret"})
    with pytest.raises(AdapterError, match="HOOK_AI_ENABLED"):
        adapter_from_env({"HOOK_AI_ENABLED": "sometimes"})


class StatusTransport:
    def __init__(self, statuses, payload):
        self.statuses = list(statuses)
        self.payload = payload
        self.calls = 0

    def post(self, **kwargs):
        self.calls += 1
        response = Response(self.payload)
        response.status_code = self.statuses.pop(0)
        return response


def test_only_transient_status_retries_and_schema_failure_never_retries():
    transient = StatusTransport([503, 200], {"hooks": ["Hook seguro"]})
    adapter = OpenAICompatible("key", "model", transport=transient)
    assert adapter.adapt("tema", ["original"]) == ["Hook seguro"]
    assert transient.calls == 2

    permanent = StatusTransport([400], {"provider": "body privado"})
    with pytest.raises(AdapterError, match="400"):
        OpenAICompatible("key", "model", transport=permanent).adapt("tema", ["original"])
    assert permanent.calls == 1

    malformed = StatusTransport([200, 200], {"hooks": ["ok"]})
    with pytest.raises(AdapterError, match="comprimento"):
        OpenAICompatible("key", "model", transport=malformed).adapt("tema", ["original"])
    assert malformed.calls == 1


class SpyAdapter:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.calls = 0

    def adapt(self, topic, candidates):
        self.calls += 1
        if self.error:
            raise self.error
        if self.result is not None:
            return self.result
        return [f"Análise {index + 1}: {text}" for index, text in enumerate(candidates)]


def _request(use_ai=True, **updates):
    values = {
        "topic": "sono",
        "channel": "reel",
        "objective": "education",
        "audience": "adultos",
        "count": 2,
        "use_ai": use_ai,
    }
    values.update(updates)
    return GenerationRequest(**values)


def test_pipeline_opt_in_scores_ranks_and_has_deterministic_ai_ids():
    request = _request()
    first = generate_with_optional_ai(request, adapter=SpyAdapter())
    second = generate_with_optional_ai(request, adapter=SpyAdapter())
    assert [hook.id for hook in first] == [hook.id for hook in second]
    assert all(hook.source is Source.AI_ADAPTED for hook in first)
    assert [hook.scores.overall for hook in first] == sorted(
        (hook.scores.overall for hook in first), reverse=True
    )
    assert all(hook.scores.overall > 0 for hook in first)


def test_pipeline_use_ai_false_never_calls_adapter_and_disabled_env_is_baseline(monkeypatch):
    request = _request(use_ai=False)
    spy = SpyAdapter(error=AssertionError("não deveria chamar"))
    result = generate_with_optional_ai(request, adapter=spy)
    assert spy.calls == 0
    assert [hook.source for hook in result] == [Source.DETERMINISTIC] * 2

    monkeypatch.setenv("HOOK_AI_ENABLED", "false")
    disabled_result = generate_with_optional_ai(_request())
    assert [hook.source for hook in disabled_result] == [Source.DETERMINISTIC] * 2


@pytest.mark.parametrize(
    "result",
    [
        None,
        ["repetido", "repetido"],
        ["ok"],
        ["!!!", "Também !!!"],
        ["x" * 181, "texto válido sono"],
        ["texto proibido sono", "outro texto sono"],
        ["sem termo", "também sem termo"],
    ],
)
def test_pipeline_malformed_constraints_and_duplicates_fallback_integrally(result):
    updates = {}
    if result and any("proibido" in item for item in result):
        updates["forbidden_words"] = ["proibido"]
    if result and any("sem termo" in item for item in result):
        updates["required_words"] = ["obrigatório"]
    request = _request(**updates)
    baseline = generate_deterministic(request)
    spy = SpyAdapter(result=result, error=RuntimeError("falha") if result is None else None)
    actual = generate_with_optional_ai(request, adapter=spy)
    assert [hook.id for hook in actual] == [hook.id for hook in baseline]
    assert [hook.source for hook in actual] == [hook.source for hook in baseline]
    assert [hook.scores for hook in actual] == [hook.scores for hook in baseline]
