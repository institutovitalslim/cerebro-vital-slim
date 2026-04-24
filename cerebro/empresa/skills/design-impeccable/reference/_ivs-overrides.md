# Overrides do Vital Slim — ler antes de qualquer reference

Este fork curado do Impeccable **não inclui os scripts** (`.mjs`, CLI `npx impeccable`, modo `/live`). Os reference files originais mencionam esses scripts. Este arquivo define o que fazer nesses casos.

## Regras de substituição

| Quando reference mencionar... | Fazer no IVS |
|---|---|
| `node .claude/skills/impeccable/scripts/load-context.mjs` | Ler `cerebro/CLAUDE.md` + `cerebro/empresa/contexto/geral.md` + `cerebro/empresa/skills/design-impeccable/brand-adapter.md` diretamente. Esses são os nossos `PRODUCT.md` + `DESIGN.md` canônicos. |
| `npx impeccable --json [target]` | Não disponível. Fazer a análise mentalmente, estruturar em markdown como resposta. |
| `npx impeccable live` ou modo `/live` | **Não disponível neste fork** (foi intencionalmente excluído por segurança — Puppeteer/Chromium não instalado). Se precisar de iteração visual, o Tiaro abre o HTML em browser manual e Clara faz ajustes baseados em screenshots. |
| `live.mjs` / `live-poll.mjs` / `live-server.mjs` | Não existem. Ignorar qualquer contrato "execute in order" baseado nesses scripts. |
| `/impeccable teach` (comando do plugin) | Não é um comando do plugin aqui. Para preencher o equivalente a `PRODUCT.md`, atualizar `cerebro/empresa/contexto/geral.md` e `cerebro/empresa/contexto/people.md`. |
| `/impeccable document` | Para documentar design do projeto, criar/atualizar `brand-adapter.md` com o que estiver faltando. |
| `PRODUCT.md` / `DESIGN.md` na raiz do projeto | No IVS, o papel deles é cumprido por `cerebro/empresa/contexto/geral.md` + `brand-adapter.md`. Não criar arquivos novos na raiz. |
| `.claude/commands/*` | Não usamos o sistema de slash commands do Claude Code nesta skill. Invocação é por referência explícita a `SKILL.md` ou `reference/<nome>.md`. |

## O que ESTÁ disponível

- ✅ Os 34 reference files em `reference/` (removemos só `live.md`) — **são consultivos/princípios**, não comandos executáveis
- ✅ `SKILL.md` (workflow IVS em PT-BR)
- ✅ `brand-adapter.md` (tokens de marca IVS)
- ✅ `NOTICE.md` (atribuição)
- ✅ `LICENSE` (Apache 2.0)

## Fluxo típico no IVS sem scripts

1. Ao receber pedido de HTML (apresentação de paciente, página, etc.), ler:
   - `cerebro/CLAUDE.md` (regras absolutas, compliance, tom)
   - `cerebro/empresa/contexto/geral.md` (identidade institucional)
   - `brand-adapter.md` (tokens IVS)
2. Identificar qual reference do Impeccable aplica (`typography.md`, `layout.md`, `color-and-contrast.md`, etc.)
3. Gerar o HTML
4. Passar pelo ciclo mínimo antes de entregar:
   - `reference/critique.md` — review UX (ignorar menções a `npx impeccable`)
   - `reference/polish.md` — passagem final
   - `reference/audit.md` — checagem técnica
5. Entregar ao Tiaro com o link do arquivo (regra do dia 2026-04-23: toda alteração em HTML, link automático)

## Como atualizar upstream

Quando o upstream Impeccable lançar nova major, seguir o processo documentado em `cerebro/learning-ledger.md` (2026-04-24): security scan + diff manual + atualização seletiva. **Nunca** `git pull` direto do upstream nesta pasta.
