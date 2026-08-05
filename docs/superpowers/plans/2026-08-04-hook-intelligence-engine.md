# Hook Intelligence Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Construir um módulo web autônomo do Content Engine OS que gere, pontue, explique, filtre e exporte hooks originais usando biblioteca universal e módulo IVS, com operação determinística e adaptação opcional por IA.

**Architecture:** O módulo viverá exclusivamente em `modules/hook-intelligence/`, com FastAPI no backend, Next.js no frontend e SQLite como persistência local. O motor será uma pipeline de unidades puras — seleção, composição, deduplicação, score, compliance e ranking — e a integração futura ocorrerá apenas por API ou contratos JSON Schema.

**Tech Stack:** Python 3.11, FastAPI, Pydantic 2, SQLAlchemy 2, SQLite, pytest, httpx, Next.js 15, TypeScript, React, Vitest, Playwright, Docker Compose, JSON Schema.

---

## File map

```text
modules/hook-intelligence/
├── README.md                         # instalação, execução e limites
├── SPEC.md                           # cópia operacional da especificação aprovada
├── HANDOFF-CLAUDE-CODE.md            # contrato de integração posterior
├── .env.example                      # configuração sem segredos
├── compose.yaml                      # stack isolada
├── contracts/                        # contratos externos versionados
├── data/                             # datasets curados e taxonomias
├── backend/
│   ├── pyproject.toml                # dependências e ferramentas Python
│   ├── hook_intelligence/
│   │   ├── api/                      # aplicação e rotas FastAPI
│   │   ├── domain/                   # modelos de domínio
│   │   ├── engine/                   # pipeline de geração
│   │   ├── adapters/                 # IA opcional
│   │   └── storage/                  # SQLite e repositórios
│   └── tests/                        # unit, contract e integration
├── web/
│   ├── app/                          # páginas Next.js
│   ├── components/                   # formulário e resultados
│   ├── lib/                          # cliente API e tipos
│   └── tests/                        # Vitest e Playwright
└── evidence/                         # outputs reais de validação
```

## Task 1: Scaffold isolado e healthcheck da API

**Files:**
- Create: `modules/hook-intelligence/backend/pyproject.toml`
- Create: `modules/hook-intelligence/backend/hook_intelligence/__init__.py`
- Create: `modules/hook-intelligence/backend/hook_intelligence/api/main.py`
- Create: `modules/hook-intelligence/backend/tests/test_health.py`
- Create: `modules/hook-intelligence/.env.example`

- [x] **Step 1: Escrever o teste de healthcheck**

```python
from fastapi.testclient import TestClient
from hook_intelligence.api.main import app


def test_health_returns_versioned_ready_status():
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "service": "hook-intelligence",
        "version": "0.1.0",
        "ai_enabled": False,
    }
```

- [x] **Step 2: Configurar o projeto Python**

```toml
[project]
name = "hook-intelligence"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
  "fastapi>=0.116,<1",
  "uvicorn[standard]>=0.35,<1",
  "pydantic>=2.11,<3",
  "sqlalchemy>=2.0,<3",
  "httpx>=0.28,<1",
  "jsonschema>=4.25,<5"
]

[project.optional-dependencies]
dev = ["pytest>=8.4,<9", "pytest-cov>=6.2,<7", "ruff>=0.12,<1"]

[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]

[tool.ruff]
line-length = 100
```

- [x] **Step 3: Rodar o teste e confirmar RED**

Run: `cd modules/hook-intelligence/backend && uv sync --extra dev && uv run pytest tests/test_health.py -q`

Expected: FAIL porque `hook_intelligence.api.main` ainda não existe.

- [x] **Step 4: Implementar o app mínimo**

```python
from fastapi import FastAPI

app = FastAPI(title="Hook Intelligence Engine", version="0.1.0")


@app.get("/health")
def health() -> dict[str, object]:
    return {
        "status": "ready",
        "service": "hook-intelligence",
        "version": "0.1.0",
        "ai_enabled": False,
    }
```

- [x] **Step 5: Rodar teste e lint**

Run: `uv run pytest tests/test_health.py -q && uv run ruff check hook_intelligence tests`

Expected: `1 passed` e `All checks passed!`.

- [x] **Step 6: Commit**

```bash
git add modules/hook-intelligence
git commit -m "feat(hooks): scaffold isolated FastAPI module"
```

## Task 2: Contratos e modelos de domínio

**Files:**
- Create: `modules/hook-intelligence/contracts/hook.schema.json`
- Create: `modules/hook-intelligence/contracts/generation-request.schema.json`
- Create: `modules/hook-intelligence/contracts/generation-response.schema.json`
- Create: `modules/hook-intelligence/contracts/content-os-export.schema.json`
- Create: `modules/hook-intelligence/backend/hook_intelligence/domain/models.py`
- Create: `modules/hook-intelligence/backend/tests/contract/test_contracts.py`

- [x] **Step 1: Escrever testes de contrato**

```python
import json
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).parents[3]


def load(name: str) -> dict:
    return json.loads((ROOT / "contracts" / name).read_text())


def test_all_contracts_are_valid_draft_2020_12():
    for name in (
        "hook.schema.json",
        "generation-request.schema.json",
        "generation-response.schema.json",
        "content-os-export.schema.json",
    ):
        Draft202012Validator.check_schema(load(name))


def test_generation_request_requires_topic_channel_objective_and_audience():
    schema = load("generation-request.schema.json")
    assert set(schema["required"]) == {"topic", "channel", "objective", "audience"}
```

- [x] **Step 2: Criar os modelos Pydantic**

```python
from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class ComplianceStatus(StrEnum):
    PASS = "pass"
    REVIEW = "review"
    BLOCK = "block"


class HookScores(BaseModel):
    clarity: float = Field(ge=0, le=100)
    specificity: float = Field(ge=0, le=100)
    novelty: float = Field(ge=0, le=100)
    retention: float = Field(ge=0, le=100)
    channel_fit: float = Field(ge=0, le=100)
    overall: float = Field(ge=0, le=100)


class ComplianceResult(BaseModel):
    status: ComplianceStatus
    reasons: list[str] = []


class Hook(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    text: str = Field(min_length=3, max_length=280)
    language: str = "pt-BR"
    library: str
    pattern_id: str
    mechanisms: list[str]
    objective: str
    channel: str
    awareness_stage: str = "problem_aware"
    audience: str
    topic: str
    tone: str = "premium"
    scores: HookScores
    compliance: ComplianceResult
    explanation: str
    source: str
    engine_version: str = "0.1.0"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class GenerationRequest(BaseModel):
    topic: str = Field(min_length=2, max_length=300)
    channel: str
    objective: str
    audience: str = Field(min_length=2, max_length=300)
    library: str = "universal"
    awareness_stage: str = "problem_aware"
    tone: str = "premium"
    intensity: int = Field(default=2, ge=1, le=3)
    mechanism: str | None = None
    context: str = Field(default="", max_length=4000)
    required_words: list[str] = []
    forbidden_words: list[str] = []
    count: int = Field(default=12, ge=1, le=50)
    max_length: int = Field(default=180, ge=30, le=280)
    use_ai: bool = False
```

- [x] **Step 3: Criar JSON Schemas equivalentes**

Cada schema deverá declarar `"$schema": "https://json-schema.org/draft/2020-12/schema"`, `additionalProperties: false`, enums para campos taxonômicos e limites iguais aos modelos Pydantic. `generation-response.schema.json` deve exigir `request_id`, `hooks`, `warnings`, `engine_version` e `duration_ms`. `content-os-export.schema.json` deve exigir `schema_version`, `workspace_ref`, `generated_at` e `hooks`.

- [x] **Step 4: Rodar contratos e modelos**

Run: `uv run pytest tests/contract/test_contracts.py -q`

Expected: `2 passed`.

- [x] **Step 5: Commit**

```bash
git add modules/hook-intelligence/contracts modules/hook-intelligence/backend
git commit -m "feat(hooks): define versioned generation contracts"
```

## Task 3: Datasets curados e carregador validado

**Files:**
- Create: `modules/hook-intelligence/data/taxonomies/*.json`
- Create: `modules/hook-intelligence/data/universal/patterns.json`
- Create: `modules/hook-intelligence/data/universal/mechanisms.json`
- Create: `modules/hook-intelligence/data/ivs-health/patterns.json`
- Create: `modules/hook-intelligence/data/ivs-health/forbidden-claims.json`
- Create: `modules/hook-intelligence/backend/hook_intelligence/engine/library.py`
- Create: `modules/hook-intelligence/backend/tests/unit/test_library.py`

- [x] **Step 1: Escrever testes do carregador**

```python
from hook_intelligence.engine.library import HookLibrary


def test_library_loads_universal_and_ivs_patterns():
    library = HookLibrary.load_default()
    assert len(library.patterns("universal")) >= 40
    assert len(library.patterns("ivs-health")) >= 20
    assert len({p.id for p in library.all_patterns}) == len(library.all_patterns)


def test_every_pattern_has_slots_and_explanation():
    library = HookLibrary.load_default()
    assert all(p.template and "{" in p.template for p in library.all_patterns)
    assert all(p.mechanism and p.explanation for p in library.all_patterns)
```

- [x] **Step 2: Definir formato dos padrões**

```json
{
  "id": "curiosity-hidden-cause-01",
  "library": "universal",
  "mechanism": "curiosity_gap",
  "objectives": ["retention", "curiosity"],
  "channels": ["reel", "ad", "carousel"],
  "awareness_stages": ["problem_aware", "solution_aware"],
  "template": "O que quase ninguém percebe sobre {topic} — e por que isso muda {desired_outcome}",
  "explanation": "Abre uma lacuna de informação e promete uma consequência concreta sem entregar a resposta no primeiro segundo.",
  "intensity": 2
}
```

- [x] **Step 3: Criar biblioteca original**

Criar pelo menos 40 estruturas universais distribuídas pelos 20 mecanismos da especificação e 20 estruturas `ivs-health`. Cada estrutura deve ser semanticamente distinta, possuir explicação e evitar promessas clínicas. Criar taxonomias explícitas para canais, objetivos, consciência e tons.

- [x] **Step 4: Implementar carregador tipado**

```python
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Pattern:
    id: str
    library: str
    mechanism: str
    objectives: tuple[str, ...]
    channels: tuple[str, ...]
    awareness_stages: tuple[str, ...]
    template: str
    explanation: str
    intensity: int


class HookLibrary:
    def __init__(self, patterns: list[Pattern]):
        self.all_patterns = patterns

    @classmethod
    def load_default(cls) -> "HookLibrary":
        root = Path(__file__).parents[4] / "data"
        rows = []
        for file in (root / "universal" / "patterns.json", root / "ivs-health" / "patterns.json"):
            rows.extend(json.loads(file.read_text(encoding="utf-8")))
        return cls([Pattern(**{**row, "objectives": tuple(row["objectives"]), "channels": tuple(row["channels"]), "awareness_stages": tuple(row["awareness_stages"])}) for row in rows])

    def patterns(self, library: str) -> list[Pattern]:
        return [p for p in self.all_patterns if p.library == library]
```

- [x] **Step 5: Rodar testes e validação de JSON**

Run: `uv run pytest tests/unit/test_library.py -q && python -m json.tool ../data/universal/patterns.json >/dev/null && python -m json.tool ../data/ivs-health/patterns.json >/dev/null`

Expected: testes verdes e JSON válido.

- [x] **Step 6: Commit**

```bash
git add modules/hook-intelligence/data modules/hook-intelligence/backend
git commit -m "feat(hooks): add original universal and IVS libraries"
```

## Task 4: Motor determinístico de seleção e composição

**Files:**
- Create: `modules/hook-intelligence/backend/hook_intelligence/engine/selector.py`
- Create: `modules/hook-intelligence/backend/hook_intelligence/engine/composer.py`
- Create: `modules/hook-intelligence/backend/tests/unit/test_generation.py`

- [x] **Step 1: Escrever testes RED**

```python
from hook_intelligence.domain.models import GenerationRequest
from hook_intelligence.engine.pipeline import generate_deterministic


def test_generation_returns_requested_unique_count():
    request = GenerationRequest(topic="qualidade do sono", channel="reel", objective="retention", audience="mulheres acima de 40", count=12)
    hooks = generate_deterministic(request)
    assert len(hooks) == 12
    assert len({h.text.casefold() for h in hooks}) == 12


def test_required_and_forbidden_words_are_enforced():
    request = GenerationRequest(topic="energia", channel="carousel", objective="education", audience="empreendedores", required_words=["rotina"], forbidden_words=["milagre"], count=8)
    hooks = generate_deterministic(request)
    assert all("rotina" in h.text.casefold() for h in hooks)
    assert all("milagre" not in h.text.casefold() for h in hooks)
```

- [x] **Step 2: Implementar seleção determinística estável**

O seletor deve filtrar por biblioteca, canal, objetivo, consciência, mecanismo e intensidade. O ranking inicial deve ser estável usando `sha256` de `topic + audience + pattern_id`, permitindo reprodução da mesma requisição.

```python
from hashlib import sha256


def stable_rank(seed: str, pattern_id: str) -> str:
    return sha256(f"{seed}:{pattern_id}".encode()).hexdigest()
```

- [x] **Step 3: Implementar composição segura**

O compositor deverá preencher apenas slots conhecidos (`topic`, `audience`, `desired_outcome`, `context`, `required_word`), normalizar espaços, limitar comprimento sem cortar palavras e rejeitar template com slot desconhecido.

- [x] **Step 4: Criar `engine/pipeline.py` e rodar testes**

Run: `uv run pytest tests/unit/test_generation.py -q`

Expected: `2 passed`.

- [x] **Step 5: Commit**

```bash
git add modules/hook-intelligence/backend
git commit -m "feat(hooks): generate deterministic contextual hooks"
```

## Task 5: Deduplicação, score, explicação e ranking

**Files:**
- Create: `modules/hook-intelligence/backend/hook_intelligence/engine/deduplicator.py`
- Create: `modules/hook-intelligence/backend/hook_intelligence/engine/scorer.py`
- Create: `modules/hook-intelligence/backend/hook_intelligence/engine/explain.py`
- Create: `modules/hook-intelligence/backend/tests/unit/test_quality.py`

- [x] **Step 1: Escrever testes de qualidade**

```python
from hook_intelligence.engine.deduplicator import deduplicate
from hook_intelligence.engine.scorer import score_text


def test_near_duplicates_are_removed():
    rows = ["O erro que trava seu sono", "O erro que está travando o seu sono", "Três hábitos noturnos que drenam sua energia"]
    assert deduplicate(rows, threshold=0.82) == [rows[0], rows[2]]


def test_score_is_bounded_and_penalizes_generic_text():
    specific = score_text("3 hábitos após as 20h que fragmentam seu sono", "reel", "sono")
    generic = score_text("Você precisa saber disso", "reel", "sono")
    assert 0 <= specific.overall <= 100
    assert specific.overall > generic.overall
```

- [x] **Step 2: Implementar similaridade local**

Usar normalização Unicode, tokens e coeficiente de Sørensen-Dice. Não adicionar modelo de embeddings nesta fase.

- [x] **Step 3: Implementar scores determinísticos**

Compor o score geral com pesos: clareza 25%, especificidade 25%, novidade heurística 15%, retenção 20% e adequação ao canal 15%. Registrar penalidades por clichês, caixa alta excessiva, pontuação exagerada, ausência do tópico e comprimento inadequado.

- [x] **Step 4: Anexar explicação do padrão e penalidades**

Cada hook deve informar mecanismo, motivo do score e recomendações curtas sem revelar raciocínio interno privado.

- [x] **Step 5: Rodar testes**

Run: `uv run pytest tests/unit/test_quality.py -q`

Expected: `2 passed`.

- [x] **Step 6: Commit**

```bash
git add modules/hook-intelligence/backend
git commit -m "feat(hooks): score explain and deduplicate candidates"
```

## Task 6: Compliance médico IVS

**Files:**
- Create: `modules/hook-intelligence/backend/hook_intelligence/engine/compliance.py`
- Create: `modules/hook-intelligence/backend/tests/unit/test_compliance.py`
- Modify: `modules/hook-intelligence/data/ivs-health/forbidden-claims.json`

- [x] **Step 1: Escrever fixtures de pass, review e block**

```python
import pytest
from hook_intelligence.engine.compliance import evaluate_compliance


@pytest.mark.parametrize("text", [
    "Você vai perder 10 kg em 30 dias",
    "Cure a obesidade definitivamente",
    "Este tratamento funciona para todas as pacientes",
])
def test_blocks_guarantees_and_cures(text):
    result = evaluate_compliance(text, "ivs-health")
    assert result.status == "block"


def test_reviews_unsourced_clinical_number():
    result = evaluate_compliance("Este método reduz 37% da gordura", "ivs-health")
    assert result.status == "review"


def test_passes_educational_non_diagnostic_hook():
    result = evaluate_compliance("Por que o sono pode influenciar suas escolhas alimentares?", "ivs-health")
    assert result.status == "pass"
```

- [x] **Step 2: Implementar regras versionadas**

As regras devem reconhecer garantias, cura, diagnóstico direto, prescrição, falsa urgência, humilhação, número clínico sem fonte e superioridade absoluta. O retorno deve conter códigos estáveis, por exemplo `GUARANTEED_RESULT`, `CURE_CLAIM`, `DIRECT_DIAGNOSIS` e `UNSOURCED_CLINICAL_NUMBER`.

- [x] **Step 3: Integrar compliance antes e depois da IA**

Hooks bloqueados não entram no ranking nem no export. Hooks em revisão permanecem visíveis com alerta.

- [x] **Step 4: Rodar suíte**

Run: `uv run pytest tests/unit/test_compliance.py -q`

Expected: `5 passed`.

- [x] **Step 5: Commit**

```bash
git add modules/hook-intelligence
git commit -m "feat(hooks): enforce IVS medical compliance gates"
```

## Task 7: Persistência, favoritos, histórico e exportação

**Files:**
- Create: `modules/hook-intelligence/backend/hook_intelligence/storage/database.py`
- Create: `modules/hook-intelligence/backend/hook_intelligence/storage/repositories.py`
- Create: `modules/hook-intelligence/backend/hook_intelligence/engine/exporter.py`
- Create: `modules/hook-intelligence/backend/tests/integration/test_storage_export.py`

- [x] **Step 1: Escrever teste de ciclo persistido**

```python
import json
from hook_intelligence.storage.database import create_database
from hook_intelligence.storage.repositories import HookRepository


def test_history_favorite_and_export_roundtrip(tmp_path, sample_hook):
    db = create_database(f"sqlite:///{tmp_path}/hooks.db")
    repo = HookRepository(db)
    session_id = repo.save_generation([sample_hook])
    repo.favorite(sample_hook.id)
    payload = repo.export_session(session_id, workspace_ref="ivs-internal")
    assert payload["schema_version"] == "1.0.0"
    assert payload["workspace_ref"] == "ivs-internal"
    assert payload["hooks"][0]["favorite"] is True
    json.dumps(payload)
```

- [x] **Step 2: Criar tabelas mínimas**

Tabelas: `generation_sessions`, `hooks`, `favorites`. Usar UUID textual, timestamps UTC e JSON para scores/compliance. Ativar foreign keys no SQLite.

- [x] **Step 3: Implementar repositórios e exportadores**

Implementar listagem paginada, favorito idempotente, export JSON validado pelo contrato e CSV UTF-8 com cabeçalho fixo.

- [x] **Step 4: Rodar integração**

Run: `uv run pytest tests/integration/test_storage_export.py -q`

Expected: `1 passed`.

- [x] **Step 5: Commit**

```bash
git add modules/hook-intelligence/backend
git commit -m "feat(hooks): persist history favorites and exports"
```

## Task 8: Adaptador de IA opcional e fallback

**Files:**
- Create: `modules/hook-intelligence/backend/hook_intelligence/adapters/base.py`
- Create: `modules/hook-intelligence/backend/hook_intelligence/adapters/disabled.py`
- Create: `modules/hook-intelligence/backend/hook_intelligence/adapters/openai_compatible.py`
- Create: `modules/hook-intelligence/backend/tests/unit/test_ai_adapter.py`

- [x] **Step 1: Escrever teste com transporte falso**

```python
from hook_intelligence.adapters.openai_compatible import OpenAICompatibleAdapter


class FakeTransport:
    def post(self, **kwargs):
        return {"hooks": ["O detalhe invisível que muda sua relação com o sono"]}


def test_adapter_returns_structured_candidates_without_logging_secret(caplog):
    adapter = OpenAICompatibleAdapter(api_key="secret-test", model="test-model", transport=FakeTransport())
    result = adapter.adapt(topic="sono", candidates=["O que você não sabe sobre sono"])
    assert len(result) == 1
    assert "secret-test" not in caplog.text


def test_pipeline_falls_back_when_provider_times_out(monkeypatch):
    adapter = OpenAICompatibleAdapter(api_key="x", model="test", transport=TimeoutTransport())
    result = adapter.adapt_or_fallback(topic="sono", candidates=["Hook determinístico"])
    assert result == ["Hook determinístico"]
```

- [x] **Step 2: Definir protocolo**

```python
from typing import Protocol


class HookAdapter(Protocol):
    def adapt(self, topic: str, candidates: list[str]) -> list[str]: ...
```

- [x] **Step 3: Implementar cliente OpenAI-compatible**

Usar endpoint configurável, timeout de 20 segundos, uma repetição apenas para falha transitória, JSON estruturado, limite de tokens e nenhuma impressão da chave. Se `HOOK_AI_ENABLED=false`, usar `DisabledAdapter` e não realizar rede.

- [x] **Step 4: Revalidar saídas de IA**

Após adaptação: normalizar, deduplicar, pontuar e executar compliance novamente. Respostas malformadas devem cair no fallback determinístico.

- [x] **Step 5: Rodar testes**

Run: `uv run pytest tests/unit/test_ai_adapter.py -q`

Expected: `2 passed`.

- [x] **Step 6: Commit**

```bash
git add modules/hook-intelligence/backend modules/hook-intelligence/.env.example
git commit -m "feat(hooks): add optional AI adaptation with safe fallback"
```

## Task 9: API versionada completa

**Files:**
- Create: `modules/hook-intelligence/backend/hook_intelligence/api/schemas.py`
- Create: `modules/hook-intelligence/backend/hook_intelligence/api/routes/*.py`
- Modify: `modules/hook-intelligence/backend/hook_intelligence/api/main.py`
- Create: `modules/hook-intelligence/backend/tests/integration/test_api.py`

- [x] **Step 1: Escrever testes de API**

```python
def test_generate_returns_ranked_hooks(client):
    response = client.post("/v1/hooks/generate", json={"topic": "sono", "channel": "reel", "objective": "retention", "audience": "mulheres 40+", "library": "ivs-health", "count": 5})
    assert response.status_code == 200
    body = response.json()
    assert len(body["hooks"]) == 5
    assert body["hooks"] == sorted(body["hooks"], key=lambda row: row["scores"]["overall"], reverse=True)


def test_invalid_count_returns_422(client):
    response = client.post("/v1/hooks/generate", json={"topic": "sono", "channel": "reel", "objective": "retention", "audience": "adultos", "count": 51})
    assert response.status_code == 422
```

- [x] **Step 2: Implementar endpoints**

Implementar exatamente: `GET /health`, `GET /v1/taxonomies`, `GET /v1/patterns`, `POST /v1/hooks/generate`, `POST /v1/hooks/score`, `POST /v1/hooks/compliance`, `POST /v1/hooks/{id}/favorite`, `GET /v1/history`, `GET /v1/favorites`, `POST /v1/exports/content-os`.

- [x] **Step 3: Adicionar request ID e duração**

Toda resposta de geração deve incluir UUID, versão do motor, duração em milissegundos e warnings sanitizados.

- [x] **Step 4: Rodar testes e conferir OpenAPI**

Run: `uv run pytest tests/integration/test_api.py -q && uv run python -c "from hook_intelligence.api.main import app; assert '/v1/hooks/generate' in app.openapi()['paths']"`

Expected: testes verdes e exit code 0.

- [x] **Step 5: Commit**

```bash
git add modules/hook-intelligence/backend
git commit -m "feat(hooks): expose versioned generation API"
```

## Task 10: Aplicativo Next.js

**Files:**
- Create: `modules/hook-intelligence/web/package.json`
- Create: `modules/hook-intelligence/web/app/layout.tsx`
- Create: `modules/hook-intelligence/web/app/page.tsx`
- Create: `modules/hook-intelligence/web/app/library/page.tsx`
- Create: `modules/hook-intelligence/web/app/saved/page.tsx`
- Create: `modules/hook-intelligence/web/components/GeneratorForm.tsx`
- Create: `modules/hook-intelligence/web/components/HookCard.tsx`
- Create: `modules/hook-intelligence/web/components/ComparisonTray.tsx`
- Create: `modules/hook-intelligence/web/lib/api.ts`
- Create: `modules/hook-intelligence/web/tests/generator.test.tsx`

- [x] **Step 1: Criar teste de interface RED**

```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import GeneratorPage from '../app/page';

it('collects the briefing and renders ranked hooks', async () => {
  render(<GeneratorPage />);
  await userEvent.type(screen.getByLabelText('Tema'), 'qualidade do sono');
  await userEvent.type(screen.getByLabelText('Público'), 'mulheres acima de 40');
  await userEvent.click(screen.getByRole('button', { name: 'Gerar hooks' }));
  expect(await screen.findByText(/score geral/i)).toBeInTheDocument();
});
```

- [x] **Step 2: Configurar Next.js e testes**

Usar Next.js App Router, TypeScript strict, ESLint, Vitest, Testing Library e CSS Modules ou tokens locais. Não importar CSS/componentes do Content OS principal.

- [x] **Step 3: Implementar tela Gerador**

Campos: tema, público, biblioteca, canal, objetivo, consciência, tom, intensidade, mecanismo, contexto, palavras obrigatórias/proibidas, quantidade e toggle de IA. Estados obrigatórios: vazio, carregando, erro recuperável e resultados.

- [x] **Step 4: Implementar cards e comparação**

Cada card mostra hook, score geral, dimensões, mecanismo, explicação, compliance, copiar, favoritar, adaptar e comparar. Impedir seleção de hook bloqueado.

- [x] **Step 5: Implementar Biblioteca e Salvos**

Biblioteca com busca e filtros; Salvos com abas histórico/favoritos e exportação em lote.

- [x] **Step 6: Rodar testes, lint e build**

Run: `cd modules/hook-intelligence/web && npm ci && npm test -- --run && npm run lint && npm run build`

Expected: testes, lint e build verdes.

- [x] **Step 7: Commit**

```bash
git add modules/hook-intelligence/web
git commit -m "feat(hooks): add standalone hook generator web app"
```

## Task 11: Docker Compose, integração e e2e

**Files:**
- Create: `modules/hook-intelligence/backend/Dockerfile`
- Create: `modules/hook-intelligence/web/Dockerfile`
- Create: `modules/hook-intelligence/compose.yaml`
- Create: `modules/hook-intelligence/web/tests/e2e/generator.spec.ts`
- Create: `modules/hook-intelligence/scripts/smoke.sh`

- [x] **Step 1: Escrever e2e**

```ts
import { test, expect } from '@playwright/test';

test('generate, compare, favorite and export', async ({ page }) => {
  await page.goto('/');
  await page.getByLabel('Tema').fill('qualidade do sono');
  await page.getByLabel('Público').fill('mulheres acima de 40');
  await page.getByRole('button', { name: 'Gerar hooks' }).click();
  await expect(page.getByTestId('hook-card')).toHaveCount(12);
  await page.getByRole('button', { name: 'Comparar' }).first().click();
  await page.getByRole('button', { name: 'Favoritar' }).first().click();
  await expect(page.getByText('1 selecionado')).toBeVisible();
});
```

- [x] **Step 2: Criar containers isolados**

API na porta interna 8000, web na 3000, volume próprio `hook_intelligence_data`, rede própria e healthchecks. Não reutilizar Postgres, Redis ou Nginx do Content OS.

- [x] **Step 3: Criar smoke determinístico**

```bash
#!/usr/bin/env bash
set -euo pipefail
curl -fsS http://127.0.0.1:18082/health | python3 -c 'import json,sys; d=json.load(sys.stdin); assert d["status"]=="ready"'
curl -fsS -X POST http://127.0.0.1:18082/v1/hooks/generate \
  -H 'content-type: application/json' \
  -d '{"topic":"sono","channel":"reel","objective":"retention","audience":"mulheres 40+","library":"ivs-health","count":5}' \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); assert len(d["hooks"])==5'
```

- [x] **Step 4: Subir stack e executar smoke/e2e**

Run: `docker compose -f modules/hook-intelligence/compose.yaml up -d --build && bash modules/hook-intelligence/scripts/smoke.sh && cd modules/hook-intelligence/web && npx playwright test`

Expected: healthcheck 200, geração com 5 hooks e e2e verde.

- [x] **Step 5: Commit**

```bash
git add modules/hook-intelligence
git commit -m "test(hooks): add isolated stack smoke and e2e"
```

## Task 12: Documentação, handoff e evidência final

**Files:**
- Create: `modules/hook-intelligence/README.md`
- Create: `modules/hook-intelligence/SPEC.md`
- Create: `modules/hook-intelligence/HANDOFF-CLAUDE-CODE.md`
- Create: `modules/hook-intelligence/evidence/verification.md`
- Modify: `modules/hook-intelligence/.env.example`

- [x] **Step 1: Documentar instalação e operação**

O README deve cobrir: requisitos, execução local, Docker Compose, testes, configuração sem IA, adaptador OpenAI-compatible, contratos, exportação, limites, troubleshooting e rollback.

- [x] **Step 2: Criar handoff exato para Claude Code**

O handoff deve mapear API, schemas, portas, persistência, variáveis, migração SQLite→Postgres, incorporação das páginas no Next.js principal, autenticação futura e responsabilidades que devem permanecer isoladas. Deve declarar que nenhuma integração já foi feita.

- [x] **Step 3: Executar gate completo**

Run:

```bash
cd modules/hook-intelligence/backend
uv run pytest --cov=hook_intelligence --cov-report=term-missing
uv run ruff check hook_intelligence tests
cd ../web
npm test -- --run
npm run lint
npm run build
cd ..
docker compose up -d --build
bash scripts/smoke.sh
```

Expected: todos os comandos com exit code 0.

- [x] **Step 4: Scan de segredos e isolamento**

Run:

```bash
! git grep -nEi '(api[_-]?key|token|secret)\s*[:=]\s*["'"'][^"'"']{8,}' -- modules/hook-intelligence
! git diff d00c92b --name-only | grep -v '^modules/hook-intelligence/' | grep .
```

Expected: nenhum segredo e nenhum arquivo fora do módulo, exceto este plano/documentação de design já aprovada.

- [x] **Step 5: Registrar evidência real**

`evidence/verification.md` deve conter data, commit, comandos, resultados, endpoints, quantidade de padrões, cobertura, screenshots do QA visual, limitações e rollback.

- [x] **Step 6: Commit final**

```bash
git add modules/hook-intelligence docs/superpowers/plans/2026-08-04-hook-intelligence-engine.md
git commit -m "docs(hooks): complete standalone module handoff"
```

## Final acceptance checklist

- [x] Módulo existe somente em `modules/hook-intelligence/`.
- [x] API responde 200 em `/health`.
- [x] Geração determinística funciona sem rede.
- [x] Biblioteca universal tem no mínimo 40 padrões originais.
- [x] Biblioteca IVS tem no mínimo 20 padrões originais.
- [x] 12 hooks padrão são únicos e ranqueados.
- [x] IA é opcional e possui fallback comprovado.
- [x] Compliance bloqueia garantias, cura e diagnóstico direto.
- [x] Histórico, favoritos e exports funcionam.
- [x] JSON exportado valida contra contrato.
- [x] Web passa testes, lint e build.
- [x] Docker smoke e Playwright passam.
- [x] QA visual não encontra quebra de layout.
- [x] Scan de segredos passa.
- [x] `HANDOFF-CLAUDE-CODE.md` permite integração posterior sem reconstrução.
- [x] Nenhum comportamento do Content Engine OS existente foi alterado.
