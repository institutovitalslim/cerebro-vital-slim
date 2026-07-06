# Preset: clara-revenue-watchdog

## Owner
Clara + Maria

## Goal
Detectar e corrigir leads/agendamentos travados, no-reply, preço antes da jornada, paciente tratado como lead e avisos operacionais ausentes.

## Source of truth
conversas/logs WhatsApp, runtime Clara, QuarkClinic read-only quando permitido

## Allowed autonomous actions
- Ler, buscar, classificar, analisar e gerar relatório interno.
- Editar arquivos de trabalho reversíveis quando necessário.
- Rodar validações, scripts e consultas read-only.

## Human gates
- Enviar mensagem externa, publicar, gastar dinheiro, escrever em sistemas sensíveis, alterar regra canônica ou ação irreversível.

## Evaluation
0 lead elegível sem resposta; 0 preço antes da jornada; agendamento com aviso Tiaro/Liane; relatório sem PII

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
