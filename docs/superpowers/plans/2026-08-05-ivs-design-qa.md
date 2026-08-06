# IVS Design QA Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Entregar uma porta única de QA para HTML de sites e apresentações IVS com bloqueio determinístico, evidência desktop/mobile e preservação do original.

**Architecture:** Uma CLI Python coordena verificações estáticas, integrações opcionais já existentes e um probe Playwright/Chromium em Node. O resultado é agregado em JSON/HTML redigidos, sem publicação e sem sobrescrever a entrada.

**Tech Stack:** Python 3.11 stdlib/unittest, Node 22, `playwright-core@1.62.1`, Chromium do sistema, `ivs-site`, `ivs-visual-layer`.

---

### Task 1: Contrato e scanner estático

**Files:**
- Create: `skills/ivs-design-qa/scripts/static_checks.py`
- Create: `skills/ivs-design-qa/tests/test_static_checks.py`

- [x] Criar teste que exige bloqueios por placeholder, ausência de viewport e PII em modo anônimo.
- [x] Rodar `python3 -m unittest skills/ivs-design-qa/tests/test_static_checks.py -v` e confirmar falha por módulo ausente.
- [x] Implementar `scan_html(path, artifact_type, data_mode)` retornando hash, blockers, concerns e métricas redigidas.
- [x] Rodar o teste específico e a suíte.

### Task 2: Probe real de navegador

**Files:**
- Create: `skills/ivs-design-qa/package.json`
- Create: `skills/ivs-design-qa/scripts/browser_probe.mjs`
- Create: `skills/ivs-design-qa/tests/test_browser_probe.py`

- [x] Criar teste de integração com HTML saudável e HTML com overflow.
- [x] Rodar e confirmar falha por probe ausente.
- [x] Instalar dependência exata com `npm install --ignore-scripts`.
- [x] Implementar duas viewports, captura de console/pageerror, imagens quebradas, overflow e screenshots.
- [x] Rodar integração e confirmar que o saudável passa e o overflow bloqueia.

### Task 3: Integrações governadas

**Files:**
- Create: `skills/ivs-design-qa/scripts/integrations.py`
- Create: `skills/ivs-design-qa/tests/test_integrations.py`

- [x] Criar testes de subprocesso para parser de `ivs-site` e Visual Layer.
- [x] Confirmar RED.
- [x] Implementar adaptadores com timeout, paths configuráveis e falha redigida.
- [x] Confirmar GREEN sem tocar no original.

### Task 4: CLI e relatórios

**Files:**
- Create: `skills/ivs-design-qa/scripts/reporting.py`
- Create: `skills/ivs-design-qa/scripts/ivs_design_qa.py`
- Create: `skills/ivs-design-qa/tests/test_cli.py`
- Create: `skills/ivs-design-qa/SKILL.md`

- [x] Criar teste end-to-end para estados, exit code, JSON/HTML e SHA imutável.
- [x] Confirmar RED.
- [x] Implementar agregação fail-closed e relatórios sem conteúdo da página.
- [x] Confirmar GREEN e `py_compile`.

### Task 5: Pilotos e fechamento

**Files:**
- Create: `skills/ivs-design-qa/fixtures/landing-piloto.html`
- Create: `skills/ivs-design-qa/fixtures/apresentacao-anonima-piloto.html`
- Create: `skills/ivs-design-qa/SKILL.md`

- [x] Criar os dois HTMLs completos, responsivos, sintéticos e sem links externos.
- [x] Executar o gate nos dois artefatos.
- [x] Verificar screenshots visualmente, console, overflow, hashes e redaction.
- [x] Rodar `python3 -m unittest discover -s skills/ivs-design-qa/tests -v`, testes do Visual Layer, `git diff --check` e busca de segredos.
- [ ] Commitar, fazer push da branch e registrar evidência real.
