# PREFLIGHT.md

Pré-checagem obrigatória para tarefas críticas, operacionais ou com chance de impacto real.

## Quando usar
Use antes de:
- editar configurações em produção
- responder ou fazer follow-up via bridge/WhatsApp
- alterar LLMs, services, skills ou cron
- executar fluxos multi-etapas importantes
- qualquer tarefa que o usuário mande "seguir" e que tenha risco de contexto errado

## Checklist
1. Qual é o objetivo exato?
2. Qual é o critério de conclusão?
3. Qual domínio operacional está envolvido?
4. Qual é a fonte canônica desse domínio? (consultar `CONTEXT_CANON.md`)
5. Existe checklist específico para esse fluxo?
6. Há risco, permissão, ou ação externa?
7. Existe guardrail automático que devo consultar antes?
8. O modelo/serviço/config atual foi validado?
9. Estou prestes a agir com contexto real ou com suposição?
10. Se houver ambiguidade, eu devo parar?

## Regra final
Se qualquer resposta essencial estiver ambígua, incompleta ou baseada em inferência fraca, não agir ainda.
Primeiro localizar a fonte de verdade.
