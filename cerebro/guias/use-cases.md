# Deep Dives — Imersão OpenClaw nos Negócios

> 2 deep dives com profundidade real. Não são exemplos genéricos — são sistemas operacionais completos.

---

## Deep Dive 1: Marketing — Sistema de Criativos com IA

### O panorama

A maioria dos negócios gerencia criativos de ads assim: sobe anúncio, olha o dashboard de vez em quando, pausa o que tá ruim quando lembra, e cria novos criativos "na intuição". Não documenta o que funcionou, não registra por que funcionou, e repete os mesmos erros toda rodada.

O que a gente vai mostrar é um **sistema completo**: o agente documenta cada criativo, testa hipóteses de forma estruturada, monitora performance automaticamente, e quando chega a hora de criar novos criativos, ele já sabe exatamente o que funcionou e o que não funcionou.

### O ciclo

```
HIPÓTESE → CRIATIVO → TESTE → DADO → CONCLUSÃO → NOVA HIPÓTESE
    ↑                                                    │
    └────────────────────────────────────────────────────┘
```

O agente opera **em todas as etapas**, mas o humano decide em duas: qual hipótese testar e aprovar criativos antes do upload.

### A estrutura no cérebro

```
areas/marketing/sub-areas/trafego-pago/
├── contexto/geral.md          ← KPIs, ferramentas, responsáveis
├── MAPA.md                    ← Tabela completa: nome interno ↔ nome no Meta Ads ↔ arquivo
├── produtos/
│   └── curso-marketing/
│       ├── PROCESSO.md        ← O DOCUMENTO CENTRAL — conecta todas as peças
│       ├── angulos/           ← Catálogo de ângulos de comunicação
│       │   ├── delegacao.md   ← "Delega tudo pra IA, foca no estratégico"
│       │   ├── resultado-rapido.md
│       │   ├── nao-tecnico.md
│       │   └── prova-social.md
│       ├── formatos/          ← Catálogo de formatos visuais
│       │   ├── screen-recording.md
│       │   ├── talking-head.md
│       │   ├── testimonial-editorial.md
│       │   └── tweet-screenshot.md
│       ├── descriptions/      ← Documentação de CADA criativo
│       │   ├── c1.md          ← Copy, hook, ângulo, formato, arquivo
│       │   ├── c2.md
│       │   └── ... (50+ criativos documentados)
│       ├── banners/           ← Arquivos visuais dos criativos
│       │   ├── story/
│       │   └── post/
│       ├── testes/
│       │   ├── abertos/       ← Testes em andamento
│       │   │   ├── teste-hook-delegacao.md
│       │   │   ├── teste-cta-vs-nocta.md
│       │   │   └── teste-formato-stack.md
│       │   └── consolidados/  ← Testes finalizados com conclusão
│       │       ├── teste-hook-overlay.md
│       │       └── teste-videos-bruno.md
│       ├── learnings/         ← Aprendizados consolidados
│       │   ├── resumo.md      ← TOP 7 aprendizados acionáveis
│       │   ├── angulos.md     ← O que funciona por ângulo
│       │   ├── hooks.md       ← Padrões de hook vencedor
│       │   └── formatos.md    ← O que funciona por formato
│       └── pipeline/
│           └── state.json     ← Estado atual dos criativos (gerado por cron)
├── rotinas/
│   ├── meta-ads-report.md     ← Relatório 3x/dia (8h, 12h, 20h)
│   ├── creative-pipeline.md   ← Recomendações diárias (pausar/escalar)
│   └── funnel-report.md       ← Relatório de funil 1x/dia
└── reports/
    ├── meta-ads/              ← Relatórios HTML gerados automaticamente
    ├── creative-pipeline/     ← Recomendações HTML
    └── funnel/                ← Relatórios de funil
```

### Como funciona na prática — Etapa por etapa

#### Etapa 1: Hipótese

O time de marketing quer testar um novo ângulo. Pergunta ao agente:

```
"Com base nos resultados dos últimos testes, qual ângulo a gente ainda não explorou 
que poderia funcionar?"
```

O agente consulta:
- `learnings/resumo.md` — o que já sabemos que funciona
- `angulos/` — catálogo de ângulos existentes
- `testes/consolidados/` — o que já foi testado
- `testes/abertos/` — o que está sendo testado agora

E responde:

```
📊 Análise de gaps nos ângulos:

Ângulos testados: delegação (ROAS 4.0x), prova-social (2.1x), não-técnico (1.8x)
Ângulos NÃO testados: resultado-rapido, urgência

Recomendação: testar "resultado-rapido" primeiro.
Motivo: top learning #1 diz que "hook funcional específico > hook emocional".
O ângulo resultado-rapido é naturalmente funcional ("em 30 min você tem X rodando").

Formato sugerido: screen-recording (mostrar o resultado acontecendo)
Hook sugerido: "Configurei isso em 30 minutos. Agora roda sozinho todo dia."
```

#### Etapa 2: Criativo

O agente gera o criativo e documenta:

**Arquivo `descriptions/c15.md`:**
```markdown
# C15 — Resultado Rápido · Screen Recording

## Ângulo: resultado-rapido
## Formato: screen-recording
## Hook: "Configurei isso em 30 minutos. Agora roda sozinho todo dia."
## Copy completa: [texto do ad]
## Arquivo: banners/c15-resultado-rapido-story.png
## Status: aguardando aprovação
```

**Arquivo `formatos/screen-recording.md`** já documenta as specs:
```markdown
# Screen Recording
- Dimensões: 1080×1920 (story) ou 1080×1350 (post)
- Estilo: gravação de tela real do produto em uso
- Quando funciona: audiências técnicas, demonstrar features
- Quando não funciona: público frio que não conhece o produto
```

O time aprova. O agente sobe na campanha de teste (ou o time sobe manualmente — por enquanto preferem subir na mão) e registra no `MAPA.md`:

| Nome Interno | Nome no Meta Ads | Arquivo |
|---|---|---|
| C15 — Resultado Rápido | open-ad015-banner-asc | c15-resultado-rapido-story.png |

E cria o arquivo de teste:

**`testes/abertos/teste-resultado-rapido-screen.md`:**
```markdown
# Teste — Resultado Rápido · Screen Recording vs Talking Head

Status: 🟢 Em andamento
Data: 23/03/2026

## Hipótese
Screen recording performa melhor que talking head para o ângulo resultado-rapido,
porque mostrar o resultado acontecendo gera mais crença que falar sobre ele.

## Criativos
| ID | Formato | Hook |
|---|---|---|
| C15 | Screen recording | "Configurei isso em 30 min..." |
| C16 | Talking head | "Configurei isso em 30 min..." |

## Variável isolada: formato (screen recording vs talking head)
## Controle: mesmo hook, mesmo ângulo, mesmo CTA

## Threshold: ≥ R$ 150 gasto por criativo
## Resultado: ⏳ pendente
```

#### Etapa 3: Monitoramento automático

Três crons rodam sem ninguém pedir:

**Cron 1 — Relatório de ads (3x/dia, 8h/12h/20h):**
```
📢 Performance Diária — 23/03

💰 Investido hoje: R$ 340
🎯 ROAS médio: 3.1x
📊 Top criativo: C8 delegação (ROAS 4.8x, 12 vendas)

⚠️ ALERTA: C11 não-técnico — ROAS 0.7x há 3 dias
→ Recomendação: pausar (já gastou R$ 180 sem retorno)
```

**Cron 2 — Pipeline de criativos (1x/dia, 9h30):**
```
📊 Pipeline — Status dos testes

🟢 Em andamento (3 testes):
- teste-resultado-rapido-screen: R$ 85/R$ 150 threshold (57%)
- teste-cta-vs-nocta: R$ 210/R$ 150 ✅ pronto pra fechar
- teste-formato-stack: R$ 120/R$ 150 (80%)

🔴 Ação necessária:
- teste-cta-vs-nocta atingiu threshold → fechar teste e documentar

📈 Recomendações:
- C8 delegação: ROAS 4.8x sustentado → escalar +30% budget
- C15 resultado-rapido: sinais iniciais positivos (CTR 3.2%)
```

**Cron 3 — Relatório de funil (1x/dia, 8h):**
```
🔄 Funil — 23/03

Página → CTA: 42% (meta: 35%) ✅
CTA → Checkout: 18% (meta: 15%) ✅
Checkout → Compra: 52% (meta: 50%) ✅

Canal top: Meta Ads (68% das conversões)
Canal fraco: Orgânico (3% das conversões, 12% do tráfego)
```

#### Etapa 4: Conclusão de teste

Quando um teste atinge o threshold de dados, o agente sugere a conclusão:

```
📋 Teste pronto para fechar: teste-cta-vs-nocta

Resultado:
- Com CTA ("Comece agora"): ROAS 2.1x, CTR 2.8%
- Sem CTA (implícito): ROAS 3.4x, CTR 2.2%

Conclusão sugerida: CTA explícito aumenta CTR mas diminui ROAS.
Hipótese: o CTA atrai curiosos (CTR alto) que não convertem (ROAS baixo).

Ação sugerida:
1. Mover teste para consolidados/
2. Atualizar learnings/hooks.md: "CTA implícito > explícito para cold traffic"
3. Aplicar learning nos próximos criativos

Aprovar? (sim/não)
```

O time aprova. O agente:
1. Move `testes/abertos/teste-cta-vs-nocta.md` → `testes/consolidados/`
2. Atualiza `learnings/hooks.md` com o novo padrão
3. Atualiza `learnings/resumo.md` se for top learning

#### Etapa 5: Nova hipótese (o ciclo recomeça)

O agente já tem todo o histórico. Na próxima rodada:

```
"Com base nos 3 últimos testes fechados, o que a gente deveria testar agora?"
```

```
📊 Sugestão de próximo teste:

Padrão encontrado: hooks com números específicos têm 3x mais ROAS.
Learning: CTA implícito > explícito.
Gap: não testamos "número + sem CTA" juntos.

Hipótese: criativo com hook "7 tarefas automatizadas sem você fazer nada"
(número específico + resultado implícito, sem CTA) deve bater o ad015.

Formato sugerido: mission-control (screenshot do painel com os 7 tasks visíveis)
```

### O que o participante leva

Não é "como criar um relatório de ads". É um **sistema que aprende sozinho**:
- Documenta cada criativo com ângulo, hook, formato, copy
- Testa hipóteses de forma isolada (uma variável por vez)
- Monitora automaticamente (3 crons, zero trabalho manual)
- Conclui testes com dados (não intuição)
- Usa aprendizados passados para gerar hipóteses novas
- O humano decide apenas O QUÊ testar e APROVA antes de subir

### Regras de decisão (documentadas no agente)

| Situação | Ação | Quem |
|----------|------|------|
| ROAS < 1.0x por 5 dias | Pausar criativo | Agente (automático) |
| ROAS > 2.0x sustentado | Sugerir escalar | Agente sugere, humano aprova |
| Teste atingiu threshold | Sugerir fechar | Agente sugere, humano aprova |
| Frequency > 3.0 | Alertar fadiga | Agente alerta |
| Novo criativo pronto | Upload na campanha | Humano (por enquanto) |

> 💡 "A gente ainda prefere subir os criativos na mão. Mas você pode configurar pra eles subirem automaticamente pela API do Meta. A gente prefere estruturar isso manualmente por enquanto porque cada criativo tem nuances que a gente quer revisar antes."

---

## Deep Dive 2: Vendas & Atendimento — Bot no WhatsApp

### O panorama

Lead entra no WhatsApp da empresa. Hoje: alguém da equipe lê, responde quando pode (às vezes 4h depois), faz perguntas manuais pra qualificar, tenta agendar call, esquece de atualizar o CRM. Resultado: lead esfria, call não acontece, pipeline vira uma bagunça.

O que a gente vai mostrar: um **agente de vendas no WhatsApp** que qualifica automaticamente, agenda call, e atualiza o CRM — tudo na mesma conversa.

### A estrutura no cérebro

```
areas/vendas/
├── contexto/geral.md              ← Processo de vendas, produtos, preços
├── skills/
│   ├── qualificacao-lead/SKILL.md ← Como qualificar (perguntas, critérios)
│   ├── agendamento-call/SKILL.md  ← Como agendar (disponibilidade, regras)
│   └── atualizar-crm/SKILL.md    ← Como registrar no CRM
├── rotinas/
│   ├── follow-up-diario.md        ← Alertar leads sem contato há 48h
│   └── relatorio-pipeline.md      ← Status do pipeline 1x/dia
└── dados/
    └── leads.csv                  ← Pipeline atualizado

areas/atendimento/
├── contexto/geral.md              ← FAQ, processos, SLA
├── skills/
│   └── resposta-suporte/SKILL.md  ← Base de conhecimento pra respostas
└── rotinas/
    └── checagem-tickets.md        ← Alertar tickets pendentes > 24h
```

### O fluxo completo

#### 1. Lead chega no WhatsApp

O lead manda mensagem no WhatsApp da empresa. O agente de vendas responde:

```
Lead: "Oi, vi o anúncio do curso de marketing. Quanto custa?"

Agente: "Oi! Obrigado pelo interesse 😊
O Curso de Marketing Digital custa R$ 197 (acesso vitalício).

Pra te dar a melhor orientação, posso te fazer 2 perguntas rápidas?"

Lead: "Pode sim"

Agente: "Legal! 
1. Você já investe em tráfego pago ou tá começando do zero?
2. Tem algum objetivo específico? (ex: vender mais um produto, captar leads, etc.)"

Lead: "Já invisto uns R$ 2K/mês em Meta Ads mas o ROAS tá ruim"

Agente: "Entendi. R$ 2K/mês com ROAS baixo é exatamente o cenário 
que o curso resolve — tem um módulo inteiro de otimização de criativos 
que mostra como a gente saiu de ROAS 1.2x pra 3.5x.

Mas se você já investe R$ 2K/mês, talvez valha a pena conhecer 
a Mentoria Individual (R$ 2.997) — é personalizada pro seu negócio.
Quer agendar uma call de 20 min com o Ricardo pra entender se faz sentido?"

Lead: "Quero sim"

Agente: "Perfeito! Tenho horários disponíveis:
- Terça 24/03 às 10h
- Quarta 25/03 às 14h
- Quinta 26/03 às 10h

Qual funciona melhor pra você?"

Lead: "Terça 10h"

Agente: "Agendado! ✅
Terça 24/03 às 10h — call com Ricardo (20 min)
Você vai receber um link do Google Meet por aqui.

Enquanto isso, dá uma olhada nesse case: [link]
Até terça! 🚀"
```

#### 2. O que acontece nos bastidores

Enquanto a conversa acontece, o agente:

**a) Qualifica o lead** usando a skill `qualificacao-lead`:
```markdown
# Qualificação — Lead WhatsApp

## Critérios de qualificação
| Critério | Peso | Resposta |
|----------|------|----------|
| Já investe em ads? | Alto | ✅ Sim, R$ 2K/mês |
| Tem budget definido? | Alto | ✅ R$ 2K/mês |
| Tem dor clara? | Alto | ✅ ROAS ruim |
| Ticket potencial | Alto | R$ 2.997 (mentoria) |
| Urgência | Médio | ⬆️ Alta (gastando sem retorno) |

## Score: 9/10 — LEAD QUENTE 🔥
## Produto recomendado: Mentoria Individual (R$ 2.997)
## Ação: agendar call imediata
```

**b) Agenda a call** usando a skill `agendamento-call`:
- Consulta disponibilidade do Ricardo
- Bloqueia horário no Google Calendar
- Envia convite com link do Meet

**c) Atualiza o CRM** usando a skill `atualizar-crm`:
```
Lead: João Silva
Fonte: WhatsApp (Meta Ads)
Produto: Mentoria Individual (R$ 2.997)
Status: Call agendada → 24/03 10h com Ricardo
Score: 9/10
Contexto: investe R$ 2K/mês em Meta Ads, ROAS ruim
Próximo passo: call de fechamento
```

**d) Notifica a equipe** no tópico 💰 Vendas:
```
💰 Novo lead qualificado

João Silva — WhatsApp (via Meta Ads)
Score: 9/10 🔥
Produto: Mentoria Individual (R$ 2.997)
Call agendada: terça 24/03 10h com Ricardo

Contexto: já investe R$ 2K/mês em Meta Ads, ROAS baixo.
Boa oportunidade — lead com dor clara e budget alto.
```

#### 3. Follow-up automático

Se o lead não aparece na call, o agente não esquece:

**Cron follow-up (diário 9h):**
```
📋 Follow-up — Leads sem ação

🔴 Call no-show (ontem):
1. João Silva — Mentoria (R$ 2.997) — não apareceu na call
   → Enviar WhatsApp: "Oi João, não conseguimos nos conectar ontem. 
     Quer reagendar? Tenho horário quinta 10h."

🟡 Sem contato há 3 dias:
2. Maria Souza — Curso (R$ 197) — pediu info e sumiu
   → Enviar WhatsApp com conteúdo de valor (case study)

📊 Pipeline: 15 leads ativos, R$ 24K em potencial
```

#### 4. Quando o lead é de suporte (não de venda)

O agente identifica e redireciona:

```
Lead: "Oi, comprei o curso semana passada mas não consigo acessar"

Agente: "Oi! Isso é suporte, vou resolver pra você agora.
Qual email você usou na compra?"

Lead: "joao@email.com"

Agente: "Encontrei seu acesso. O problema é que o email de login 
é diferente (joaosilva@email.com). Tenta com esse.

Se não funcionar, me avisa que escalo pro time de suporte."
```

E nos bastidores:
- Consulta a base de dados de alunos
- Verifica o problema
- Se resolver, registra como ticket resolvido
- Se não resolver, escala pro time de atendimento (tópico 🎧 Atendimento)

### O que o participante leva

Um fluxo de vendas que:
- **Nunca dorme** — lead às 23h recebe resposta imediata
- **Qualifica automaticamente** — perguntas certas, score, produto recomendado
- **Agenda sem atrito** — propõe horários, bloqueia agenda, envia link
- **Atualiza CRM sozinho** — zero trabalho manual de registro
- **Faz follow-up** — nenhum lead esquecido, nenhuma call perdida sem retry
- **Distingue venda de suporte** — redireciona sem perder o contexto

### Configuração do agente WhatsApp

```json
{
  "channel": "whatsapp",
  "agent": "vendas",
  "allowFrom": ["*"],  // qualquer lead pode falar
  "mode": "ask",       // ações sensíveis pedem aprovação
  "context": [
    "areas/vendas/",
    "empresa/contexto/empresa.md",
    "empresa/contexto/equipe.md"
  ]
}
```

### Regras de decisão

| Situação | Ação | Quem |
|----------|------|------|
| Lead pergunta preço | Responder + qualificar | Agente |
| Lead qualificado (score ≥ 7) | Propor call | Agente |
| Lead quer comprar direto | Enviar link de checkout | Agente |
| Lead reclama / suporte | Redirecionar pra atendimento | Agente |
| Reembolso solicitado | Escalar pra liderança | Agente escala, humano decide |
| Call no-show | Retry 1x (reagendar) | Agente |
| Retry ignorado 2x | Marcar como "frio" e parar | Agente |
| Lead de ticket > R$ 2K | Notificar liderança imediatamente | Agente |

> 💡 "A gente configura o agente de vendas em modo ask pra ações sensíveis — ele qualifica e agenda sozinho, mas se for um reembolso ou um lead muito grande, ele escala pro time humano aprovar."

---

## Como os Deep Dives se encaixam na Imersão

### Dia 1 (expositivo — 3h)
O Bruno mostra **o sistema funcionando**:
- Abre o repo, navega pela estrutura de marketing
- Mostra o PROCESSO.md e o ciclo completo
- Mostra um teste aberto, um consolidado, e os learnings
- Mostra o bot de WhatsApp respondendo um lead ao vivo
- Mostra o CRM sendo atualizado em tempo real

### Dia 2 (hands-on — 3h)
Os participantes **montam o próprio sistema**:
- Escolhem: marketing (criativos) ou vendas (bot WhatsApp)
- Criam a estrutura de pastas
- Documentam seus próprios ângulos/formatos OU fluxo de qualificação
- Configuram pelo menos 1 cron
- Saem com o sistema básico rodando

---

*Deep dives — Imersão OpenClaw nos Negócios*
