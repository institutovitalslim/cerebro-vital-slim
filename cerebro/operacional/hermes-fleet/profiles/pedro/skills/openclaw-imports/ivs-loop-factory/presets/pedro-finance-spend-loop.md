# Preset: pedro-finance-spend-loop

## Owner
Pedro

## Goal
Auditar gasto recorrente, duplicidade, spikes, ferramentas sem uso, renovação e potencial economia.

## Source of truth
Omie/read-only, planilhas, faturas, contratos quando disponíveis

## Allowed autonomous actions
- Ler, buscar, classificar, analisar e gerar relatório interno.
- Editar arquivos de trabalho reversíveis quando necessário.
- Rodar validações, scripts e consultas read-only.

## Human gates
- Enviar mensagem externa, publicar, gastar dinheiro, escrever em sistemas sensíveis, alterar regra canônica ou ação irreversível.

## Evaluation
Pauta de economia com fonte, impacto estimado, risco e nenhum write sem gate

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
