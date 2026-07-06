# Preset: continuation-handoff-loop

## Owner
Todos os agentes IVS

## Goal
Manter state/trace/next_action entre runs para evitar perda de contexto, repetição e falso DONE.

## Source of truth
state.json, trace.md, relatórios, paths/logs reais

## Allowed autonomous actions
- Ler, buscar, classificar, analisar e gerar relatório interno.
- Editar arquivos de trabalho reversíveis quando necessário.
- Rodar validações, scripts e consultas read-only.

## Human gates
- Enviar mensagem externa, publicar, gastar dinheiro, escrever em sistemas sensíveis, alterar regra canônica ou ação irreversível.

## Evaluation
Próximo agente entende status em 2 minutos e continua do ponto validado

## Stop conditions
Success:
- Eval atendido com evidência real.

Blocked:
- Fonte indisponível, credencial ausente, dado crítico inacessível ou risco sensível sem aprovação.

Budget/plateau:
- Parar após 5 iterações ou 2 rodadas sem avanço material.

## Final output
- Status
- Stop reason
- Evidence
- Iteration trace
- Remaining risks
- Next action
