# SPEC-CEOS-PHASE2-001: Sprint Semanal de Posicionamento

## Goal
Transformar o Content Engine OS em uma máquina guiada de produção semanal: BI → tese → família de conteúdo → aprovação → publicação → aprendizado.

## Acceptance Criteria
- [x] Usuário tem uma tela única para iniciar a semana por tese, não por peça solta.
- [x] Sistema sugere teses/pilares IVS com base em sinais agregados e governança.
- [x] Uma tese vira plano de família: carrossel, reels, estático e stories, com CTA, função e métrica.
- [x] UI expõe próximos passos claros para produção e aprovação.
- [x] Smoke público valida a nova página e endpoint.

## Scope
**In scope:** endpoint read-only/determinístico de comando semanal, página `/sprint-semanal`, navegação e smoke.

**Out of scope:** envio automático, publicação externa, DM, escrita Z-API, coleta real RapidAPI. Esses ficam para fases posteriores com approval gates.

## Data/Security
- Sem PII.
- Usa apenas contagens agregadas de criativos, stories e BI.
- Não cria peças automaticamente; gera plano operacional e direciona para módulos de produção.

## Agents ativados via ivs-data-dev-os
- Product Analyst IVS: problema = sistema ainda depende do usuário saber por onde começar.
- Solution Architect IVS: solução = cockpit de sprint semanal com tese central.
- Data Architect IVS: contratos read-only para métricas agregadas e plano de família.
- Security/LGPD Guard IVS: bloqueio de PII/publicação/envio automático.
- Builder IVS: API + UI + navegação.
- QA/Bench Engineer IVS: compile, build, smoke, validação pública.
- Release Engineer IVS: restart API/Web.
- Executive Narrator IVS: reporte executivo.

## Quality Gate
- `python3 -m compileall apps/api scripts render_worker -q`
- `npm run build`
- `python3 scripts/content_engine_smoke.py --json`
- Validação pública `/sprint-semanal` e `/api/weekly-command/overview`.
