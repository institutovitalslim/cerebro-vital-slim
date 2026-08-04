import httpx
import pytest

import hook_intelligence.adapters.openai_compatible as adapter_module
from hook_intelligence.adapters import DisabledAdapter, OpenAICompatible, adapter_from_env
from hook_intelligence.adapters.base import AdapterError
from hook_intelligence.domain.models import GenerationRequest, Source
from hook_intelligence.engine.library import HookLibrary
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


def _assert_public_exception_is_detached(error, *secrets):
    assert error.__cause__ is None
    assert error.__context__ is None
    exposed = f"{error!s} {error!r}"
    assert all(secret not in exposed for secret in secrets)


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


def test_sensitive_transport_decode_and_endpoint_errors_are_fully_detached():
    class SensitiveTimeoutTransport:
        def __init__(self):
            self.calls = 0

        def post(self, **kwargs):
            self.calls += 1
            raise httpx.TimeoutException(
                "PROVIDER_BODY_SECRET endpoint=https://x/?token=QUERY_SECRET"
            )

    transport = SensitiveTimeoutTransport()
    with pytest.raises(AdapterError) as caught:
        OpenAICompatible("KEY_SECRET", "model", transport=transport).adapt("tema", ["original"])
    assert transport.calls == 2
    _assert_public_exception_is_detached(
        caught.value, "PROVIDER_BODY_SECRET", "QUERY_SECRET", "KEY_SECRET"
    )

    class SensitiveDecoderResponse:
        status_code = 200

        def json(self):
            raise RuntimeError("PROVIDER_BODY_SECRET")

    with pytest.raises(AdapterError) as caught:
        OpenAICompatible("KEY_SECRET", "model")._decode(SensitiveDecoderResponse(), 1)
    _assert_public_exception_is_detached(caught.value, "PROVIDER_BODY_SECRET", "KEY_SECRET")

    with pytest.raises(AdapterError) as caught:
        OpenAICompatible("KEY_SECRET", "model", endpoint="https://[invalid/?token=QUERY_SECRET")
    _assert_public_exception_is_detached(caught.value, "QUERY_SECRET", "KEY_SECRET")


class RaiseForStatusTransport:
    def __init__(self, statuses):
        self.statuses = list(statuses)
        self.calls = 0

    def post(self, **kwargs):
        self.calls += 1
        status = self.statuses.pop(0)
        if status == 200:
            return Response({"hooks": ["Hook seguro"]})

        class RaiseForStatusResponse:
            status_code = None

            def raise_for_status(self):
                request = httpx.Request("POST", "https://provider.test/?token=QUERY_SECRET")
                response = httpx.Response(status, request=request, content=b"PROVIDER_BODY_SECRET")
                raise httpx.HTTPStatusError(
                    "PROVIDER_BODY_SECRET", request=request, response=response
                )

        return RaiseForStatusResponse()


def test_raise_for_status_uses_safe_status_for_retry_policy():
    recovered = RaiseForStatusTransport([503, 200])
    assert OpenAICompatible("KEY_SECRET", "model", transport=recovered).adapt(
        "tema", ["original"]
    ) == ["Hook seguro"]
    assert recovered.calls == 2

    exhausted = RaiseForStatusTransport([503, 503])
    with pytest.raises(AdapterError) as caught:
        OpenAICompatible("KEY_SECRET", "model", transport=exhausted).adapt("tema", ["original"])
    assert exhausted.calls == 2
    _assert_public_exception_is_detached(
        caught.value, "PROVIDER_BODY_SECRET", "QUERY_SECRET", "KEY_SECRET"
    )

    permanent = RaiseForStatusTransport([400])
    with pytest.raises(AdapterError) as caught:
        OpenAICompatible("KEY_SECRET", "model", transport=permanent).adapt("tema", ["original"])
    assert permanent.calls == 1
    _assert_public_exception_is_detached(
        caught.value, "PROVIDER_BODY_SECRET", "QUERY_SECRET", "KEY_SECRET"
    )


def test_raw_hook_limits_are_checked_before_any_normalization(monkeypatch):
    normalize_calls = 0
    original_normalize = adapter_module.unicodedata.normalize

    def counted_normalize(form, value):
        nonlocal normalize_calls
        normalize_calls += 1
        return original_normalize(form, value)

    monkeypatch.setattr(adapter_module.unicodedata, "normalize", counted_normalize)
    adapter = OpenAICompatible("key", "model", transport=FakeTransport({}))

    huge = " " * 1_000_000 + "ABC" + " " * 1_000_000
    with pytest.raises(AdapterError, match="limite"):
        adapter._decode({"hooks": [huge]}, 1)
    assert normalize_calls == 0

    over_total = ["A" * 4096 for _ in range(25)]
    with pytest.raises(AdapterError, match="limite total"):
        adapter._decode({"hooks": over_total}, len(over_total))
    assert normalize_calls == 0

    original = ["Hook original"]
    fallback_adapter = OpenAICompatible("key", "model", transport=FakeTransport({"hooks": [huge]}))
    fallback = fallback_adapter.adapt_or_fallback("tema", original)
    assert fallback == original
    assert fallback is not original


@pytest.mark.parametrize(
    "api_key",
    ["", " key", "key ", "ke y", "key\r\nInjected: yes", "key\tvalue", "key\x00", "key\ufeff"],
)
def test_invalid_api_keys_are_rejected_before_transport(api_key):
    transport = FakeTransport({"hooks": ["Hook seguro"]})
    with pytest.raises(AdapterError) as caught:
        OpenAICompatible(api_key, "model", transport=transport)
    assert transport.calls == []
    if api_key:
        assert api_key not in str(caught.value)


def test_oversized_api_key_is_rejected_without_disclosure():
    key = "K" * (adapter_module.MAX_API_KEY_CHARS + 1)
    with pytest.raises(AdapterError) as caught:
        OpenAICompatible(key, "model")
    assert key not in str(caught.value)


@pytest.mark.parametrize("library_name", ["universal", "ivs-health"])
def test_pipeline_resolves_default_library_once_for_valid_ai(monkeypatch, library_name):
    original_load = HookLibrary.load_default
    provided_library = original_load()
    calls = 0

    def counted_load(cls):
        nonlocal calls
        calls += 1
        return original_load()

    monkeypatch.setattr(HookLibrary, "load_default", classmethod(counted_load))
    result = generate_with_optional_ai(_request(library=library_name), adapter=SpyAdapter())
    assert calls == 1
    assert all(hook.source is Source.AI_ADAPTED for hook in result)

    calls = 0
    fallback = generate_with_optional_ai(
        _request(library=library_name), adapter=SpyAdapter(error=RuntimeError("falha"))
    )
    assert calls == 1
    assert all(hook.source is Source.DETERMINISTIC for hook in fallback)

    calls = 0
    disabled = generate_with_optional_ai(_request(use_ai=False, library=library_name))
    assert calls == 1
    assert all(hook.source is Source.DETERMINISTIC for hook in disabled)

    calls = 0
    provided = generate_with_optional_ai(
        _request(library=library_name), library=provided_library, adapter=SpyAdapter()
    )
    assert calls == 0
    assert all(hook.source is Source.AI_ADAPTED for hook in provided)
