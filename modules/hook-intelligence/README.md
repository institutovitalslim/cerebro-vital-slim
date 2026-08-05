# Hook Intelligence Engine

Módulo autônomo e local-first para gerar, avaliar, comparar, favoritar e exportar hooks em português brasileiro. Ele roda isolado do Content Engine OS principal e **não publica conteúdo, não aprova peças e não altera sistemas externos**.

## Arquitetura

- **API:** FastAPI + Pydantic + SQLAlchemy.
- **Motor:** seleção, composição, deduplicação, score, compliance, explicação e ranking determinísticos.
- **Persistência:** SQLite local; em Docker, arquivo em volume nomeado.
- **Web:** Next.js standalone, com proxy same-origin `/api/backend/*`.
- **IA:** adaptador OpenAI-compatible opcional. Desligada por padrão e com fallback determinístico.
- **Contratos:** JSON Schema em [`contracts/`](contracts/).

## Requisitos

### Execução local

- Python 3.11
- `uv`
- Node.js 22
- npm

### Stack isolada

- Docker Engine
- Docker Compose

## Configuração

Copie o exemplo sem inserir segredos no Git:

```bash
cp .env.example .env
```

| Variável | Padrão | Uso |
|---|---|---|
| `HOOK_API_PORT` | `18082` | Porta externa da API; `18080` permanece reservada ao Evolution no host IVS |
| `HOOK_WEB_PORT` | `13000` | Porta externa da interface web |
| `HOOK_DATABASE_URL` | `sqlite:////data/hooks.db` no container | Persistência da API |
| `HOOK_AI_ENABLED` | `false` | Ativa adaptação por IA somente quando explicitamente verdadeiro |
| `HOOK_AI_ENDPOINT` | OpenAI-compatible | Endpoint remoto opcional |
| `HOOK_AI_API_KEY` | vazio | Segredo injetado apenas em runtime |
| `HOOK_AI_MODEL` | vazio | Modelo do adaptador opcional |
| `HOOK_AI_TIMEOUT_SECONDS` | `20` | Timeout limitado |
| `HOOK_AI_MAX_TOKENS` | `2048` | Limite defensivo de saída |
| `HOOK_API_URL` | `http://backend:8000` em Docker | Destino server-side do proxy Next.js |
| `PLAYWRIGHT_BASE_URL` | `http://127.0.0.1:13000` | Base URL do E2E |

Com `HOOK_AI_ENABLED=false`, endpoint, chave e modelo não são necessários. Nunca grave tokens no `.env.example`, em imagens ou em relatórios.

## Execução local

### Backend

```bash
cd backend
uv sync --extra dev
HOOK_DATABASE_URL='sqlite:///./data/hooks.db' uv run python -c \
  "import os, uvicorn; from hook_intelligence.api.main import create_app; uvicorn.run(create_app(database_url=os.environ['HOOK_DATABASE_URL']), host='127.0.0.1', port=18082)"
```

O entrypoint lê a URL do banco e chama `create_app(database_url=...)`; importar `api.main` não cria arquivo SQLite.

### Web

```bash
cd web
npm ci
HOOK_API_URL=http://127.0.0.1:18082 npm run dev -- --hostname 127.0.0.1 --port 13000
```

Abra `http://127.0.0.1:13000`.

## Docker Compose

```bash
docker compose up -d --build
docker compose ps
bash scripts/smoke.sh
```

A stack usa rede e volume próprios. Não reutiliza Postgres, Redis, Nginx ou volumes do Content OS.

Parar sem apagar dados:

```bash
docker compose down
```

Apagar o volume SQLite é destrutivo e não faz parte do fluxo normal. Só execute `docker compose down -v` após backup e autorização explícita.

## Endpoints

| Método | Endpoint | Função |
|---|---|---|
| `GET` | `/health` | Readiness e estado opt-in da IA |
| `GET` | `/v1/taxonomies` | Taxonomias e mecanismos |
| `GET` | `/v1/patterns` | Catálogo, opcionalmente filtrado por biblioteca |
| `POST` | `/v1/hooks/generate` | Gera, valida, persiste e ranqueia hooks |
| `POST` | `/v1/hooks/score` | Calcula score determinístico |
| `POST` | `/v1/hooks/compliance` | Avalia compliance |
| `POST` | `/v1/hooks/{id}/favorite` | Favorita hook persistido |
| `GET` | `/v1/history` | Histórico paginado de sessões |
| `GET` | `/v1/favorites` | Favoritos paginados |
| `POST` | `/v1/exports/content-os` | Gera payload JSON compatível com o contrato |

Swagger local: `http://127.0.0.1:18082/docs`.

## Exemplo determinístico

```bash
curl -fsS http://127.0.0.1:18082/v1/hooks/generate \
  -H 'content-type: application/json' \
  -d '{
    "topic":"qualidade do sono",
    "channel":"reel",
    "objective":"retention",
    "audience":"mulheres acima de 40",
    "library":"universal",
    "count":5,
    "use_ai":false
  }'
```

Cada item contém score `0..100`, explicação pública, status de compliance e origem. A resposta é ordenada por `scores.overall` decrescente. Hooks `BLOCK` não entram em favoritos apresentados, comparação ou exportação.

## Bibliotecas

- `universal`: 40 padrões originais.
- `ivs-health`: 20 padrões originais e regras adicionais de compliance em saúde.

`REVIEW` significa revisão humana necessária; não significa aprovação. `BLOCK` impede uso no fluxo público.

## Contratos e Exportação

- `generation-request.schema.json`
- `generation-response.schema.json`
- `hook.schema.json`
- `content-os-export.schema.json`

O schema de exportação atual é `1.0.0`. Consumidores devem validar antes de importar e rejeitar versões incompatíveis. Os schemas possuem referências entre arquivos; para validação totalmente offline, registre **todos** os documentos de `contracts/` pelo respectivo `$id` e também pelo nome do arquivo no resolver local antes de validar o payload.

## Testes

```bash
cd backend
uv run pytest --cov=hook_intelligence --cov-report=term-missing
uv run ruff check hook_intelligence tests

cd ../web
npm test -- --run
npm run lint
npm run build

cd ..
docker compose up -d --build
bash scripts/smoke.sh
cd web
npx playwright test
```

## Persistência e backup

O Compose monta o banco SQLite em `/data/hooks.db`. Para backup, pare gravações ou copie usando a ferramenta de backup SQLite. Nunca edite o arquivo enquanto a API grava.

Migração futura para Postgres deve preservar os contratos HTTP e substituir somente a camada `storage`; consulte [`HANDOFF-CLAUDE-CODE.md`](HANDOFF-CLAUDE-CODE.md).

## Troubleshooting

### API não fica healthy

```bash
docker compose ps
docker compose logs --no-color backend
```

Confira permissões do volume, `HOOK_DATABASE_URL` e se a porta externa está livre.

### Web responde, mas geração falha

Confira `HOOK_API_URL`; no Compose deve apontar para `http://backend:8000`, não para `localhost`.

### Porta ocupada

```bash
HOOK_API_PORT=18083 HOOK_WEB_PORT=13001 docker compose up -d --build
```

### IA indisponível

Mantenha `HOOK_AI_ENABLED=false` para operação determinística. Se a IA estiver ativa e falhar, a geração retorna fallback determinístico e aviso público sanitizado.

## Rollback

1. Não apague o volume.
2. Registre o commit atual e faça backup do SQLite.
3. Volte para a imagem/commit anterior.
4. Execute `docker compose up -d --build`.
5. Valide `/health`, geração e leitura de histórico.
6. Se o schema de persistência tiver mudado no futuro, execute migração reversa documentada antes de iniciar a versão anterior.

## Limites e não objetivos

- Sem autenticação nesta versão: bind local por padrão; não exponha diretamente à internet.
- Sem publicação externa ou aprovação automática.
- Sem integração já realizada com o Content Engine OS principal.
- Sem Postgres/Redis/Nginx compartilhados.
- IA é opt-in e exige governança de credenciais/custo.
- `npm audit --omit=dev` está em zero; o audit completo mantém alertas somente na cadeia Vitest 2 de desenvolvimento, cuja correção exige upgrade major para Vitest 4.
