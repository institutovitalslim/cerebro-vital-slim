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
- Papel observado: **operação transversal / comando geral / memória operacional**
- Uso real já visto: Quarkclinic, agenda, GitHub/cérebro, WhatsApp/Z-API, estrutura de memória, regras operacionais
- Status: **tópico fortemente canônico**; várias decisões estruturais importantes nasceram aqui

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

### Tópico "Pacientes" (topic_id a confirmar)
- Nome do tópico: **Pacientes**
- Volume observado em 2026-04-23: 589 mensagens
- Contexto: usado para conversas/apresentações relacionadas a pacientes específicos (ex.: apresentação clínica HTML por paciente, follow-up de caso)
- **Pendente:** confirmar `topic_id` numérico no Telegram e mapear para a área canônica (provavelmente Atendimento ou Operação Clínica)
- **Identidade neste tópico:** quando perguntarem "qual seu nome" / "você é a Clara" aqui, a resposta canônica é **"Sou a Clara, assistente digital do Instituto Vital Slim"**. Em 2026-04-23 a Clara respondeu "ainda não tenho um nome fixo, pode me chamar como quiser" neste tópico — bug de identidade (carregava só `IDENTITY.md` template em vez de `cerebro/CLAUDE.md`). Corrigido preenchendo `IDENTITY.md` e adicionando regra de precedência em `AGENTS.md`.

### Tópico "Financeiro" (topic_id 1980, a confirmar)
- Nome do tópico: **💰 Financeiro**
- Ícone observado: saco de dinheiro 💰
- Link: `t.me/c/3803476669/1980`
- Possível `topic_id`: **1980** (extraído do link; confirmar)
- Contexto: usado para análise financeira (extratos, empréstimos, relatórios PDF, boletos, Omie)
- **Incidente 2026-04-24:** Clara retornou `Agent couldn't generate a response. Please try again.` quando Tiaro anexou `relatório.pdf` (203 KB) e perguntou sobre valor total de empréstimo. Erro do gateway do OpenClaw chamando o modelo (não bug da Clara) — suspeita: PDF grande estourou contexto OU quota do modelo. Ver `memory/2026-04-24.md` para diagnóstico detalhado.

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
