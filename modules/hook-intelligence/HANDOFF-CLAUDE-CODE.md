# HANDOFF — integração futura com Claude Code

## Declaração de estado

O Hook Intelligence Engine está implementado como módulo standalone em `modules/hook-intelligence/`.

**Nenhuma integração com o Next.js principal, banco principal, autenticação, Redis, Nginx, filas ou publicação do Content Engine OS foi realizada.** Este documento descreve a integração futura; não autoriza mudanças automáticas.

## 1. Mapa do módulo

```text
modules/hook-intelligence/
├── backend/                    FastAPI, motor, adapters, storage e testes
├── web/                        Next.js standalone e testes
├── contracts/                  JSON Schemas versionados
├── data/                       bibliotecas e taxonomias
├── scripts/                    smoke operacional
├── compose.yaml                stack isolada
├── README.md                   operação e rollback
├── SPEC.md                     invariantes e critérios
└── evidence/verification.md    evidência do gate final
```

## 2. Contratos de integração

### API

Base versionada: `/v1`.

Rotas centrais:

- geração: `POST /v1/hooks/generate`;
- catálogo: `GET /v1/patterns`, `GET /v1/taxonomies`;
- histórico/favoritos: `GET /v1/history`, `GET /v1/favorites`, `POST /v1/hooks/{id}/favorite`;
- exportação: `POST /v1/exports/content-os`.

Não acople consumidores a modelos Python internos. Use os JSON Schemas em `contracts/` e preserve `schema_version`.

### Proxy web atual

O Next standalone reescreve `/api/backend/:path*` para `HOOK_API_URL`. Ao incorporar páginas ao Next principal, mantenha same-origin e faça o destino ser server-side; nunca exponha chave de IA ao browser.

## 3. Portas e runtime standalone

- API interna: `8000`.
- Web interna: `3000`.
- API externa padrão: `18082`.
- Web externa padrão: `13000`.
- SQLite no container: `/data/hooks.db`.

A porta `18080` não deve ser usada no host IVS porque pertence ao Evolution.

## 4. Variáveis

### Backend

- `HOOK_DATABASE_URL`
- `HOOK_AI_ENABLED`
- `HOOK_AI_ENDPOINT`
- `HOOK_AI_API_KEY`
- `HOOK_AI_MODEL`
- `HOOK_AI_TIMEOUT_SECONDS`
- `HOOK_AI_MAX_TOKENS`

### Web/E2E

- `HOOK_API_URL`
- `HOOK_API_PORT`
- `HOOK_WEB_PORT`
- `PLAYWRIGHT_BASE_URL`

Credenciais devem vir do runtime governado; não mover chave para variável `NEXT_PUBLIC_*`.

## 5. Migração SQLite → Postgres

A migração futura deve ocorrer atrás da interface de repository.

Sequência recomendada:

1. congelar e versionar o schema persistente atual;
2. criar migrations forward/rollback;
3. implementar repository Postgres com a mesma semântica de transação, paginação e idempotência;
4. rodar suíte de storage contra SQLite e Postgres;
5. fazer export/import de uma cópia sanitizada;
6. comparar sessões, hooks, favoritos e timestamps;
7. executar dual-read ou shadow validation antes do corte;
8. trocar `HOOK_DATABASE_URL` somente após backup e gate humano;
9. preservar rollback para SQLite até a reconciliação final.

Não reutilizar tabelas do Content OS sem decisão arquitetural explícita.

## 6. Incorporação no Next.js principal

1. Tratar as páginas standalone como referência funcional, não copiar cegamente.
2. Migrar componentes e tokens visuais para o design system principal.
3. Preservar contratos de `web/lib/types.ts` e cliente cancelável.
4. Implementar autenticação no boundary server-side.
5. Autorizar por workspace/usuário antes de histórico, favoritos e exportação.
6. Manter warnings sanitizados e interface pt-BR.
7. Reexecutar unit, contract, E2E e QA visual dentro do host principal.
8. Só remover o standalone depois de rollback comprovado.

## 7. Autenticação futura

Esta versão não autentica usuários. Antes de qualquer exposição externa:

- colocar API atrás de gateway privado/reverse proxy seguro;
- autenticar sessão no servidor;
- autorizar `workspace_ref` e ownership de sessões/hooks;
- adicionar rate limiting e auditoria;
- impedir IDOR em favoritos/exportações;
- manter CORS fechado/same-origin;
- nunca aceitar identidade apenas de header enviado pelo cliente.

## 8. Responsabilidades que permanecem isoladas

- motor determinístico e bibliotecas;
- compliance e regras de saúde;
- score e explicações públicas;
- contratos JSON versionados;
- adapters de IA opt-in;
- repository e persistência;
- testes de contrato e fallback.

Integração visual não deve mover essas responsabilidades para componentes React.

## 9. Gates antes da integração

- aprovação arquitetural do proprietário do Content OS;
- plano de autenticação/autorização;
- backup e migração de dados;
- contract tests entre consumidor e API;
- E2E no host principal;
- scan de segredos;
- rollback executável;
- aprovação explícita antes de deploy/publicação.

## 10. Verificação e rollback

Consulte `evidence/verification.md` para o baseline standalone. Qualquer integração deve manter ou superar esse baseline. Em falha, reverta rotas/feature flag para o standalone, preserve o banco e valide `/health`, geração, histórico e exportação antes de declarar recuperação.
