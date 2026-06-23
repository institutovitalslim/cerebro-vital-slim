# SPEC-CEOS-STORIES-003: Analytics real e contrato Clara do Stories Engine IVS

## Goal
Conectar o Stories Engine a métricas operacionais mais próximas de negócio: retenção por bloco/story, clique, lead, agendamento, custo e relatório executivo semanal.

## Acceptance Criteria
- [x] Banco suporta métricas por bloco/story e conversões/agendamentos agregados por `origin_tag`.
- [x] API registra conversão sem PII e sem escrita em Clara/Z-API.
- [x] API entrega analytics consolidado por sequência.
- [x] API entrega contrato Clara por `origin_tag` para condução SPIN.
- [x] API gera relatório semanal HTML para João/Tiaro.
- [x] UI expõe analytics/relatório/contrato sem disparar ações externas.
- [x] Smoke dedicado valida o ciclo completo.

## Scope
- **In scope:** Content Engine OS, Postgres, FastAPI, UI `/stories-engine`, smoke sintético.
- **Out of scope:** leitura real de Instagram/Meta, escrita Z-API, agendamento QuarkClinic, envio a paciente/lead.

## Technical Approach
Modo DDD: preservar Fases 1 e 2. Acrescentar tabelas idempotentes, endpoints read/write internos com dados agregados e relatório HTML. O contrato Clara é apenas leitura: dado de campanha, objeções e instrução SPIN.

## Governance
- Sem nome, telefone, mensagem do lead ou dado clínico identificável.
- Conversão usa `conversion_type`, `origin_tag`, `source`, `value` e `notes` genéricos.
- Relatório executivo mostra dados agregados.
- Nenhum endpoint chama Z-API, QuarkClinic ou Omie.

## TRUST 5 Checklist
- [x] **Tested:** migration, py_compile, compileall, build, smoke dedicado, smoke geral.
- [x] **Readable:** endpoints e helpers com nomes explícitos.
- [x] **Unified:** segue padrões do router Stories.
- [x] **Secured:** dados agregados e sem PII.
- [x] **Trackable:** spec, smoke e commit no cérebro.
