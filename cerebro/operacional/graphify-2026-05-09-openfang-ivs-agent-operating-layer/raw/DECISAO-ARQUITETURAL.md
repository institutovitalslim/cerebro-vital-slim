# Decisão Arquitetural — IVS Agent Operating Layer

Data: 2026-05-09
Dono operacional: Maria — Gerente Geral IVS
Origem: análise repo-reverse do RightNow-AI/openfang com URL sanitizada.

## Decisão

Usar a arquitetura do OpenFang como referência prática para melhorias no IVS, sem migrar o OpenClaw e sem copiar código externo para produção.

## Primeira implementação

Skill interna `ivs-agent-operating-layer` criada em `/root/.openclaw/workspace/skills/ivs-agent-operating-layer`.

Primeiro módulo: `Clara Safety Monitor`, script somente leitura que audita:
- saúde do bridge Z-API/Clara;
- pausa global;
- overrides manuais;
- exclusões por motivo;
- colisões entre leads ativos e bloqueios de paciente/do_not_reply;
- amostras para revisão operacional.

## Guardrails

- Não envia WhatsApp.
- Não pausa nem despausa Clara.
- Não libera exceções automaticamente.
- `patient_do_not_reply` e `patient_bridge_known` permanecem bloqueados por padrão.
- Testes de envio seguem `dry_run:true` salvo ordem explícita.

## Resultado do primeiro run

Bridge saudável; Clara sem pausa global; 396 exclusões; 6 `patient_do_not_reply`; 390 `patient_bridge_known`; 25 leads ativos colidindo com bloqueio paciente-like. Essas colisões são bloqueios conservadores e exigem revisão antes de qualquer exceção.

## Próximos passos

1. Criar rotina diária do Safety Monitor com resumo para Maria/Tiaro.
2. Definir workflow `followup-seguro`: validar lead → checar exclusões → dry-run → aprovação → envio.
3. Criar cockpit simples com indicadores Clara/Z-API.
4. Evoluir para Hand Marketing OS e Hand Pré-consulta.
