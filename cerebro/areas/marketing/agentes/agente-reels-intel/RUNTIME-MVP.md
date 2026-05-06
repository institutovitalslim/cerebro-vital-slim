# Runtime MVP — Agente Reels Intel

## Estado atual
**Status Operacional:** MVP_EM_TESTE

## O que já faz
- recebe uma URL de reel/post
- usa a API canônica do Instagram para coletar os dados
- salva input bruto em JSON
- gera um output estruturado inicial em Markdown
- prepara uma base utilizável para análise/adaptação manual assistida

## O que ainda não faz sozinho
- classificação IVS automática confiável
- adaptação IVS totalmente automática
- promoção automática de aprendizado para docs canônicos
- score comparativo entre referências
- gestão autônoma de contexto fora do tópico próprio sem mediação da Clara

## Interface operacional
- Tópico associado do agente: **Reels**
- Nome humano interno do agente nesse contexto: **João**
- Dentro do tópico próprio, o agente pode responder diretamente.
- Fora do tópico próprio, a Clara segue como interface principal e orquestradora.

## Roteamento nativo no runtime
- Em 2026-04-29 foi implementado suporte real no runtime do OpenClaw para mapear **tópico Telegram -> agentId**.
- Mapa vivo registrado em `/root/.openclaw/topic-agent-routing.json` e espelhado canonicamente em `cerebro/telegram-topic-agent-routing.json`.
- Rota ativa atual:
  - grupo `-1003803476669`
  - tópico `5782` (`Reels`)
  - agentId `agente-reels-intel`
- O agente também foi cadastrado em `~/.openclaw/openclaw.json` com identidade `João`.
- Status honesto: a implementação foi aplicada e carregada no gateway, mas a validação final ainda depende de um próximo teste real de entrada no tópico após o patch.

## Critério para subir de status
Este agente só sobe para `REALIDADE_OPERACIONAL` quando tiver:
1. pelo menos 1 caso real executado ponta a ponta
2. output salvo e reaproveitado em conteúdo do IVS
3. uma lição registrada
4. um limite conhecido documentado
