# Telegram Topics

## Grupo principal
- Nome: `AI Vital Slim`
- Chat ID: `telegram:-1003803476669`
- Tipo: grupo com múltiplos tópicos

## Regra de operação
Em grupos com múltiplos tópicos, o tópico atual **não deve ser tratado como memória isolada**. Sempre que a pergunta tocar um domínio recorrente ou contexto já discutido em outro tópico, consultar a memória transversal e o protocolo intertópicos.
Regra reforçada por Tiaro em 2026-04-14: compartilhar informações importantes para a memória geral, para que a execução não dependa do contexto do tópico.
Regra reforçada novamente por Tiaro em 2026-04-21: **todos os tópicos devem estar interligados por um conhecimento único**. Logo, nenhuma área deve “desconhecer” uma integração, fluxo, decisão ou contexto canônico só porque ele surgiu em outro tópico.

## Mapa atual de tópicos conhecidos

### Topic 271
- Nome do tópico: **Pacientes**
- Papel observado: **pacientes / apresentações de casos / operação clínica individual no grupo**
- Uso real já visto: apresentações clínicas HTML por paciente, follow-up de caso, conversas relacionadas a pacientes específicos
- Confirmação factual: Tiaro confirmou em 2026-05-03 que o `topic_id` de **Pacientes** é **271**
- Status: **tópico confirmado canonicamente**

### Topic 3
- Área provável: **📢 Marketing**
- Evidência: rotinas de análise de criativos, métricas de ads, conteúdo agendado e relatórios de campanha apontam para `topic_id: 3`

### Topic 4
- Área provável: **💰 Vendas**
- Evidência: rotinas de pipeline, leads esfriando e relatório de vendas apontam para `topic_id: 4`

### Topic 5
- Área provável: **💬/🎧 Atendimento**
- Evidência: rotinas de tickets, NPS e health score apontam para `topic_id: 5`

### Topic 6
- Área provável: **⚙️ Operações / Gestão operacional**
- Evidência: sync GitHub, agenda do dia, consolidação de memória e heartbeat apontam para `topic_id: 6`

### Topic 7
- Área provável: **💻 Desenvolvimento**
- Evidência: rotinas de code review, sprint digest e testes automatizados apontam para `topic_id: 7`

### Topic 8
- Área provável: **Pessoas / RH**
- Evidência: rotinas de clima, contratos vencendo e onboarding apontam para `topic_id: 8`

- **Identidade neste tópico:** quando perguntarem "qual seu nome" / "você é a Clara" aqui, a resposta canônica é **"Sou a Clara, assistente digital do Instituto Vital Slim"**. Em 2026-04-23 a Clara respondeu "ainda não tenho um nome fixo, pode me chamar como quiser" neste tópico — bug de identidade (carregava só `IDENTITY.md` template em vez de `cerebro/CLAUDE.md`). Corrigido preenchendo `IDENTITY.md` e adicionando regra de precedência em `AGENTS.md`.

## Regra de promoção entre tópicos
Quando uma decisão, regra, contato, integração, ID, convenção ou fluxo recorrente surgir em qualquer tópico:
1. identificar o domínio real do conteúdo;
2. promover a informação para a memória canônica daquele domínio;
3. registrar a origem no ledger de aprendizagem;
4. garantir que a próxima execução da tarefa não dependa de lembrar qual tópico originou a decisão;
5. manter este mapa como referência de origem, e não como único lugar da verdade.

## Regra prática de resposta
Antes de responder algo importante em qualquer tópico:
1. identificar o domínio da pergunta;
2. consultar o arquivo canônico do domínio;
3. consultar este mapa se houver chance de a origem ter sido outro tópico;
4. só então responder.

### Topic 5782
- Nome do tópico: **Reels**
- Link interno observado: `https://t.me/c/3803476669/5782`
- Papel operacional: cockpit do operador de inteligência de conteúdo / engenharia reversa de reels
- Agente associado: `agente-reels-intel`
- Nome humano interno do agente: **João**
- Regra de interface: dentro deste tópico, o agente especializado de reels pode responder diretamente; fora dele, a Clara segue como interface principal.
- Estado de runtime em 2026-04-29: suporte nativo `topic -> agentId` implementado no OpenClaw para este tópico.
- Mapa operacional vivo: `/root/.openclaw/topic-agent-routing.json`
- Espelho canônico do mapa: `cerebro/telegram-topic-agent-routing.json`
- Correção importante em 2026-04-30: o identificador correto do tópico de Reels é **5782**. O número **768** apareceu no contexto da conversa, mas não é o `topic_id` real usado no roteamento.
- Status honesto atual: **território comprovado**. Tiaro validou em 2026-05-01 que o João está respondendo corretamente no tópico 5782.
- Regra adicional de robustez: manter o tópico 5782 tratado como referência canônica do João e evitar qualquer documentação, contexto de conversa ou parâmetro solto que volte a misturar `768` com `5782`.
