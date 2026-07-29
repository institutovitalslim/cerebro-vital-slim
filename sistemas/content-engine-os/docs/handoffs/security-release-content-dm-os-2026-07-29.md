# Handoff — Security release do IVS Content DM OS

**Data:** 2026-07-29  
**Origem:** Maria, Gerente Geral IVS  
**Destino:** Claude Main, dono atual do Content Engine OS  
**Status:** correções, deploy VPS e integração interna concluídos e validados

## Resumo

A revisão de segurança do IVS Content DM OS e do adaptador Content Engine foi concluída. O runtime Meta permanece fail-closed e sem ativação live.

## Commit e branch

- Repositório local: `/root/.hermes/maria-workspace/projects/ivs-content-dm-os`
- Base: `ivs/main` (`79de081`)
- Branch: `fix/ivs-security-release-blockers`
- Commit de segurança: `75def0a` — `fix: harden IVS content delivery and retention`
- Commit VPS local: `9d80158` — `feat: operate IVS Content DM OS fully on VPS`
- Upstream público foi preservado e não recebeu push.

## Correções principais

1. Kill switch Meta global, com worker inerte sem aprovação live.
2. Purge transacional, desativado por padrão e sem cron automático.
3. Contrato Content OS estrito, sem PII e com tenant binding fail-closed.
4. Endpoint de capabilities autenticado.
5. Content Engine sem segredo default e com autorização fail-closed.
6. Conteúdo publicado imutável; learning sem fallback clínico inventado.
7. Renders autenticados e render worker com claim atômico.
8. Uploads limitados em streaming e remoção de arquivo parcial.
9. Next.js 16.2.12 nos dois frontends; audits Node/Python zerados.

## Evidência

- DM OS: 129 testes, lint, typecheck e build aprovados; npm audit 0.
- Content Engine API: 48 testes e compileall aprovados; pip-audit 0.
- Content Engine Web: typecheck e build aprovados; npm audit 0.
- Smoke negativo: 401 sem auth; 200 autenticado; live Meta falso; tenant não permitido 403; porta temporária fechada.
- Gate IVS: 15 arquivos críticos OK.

## Artefatos

- Relatório: `/root/deliverables/relatorio-final-security-fixes-2026-07-29.html`
- Bundle completo DM OS: `/root/deliverables/ivs-content-dm-os-security-fixed-2026-07-29.tar.gz`
- Bundle seletivo Content Engine: `/root/deliverables/content-engine-os-security-fixed-selective-2026-07-29.tar.gz`
- Patch: `/root/deliverables/ivs-content-dm-os-security-fixes-2026-07-29.patch`
- Rollback: `/root/deliverables/ROLLBACK-security-fixes-2026-07-29.md`
- Checksums: `/root/deliverables/SHA256SUMS-security-fixes-2026-07-29.txt`

## Decisão de hospedagem

Tiaro determinou que o Content DM OS siga a mesma lógica do Content OS: sistema integralmente criado e operado na VPS. Repositório GitHub separado não é requisito. Nenhum repositório remoto ou push do DM OS foi criado; o histórico local e o Git bundle são os mecanismos de versionamento/recuperação.

## Deploy local autorizado por Tiaro

Em 2026-07-29, Tiaro autorizou explicitamente seguir com a promoção local. Foi executado restart sequencial apenas de API e web; Postgres e Redis não foram recriados.

### Evidência pós-deploy

- Snapshot completo pré-deploy: `/root/deliverables/content-engine-os-predeploy-full-2026-07-29.tar.gz`
- SHA-256 do snapshot: `037e278932362dcb3e34d8a1ebe10d2130e4074f1c4f70f55ec66200b23cfa3a`
- API: container novo `086cffeca2d1...`, running, restart count 0, `/health` HTTP 200.
- Web: container novo `57411b9550f9...`, running, restart count 0, raiz HTTP 307.
- Adaptador Content DM OS sem autenticação: HTTP 401.
- Postgres e Redis permaneceram running, restart count 0.
- Logs recentes: zero `traceback`, `uncaught`, `fatal` ou `error`.
- Meta live não foi ativado e nenhuma entrega externa foi feita.

A configuração Nginx versionada ainda usa o placeholder `contentos.seudominio.com` e não há endpoint público canônico instalado para validação externa.

## Content DM OS integral na VPS

- Web local: `127.0.0.1:3020`.
- Postgres e Redis somente nas redes Docker; sem portas públicas.
- Redis autenticado e validado: comando anônimo negado, comando autenticado `PONG`.
- Worker saudável em `standby_dry_run`, sem criar fila live ou chamar Meta.
- Migração Prisma one-shot concluída com exit code `0`.
- Health final: HTTP 200 com database, redis, queue e worker `ok`.
- Containers Postgres, Redis, web e worker: running/healthy, restart count 0.
- Integração Content OS pela rede `content-engine-os_default` com origem HTTP privada exata e token dedicado.
- Smoke ponta a ponta: Content Engine 200; anônimo 401; adapter status 200; campanha 202; `persisted=false`; `dispatched=false`; `live_meta_delivery=false`.
- Backup validado: `/root/backups/ivs-content-dm-os/20260729T155551Z/`.
- Bundle local atualizado: `/root/deliverables/ivs-content-dm-os-vps-9d80158.bundle`.
- Pacote seletivo do adaptador: `/root/deliverables/content-engine-dm-integration-2026-07-29.tar.gz`.
- Runbook: `/root/.hermes/maria-workspace/projects/ivs-content-dm-os/docs/vps-runbook.md`.

## Governança após a janela

O `BUILD_LOCK.md` permanece vigente e o Claude Main continua sendo o dono do Content Engine OS. A autorização foi aplicada como janela operacional pontual; o lock permanente não foi removido.
