# Integração Hook Intelligence → Content Engine OS

## Arquitetura

- UI integrada ao Next principal:
  - `/hook-intelligence`
  - `/hook-intelligence/biblioteca`
  - `/hook-intelligence/salvos`
- Gateway autenticado no FastAPI principal: `/hook-intelligence/{path}`.
- Serviço isolado interno: `hook-intelligence-api:8000`, sem porta pública no Compose principal.
- Persistência própria em volume `hook_intelligence_data`.

## Segurança

- O navegador nunca recebe `HOOK_INTEGRATION_SECRET` nem acessa o serviço isolado diretamente.
- O gateway extrai `tid` e `uid` exclusivamente da sessão assinada do Content Engine OS.
- Cada chamada interna envia HMAC-SHA256 sobre a sequência canônica:

```text
tenant_id
user_id
timestamp
HTTP_METHOD
/canonical/path
raw_query
sha256(exact_body)
```

- Alterar método, path, query ou qualquer byte do corpo invalida a assinatura.
- O backend rejeita assinatura ausente/inválida e timestamp fora da janela de 300 segundos.
- `standalone` é identificador reservado e não pode ser usado por requests assinados.
- Histórico, hooks, favoritos e exportações são escopados por tenant e usuário.
- Dados SQLite legados ficam no modo explícito `standalone` e não vazam para sessões integradas.
- Gateway usa allowlist fechada, limite de payload de 256 KiB, timeout, sanitização de erros, lifecycle garantido do cliente e validação de host interno.
- Apenas `GET /health` permanece público para readiness; nenhuma rota de dados é pública quando o segredo está configurado.

## Configuração

O Compose principal depende do arquivo local `sistemas/content-engine-os/.env`, que não é versionado. Antes de executar `docker compose`, criar/provisionar esse arquivo pelo runtime governado.

Feature flag — padrão seguro é desligado:

```text
HOOK_INTELLIGENCE_ENABLED=false
```

Para habilitar, definir **ambas** as variáveis no runtime:

```text
HOOK_INTELLIGENCE_ENABLED=true
HOOK_INTEGRATION_SECRET=<provisionar-segredo-forte-no-runtime>
```

O Compose injeta o mesmo valor nos dois serviços. Com a flag desligada, UI e gateway ficam indisponíveis. Com a flag ligada e segredo vazio, o gateway falha fechado em `503`.

## Migração e rollback

A primeira abertura de uma base SQLite legada:

1. cria automaticamente `<database>.pre-multitenant.bak` por meio da API de backup consistente do SQLite;
2. adiciona ownership `tenant_id/user_id` aos dados legados com valor `standalone`;
3. reconstrói favoritos com chave composta;
4. cria explicitamente o índice `ix_hooks_owner_hook_id` mesmo quando as tabelas já existiam.

**Não é seguro fazer rollback apenas da imagem/código antigo contra uma base já migrada.** A versão antiga não conhece ownership e pode ler dados globalmente.

Rollback obrigatório:

1. parar `hook-intelligence-api`;
2. preservar a base migrada para análise;
3. restaurar o arquivo `.pre-multitenant.bak` como base ativa;
4. somente então iniciar a imagem anterior;
5. validar `/health`, histórico e contagem de favoritos em modo standalone.

O teste de migração prova que o backup mantém o schema e os dados pré-migração e que a base migrada contém o índice composto.

## Validação executada

- Backend standalone com `HOOK_INTEGRATION_SECRET` removido: **570 testes aprovados**.
- Ruff: lint e format check aprovados em 48 arquivos.
- API principal: **124 testes aprovados**.
- Gateway focado: **9 testes aprovados**, incluindo lifecycle em rejeição precoce.
- Frontend standalone: **20 testes aprovados**, lint, TypeScript e build aprovados.
- Web principal: TypeScript e build aprovados, **39 rotas**, incluindo as três rotas integradas.
- `npm audit` de produção e completo nos dois frontends: **0 vulnerabilidades**.
- Compose com feature desligada e ligada: `COMPOSE_OFF_ON_OK`.
- E2E autenticado e HMAC completo: **12 hooks**, histórico, favorito, 40 patterns e página final `/hook-intelligence/salvos` — PASS.
- Captura visual: revisão de privacidade PASS; nenhum dado pessoal ou segredo visível.

Evidência visual:

```text
modules/hook-intelligence/evidence/screenshots/integrated-content-os.png
```

## Gate de deploy

Antes de subir o Compose principal:

1. garantir `.env` local governado e backup externo do volume;
2. provisionar flag e segredo no runtime;
3. executar `docker compose config --quiet` nos modos desligado e ligado;
4. subir `hook-intelligence-api` e confirmar health `ready`;
5. subir API/web e repetir smoke autenticado;
6. registrar o path do backup pré-migração antes de qualquer promoção;
7. não habilitar AI real até provisionar credencial própria e aprovar o gate correspondente.
