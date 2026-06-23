# SPEC-CEOS-STORIES-001: Stories Engine 10x IVS

## Goal
Transformar o mapeamento do AppBumper/Stories 10x em um módulo IVS-first dentro do Content Engine OS que fecha o ciclo `story → CTA → WhatsApp/Clara → lead/agendamento → debrief/aprendizado`.

## Acceptance Criteria
- [ ] Banco possui entidades mínimas para temas, produtos, stories individuais e debrief enriquecido.
- [ ] API expõe leitura de temas/produtos seed e handoff Clara/WhatsApp para uma sequência salva.
- [ ] UI `/stories-engine` mostra handoff de campanha, UTM, tag de origem e script inicial da Clara.
- [ ] Smoke test cria sequência, gera handoff, registra performance e consulta ranking sem erro.
- [ ] Build web e compile Python passam.

## Scope

### In scope
- Schema idempotente e seed IVS.
- API read/write governada para módulo de stories.
- Handoff determinístico para Clara/Z-API sem envio real.
- Documentação do mapeamento e evolução no Content Engine OS.

### Out of scope
- Publicação automática no Instagram.
- Escrita real na Clara/Z-API.
- Integração Meta/RapidAPI live nesta fase.
- Uso de PII ou conversas reais.

## Technical Approach
- Manter compatibilidade com o módulo já existente `stories.py`.
- Adicionar tabelas complementares (`story_themes`, `story_products`, `story_items`, `story_debriefs`) sem quebrar `story_sequences` e `story_sequence_performance`.
- Usar handoff determinístico baseado no payload da sequência.
- Gerar links de WhatsApp com texto pré-preenchido e UTMs sanitizadas.

## Log Points
- API de handoff: sem log de telefone/PII; resposta determinística.
- Smoke test: IDs internos e status HTTP apenas.

## TRUST 5 Checklist
- [ ] Tested: smoke real contra API local.
- [ ] Readable: nomes claros e JSON explícito.
- [ ] Unified: segue FastAPI + psycopg atuais.
- [ ] Secured: sem senha, token ou PII nova.
- [ ] Trackable: spec + migration + smoke + commit.
