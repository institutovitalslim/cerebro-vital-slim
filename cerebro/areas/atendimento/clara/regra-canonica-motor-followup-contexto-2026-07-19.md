# Regra canônica — Motor de follow-up com análise de contexto

**Data:** 2026-07-19  
**Origem:** Tiaro  
**Escopo:** Clara WhatsApp · motor de cadência/follow-up de leads

## Regra

O motor de follow-up deve ter como **primeira tarefa obrigatória** analisar todo o contexto disponível das mensagens do lead antes de selecionar, gerar ou enviar qualquer retomada.

## Objetivo

Voltar a se conectar com o lead da forma certa, retomando o ponto real da conversa e evitando mensagens que pareçam genéricas, repetidas ou desconectadas do histórico.

## Implicações operacionais

1. O motor deve ler o histórico recente real do lead antes de escolher o texto.
2. A retomada deve considerar, no mínimo:
   - última fala do lead;
   - última resposta da Clara;
   - dúvidas/objeções já verbalizadas;
   - dores citadas;
   - se já existe pergunta de descoberta aberta aguardando resposta;
   - sinais de recusa final, pedido de retorno futuro ou bloqueio de follow-up.
3. Se a última mensagem da Clara já deixou uma pergunta aberta e o lead ainda não respondeu, o motor não deve mandar outra pergunta genérica parecida.
4. A mensagem de follow-up deve reconectar a partir do contexto, sem expor dados sensíveis e sem inventar informações.
5. Evidência operacional deve ser redigida: categoria/contexto/âncora são permitidos; dump de conversa, telefone completo e PII não são permitidos em relatório.

## Estado de implementação

Aplicado no motor `clara_followup_cadence.py` com as funções:

- `recent_conversation_for_phone()`
- `analyze_lead_message_context()`
- `contextualize_followup_message()`

O relatório do motor passa a incluir `context_category` e `context_anchor` por lead selecionado.
