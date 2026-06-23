# SPEC-CEOS-STORIES-002: Persistência, export e tracking do Stories Engine IVS

## Goal
Fechar a Fase 2 do Stories Engine IVS com story_items persistidos, link de tracking interno, export Telegram/HTML e validação por smoke test.

## Acceptance Criteria
- [x] Ao salvar sequência, cada story do payload vira registro em `story_items`.
- [x] API expõe `GET /stories/sequences/{id}/items`.
- [x] API expõe `GET /stories/sequences/{id}/export?format=telegram|html`.
- [x] Handoff inclui `tracking_url` interno governado.
- [x] `GET /stories/track/{id}` registra clique agregado e redireciona para WhatsApp sem Z-API.
- [x] Smoke dedicado valida items, export, handoff e tracking.

## Scope
- **In scope:** Content Engine OS / Stories Engine, API FastAPI, migration SQL, UI React, smoke.
- **Out of scope:** envio real para paciente, publicação Instagram, escrita Z-API, ingestão automática Meta/Instagram.

## Technical Approach
Modo DDD: preservar módulo existente e adicionar endpoints idempotentes. Tracking armazena evento agregado sem PII explícita. Export gera texto/HTML para João/Maria revisarem antes de publicar.

## Security / Governance
- Tracking não identifica lead.
- Handoff não envia WhatsApp automaticamente.
- `zapi_write=false`, `send_to_patient=false` permanecem no contrato.
- Sem credenciais, tokens ou dados de paciente.

## TRUST 5 Checklist
- [x] **Tested:** py_compile, compileall, build Next, smoke dedicado, smoke geral.
- [x] **Readable:** helpers explícitos para payload, items e export.
- [x] **Unified:** segue padrão do router `stories.py` e UI existente.
- [x] **Secured:** sem PII, sem envio externo automático.
- [x] **Trackable:** spec + migration + commit no cérebro.
