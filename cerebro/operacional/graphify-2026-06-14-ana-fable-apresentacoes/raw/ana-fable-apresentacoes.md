---
type: raw-rc25
status: active
owner: maria
source_of_truth: true
created: 2026-06-14
updated: 2026-06-14
rc25: graphify-2026-06-14-ana-fable-apresentacoes
---
# RC-25 — Ana/Fable para apresentações clínicas

## Decisão
Tiaro determinou configurar o Fable para o tópico de Pesquisas Científicas da Ana, com foco específico em:

1. apresentações de leads / pacientes novos;
2. apresentações de pacientes em programas de acompanhamento.

## Configuração aplicada

### Agente Ana no OpenClaw
- Agente: `ana-medica`.
- Tópico Telegram: `6` no grupo `AI Vital Slim`.
- Modelo primário configurado: `openrouter/anthropic/claude-fable-5`.
- Fallbacks configurados:
  1. `openrouter/anthropic/claude-opus-4.8`;
  2. `openrouter/anthropic/claude-sonnet-4.6`;
  3. `openai-codex/gpt-5.5`.

O prompt da Ana foi atualizado para incluir apoio às apresentações clínicas de leads/pacientes novos e pacientes em acompanhamento, mantendo decisão clínica final com a Dra. Daniely / médico responsável.

### Scripts de apresentação
Foram ajustados para usar `anthropic/claude-fable-5` como primário na camada narrativa/raciocínio clínico via OpenRouter:

- `/root/cerebro-vital-slim/skills/geracao-apresentacao-paciente/scripts/analisar_questionario_llm.py`
- `/root/cerebro-vital-slim/skills/geracao-apresentacao-paciente/scripts/interpretar_exames_clinico_llm.py`
- `/root/cerebro-vital-slim/skills/geracao-apresentacao-paciente/scripts/cruzar_q_x_e_llm.py`
- `/root/cerebro-vital-slim/skills/apresentacao-acompanhamento-paciente/analisar_evolucao_fable_llm.py`

Extrações visuais/estruturadas que dependem de visão ou backend específico permanecem nos modelos próprios já definidos pelos scripts.

## Validação
- Configuração JSON do OpenClaw lida com sucesso após alteração.
- Roteamento do tópico `6` confirmado para `ana-medica`.
- Compilação Python dos scripts alterados: OK.
- OpenRouter lista `anthropic/claude-fable-5` e `~anthropic/claude-fable-latest` no catálogo.
- Smoke test de execução retornou 404 `Claude Fable 5 is not available` para a conta atual. Portanto, a configuração fica preparada para usar Fable assim que a conta/liberação permitir; até lá, a operação cai nos fallbacks configurados, principalmente Opus 4.8.

## Governança
- A Ana continua sendo consultoria médica/científica interna.
- A decisão clínica final permanece com a Dra. Daniely / médico responsável.
- Não há contato direto da Ana com pacientes.
- Mudanças persistentes relacionadas ao fluxo devem continuar passando por Graphify/RC-25.
