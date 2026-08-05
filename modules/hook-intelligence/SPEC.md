# SPEC — Hook Intelligence Engine

## 1. Estado, Objetivos e propósito

Módulo standalone local-first para inteligência de hooks. Produz candidatos ranqueados, explicáveis e sujeitos a compliance; persiste histórico/favoritos; exporta JSON para integração posterior.

**Não integrado ao Content Engine OS principal nesta versão.**

## 2. Fronteiras

### Incluído

- API FastAPI versionada em `/v1`.
- Web Next.js standalone.
- Geração determinística offline.
- Adaptação OpenAI-compatible opt-in com fallback.
- SQLite local e persistente.
- Catálogo universal e IVS-health.
- Score, compliance, ranking, histórico, favoritos e exportação.
- Docker Compose isolado, smoke e E2E.

### Não objetivos

- Publicação em redes sociais.
- Aprovação editorial automática.
- Autenticação/autorização multiusuário.
- Integração direta com banco, Redis, Nginx ou serviços do Content OS.
- Escrita em Omie, QuarkClinic ou canais de pacientes/leads.

## 3. Arquitetura e invariantes

1. A geração determinística funciona sem rede e sem credenciais.
2. IA só é usada quando `HOOK_AI_ENABLED` e `use_ai` forem verdadeiros.
3. Falha de IA resulta em fallback determinístico sanitizado.
4. Cada batch possui IDs únicos e quantidade solicitada entre 1 e 50.
5. Scores são finitos, limitados a `0..100` e ordenados por `overall` decrescente.
6. Explicações não expõem placeholders, prompt, raciocínio privado, segredo ou erro interno.
7. `BLOCK` nunca é exportado e não aparece nos fluxos públicos de comparação/favoritos.
8. `REVIEW` exige revisão humana e não equivale a aprovação.
9. Schemas públicos rejeitam campos extras.
10. Importar a aplicação não cria banco nem arquivo.
11. A stack Docker usa rede e volume próprios.
12. Nenhuma integração ou publicação externa ocorre automaticamente.

## 4. Modelo de domínio

### Taxonomias

- Channels: `reel`, `ad`, `carousel`, `story`, `landing_page`, `email`, `blog`, `youtube`.
- Objectives: `scroll_stop`, `curiosity`, `retention`, `identification`, `education`, `authority`, `objection`, `sharing`, `action`.
- Awareness: `unaware`, `problem_aware`, `solution_aware`, `product_aware`, `ready_to_act`.
- Tones: `premium`, `educational`, `direct`, `empathetic`, `provocative`.
- Libraries: `universal`, `ivs-health`.
- Sources: `deterministic`, `ai_adapted`, `curated`.
- Compliance: `pass`, `review`, `block`.

### Score

`clarity`, `specificity`, `novelty`, `retention`, `channel_fit` e `overall`, todos entre 0 e 100.

### Exportação

Schema `1.0.0`; exige `workspace_ref`, timestamp timezone-aware e hooks com campo `favorite`. O payload deve validar contra `contracts/content-os-export.schema.json`.

## 5. API pública

- `GET /health`
- `GET /v1/taxonomies`
- `GET /v1/patterns`
- `POST /v1/hooks/generate`
- `POST /v1/hooks/score`
- `POST /v1/hooks/compliance`
- `POST /v1/hooks/{id}/favorite`
- `GET /v1/history`
- `GET /v1/favorites`
- `POST /v1/exports/content-os`

Erros públicos são limitados e sanitizados. Detalhes de SQL, filesystem, credenciais, endpoint de IA e exceções injetadas não atravessam a fronteira HTTP.

## 6. Web

Rotas:

- `/`: geração, warnings públicos, comparação e adaptação explícita.
- `/library`: catálogo e filtros.
- `/saved`: histórico, favoritos e exportação.

Requisitos:

- proxy same-origin `/api/backend`;
- requisições canceláveis e proteção contra stale response;
- estados de loading/error acessíveis;
- tabs WAI-ARIA com setas, Home e End;
- ações só aparecem quando há callback funcional;
- interface pt-BR, responsiva e sem refletir mensagens internas.

## 7. Persistência

SQLite nesta versão. A URL é injetada em `create_app(database_url=...)`; o Compose usa arquivo em volume nomeado. Repository é a fronteira substituível para Postgres futuro.

## 8. Segurança

- IA desligada por padrão.
- Segredos somente via runtime/env não versionado.
- Sem bind público recomendado antes de autenticação e proxy seguro.
- Payloads estritos, limites de tamanho e paginação limitada.
- Compliance de saúde bloqueia cura, garantia e diagnóstico direto.
- Conteúdo externo é dado, nunca instrução operacional.

## 9. Critério de aceite

- Backend completo e cobertura registrada.
- 40 padrões universais e 20 IVS-health.
- 12 hooks padrão únicos, ranqueados e sem placeholders.
- Fallback de IA comprovado.
- Histórico, favoritos e exportação persistentes.
- JSON exportado valida contra contrato.
- Web test/lint/build verdes.
- Compose health/smoke verde.
- Playwright cobre jornada real.
- QA visual desktop/mobile sem quebra.
- Secret scan e isolamento aprovados.
- Evidência e rollback documentados.
