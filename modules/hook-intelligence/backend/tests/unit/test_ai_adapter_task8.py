from collections.abc import Mapping

import pytest

import hook_intelligence.adapters.openai_compatible as adapter_module
import hook_intelligence.engine.pipeline as pipeline_module
from hook_intelligence.adapters import OpenAICompatible
from hook_intelligence.adapters.base import AdapterError
from hook_intelligence.domain.models import GenerationRequest


class SafeTransport:
    def __init__(self, response=None):
        self.response = response

    def post(self, **kwargs):
        return self.response


class JsonResponse:
    status_code = 200

    def __init__(self, body):
        self.body = body

    def json(self):
        return self.body


def assert_detached(error, *secrets):
    assert error.__cause__ is None
    assert error.__context__ is None
    public = f"{error!s} {error!r}"
    assert all(secret not in public for secret in secrets)


class ExplodingMapping(Mapping):
    def __iter__(self):
        raise RuntimeError("BODY_SECRET")

    def __len__(self):
        raise RuntimeError("BODY_SECRET")

    def __getitem__(self, key):
        raise RuntimeError("BODY_SECRET")


class EvilResponseKey(str):
    __hash__ = str.__hash__

    def __eq__(self, other):
        raise RuntimeError("BODY_SECRET")


@pytest.mark.parametrize(
    "response",
    [
        type(
            "BadJsonProperty",
            (),
            {
                "status_code": 200,
                "json": property(
                    lambda self: (_ for _ in ()).throw(RuntimeError("Bearer KEY_SECRET"))
                ),
            },
        )(),
        ExplodingMapping(),
        {"choices": ExplodingMapping()},
        {"choices": [ExplodingMapping()]},
    ],
)
def test_malicious_response_objects_are_sanitized_and_fallback_exact(response, caplog):
    adapter = OpenAICompatible("KEY_SECRET", "model", transport=SafeTransport(response))
    original = ["Hook original"]
    with pytest.raises(AdapterError) as caught:
        adapter.adapt("tema", original)
    assert_detached(caught.value, "KEY_SECRET", "BODY_SECRET", "Bearer")
    assert "KEY_SECRET" not in caplog.text
    assert "BODY_SECRET" not in caplog.text
    fallback = adapter.adapt_or_fallback("tema", original)
    assert fallback == original
    assert fallback is not original


@pytest.mark.parametrize(
    "response",
    [
        {EvilResponseKey("hooks"): ["Hook seguro"]},
        {EvilResponseKey("choices"): [{"message": {"content": '{"hooks":["Hook seguro"]}'}}]},
        {"choices": [{EvilResponseKey("message"): {"content": '{"hooks":["Hook seguro"]}'}}]},
        {"choices": [{"message": {EvilResponseKey("content"): '{"hooks":["Hook seguro"]}'}}]},
    ],
    ids=["hooks", "choices", "message", "content"],
)
def test_str_subclass_response_keys_are_rejected_without_lookup(response, caplog):
    adapter = OpenAICompatible("KEY_SECRET", "model", transport=SafeTransport(response))
    original = ["Hook original"]

    with pytest.raises(AdapterError) as caught:
        adapter.adapt("tema", original)

    assert_detached(caught.value, "KEY_SECRET", "BODY_SECRET")
    assert "KEY_SECRET" not in caplog.text
    assert "BODY_SECRET" not in caplog.text
    fallback = adapter.adapt_or_fallback("tema", original)
    assert fallback == original
    assert fallback is not original


def test_deep_choices_json_is_sanitized_and_falls_back():
    content = '{"hooks":' + "[" * 1500 + '"Hook seguro"' + "]" * 1500 + "}"
    response = JsonResponse({"choices": [{"message": {"content": content}}]})
    adapter = OpenAICompatible("KEY_SECRET", "model", transport=SafeTransport(response))
    with pytest.raises(AdapterError) as caught:
        adapter.adapt("tema", ["original"])
    assert_detached(caught.value, "KEY_SECRET")
    assert adapter.adapt_or_fallback("tema", ["original"]) == ["original"]


@pytest.mark.parametrize(
    "endpoint",
    [
        "https://example.test:bad/path",
        "https://example.test:99999/path",
        "https://example.test:0/path",
        "https://example.test/path#frag",
        "https://example.test/a b",
        "https://example.test\\@evil.test/path",
        "https://user%40mail.test:pass@example.test/path",
    ],
)
def test_invalid_endpoint_matrix_is_rejected_without_disclosure(endpoint):
    with pytest.raises(AdapterError) as caught:
        OpenAICompatible("KEY_SECRET", "model", endpoint=endpoint, transport=SafeTransport())
    assert_detached(caught.value, "KEY_SECRET", endpoint, "user%40mail")


@pytest.mark.parametrize(
    "endpoint",
    [
        "http://[::1]:8080/v1/chat/completions",
        "https://münich.example/v1/chat/completions",
    ],
)
def test_valid_ipv6_localhost_and_unicode_https_endpoints(endpoint):
    adapter = OpenAICompatible("key", "model", endpoint=endpoint, transport=SafeTransport())
    assert adapter.endpoint == endpoint


class OddStatusResponse(JsonResponse):
    def __init__(self, status):
        super().__init__({"hooks": ["Hook seguro"]})
        self.status_code = status


class IntSubclass(int):
    pass


@pytest.mark.parametrize("status", [True, IntSubclass(200)])
def test_non_exact_integer_status_is_not_treated_as_absent(status):
    adapter = OpenAICompatible("key", "model", transport=SafeTransport(OddStatusResponse(status)))
    with pytest.raises(AdapterError) as caught:
        adapter.adapt("tema", ["original"])
    assert_detached(caught.value)


@pytest.mark.parametrize("status", [302, 204])
def test_http_status_semantics(status):
    response = OddStatusResponse(status)
    if status == 204:
        response.body = None
    adapter = OpenAICompatible("key", "model", transport=SafeTransport(response))
    with pytest.raises(AdapterError):
        adapter.adapt("tema", ["original"])


def test_owned_client_context_manager_and_close_are_idempotent(monkeypatch):
    class ClientSpy:
        def __init__(self):
            self.closes = 0

        def close(self):
            self.closes += 1

    spy = ClientSpy()
    monkeypatch.setattr(adapter_module.httpx, "Client", lambda: spy)
    with OpenAICompatible("key", "model") as adapter:
        assert adapter is not None
    adapter.close()
    assert spy.closes == 1


def test_injected_transport_is_never_closed():
    class TransportSpy(SafeTransport):
        def __init__(self):
            super().__init__()
            self.closes = 0

        def close(self):
            self.closes += 1

    transport = TransportSpy()
    adapter = OpenAICompatible("key", "model", transport=transport)
    adapter.close()
    adapter.close()
    assert transport.closes == 0


def test_client_creation_and_close_failures_are_detached(monkeypatch):
    def fail_creation():
        raise RuntimeError("CLIENT_CREATION_SECRET")

    monkeypatch.setattr(adapter_module.httpx, "Client", fail_creation)
    with pytest.raises(AdapterError) as caught:
        OpenAICompatible("KEY_SECRET", "model")
    assert_detached(caught.value, "CLIENT_CREATION_SECRET", "KEY_SECRET")

    class BadCloseClient:
        def close(self):
            raise RuntimeError("CLIENT_CLOSE_SECRET")

    monkeypatch.setattr(adapter_module.httpx, "Client", BadCloseClient)
    adapter = OpenAICompatible("KEY_SECRET", "model")
    with pytest.raises(AdapterError) as caught:
        adapter.close()
    assert_detached(caught.value, "CLIENT_CLOSE_SECRET", "KEY_SECRET")
    adapter.close()


def request():
    return GenerationRequest(
        topic="sono",
        channel="reel",
        objective="education",
        audience="adultos",
        count=1,
        use_ai=True,
    )


@pytest.mark.parametrize("mode", ["success", "fallback", "exception"])
def test_pipeline_closes_factory_adapter_exactly_once(monkeypatch, mode):
    class FactoryAdapter(OpenAICompatible):
        def __init__(self):
            super().__init__("key", "model", transport=SafeTransport())
            self.closes = 0

        def adapt(self, topic, candidates):
            if mode == "exception":
                raise RuntimeError("secret")
            if mode == "fallback":
                return ["x"]
            return ["Sono: uma análise útil"]

        def close(self):
            self.closes += 1

    factory_adapter = FactoryAdapter()
    monkeypatch.setattr(pipeline_module, "adapter_from_env", lambda: factory_adapter)
    pipeline_module.generate_with_optional_ai(request())
    assert factory_adapter.closes == 1


def test_pipeline_never_closes_caller_adapter():
    class CallerAdapter:
        def __init__(self):
            self.closes = 0

        def adapt(self, topic, candidates):
            return ["Sono: uma análise útil"]

        def close(self):
            self.closes += 1

    adapter = CallerAdapter()
    pipeline_module.generate_with_optional_ai(request(), adapter=adapter)
    assert adapter.closes == 0
