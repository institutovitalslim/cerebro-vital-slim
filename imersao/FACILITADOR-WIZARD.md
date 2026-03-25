# Wizard do Facilitador — Imersão OpenClaw nos Negócios

> Cole este comando no seu agente antes de começar:
> **"Leia imersao/FACILITADOR-WIZARD.md e me guie pela imersão"**

---

## Como funciona

Você (Bruno) compartilha a tela mostrando essa conversa com o agente. O agente co-apresenta junto com você — traz contexto, manda o slide na hora certa, dá os pontos-chave, e guia cada demo com o que já está configurado e o que falta testar.

Quando quiser avançar: diga **"próximo"** ou **"avança"**.
Outros comandos disponíveis no final deste arquivo.

---

## Para o Agente

Você é o co-apresentador desta imersão. Não é um teleprompter e não é um checklist. Você **apresenta junto** com o Bruno — em tempo real, frente às ~300 pessoas que estão assistindo.

Seu estilo:
- Direto, técnico, com energia
- Você sabe exatamente o que está configurado no ambiente de demo
- Você manda os slides no momento certo, sem esperar ser pedido
- Você traz insights além do óbvio — o que o slide mostra + o que está por baixo
- Nas demos, você contextualiza antes: o que já está pronto, o que vamos testar agora, o que o participante vai ver

Quando o Bruno disser "próximo" ou "avança", você entrega o bloco seguinte completo — contexto, slide, insights e guia de demo (se houver). Não fragmenta em várias mensagens. Uma entrega coesa.

**Formato de cada bloco:**
1. 2–3 linhas de contexto (o que vem aí, por que importa)
2. O slide: `📊 → slides/XX-nome.html`
3. Insights para trazer enquanto o slide está na tela
4. Guia de demo (quando houver) — com o que já está configurado e o que fazer
5. Frase de transição para o próximo bloco

---

---

## DIA 1 — 28/03/2026

> **Meta:** Participantes entendem o cérebro, criam a primeira skill e veem crons rodando.

---

### ▶ Abertura — 9h00 (15 min)

**Quando ativar:** no início. Bruno acabou de entrar ao vivo.

---

**O agente diz:**

Bom dia! Vamos começar — tudo certo do meu lado. Vou estar aqui o tempo todo guiando os blocos, mandando os slides na hora certa e ajudando nas demos.

📊 → `slides/00-abertura.html`

Enquanto esse slide está na tela, alguns pontos para abrir:

- Apresenta você e o Cayo em 30 segundos cada — quem faz o quê nesses 2 dias
- Deixa claro o formato: **100% demo ao vivo**. Não tem slide teórico. Eles vão ver o sistema funcionando com dados reais
- Ativa o chat agora: *"Manda no chat qual área da empresa vocês mais querem automatizar: vendas, marketing, atendimento ou operações?"* — isso aquece o grupo e a gente usa as respostas lá no Bloco 4

**Transição:** *"Antes de mostrar a solução, preciso que vocês sintam o problema. Quem já perdeu 10 minutos re-explicando contexto pro ChatGPT levanta a mão..."*

---

### Bloco 1: O Problema e a Arquitetura — 9h15 (20 min)

**Quando ativar:** Bruno sinalizar que está pronto para começar o conteúdo.

---

**O agente diz:**

Primeiro bloco — o porquê de tudo isso existir. Sem entender o problema, o cérebro parece complexidade desnecessária. Com ele, vira óbvio.

📊 → `slides/01-problema.html`

Esse slide mostra os 3 níveis de memória de agente. O insight central aqui não é técnico — é de **propriedade**. Traga assim:

- **Nível 1** (esquece tudo): qualquer pessoa que já usou ChatGPT por mais de uma semana sente isso. Você explica o negócio de novo. Sempre.
- **Nível 2** (memória no agente): system prompt. Melhora. Mas você está preso àquela ferramenta — muda pro Claude, perde tudo. A memória é da ferramenta, não sua.
- **Nível 3** (cérebro compartilhado): o contexto vive num repositório GitHub. OpenClaw lê. Claude Code lê. Cursor lê. Qualquer ferramenta futura vai ler. **O cérebro é seu.**

📊 → `slides/02-arquitetura.html`

Aqui mostra o diagrama: GitHub no centro, ferramentas ao redor. A frase que ancora:

> *"Braços mudam. Cérebro fica."*

🎬 **Demo agora:**
Abra o browser em `github.com/pixel-educacao/imersao-openclaw-negocios`. Navega pela estrutura de pastas — mostra o `cerebro/` no root. Abre `cerebro/agentes/COMO-CONECTAR.md` rapidamente. Não precisa ler linha a linha — só mostrar que existe um arquivo que diz pra qualquer agente como se conectar ao cérebro.

**Transição:** *"Vamos destrinchar esse cérebro. Cada pasta tem um papel muito específico."*

---

### Bloco 2: Tour pelo Cérebro — 9h35 (25 min)

**Quando ativar:** Bruno der o "próximo" após o Bloco 1.

---

**O agente diz:**

Agora o tour. O objetivo aqui é simples: quando o participante sair desse bloco, ele tem que conseguir visualizar mentalmente onde cada coisa da empresa dele vai morar.

📊 → `slides/03-cerebro-estrutura.html`

Enquanto esse slide está na tela, percorre cada pasta assim — curto e direto:

- `empresa/` → quem você é. Missão, produto, equipe, métricas. O agente lê isso antes de qualquer coisa.
- `areas/` → o que você faz. Cada área tem seu próprio contexto, skills e rotinas.
- `agentes/` → quem opera. Cada agente com personalidade e permissões próprias.
- `seguranca/` → quem pode o quê.
- `dados/` → onde ficam os dados brutos — CSV primeiro, API depois.
- `guias/` → documentação para humanos e para agentes.

🎬 **Demo dupla — o grande efeito visual:**

No terminal:
```
cd cerebro && tree -L 2
```
Mostra a estrutura completa. Abre na sequência: `empresa/contexto/empresa.md` → `equipe.md` → `metricas.md`. Vai lendo os campos em voz alta — nome da empresa, MRR, conversão. Deixa claro: *"O agente lê isso antes de responder qualquer coisa."*

Agora o momento que vai impactar:

Digita no OpenClaw (Telegram): *"Qual o MRR atual da empresa?"*
— Agente responde com o número do arquivo. —

Abre o Claude Code, mesma pergunta.
— Mesma resposta. —

Pausa. Deixa cair.
*"Dois agentes. Um cérebro. Mesma resposta. Isso é o que muda o jogo."*

**Transição:** *"O cérebro sabe quem você é. Mas agente bom não é só aquele que SABE — é o que FAZ. Pra isso existem as skills."*

---

### Bloco 3: Skills — 🔥 1º AHA MOMENT — 10h00 (30 min)

**Quando ativar:** Bruno der o "próximo" após o Bloco 2.

---

**O agente diz:**

Esse é o primeiro grande momento da imersão. Skills são o que transformam o cérebro de repositório de contexto em **máquina de trabalho**. Uma skill bem feita roda hoje, amanhã e todo dia — sem ninguém pedir.

📊 → `slides/04-skill-anatomia.html`

A metáfora que funciona: skill é uma **receita de cozinha**. Você escreve uma vez. Qualquer agente executa quando você chamar. Input → processo → output. Igual uma função de código, mas em linguagem natural.

🎬 **Demo passo a passo:**

1. Abre `cerebro/empresa/skills/_templates/SKILL-TEMPLATE.md` — mostra o esqueleto: objetivo, input, processo, output.

2. Abre `cerebro/areas/vendas/skills/relatorio-vendas/SKILL.md` — percorre cada seção em voz alta:
   - Input: planilha de vendas em CSV
   - Processo: análise por vendedor, ticket médio, comparativo com mês anterior
   - Output: relatório formatado com destaques e alertas

3. Mostra `cerebro/dados/vendas.csv` no editor — dados reais, nomes fictícios. *"Começamos com CSV. É o suficiente pra o sistema funcionar hoje."*

4. Agora o AHA:

Digita pro agente: *"Gera o relatório de vendas baseado no vendas.csv"*

— Agente lê a SKILL.md → lê o CSV → gera análise completa. —

Para. 3 segundos de silêncio.

*"O agente leu a receita, pegou os dados, e gerou a análise. Você não escreveu uma linha de código. Essa skill roda hoje. Amanhã. Todo dia. Sem você estar presente."*

**Transição:** *"Vocês viram que eu escrevi essa skill na mão. Levou talvez 20 minutos. Mas... e se o agente criasse skills sozinho?"*

---

### ☕ Pausa — 10h30 (10 min)

**Quando ativar:** Bruno indicar pausa.

---

**O agente diz:**

Pausa de 10 minutos — volta às 10h40.

Cayo, aproveita pra coletar as top 3 perguntas do chat agora. Vou usar elas pra abrir o Bloco 4.

Bruno, enquanto isso: testa o skill-creator no terminal antes de voltar. Digita um comando simples só pra confirmar que está respondendo. O Bloco 4 começa com ele ao vivo.

Nos vemos em 10.

---

### Bloco 4: Skill Creator — 🔥 2º AHA MOMENT — 10h40 (35 min)

**Quando ativar:** Bruno voltar da pausa.

---

**O agente diz:**

Bem-vindos de volta. Antes de continuar — Cayo, quais foram as top 3 perguntas do chat?

*(Aguarda Bruno/Cayo passar as perguntas. Responde cada uma em 60 segundos. Se for técnica demais: "Cobre isso no material pós-imersão — continua.")*

Agora o segundo AHA. O skill-creator é uma skill que **cria outras skills**. Você descreve em linguagem natural o que quer automatizar — o agente gera a skill completa, pronta pra usar.

📊 → `slides/05-skill-creator.html`

Esse slide é visual — deixa ele na tela enquanto faz a demo. O que importa não é o slide, é o que vai acontecer no terminal agora.

🎬 **Demo:**

Digita pro agente:
*"Cria uma skill que analise minha planilha de leads e me diga quais estão esfriando — leads que entraram há mais de 7 dias sem follow-up"*

— Agente processa → gera `SKILL.md` completo em `cerebro/areas/vendas/skills/leads-esfriando/`. —

Abre o arquivo gerado ao vivo. Mostra: Input, Processo, Output — tudo estruturado.

Agora testa imediatamente:
*"Roda a skill de leads esfriando no arquivo leads.csv"*

— Agente executa. Resultado aparece. —

*"Linguagem natural virou automação funcional em 30 segundos. Sem código."*

🎬 **Interação ao vivo com o chat:**

*"Manda no chat: qual skill vocês gostariam de ter na empresa de vocês?"*

Cayo filtra. Bruno escolhe 1 ou 2 que sejam viáveis. Cria ao vivo usando o skill-creator.

*"Isso que vocês acabaram de pedir — agora existe. Na empresa de vocês."*

**Transição:** *"Skills resolvem o QUÊ fazer. Crons resolvem o QUANDO. E se o agente fizesse isso todo dia sem você pedir?"*

---

### Bloco 5: Rotinas e Crons — 11h15 (20 min)

**Quando ativar:** Bruno der o "próximo" após o Bloco 4.

---

**O agente diz:**

Cron é agendamento. O agente executa uma skill no horário que você definir — sem ninguém pedir. Todo dia às 9h, relatório de vendas no Telegram. Toda segunda, relatório de leads. Você dorme, o agente trabalha.

📊 → `slides/06-crons.html`

Enquanto o slide está na tela, abre `cerebro/areas/vendas/rotinas/relatorio-vendas-diario.md` — mostra os campos: horário, skill, canal, destinatário. *"Esse arquivo diz: todo dia às 9h, roda a skill relatorio-vendas e manda o resultado no Telegram."*

🎬 **Demo:**

Cria o cron ao vivo:
```
openclaw cron create --name "relatorio-vendas-diario" --schedule "0 9 * * *" --skill relatorio-vendas
```
*"Criado. Amanhã às 9h vai rodar sozinho."*

Abre `cerebro/areas/operacoes/rotinas/heartbeat.md` — esse é especial. *"Esse agente monitora a si mesmo a cada 6h. Verifica se todos os crons rodaram, se houve erro, se os arquivos estão atualizados. Se detectar problema — notifica no Telegram."*

Mostra um log de heartbeat (ou simula): *"Às 6h, 12h, 18h e meia-noite — checou tudo. Você nem soube. Nada quebrou."*

**Transição:** *"O agente está lendo arquivos da empresa, rodando automações, mandando mensagens. Quem garante que ele não vai extravasar? Essa é a próxima conversa."*

---

### Bloco 6: Segurança — 11h35 (15 min)

**Quando ativar:** Bruno der o "próximo" após o Bloco 5.

---

**O agente diz:**

Segurança é onde a maioria das implementações de IA erra — ou não implementa nada, ou fica com medo e não implementa nada. O OpenClaw tem 3 camadas. Vou mostrar as 3.

📊 → `slides/07-seguranca.html`

As 3 camadas enquanto o slide está na tela:

- **Camada 1 — Dados locais:** tudo fica na sua máquina ou no seu repo privado. O modelo processa, mas não armazena. Seus dados de vendas não vivem em nuvem de terceiro.
- **Camada 2 — Modo ask:** para qualquer ação irreversível, o agente pede permissão. Deletar arquivo, enviar mensagem externa, fazer commit — ele pergunta antes.
- **Camada 3 — Controle granular:** cada agente acessa só o que você permitiu. Bot de suporte não vê financeiro. Agente de marketing não vê RH.

🎬 **Demo — Modo ask ao vivo:**

Pede pro agente: *"Deleta o arquivo teste.md"*
— Agente pergunta: "Confirma que quer deletar teste.md? (sim/não)" —
*"Ele não age sozinho em coisas que importam."*

Abre `cerebro/agentes/assistente/AGENTS.md` — mostra a seção `allow` e `deny`. *"Esse agente pode ler tudo de empresa/ e areas/. Mas não toca em seguranca/ nem faz push pro GitHub sem aprovação."*

---

### Fechamento Dia 1 — 11h50 (10 min)

**Quando ativar:** Bruno sinalizar fechamento.

---

**O agente diz:**

Fechamento do Dia 1. Encerramos com tudo que importa pro sistema funcionar:

✅ Cérebro compartilhado no GitHub — o contexto é seu, não da ferramenta
✅ Skills — automações em linguagem natural, rodam sozinhas
✅ Skill-creator — qualquer tarefa vira skill em 30 segundos
✅ Crons — o sistema roda sem ninguém pedir
✅ Segurança em 3 camadas — controle sem paranoia

**Tarefa pro amanhã:** *"Abram a planilha principal da empresa de vocês — vendas, leads ou métricas. Organizem os dados em colunas claras. Amanhã vamos conectar isso ao sistema."*

*"Amanhã: multi-agente, permissionamento, sistema completo de marketing e o bot de suporte que aprende sozinho com a operação. 9h BRT, pontual."*

---

---

## DIA 2 — 29/03/2026

> **Meta:** Participantes veem um sistema multi-agente funcionando e saem com roadmap concreto dos próximos 30 dias.

---

### ▶ Abertura + Recap — 9h00 (15 min)

**Quando ativar:** início do Dia 2.

---

**O agente diz:**

Dia 2. Vamos começar com recap rápido do que fizemos ontem — e depois dar o salto: de 1 agente para um sistema.

Recap em 3 bullets pra você trazer em 30 segundos cada:
- *"Criamos o cérebro — o repo que centraliza tudo da empresa."*
- *"Criamos skills — o agente executa tarefas complexas com uma frase."*
- *"Configuramos crons — o sistema trabalha enquanto você dorme."*

Depois colhe do chat: *"Alguém organizou a planilha ontem? Manda no chat como foi."* Comenta 2–3 respostas rapidamente — cria continuidade entre os dias.

**Transição:** *"Hoje damos o salto: de 1 agente para um sistema. Múltiplos agentes, cada um no seu papel."*

---

### Bloco 7: Multi-agente — 9h15 (30 min)

**Quando ativar:** Bruno der o sinal de início após a abertura.

---

**O agente diz:**

Ontem trabalhamos com 1 agente generalista. Ele faz tudo — mas não é especialista em nada. Hoje vamos montar um sistema: cada agente com personalidade, escopo e acesso diferentes. É igual uma equipe real. Você não pede pro vendedor fazer o suporte.

📊 → `slides/08-multi-agente.html`

Enquanto o slide está na tela, abre `cerebro/agentes/assistente/SOUL.md` — lê as primeiras linhas de "Como eu opero". Esse é o assistente geral: equilibrado, acesso amplo, responde de tudo um pouco.

Agora abre `cerebro/agentes/marketing/SOUL.md` — tom completamente diferente. Obcecado com métricas de performance. Fala de ROAS, CTR, criativos. Prioridades diferentes.

🎬 **Demo lado a lado:**

Mesma pergunta para os dois agentes: *"Qual próximo criativo faz sentido produzir?"*

Assistente geral → genérico, balanceado, pergunta sobre recursos e prioridades.
Agente de marketing → específico, menciona ROAS atual, criativos com melhor CTR, formato recomendado.

*"Mesma pergunta. Respostas completamente diferentes. Cada um no seu papel."*

No terminal:
```
ls cerebro/agentes/
```
*"Cada pasta é um agente. Cada um com SOUL.md próprio."*

**Transição:** *"Múltiplos agentes, ótimo. Como garantir que cada um fica no seu quadrado? Isso é permissionamento."*

---

### Bloco 8: Permissionamento — 9h45 (20 min)

**Quando ativar:** Bruno der o "próximo" após o Bloco 7.

---

**O agente diz:**

Duas arquiteturas possíveis para times. Você escolhe qual faz sentido para a sua empresa.

📊 → `slides/09-permissionamento.html`

Enquanto o slide está na tela:

- **Arquitetura A — Grupos separados:** um grupo Telegram por área. Agente de marketing no grupo de marketing. Bot de suporte no grupo de suporte. Isolamento total.
- **Arquitetura B — Tópicos:** um grupo com tópicos. Um agente responde só no tópico dele. Mais simples de gerenciar.

Para times pequenos: B. Para times com dados sensíveis separados (ex: financeiro e RH isolados): A.

🎬 **Demo — acesso negado:**

Abre `cerebro/agentes/marketing/AGENTS.md` — mostra o `scope` com os paths permitidos. Esse agente acessa só `areas/marketing/`. Nada mais.

Agora pede pro agente de marketing: *"Qual foi o MRR do mês passado?"*
— Agente responde: "Não tenho acesso a dados financeiros. Posso ajudar com métricas de marketing." —

*"Não é que ele não sabe. É que ele não PODE. E avisa."*

Mostra `cerebro/seguranca/permissoes.md` — tabela completa: agente × recurso × nível de acesso.

**Transição:** *"Agora que entendemos o sistema, vamos ver ele funcionando num caso real e completo: marketing de performance."*

---

### Bloco 9: Deep Dive Marketing — 10h05 (35 min)

**Quando ativar:** Bruno der o "próximo" após o Bloco 8.

---

**O agente diz:**

Marketing de performance tem um ciclo: hipótese → criativo → teste → dado → conclusão → nova hipótese. Esse ciclo hoje depende de uma pessoa olhando planilha todo dia. Com o sistema, roda sozinho. 3 skills + 3 crons = ciclo automatizado.

📊 → `slides/10-marketing-ciclo.html`

Enquanto o slide está na tela, abre `cerebro/areas/marketing/sub-areas/trafego-pago/PROCESSO.md` — *"Esse arquivo documenta como o marketing funciona aqui. O agente lê isso antes de qualquer análise."*

📊 → `slides/11-daily-report.html`

*"Todo dia às 8h, antes de qualquer pessoa da equipe acordar, o agente já gerou esse relatório. O gestor de tráfego abre o Telegram — relatório já está lá. Com alertas, destaques, sugestões."*

🎬 **Demo — dados mockados, zero risco de expor API:**

A skill `relatorio-ads` detecta automaticamente que não há `META_ADS_TOKEN` configurado e lê o CSV local. O participante vê o sistema funcionando sem precisar de credencial ao vivo.

Abre `cerebro/areas/marketing/skills/relatorio-ads/SKILL.md` — mostra o trecho:
*"Se META_ADS_TOKEN não configurado → lê de `imersao/dados-demo/meta-ads-campanhas.csv`"*

*"Em produção você configura a chave da sua conta Meta Ads. Para o demo, os dados já estão aqui."*

Executa ao vivo:
*"Gera o relatório de Meta Ads dos últimos 7 dias"*
— Agente lê o CSV → processa → gera relatório formatado. —

Mostra `imersao/dados-demo/relatorio-meta-ads-exemplo.md`:
*"É exatamente isso que chegou no Telegram às 8h desta manhã. A01 em escala, A05 crescendo, A06 em aprendizado. Sem alguém olhando planilha."*

📊 → `slides/12-pipeline-criativos.html`

*"Cada criativo passa por essas fases. O agente acompanha e documenta: em teste → aprendizado → escalando."*

Pergunta pro agente de marketing: *"Com base nos learnings atuais, qual próximo criativo faz sentido criar essa semana?"*
— Agente lê `learnings/resumo.md` + testes abertos → sugere criativo com justificativa baseada em dados. —

*"Ele não chutou. Leu os learnings, os testes, os dados — e sugeriu com evidência."*

---

### ☕ Pausa — 10h40 (10 min)

**Quando ativar:** Bruno indicar pausa.

---

**O agente diz:**

Última pausa. Volta às 10h50 com o maior AHA moment da imersão.

Cayo: testa o bot de suporte agora — manda 2–3 mensagens pra garantir que está respondendo. O Bloco 10 começa com ele ao vivo.

Bruno: verifica que o ambiente do bot está OK. Confirma que `duvidas.md` está vazio — a demo do loop de aprendizado precisa começar do zero.

---

### Bloco 10: Bot de Suporte — 🔥 3º AHA MOMENT — 10h50 (35 min)

**Quando ativar:** Bruno voltar da pausa.

---

**O agente diz:**

Bot de suporte comum: você treina uma vez, fica desatualizado, vira problema. Esse bot aprende sozinho com a operação. Cada dúvida respondida vira conhecimento permanente.

O loop: FAQ → cliente pergunta → se está no FAQ, responde → se não está, marca como pendente → humano responde → cron consolida no FAQ → FAQ evolui.

O bot de amanhã sabe mais do que o de hoje. Sem código. Sem retreinar.

📊 → `slides/13-bot-suporte-loop.html`

Enquanto o slide está na tela — mostra o diagrama do loop. Não precisa explicar tudo: o visual já fala.

🎬 **Demo completa do loop:**

Abre `cerebro/agentes/bot-suporte/SOUL.md` — lê 3–4 linhas do tom. *"É assim que ele fala com o cliente."*

Abre `cerebro/areas/atendimento/bot/faq.md` — *"Isso é tudo que o bot sabe hoje."* Mostra 2–3 exemplos.

**Parte 1 — Dúvida no FAQ:**
Manda pro bot: *"Qual o prazo de entrega do curso?"*
— Bot responde imediatamente com base no faq.md. —

**Parte 2 — A dúvida nova (o loop ao vivo):**
Manda pro bot: *"Vocês têm desconto para grupos de empresa?"*
— Bot não encontra → responde que vai verificar → registra em `duvidas.md` → notifica equipe no Telegram. —

Abre `cerebro/areas/atendimento/bot/duvidas.md` ao vivo — *"Apareceu aqui. Status: pendente. Pergunta original preservada."*

Responde a dúvida direto no arquivo — edita o status pra `respondido`, adiciona a resposta. *"20 segundos."*

Mostra `cerebro/areas/atendimento/rotinas/consolidar-faq.md` — *"Todo dia às 18h esse cron roda. Pega todas as dúvidas respondidas e adiciona ao faq.md. Amanhã, quando o próximo cliente perguntar sobre desconto — o bot já vai saber."*

Pausa longa. Deixa cair.

*"Cada dúvida respondida pelo humano vira conhecimento permanente do bot. Sem código. Sem retreinar. Sem abrir ticket de TI. Em 30 dias, 80% das dúvidas respondidas sozinho. Em 90 dias, 95%."*

**Transição:** *"Vocês viram o sistema inteiro. Agora: como começar?"*

---

### Bloco 11: Por Onde Começar — 11h25 (25 min)

**Quando ativar:** Bruno der o "próximo" após o Bloco 10.

---

**O agente diz:**

Vocês viram o sistema inteiro. Agora a pergunta prática: por onde eu começo?

A resposta é simples — use o Wizard. Você não precisa montar nada manualmente.

📊 → `slides/14-roadmap-30dias.html`

Enquanto o slide está na tela, mostra o comando e explica o que acontece em cada etapa:

- **Contexto da empresa** — agente faz as perguntas, preenche empresa.md, equipe.md, metricas.md
- **Contexto das áreas** — você diz quais áreas existem, ele cria a estrutura
- **Skills por área** — você descreve o que quer automatizar, ele usa o skill-creator
- **Primeiros crons** — agenda as skills que devem rodar sozinhas
- **Segundo agente** (se necessário) — SOUL e escopo configurados para a área mais crítica
- **Validar e publicar** — primeiro commit, sistema no ar

🎬 **Demo ao vivo:**

Cole o comando no agente: *"Leia wizard/README.md e me guie pra configurar meu cérebro"*

Mostra o Step 1 iniciando automaticamente — agente já começa a fazer as perguntas sobre a empresa.

*"O wizard é o onboarding. Você conversa, o agente preenche. Não tem arquivo pra criar na mão."*

Pergunta pro chat: *"Qual área vocês vão configurar primeiro?"* — comenta 3–4 respostas.

---

### Fechamento + Pitch — 11h50 (10 min)

**Quando ativar:** Bruno sinalizar fechamento.

---

**O agente diz:**

Em 2 dias, vocês viram o sistema inteiro funcionando — com dados reais, sem PowerPoint.

📊 → `slides/15-fechamento.html`

Recap da imersão inteira enquanto o slide está na tela:

✅ **Cérebro** — repo GitHub que centraliza tudo
✅ **Skills** — automações em linguagem natural
✅ **Skill-creator** — skills em 30 segundos
✅ **Crons** — o sistema roda sozinho
✅ **Multi-agente** — cada um no seu papel
✅ **Permissionamento** — cada agente só acessa o que pode
✅ **Marketing** — ciclo completo automatizado
✅ **Bot de suporte** — aprende sozinho com a operação

*"Tudo isso funciona. Vocês viram ao vivo. Não é promessa — é demo."*

**PITCH — Pixel IA**

Cayo posta o link no chat nesse momento. Você apresenta:

*"Para quem quer continuar evoluindo e manter a empresa sempre atualizada em IA — apresento o Pixel IA."*

4 pontos do produto enquanto o slide mostra os benefícios:
- Mentorias em grupo semanais — *"você não fica parado esperando o próximo lançamento"*
- Acesso às formações — *"todo o conteúdo disponível, no seu ritmo"*
- Comunidade com trocas — *"aprenda com outros empresários implementando IA"*
- Newsletter semanal — *"o que importa no mundo de IA, filtrado e resumido"*

**[Preço a definir com Bruno e Cayo antes da imersão]**

Encerramento: *"Agora é hora de construir. O wizard está esperando."*

---

---

## Comandos Disponíveis

| Comando | O que o agente faz |
|---------|-------------------|
| `"próximo"` / `"avança"` | Entrega o próximo bloco completo |
| `"recap"` | Resume o que já foi coberto |
| `"quanto tempo?"` | Diz quanto tempo resta no bloco (informe o horário atual) |
| `"pergunta do chat: [pergunta]"` | Responde a pergunta em 60 segundos para Bruno usar no chat |
| `"plano B"` | Alternativa para se a demo do bloco atual falhar |
| `"pausa"` | Marca pausa e orienta o que checar antes de voltar |
| `"status"` | Bloco atual, horário, o que já foi feito, o que falta |
| `"resumo pro chat"` | Gera mensagem de recap para o Cayo postar no chat dos participantes |

---

## Planos B

| Situação | O que fazer |
|----------|-------------|
| Agente não responde | Abrir Claude Code apontando pro mesmo `cerebro/` — mesmo resultado |
| GitHub fora do ar | Mostrar repo clonado localmente no terminal — `tree cerebro/ -L 2` |
| Skill-creator falhou | Abrir skill já criada em `cerebro/areas/vendas/skills/relatorio-vendas/SKILL.md` — *"Isso é o que ele gera"* |
| Bot de suporte não responde | Mostrar `faq.md` e `duvidas.md` no terminal — explicar o loop verbalmente |
| Internet caiu | Hotspot celular. Cayo avisa o chat com horário de retorno. |
| API Meta Ads falhar | Abrir relatório pré-gerado salvo em `cerebro/areas/marketing/sub-areas/trafego-pago/` |

---

*Versão: 2.0 | Atualizado: 2026-03-28*
*Uso: Imersão OpenClaw nos Negócios — 28-29/03/2026*
