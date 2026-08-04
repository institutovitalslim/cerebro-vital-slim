import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator, FormatChecker
from pydantic import ValidationError
from referencing import Registry, Resource

from hook_intelligence.api.main import app
from hook_intelligence.domain.models import (
    Channel,
    ContentOSExport,
    GenerationRequest,
    GenerationResponse,
    Hook,
    HookScores,
    Objective,
)

CONTRACTS_DIR = Path(__file__).parents[3] / "contracts"
SCHEMA_FILES = (
    "hook.schema.json",
    "generation-request.schema.json",
    "generation-response.schema.json",
    "content-os-export.schema.json",
)


def load_schemas() -> dict[str, dict]:
    return {name: json.loads((CONTRACTS_DIR / name).read_text()) for name in SCHEMA_FILES}


def registry_for(schemas: dict[str, dict]) -> Registry:
    registry = Registry()
    for schema in schemas.values():
        registry = registry.with_resource(schema["$id"], Resource.from_contents(schema))
    return registry


def sample_hook() -> Hook:
    return Hook(
        text="Você sabe por que sua dieta sempre falha?",
        library="universal",
        pattern_id="curiosity-gap",
        mechanisms=["open_loop"],
        objective="curiosity",
        channel="reel",
        audience="mulheres que buscam saúde",
        topic="emagrecimento sustentável",
        scores=HookScores(
            clarity=90,
            specificity=80,
            novelty=75,
            retention=88,
            channel_fit=95,
            overall=86,
        ),
        compliance={"status": "pass"},
        explanation="Abre uma lacuna de curiosidade relevante para a audiência.",
        source="deterministic",
    )


def test_contracts_are_valid_draft_2020_12_schemas():
    for schema in load_schemas().values():
        Draft202012Validator.check_schema(schema)


def test_generation_request_has_exact_required_fields():
    schema = load_schemas()["generation-request.schema.json"]

    assert set(schema["required"]) == {"topic", "channel", "objective", "audience"}


def test_generation_request_minimum_and_list_defaults_are_isolated():
    first = GenerationRequest(
        topic="sono reparador",
        channel="reel",
        objective="education",
        audience="adultos com sono ruim",
    )
    second = GenerationRequest(
        topic="sono reparador",
        channel="reel",
        objective="education",
        audience="adultos com sono ruim",
    )

    assert first.library == "universal"
    assert first.awareness_stage == "problem_aware"
    assert first.tone == "premium"
    assert first.intensity == 2
    assert first.count == 12
    assert first.max_length == 180
    assert first.use_ai is False
    assert first.required_words == []
    assert first.forbidden_words == []
    assert first.required_words is not second.required_words
    assert first.forbidden_words is not second.forbidden_words


def test_pydantic_rejects_generation_count_above_limit():
    with pytest.raises(ValidationError):
        GenerationRequest(
            topic="sono reparador",
            channel="reel",
            objective="education",
            audience="adultos com sono ruim",
            count=51,
        )


def test_pydantic_rejects_score_above_limit():
    with pytest.raises(ValidationError):
        HookScores(
            clarity=101,
            specificity=80,
            novelty=75,
            retention=88,
            channel_fit=95,
            overall=86,
        )


def test_timestamp_defaults_are_utc():
    hook = sample_hook()
    export = ContentOSExport(workspace_ref="content-os/ivs", hooks=[hook])

    assert hook.created_at.utcoffset() == timedelta(0)
    assert export.generated_at.utcoffset() == timedelta(0)


def test_hook_rejects_naive_created_at():
    hook_data = sample_hook().model_dump(exclude={"created_at"})

    with pytest.raises(ValidationError):
        Hook(**hook_data, created_at=datetime(2026, 1, 1))  # noqa: DTZ001


def test_content_os_export_rejects_naive_generated_at():
    with pytest.raises(ValidationError):
        ContentOSExport(
            workspace_ref="content-os/ivs",
            hooks=[sample_hook()],
            generated_at=datetime(2026, 1, 1),  # noqa: DTZ001
        )


def test_utc_timestamps_serialize_with_timezone_designator():
    hook = sample_hook()
    export = ContentOSExport(workspace_ref="content-os/ivs", hooks=[hook])

    hook_timestamp = hook.model_dump(mode="json")["created_at"]
    export_timestamp = export.model_dump(mode="json")["generated_at"]

    assert hook_timestamp.endswith(("Z", "+00:00"))
    assert export_timestamp.endswith(("Z", "+00:00"))


def test_serialized_domain_models_validate_against_contracts_with_local_refs():
    schemas = load_schemas()
    registry = registry_for(schemas)
    request = GenerationRequest(
        topic="emagrecimento sustentável",
        channel=Channel.REEL,
        objective=Objective.EDUCATION,
        audience="mulheres que buscam saúde",
    )
    hook = sample_hook()
    response = GenerationResponse(request_id=hook.id, hooks=[hook], duration_ms=4.2)
    export = ContentOSExport(workspace_ref="content-os/ivs", hooks=[hook])
    instances = {
        "generation-request.schema.json": request.model_dump(mode="json"),
        "hook.schema.json": hook.model_dump(mode="json"),
        "generation-response.schema.json": response.model_dump(mode="json"),
        "content-os-export.schema.json": export.model_dump(mode="json"),
    }

    for schema_name, instance in instances.items():
        Draft202012Validator(
            schemas[schema_name],
            registry=registry,
            format_checker=FormatChecker(),
        ).validate(instance)


def test_health_keeps_exact_payload_and_exposes_explicit_response_schema():
    client = TestClient(app)

    assert client.get("/health").json() == {
        "status": "ready",
        "service": "hook-intelligence",
        "version": "0.1.0",
        "ai_enabled": False,
    }
    health_schema = app.openapi()["paths"]["/health"]["get"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"]
    assert health_schema == {"$ref": "#/components/schemas/HealthResponse"}
