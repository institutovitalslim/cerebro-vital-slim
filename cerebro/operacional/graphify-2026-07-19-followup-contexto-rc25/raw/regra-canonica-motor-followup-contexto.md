# RC-25 — Regra canônica do motor de follow-up por contexto

**Data:** 2026-07-19
**Origem:** Tiaro
**Decisão:** O motor de follow-up da Clara deve começar analisando todo o contexto disponível das mensagens do lead antes de selecionar/redigir qualquer retomada.

## Ensinamento canônico

Follow-up não é disparo de cadência genérica. A primeira etapa é entender a conversa: o que o lead disse, o que a Clara respondeu, qual pergunta ficou aberta, qual dor/objeção apareceu e qual é a forma certa de reconectar.

## Regras derivadas

- Antes de escolher texto, carregar o histórico recente real do lead.
- Bloquear follow-up quando já houver pergunta de descoberta aberta aguardando resposta.
- Bloquear/encerrar cadência quando houver recusa final, pedido de retorno futuro ou negativa terminal financeira/sem avanço (ex.: "é muito caro para mim", "não tenho condições", "não consigo pagar", "fora do meu orçamento", "não dá para mim agora").
- Quando elegível, contextualizar a abertura pela categoria da conversa: investimento, agenda, peso/corpo, energia/rotina, exames/metabolismo ou retomada genérica contextual.
- Registrar evidência redigida (`context_category`, `context_anchor`) sem expor PII ou dump de conversa.

## Arquivos impactados

- `cerebro/areas/atendimento/clara/regra-canonica-motor-followup-contexto-2026-07-19.md`
- `cerebro/areas/atendimento/clara-operacao/runtime/clara_followup_cadence.py`
- `cerebro/areas/tecnologia/skills/ivs-agent-operating-layer/workflows/followup-seguro.json`
- runtime operacional: `/root/.openclaw/workspace/ops/zapi_bridge/clara_followup_cadence.py`
