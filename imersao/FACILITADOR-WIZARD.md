# Wizard do Facilitador — Imersão OpenClaw nos Negócios

> Este arquivo guia o facilitador (Bruno) durante a imersão ao vivo.
> Cole este comando no seu agente para começar:
> **"Leia imersao/FACILITADOR-WIZARD.md e me guie pela imersão"**

---

## Como funciona

Eu (agente) vou guiar você bloco a bloco. A cada momento, vou dizer:

1. **O que projetar** — qual HTML abrir no browser
2. **O que falar** — pontos-chave para cobrir
3. **O que fazer** — comandos/demos ao vivo
4. **NÃO falar** — armadilhas a evitar (quando relevante)
5. **Transição** — frase de gancho pro próximo bloco

Quando estiver pronto para avançar, diga **"próximo"** ou **"avança"**.

---

## DIA 1 — 28/03/2026

> **Meta do dia:** Participantes entendem o cérebro, criam a primeira skill e veem crons rodando.

---

### ▶ Abertura (9:00–9:15)

**Projetar:** `slides/00-abertura.html`

**Falar:**
- Boas-vindas. 2 dias, 100% demo, zero PowerPoint
- "Vocês não vão ver slide. Vão ver funcionando na empresa de vocês"
- Apresentar Bruno (criador) + Cayo (CEO/facilitador de chat) — 30 segundos cada
- Ativar participação: **"Mandem no chat: qual área da empresa vocês mais querem automatizar? Vendas, marketing, atendimento ou operações?"**
- Combinar: responder 3 perguntas do chat a cada pausa

**Fazer:** Nada técnico. Só presença e energia.

**Transição:** "Antes de mostrar a solução, preciso que vocês sintam o problema. Quem já perdeu 10 minutos re-explicando contexto pro ChatGPT levanta a mão..."

---

### Bloco 1: O Problema e a Arquitetura (9:15–9:35)

**⏱ Duração:** 20 minutos

**Projetar:** `slides/01-problema.html`

**Falar — Os 3 níveis de memória:**
- **Nível 1 — Amnésia total:** "Todo chat começa do zero. O agente não sabe quem você é, o que você vende, quem é seu cliente. Você explica tudo de novo toda vez."
- **Nível 2 — Memória no agente:** "Aí você configura o system prompt. Melhora. Mas agora você tá preso àquela ferramenta. Muda pro Claude, perde tudo."
- **Nível 3 — Cérebro compartilhado:** "E se o contexto ficasse num lugar que qualquer ferramenta acessa? Um repo GitHub que é o cérebro da empresa. OpenClaw lê. Claude Code lê. Cursor lê. O cérebro é seu."

**Trocar para:** `slides/02-arquitetura.html`

**Falar:**
- Mostrar diagrama: GitHub no centro, ferramentas ao redor
- "O repo é o cérebro. OpenClaw, Claude Code, Cursor — são os braços. Braços mudam. Cérebro fica."
- "Hoje vocês vão ver esse cérebro funcionando com dados reais"

**Fazer:**
1. Abrir o repo no browser: `github.com/pixel-educacao/imersao-openclaw-negocios`
2. Navegar pela estrutura de pastas — mostrar `cerebro/` no root
3. Abrir `cerebro/agentes/COMO-CONECTAR.md` — "É aqui que qualquer agente aprende a se conectar ao cérebro"

**NÃO falar:**
- Como criar conta no GitHub
- Como instalar OpenClaw / Claude Code
- Detalhes técnicos de git (clone, push, etc.)
- Preço de qualquer ferramenta

**Transição:** "Agora vamos destrinchar esse cérebro. Cada pasta tem um papel. Vou mostrar."

---

### Bloco 2: Tour pelo Cérebro (9:35–10:00)

**⏱ Duração:** 25 minutos

**Projetar:** `slides/03-cerebro-estrutura.html`

**Falar — A anatomia do cérebro:**
- "Esse é o mapa. Cada pasta tem um papel muito específico."
- `cerebro/empresa/` → quem você é (contexto, missão, equipe, métricas)
- `cerebro/areas/` → o que você faz (vendas, marketing, atendimento, operações)
- `cerebro/agentes/` → quem opera (cada agente com sua personalidade e permissões)
- `cerebro/seguranca/` → quem pode o quê (controle de acesso)
- `cerebro/dados/` → onde ficam os dados brutos (CSVs, JSONs)
- `cerebro/guias/` → documentação para humanos e agentes

**Fazer — Demo dupla (o grande efeito visual):**

1. No terminal:
   ```bash
   cd cerebro && tree -L 2
   ```
   Mostrar a estrutura completa na tela

2. Abrir `cerebro/empresa/contexto/empresa.md`
   - "Esse arquivo é quem a empresa é. Nome, segmento, produto, posicionamento. O agente lê isso antes de qualquer coisa."

3. Abrir `cerebro/empresa/contexto/equipe.md`
   - "E aqui está quem trabalha aqui. O agente sabe os nomes, os papéis, os contatos."

4. Abrir `cerebro/empresa/contexto/metricas.md`
   - "E aqui os números que importam. MRR, leads, conversão."

5. **Demo ao vivo — Parte 1:** Perguntar no OpenClaw (Telegram):
   - Digitar: _"Qual o MRR atual da empresa?"_
   - Agente responde com o número do `metricas.md`
   - "Ele sabia porque leu o arquivo. Não inventou."

6. **Demo ao vivo — Parte 2:** Abrir Claude Code, mesma pergunta:
   - Digitar: _"Qual o MRR atual da empresa?"_
   - Mesma resposta
   - "**Dois agentes. Um cérebro. Mesma resposta.** Isso é o que muda o jogo."

**NÃO falar:**
- Como editar markdown na mão
- Sintaxe de YAML ou frontmatter
- Como configurar o repo pela primeira vez (isso é pós-imersão)

**Transição:** "O cérebro sabe quem você é. Mas agente bom não é só aquele que SABE — é o que FAZ. Pra isso existem as skills..."

---

### Bloco 3: Skills — 🔥 1º AHA MOMENT (10:00–10:30)

**⏱ Duração:** 30 minutos

**Projetar:** `slides/04-skill-anatomia.html`

**Falar:**
- "Skill é uma receita. Você escreve uma vez. O agente executa toda hora."
- "Input → Processo → Output. Igual uma função de código, mas em linguagem natural."
- "A skill diz: 'Quando eu pedir relatório de vendas, você vai: pegar esse arquivo, analisar essas colunas, gerar esse formato de saída.'"

**Fazer:**

1. Abrir `cerebro/empresa/skills/_templates/SKILL-TEMPLATE.md`
   - "Esse é o template. Toda skill tem esse esqueleto: objetivo, input, processo, output."

2. Abrir `cerebro/areas/vendas/skills/relatorio-vendas/SKILL.md`
   - Percorrer cada seção em voz alta:
     - **Input:** planilha de vendas em CSV
     - **Processo:** análise por vendedor, ticket médio, comparativo com mês anterior
     - **Output:** relatório formatado com destaques e alertas

3. "Agora vamos conectar com dados reais"

4. Mostrar `cerebro/dados/vendas.csv` — abrir no editor
   - "Começamos simples, com CSV. Dados reais, nomes fictícios."

5. Mostrar `cerebro/dados/README.md`
   - "Depois que o sistema estiver rodando, você conecta Google Sheets. O CSV é pra começar rápido."

6. **🔥 Demo ao vivo — O 1º AHA MOMENT:**
   - Digitar pro agente: _"Gera o relatório de vendas baseado no vendas.csv"_
   - Agente lê `SKILL.md` → lê `vendas.csv` → gera relatório completo com análise
   - Parar. Silêncio de 3 segundos.
   - "Isso. O agente LEU a receita, pegou os dados, e gerou análise. Você não escreveu uma linha de código."
   - "Essa skill roda hoje. Amanhã. Todo dia. Sem você estar presente."

**NÃO falar:**
- Como configurar OAuth do Google Sheets (bloco específico pós-imersão)
- Detalhes de como o modelo interpreta o markdown
- Comparação com n8n ou outras ferramentas de automação

**Transição:** "Vocês viram que eu escrevi essa skill na mão. Levou talvez 20 minutos. Mas... e se o agente pudesse criar skills SOZINHO?"

---

### ☕ Pausa (10:30–10:40)

**Projetar:** `slides/00-abertura.html` (tela de espera com timer)

**Cayo faz:** Coleta as top 3 perguntas do chat. Anota num papel ou doc.

**Bruno faz:** Água. Respirar. Revisar mentalmente o Bloco 4. Testar no terminal que o skill-creator está funcionando.

**Voltar:** 10:40 em ponto.

---

### Bloco 4: Skill Creator — 🔥 2º AHA MOMENT (10:40–11:15)

**⏱ Duração:** 35 minutos

**Projetar:** `slides/05-skill-creator.html`

**Falar — Responder perguntas (5 min):**
- Cayo passa as 3 perguntas. Responder cada uma em 60 segundos.
- Se a pergunta for técnica demais: "Ótima pergunta. A gente cobre isso no material pós-imersão. Continua."

**Falar — Introdução ao skill-creator:**
- "O skill-creator é uma skill que cria outras skills."
- "Você descreve em linguagem natural o que quer automatizar. O agente gera a skill completa."
- "Não precisa saber a estrutura. Não precisa de template. Só descrever."

**Fazer:**

1. No terminal ou Telegram, pedir pro agente:
   - _"Cria uma skill que analise minha planilha de leads e me diga quais estão esfriando — ou seja, leads que entraram há mais de 7 dias e não tiveram follow-up"_

2. Agente usa o skill-creator → processa → gera `SKILL.md` completo em `cerebro/areas/vendas/skills/leads-esfriando/`

3. Abrir o arquivo gerado ao vivo:
   - "Olha o que ele criou. Input, processo, output. Pronto pra usar."

4. **Testar a skill imediatamente:**
   - _"Roda a skill de leads esfriando no arquivo leads.csv"_
   - Agente executa e retorna resultado

5. 🔥 "**2º AHA MOMENT.** Linguagem natural virou automação funcional em 30 segundos. Sem código."

6. **Interação ao vivo com o chat:**
   - "Mandem no chat: qual skill vocês gostariam de ter na empresa de vocês?"
   - Cayo filtra. Bruno escolhe 1 ou 2 sugestões viáveis.
   - Criar ao vivo usando skill-creator para cada uma.
   - "Isso que vocês acabaram de pedir — agora existe. Na empresa de vocês."

**NÃO falar:**
- Arquitetura interna do skill-creator (como ele é implementado)
- Limitações de tamanho de context window
- Comparação com agentes de outras plataformas

**Transição:** "Skills resolvem o QUÊ fazer. Crons resolvem o QUANDO fazer. E se o agente fizesse isso TODO DIA sem você pedir?"

---

### Bloco 5: Rotinas e Crons (11:15–11:35)

**⏱ Duração:** 20 minutos

**Projetar:** `slides/06-crons.html`

**Falar:**
- "Cron = agendamento. O agente executa uma skill no horário que você definir. Sem ninguém pedir."
- "Todo dia às 9h → relatório de vendas no Telegram. Toda segunda às 8h → relatório de leads. A cada 6h → checagem de saúde do sistema."
- "Você dorme. O agente trabalha."

**Fazer:**

1. Abrir `cerebro/areas/vendas/rotinas/relatorio-vendas-diario.md`
   - "Esse arquivo diz: todo dia às 9h, roda a skill `relatorio-vendas`, e manda o resultado no Telegram."
   - Ler os campos em voz alta: `horario`, `skill`, `canal`, `destinatario`

2. "Agora vamos criar isso ao vivo"
   ```bash
   openclaw cron create --name "relatorio-vendas-diario" --schedule "0 9 * * *" --skill relatorio-vendas
   ```
   - "Criado. Amanhã às 9h vai rodar sozinho."

3. Abrir `cerebro/areas/operacoes/rotinas/heartbeat.md`
   - "Esse é especial. O agente monitora a SI MESMO a cada 6h."
   - "Verifica se todos os crons rodaram, se houve erro, se os arquivos estão atualizados."
   - "Se detectar problema → notifica no Telegram."

4. Mostrar um log de heartbeat anterior (ou simular):
   - "Às 6h, às 12h, às 18h, à meia-noite — esse agente checou tudo. Você nem soube. Nada quebrou."

**NÃO falar:**
- Sintaxe cron detalhada (0 9 * * * etc.) — só mostrar o funcionamento
- Como configurar servidor para rodar crons
- Diferença entre cron do sistema e cron do OpenClaw

**Transição:** "Mas espera. O agente está lendo arquivos da empresa, rodando automações, mandando mensagens. Quem garante que ele não vai extravasar? Essa é a próxima conversa..."

---

### Bloco 6: Segurança (11:35–11:50)

**⏱ Duração:** 15 minutos

**Projetar:** `slides/07-seguranca.html`

**Falar — As 3 camadas:**
- **Camada 1 — Dados locais:** "Tudo fica na sua máquina ou no seu repo privado. Não existe nuvem de terceiros com seus dados de vendas."
- **Camada 2 — Modo ask:** "Para qualquer ação irreversível — deletar arquivo, enviar mensagem externa, fazer commit — o agente PEDE permissão. Você aprova ou nega."
- **Camada 3 — Controle granular:** "Cada agente só acessa o que você permitiu. O bot de suporte não vê dados financeiros. O agente de marketing não vê dados de RH."

**Fazer:**

1. Mostrar onde os dados ficam:
   - "Pasta `cerebro/` — local ou repo privado. O modelo da Anthropic/OpenAI processa os dados mas não armazena."

2. Mostrar modo ask funcionando:
   - Pedir pro agente fazer algo que exige confirmação: _"Deleta o arquivo teste.md"_
   - Agente pergunta: "Confirma que quer deletar `teste.md`? (sim/não)"
   - "Ele não age sozinho em coisas que importam."

3. Abrir `cerebro/agentes/assistente/AGENTS.md`:
   - Mostrar a seção `allow` e `deny`
   - "Esse agente pode ler tudo de `empresa/` e `areas/`. Mas não pode tocar em `seguranca/` nem fazer push pro GitHub sem aprovação."

**NÃO falar:**
- Criptografia de chaves (AES, RSA, etc.)
- Detalhes de infraestrutura de servidores
- Comparação com soluções enterprise de segurança

---

### Fechamento Dia 1 (11:50–12:00)

**Projetar:** `slides/00-abertura.html`

**Falar:**
- "Em 3 horas vocês viram: o cérebro, as skills, o skill-creator, os crons e a segurança."
- "Isso não é teoria. Vocês viram funcionar com dados reais."
- Recap em 5 bullets:
  - ✅ Cérebro compartilhado no GitHub
  - ✅ Skills = receitas que o agente executa
  - ✅ Skill-creator cria skills em 30 segundos
  - ✅ Crons rodam tudo sem você pedir
  - ✅ Segurança em 3 camadas

- **Tarefa pro amanhã:** "Abram a planilha principal da empresa de vocês — pode ser vendas, leads, ou métricas. Organizem os dados em colunas claras. Amanhã vamos conectar isso ao sistema."

- "Amanhã: multi-agente, permissionamento, sistema completo de marketing e o bot de suporte que aprende sozinho. 9h BRT, pontual."

---

---

## DIA 2 — 29/03/2026

> **Meta do dia:** Participantes veem um sistema multi-agente funcionando e saem com roadmap concreto dos próximos 30 dias.

---

### ▶ Abertura + Recap (9:00–9:15)

**Projetar:** `slides/00-abertura.html`

**Falar:**
- Recap Dia 1 em 3 bullets (30 segundos cada):
  - "Ontem criamos o cérebro. O repo que centraliza tudo."
  - "Criamos skills — automações em linguagem natural."
  - "Configuramos crons — o agente trabalha enquanto vocês dormem."
- "Hoje damos o salto: de 1 agente para um SISTEMA. Múltiplos agentes, cada um no seu papel."
- **Colher da tarefa:** "Alguém organizou a planilha ontem? Manda no chat como foi. Quero ver."
- Comentar 2-3 respostas do chat rapidamente.

---

### Bloco 7: Multi-agente (9:15–9:45)

**⏱ Duração:** 30 minutos

**Projetar:** `slides/08-multi-agente.html`

**Falar:**
- "Ontem tinham 1 agente generalista. Ele faz tudo, mas não é especialista em nada."
- "Hoje vão ter um sistema. Cada agente com personalidade, escopo e acesso diferentes."
- "Assistente geral. Agente de marketing. Bot de suporte. Agente de vendas. Cada um no seu papel."
- "É igual uma equipe. Você não pede pro vendedor fazer o suporte. Pede pro especialista."

**Fazer:**

1. Abrir `cerebro/agentes/assistente/SOUL.md`
   - "Esse é o assistente geral. Personalidade equilibrada, acesso amplo, responde de tudo um pouco."
   - Ler em voz alta as primeiras linhas de `Como eu opero`

2. Abrir `cerebro/agentes/marketing/SOUL.md`
   - "Esse é o agente de marketing. Obcecado com métricas de performance. Fala diferente. Prioriza diferente."
   - Ler o tom e as prioridades em voz alta

3. **Demo — A mesma pergunta, respostas diferentes:**
   - Perguntar pro assistente: _"Qual próximo criativo faz sentido produzir?"_
   - Resposta: genérica, balanceada, pergunta sobre recursos e prioridades
   - Mesma pergunta pro agente de marketing:
   - Resposta: específica, menciona ROAS atual, criativos com melhor CTR, formato recomendado
   - "Mesma pergunta. Respostas completamente diferentes. Cada um no seu papel."

4. Mostrar `cerebro/agentes/` — listar todos os agentes configurados:
   ```bash
   ls cerebro/agentes/
   ```
   - "Cada pasta é um agente. Cada um com SOUL.md próprio e AGENTS.md próprio."

**NÃO falar:**
- Como configurar OpenClaw para múltiplos canais Telegram
- Custo de rodar múltiplos agentes em paralelo
- Limitações técnicas de context window por agente

**Transição:** "Múltiplos agentes, ótimo. Mas como garantir que cada um fica no seu quadrado? Isso é permissionamento."

---

### Bloco 8: Permissionamento (9:45–10:05)

**⏱ Duração:** 20 minutos

**Projetar:** `slides/09-permissionamento.html`

**Falar:**
- "2 arquiteturas possíveis para times. Vocês escolhem qual faz sentido."
- **Arquitetura A — Grupos separados:** Um grupo Telegram por área. Agente de marketing no grupo de marketing. Bot de suporte no grupo de suporte. Isolamento total.
- **Arquitetura B — Tópicos:** Um grupo com tópicos (Telegram). Um agente responde só no tópico dele. Mais simples de gerenciar.
- "Os dois têm 2 camadas de segurança: permissões no AGENTS.md e isolamento de canal."

**Fazer:**

1. Abrir `cerebro/agentes/marketing/AGENTS.md`
   - "Esse agente tem acesso somente a `areas/marketing/`. Não vê vendas, não vê financeiro, não vê RH."
   - Mostrar a seção `scope` com os paths permitidos

2. Abrir `cerebro/agentes/bot-suporte/AGENTS.md`
   - "Bot de suporte: acesso mínimo. Só `areas/atendimento/bot/`. Nada mais."

3. **Demo — Tentativa de acesso negado:**
   - Pedir pro agente de marketing: _"Qual foi o MRR do mês passado?"_
   - Agente responde: "Não tenho acesso a dados financeiros. Posso ajudar com métricas de marketing."
   - "Não é que ele não sabe. É que ele não PODE. E avisa."

4. Abrir `cerebro/seguranca/permissoes.md`
   - Mostrar a tabela completa: agente × recurso × nível de acesso (leitura/escrita/negado)

5. Comparar Arquitetura A vs B:
   - A: mais isolamento, mais grupos para gerenciar
   - B: mais simples, menos isolamento entre tópicos
   - "Para times pequenos: B. Para times com dados sensíveis separados: A."

**Transição:** "Agora que entendemos o sistema, vamos ver ele funcionando num caso real e completo: marketing de performance."

---

### Bloco 9: Deep Dive Marketing (10:05–10:40)

**⏱ Duração:** 35 minutos

**Projetar:** `slides/10-marketing-ciclo.html`

**Falar — O ciclo completo:**
- "Marketing de performance tem um ciclo: hipótese → criativo → teste → dado → conclusão → nova hipótese."
- "Esse ciclo hoje depende de uma pessoa olhando planilha todo dia. Com o sistema, roda sozinho."
- "3 skills + 3 crons = ciclo automatizado."

**Trocar para:** `slides/11-daily-report.html`

**Falar:**
- "Todo dia às 8h, antes de qualquer pessoa da equipe acordar, o agente já gerou esse relatório."
- "Gestor de tráfego abre o Telegram às 8h → relatório já está lá. Com alertas, destaques, sugestões."
- Mostrar exemplo do daily report gerado

**Fazer:**

1. Abrir `cerebro/areas/marketing/sub-areas/trafego-pago/PROCESSO.md`
   - "Esse arquivo documenta como o marketing funciona. O agente lê isso antes de qualquer análise."

2. Mostrar as 3 skills:
   - `cerebro/areas/marketing/sub-areas/trafego-pago/skills/relatorio-ads/SKILL.md`
     → "Coleta dados do Meta Ads e gera relatório diário"
   - `cerebro/areas/marketing/sub-areas/trafego-pago/skills/analise-criativos/SKILL.md`
     → "Analisa performance de cada criativo e identifica padrões"
   - `cerebro/areas/marketing/sub-areas/trafego-pago/skills/criacao-criativos/SKILL.md`
     → "Sugere próximos criativos baseado em learnings anteriores"

3. Mostrar as 3 rotinas:
   - `cerebro/areas/marketing/sub-areas/trafego-pago/rotinas/daily-report.md` → toda manhã
   - `cerebro/areas/marketing/sub-areas/trafego-pago/rotinas/pipeline-semanal.md` → toda segunda
   - `cerebro/areas/marketing/sub-areas/trafego-pago/rotinas/analise-funnel.md` → toda sexta

**Trocar para:** `slides/12-pipeline-criativos.html`

4. Explicar o pipeline visual:
   - Backlog → Em teste → Aprendizado → Escalando → Morto
   - "Cada criativo passa por essas fases. O agente move e documenta automaticamente."

5. Abrir `cerebro/areas/marketing/sub-areas/trafego-pago/formatos/`
   - "Aqui ficam os formatos que funcionam. Carrossel, vídeo curto, estático. Com benchmarks de CTR."

6. Abrir `cerebro/areas/marketing/sub-areas/trafego-pago/criativos/`
   - "E aqui ficam os criativos documentados. O que foi testado, resultado, o que aprendemos."

7. **Demo final do bloco:**
   - Perguntar pro agente de marketing: _"Qual próximo criativo faz sentido produzir essa semana?"_
   - Agente analisa learnings, formatos com melhor performance → sugere criativo específico com justificativa
   - "Ele não chutou. Leu os dados, leu os learnings, e sugeriu com base em evidência."

**NÃO falar:**
- Como conectar Meta Ads API (tem guia separado)
- Quanto custa o tráfego pago
- Detalhes de configuração de pixels

---

### ☕ Pausa (10:40–10:50)

**Projetar:** `slides/00-abertura.html` (tela de espera com timer)

**Cayo faz:** Testar o bot de suporte antes de voltar — mandar 2-3 mensagens para garantir que está funcionando. Coletar perguntas do chat.

**Bruno faz:** Verificar que o ambiente do bot de suporte está OK. Ter uma "dúvida nova" preparada para a demo do loop de aprendizado.

---

### Bloco 10: Bot de Suporte — 🔥 3º AHA MOMENT (10:50–11:25)

**⏱ Duração:** 35 minutos

**Projetar:** `slides/13-bot-suporte-loop.html`

**Falar:**
- "Bot de suporte comum: você treina uma vez, fica desatualizado, vira problema."
- "Esse bot aprende sozinho com a operação. Cada dúvida respondida vira conhecimento permanente."
- O loop: FAQ → cliente pergunta → se está no FAQ, responde → se não está, marca como pendente → humano responde → cron consolida no FAQ → FAQ evolui
- "O bot de amanhã sabe mais do que o de hoje. Sem código. Sem retreinar."

**Fazer:**

1. Abrir `cerebro/agentes/bot-suporte/SOUL.md`
   - "É assim que ele fala com cliente. Tom específico, empático, dentro dos limites da empresa."
   - Ler 3-4 linhas do tom em voz alta

2. Abrir `cerebro/agentes/bot-suporte/AGENTS.md`
   - "Escopo mínimo de segurança: só acessa `areas/atendimento/bot/`. Nada mais da empresa."

3. Abrir `cerebro/areas/atendimento/bot/faq.md`
   - "Isso é tudo que o bot sabe hoje. Cada item com pergunta, resposta e categoria."
   - Mostrar 2-3 exemplos de perguntas e respostas no arquivo

4. **Demo — Cliente perguntando algo que está no FAQ:**
   - Enviar mensagem pro bot: _"Qual o prazo de entrega do curso?"_
   - Bot responde imediatamente com base no faq.md
   - "Ele achou no FAQ. Respondeu em segundos."

5. **Demo — A dúvida nova (o loop de aprendizado):**
   - Enviar mensagem pro bot: _"Vocês têm desconto para grupos de empresa?"_
   - Bot não encontra no FAQ → responde que vai verificar → registra em `cerebro/areas/atendimento/bot/duvidas.md` → notifica equipe no Telegram

6. Abrir `cerebro/areas/atendimento/bot/duvidas.md` ao vivo:
   - "Apareceu aqui. Status: pendente. Pergunta original preservada."

7. Responder a dúvida diretamente no arquivo:
   - Editar a linha: trocar `status: pendente` para `status: respondido`
   - Adicionar a resposta no campo `resposta`
   - "Fiz isso em 20 segundos no arquivo."

8. Mostrar `cerebro/areas/atendimento/rotinas/consolidar-faq.md`:
   - "Todo dia às 18h, esse cron roda. Pega todas as dúvidas com status `respondido`, formata, e adiciona ao faq.md."
   - "Amanhã, quando o próximo cliente perguntar sobre desconto para grupos — o bot já vai saber."

9. 🔥 Pausar. Deixar cair.
   - "Cada dúvida respondida pelo humano vira conhecimento permanente do bot. Sem código. Sem retreinar. Sem abrir ticket de TI."
   - "Em 30 dias, o bot vai saber responder 80% das dúvidas sozinho. Em 90 dias, 95%."

**NÃO falar:**
- Como integrar com WhatsApp Business API
- Como conectar Crisp ou Intercom
- Detalhes de como o consolidador de FAQ funciona internamente

**Transição:** "Vocês viram o sistema inteiro funcionando. Agora a pergunta é: como começo? Qual é o primeiro passo?"

---

### Bloco 11: Próximos 30 Dias (11:25–11:50)

**⏱ Duração:** 25 minutos

**Projetar:** `slides/14-roadmap-30dias.html`

**Falar:**
- "O maior erro que as pessoas cometem: tentam implementar tudo na semana 1."
- "Querem cérebro, skills, multi-agente, bot de suporte e crons ao mesmo tempo. Aí nada fica pronto direito."
- "O roadmap correto é sequencial. Cada semana constrói sobre a anterior."

**O Roadmap das 4 semanas:**

- **Semana 1 — Fundação:**
  - Criar o repo cerebro
  - Preencher `empresa/contexto/empresa.md`, `equipe.md`, `metricas.md`
  - Conectar 1 agente (assistente geral)
  - Testar: "O agente me conhece?"

- **Semana 2 — Primeira área:**
  - Escolher 1 área (recomendado: vendas ou marketing)
  - Criar 2-3 skills para ela
  - Trazer dados reais (CSV primeiro, depois API)
  - Testar: "O agente gera relatório sem eu pedir detalhes?"

- **Semana 3 — Automação:**
  - Configurar crons para as skills da Semana 2
  - Criar skill-creator para gerar novas skills com a equipe
  - Adicionar segundo agente (área prioritária)
  - Testar: "O sistema roda sem minha intervenção?"

- **Semana 4 — Bot e refinamento:**
  - Configurar bot de suporte com FAQ inicial (30-50 perguntas)
  - Ajustar permissionamentos
  - Revisar o que não está funcionando
  - Testar: "A equipe está usando sem me chamar?"

**Fazer:**

1. Abrir `cerebro/guias/roadmap-90-dias.md`
   - "Esse arquivo é o mapa completo. As semanas 1-4 são o mínimo viável. As semanas 5-12 são expansão."
   - Mostrar a estrutura das primeiras 4 semanas

2. Mostrar que o wizard existe:
   - "E vocês não precisam fazer isso sozinhos. O wizard faz com vocês."
   - Abrir `wizard/README.md`
   - "Cole isso no agente: 'Leia wizard/README.md e me guie pra configurar meu cérebro.'"
   - "Ele vai perguntar sobre a empresa, criar os arquivos, preencher o contexto, configurar o primeiro agente."
   - "O wizard é o onboarding automatizado."

3. **Pergunta pro chat:**
   - "Qual área vocês vão atacar na Semana 2? Manda no chat."
   - Ler 3-4 respostas. Comentar brevemente cada uma.

**NÃO falar:**
- Quanto tempo demora para ter ROI (varia muito por empresa)
- Garantias de resultado
- Comparação com contratar desenvolvedor

---

### Fechamento + Pitch (11:50–12:00)

**⏱ Duração:** 10 minutos

**Projetar:** `slides/15-fechamento.html`

**Falar — Recap final:**
- "Em 2 dias vocês viram o sistema inteiro funcionando, com dados reais, sem PowerPoint."
- Recap completo em bullets:
  - ✅ **Cérebro** — repo GitHub que centraliza tudo
  - ✅ **Skills** — automações em linguagem natural
  - ✅ **Skill-creator** — skills geradas em 30 segundos
  - ✅ **Crons** — o sistema roda sozinho
  - ✅ **Multi-agente** — cada um no seu papel
  - ✅ **Permissionamento** — cada agente só acessa o que pode
  - ✅ **Marketing** — ciclo completo automatizado
  - ✅ **Bot de suporte** — aprende sozinho com a operação
- "Tudo isso FUNCIONA. Vocês viram ao vivo. Não é promessa — é demo."

**[PITCH — produto/preço a definir com Bruno e Cayo antes da imersão]**

- Apresentar a oferta de acompanhamento / implementação guiada
- Urgência e condições especiais para quem está ao vivo
- CTA claro: "Para quem quer implementar com suporte, o link está no chat agora"

**Encerramento:**
- "Obrigado. Agora é hora de construir. O wizard está esperando."
- Abrir para perguntas finais (se houver tempo)

---

---

## Comandos do Facilitador

> Use durante a imersão ao vivo para navegar com o agente.

| Comando | O que o agente faz |
|---------|-------------------|
| `"próximo"` ou `"avança"` | Passa pro próximo bloco com instruções completas |
| `"recap"` | Resume o que já foi coberto até agora |
| `"quanto tempo?"` | Diz quanto tempo resta no bloco atual (baseado no horário informado) |
| `"perguntas"` | Sugere como responder as top perguntas do chat de forma eficiente |
| `"plano B"` | Fornece alternativa se algo falhar na demo ao vivo |
| `"pausa"` | Marca pausa, diz o que fazer nos 10 min e o que checar antes de voltar |
| `"status"` | Resume onde estamos: bloco atual, horário, o que já foi feito, o que falta |
| `"resumo para o chat"` | Gera uma mensagem de recap para o Cayo colar no chat dos participantes |

---

## Planos B — Se Algo Falhar

> Tenha esses na cabeça. Use o comando `"plano B"` para o agente detalhar.

| Situação | Alternativa |
|----------|-------------|
| Internet caiu | Mostrar screenshots pré-preparados de cada demo. Ter pasta `demos/screenshots/` pronta. |
| Agente não responde | Mostrar saída pré-gerada salva em `demos/outputs/`. "Isso é o que ele gera. Já rodei antes." |
| Terminal travou | Terminal secundário já aberto em background. Alt+Tab. |
| GitHub fora do ar | Repo clonado localmente. Mostrar estrutura de pastas no próprio terminal. |
| Skill-creator falhou | Mostrar skill já criada e salva em `demos/skills-exemplo/`. "Esse foi criado ontem." |
| Bot de suporte não responde | Ter conversa de demonstração gravada. Mostrar o vídeo. |

---

## Checklist Pré-Imersão

> Executar na noite anterior (27/03 e 28/03). Testa tudo antes.

### Dia 1 (27/03 noite)
- [ ] Repo `pixel-educacao/imersao-openclaw-negocios` acessível e público
- [ ] Todos os slides em `slides/` abrindo corretamente no browser
- [ ] `cerebro/empresa/contexto/metricas.md` com dados atuais
- [ ] `cerebro/dados/vendas.csv` com dados de exemplo limpos
- [ ] Agente no OpenClaw lendo `cerebro/` corretamente (testar "Qual o MRR?")
- [ ] Claude Code com mesmo repo configurado (testar mesma pergunta)
- [ ] skill-creator funcionando: testar criar 1 skill ao vivo
- [ ] Cron de exemplo configurado e visível no dashboard
- [ ] Terminal com `tree` instalado (`apt install tree` se necessário)

### Dia 2 (28/03 noite)
- [ ] Agentes de marketing e assistente com SOUL.md diferentes — testar mesma pergunta
- [ ] AGENTS.md com permissões configuradas — testar acesso negado
- [ ] `cerebro/areas/marketing/` com todas as skills e rotinas
- [ ] Bot de suporte respondendo no canal de teste
- [ ] `cerebro/areas/atendimento/bot/faq.md` com pelo menos 20 perguntas
- [ ] `cerebro/areas/atendimento/bot/duvidas.md` vazio (ou com 1 exemplo)
- [ ] Cron consolidador de FAQ configurado
- [ ] `cerebro/guias/roadmap-90-dias.md` atualizado
- [ ] `wizard/README.md` testado e funcionando
- [ ] Screenshots de backup em `demos/screenshots/` para todos os blocos

---

*Criado em: 2026-03-25*
*Versão: 1.0*
*Uso: Imersão OpenClaw nos Negócios — 28-29/03/2026*
