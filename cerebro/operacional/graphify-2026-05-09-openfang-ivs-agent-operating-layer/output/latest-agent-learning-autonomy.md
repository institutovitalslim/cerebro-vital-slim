# IVS Agent Learning Autonomy

Gerado em: `20260509-194058 UTC`

Modo: `read_only_learning_autonomy`

## Governança
- Todo agente IVS pode aprender de fontes externas, mas aprendizado externo vira hipótese, não regra canônica automática.
- Promoção: Regra fixa, memória ou mudança estrutural exige Maria/Tiaro e RC-25/graphify.

## Briefs por agente

### Maria (`maria-gerente`)
- Domínio: gestão geral, operação, coordenação, segurança operacional e qualidade
- Foco de hoje: **liderança operacional**
- Instagram/X: healthcare operations, customer experience, premium service, AI agents operations
- YouTube: Will Guidara unreasonable hospitality, Shep Hyken customer service, G4 Educação gestão, HubSpot operations customer experience
- Aplicação: converter em processos, checklists, auditorias e decisões operacionais seguras
- Métrica: 1 evidência operacional antes/depois ou 1 decisão melhor suportada por dados
- Classificação obrigatória: aplicar amanhã / testar 3 dias / descartar / propor RC-25

### Clara (`clara-whatsapp`)
- Domínio: concierge comercial WhatsApp, conversão, SPIN, objeções, follow-up e experiência premium
- Foco de hoje: **atendimento premium**
- Instagram/X: SPIN Selling, social selling, WhatsApp vendas, negociação
- YouTube: Patrick Dang sales scripts, Alex Hormozi sales objections, Gong discovery questions, Chris Voss negotiation
- Aplicação: converter em comportamento de atendimento: pergunta melhor, frase curta, follow-up premium e métrica de conversão
- Métrica: 1 evidência operacional antes/depois ou 1 decisão melhor suportada por dados
- Classificação obrigatória: aplicar amanhã / testar 3 dias / descartar / propor RC-25

### João (`agente-reels-intel`)
- Domínio: marketing, reels, conteúdo, sistema de demanda, design e engenharia de ferramentas web
- Foco de hoje: **criativos**
- Instagram/X: marketing médico, reels saúde premium, copywriting, design premium
- YouTube: Pedro Sobral tráfego para WhatsApp, Leandro Ladeira oferta, Alex Hormozi offer, G4 Educação growth
- Aplicação: converter em backlog, criativos, hipóteses de campanha, melhoria de landing/cockpit e QA visual
- Métrica: 1 evidência operacional antes/depois ou 1 decisão melhor suportada por dados
- Classificação obrigatória: aplicar amanhã / testar 3 dias / descartar / propor RC-25

### Pedro (`pedro-controller-ivs`)
- Domínio: financeiro, controladoria, DRE, caixa, auditoria e investimento
- Foco de hoje: **DRE gerencial**
- Instagram/X: controller financeiro, FP&A, cash flow management, small business finance
- YouTube: FP&A explained, cash flow management business, DRE gerencial, controladoria para clínicas
- Aplicação: converter em checklists financeiros, indicadores, auditorias, cenários e alertas para Maria/Tiaro
- Métrica: 1 evidência operacional antes/depois ou 1 decisão melhor suportada por dados
- Classificação obrigatória: aplicar amanhã / testar 3 dias / descartar / propor RC-25

### Conselho Growth Vital Slim (`conselho-growth-vital-slim`)
- Domínio: estratégia, crescimento, vendas, oferta, experiência e posicionamento
- Foco de hoje: **experiência**
- Instagram/X: growth strategy, healthcare marketing, premium offer, customer experience
- YouTube: Alex Hormozi offer, HubSpot sales process, G4 Educação growth, Will Guidara hospitality
- Aplicação: avaliar decisões e gerar recomendações estratégicas com riscos, trade-offs e testes
- Métrica: 1 evidência operacional antes/depois ou 1 decisão melhor suportada por dados
- Classificação obrigatória: aplicar amanhã / testar 3 dias / descartar / propor RC-25

### LLM Council (`llm-council`)
- Domínio: revisão crítica multi-perspectiva, riscos, trade-offs e decisões complexas
- Foco de hoje: **operações**
- Instagram/X: AI governance, agentic workflows, risk management, product strategy
- YouTube: AI agent governance, product strategy, risk management frameworks, healthcare AI safety
- Aplicação: stress-test de decisões, identificação de riscos e validação de governança
- Métrica: 1 evidência operacional antes/depois ou 1 decisão melhor suportada por dados
- Classificação obrigatória: aplicar amanhã / testar 3 dias / descartar / propor RC-25

## Coletas locais
```json
{
  "social_daily_plan": {
    "ok": true,
    "returncode": 0,
    "stdout": "{\n  \"ok\": true,\n  \"rotina_diaria_clara\": {\n    \"07:10\": {\n      \"fonte\": \"Instagram\",\n      \"buscar\": \"1 post/reel recente de vendas consultivas, WhatsApp, atendimento premium ou clínica premium\",\n      \"objetivo\": \"extrair 1 pergunta melhor para abrir conversas\"\n    },\n    \"12:40\": {\n      \"fonte\": \"X/Twitter\",\n      \"buscar\": \"posts de alto engajamento sobre persuasão, objeções, atendimento, negócios locais, experiência do cliente\",\n      \"objetivo\": \"extrair 1 frase curta ou ângulo de objeção\"\n    },\n    \"17:40\": {\n      \"fonte\": \"Instagram\",\n      \"buscar\": \"1 conteúdo de referência em SPIN, negociação ou social selling\",\n      \"objetivo\": \"transformar em 2 scripts WhatsApp: antes/depois\"\n    },\n    \"21:20\": {\n      \"fonte\": \"Relatório interno\",\n      \"buscar\": \"conversas do dia e aprendizados coletados\",\n      \"objetivo\": \"decidir o treino de amanhã e propor atualização se houver padrão recorrente\"\n    }\n  },\n  \"perfis_semente\": {\n    \"instagram_vendas_whatsapp\": [\n      \"vitoroliveiraconsultor\",\n      \"camilaporto\",\n      \"leandroladeira\",\n      \"pedrosobral\",\n      \"icaro.de.carvalho\"\n    ],\n    \"vendas_consultivas\": [\n      \"vitoroliveiraconsultor\",\n      \"thiagoconcer\",\n      \"g4educacao\"\n    ],\n    \"premium_experiencia\": [\n      \"willguidara\",\n      \"shephyken\"\n    ],\n    \"medicina_premium_validar_antes\": [\n      \"dr.marlonbatista\",\n      \"dra.camilapaes\"\n    ],\n    \"x_clara_prioridade_1_agendamento_vendas_consultivas\": [\n      \"Gong_io\",\n      \"close\",\n      \"Outreach_io\",\n      \"patrickdang\",\n      \"AlexHormozi\"\n    ],\n    \"x_clara_prioridade_2_experiencia_premium\": [\n      \"Hyken\",\n      \"willguidara\",\n      \"Salesforce\"\n    ],\n    \"x_clara_prioridade_3_healthcare_jornada_paciente\": [\n      \"Zocdoc\"\n    ],\n    \"x_clara_buscas_tematicas\": [\n      \"consultative selling objection handling\",\n      \"customer experience appointment booking\",\n      \"sales follow up no show reduction\",\n      \"healthcare patient scheduling experience\"\n    ]\n  }\n}\n",
    "stderr": ""
  },
  "youtube_plan": {
    "ok": true,
    "returncode": 0,
    "stdout": "ng\",\n          \"labeling\",\n          \"negotiation questions\"\n        ]\n      },\n      {\n        \"nome\": \"Shep Hyken\",\n        \"url\": \"buscar no YouTube por Shep Hyken\",\n        \"buscar\": [\n          \"customer service\",\n          \"customer experience\",\n          \"hospitality\"\n        ]\n      },\n      {\n        \"nome\": \"Will Guidara\",\n        \"url\": \"buscar no YouTube por Will Guidara Unreasonable Hospitality\",\n        \"buscar\": [\n          \"unreasonable hospitality\",\n          \"premium service\",\n          \"customer experience\"\n        ]\n      }\n    ],\n    \"prioridade_3_com_filtro\": [\n      {\n        \"nome\": \"Jordan Belfort\",\n        \"url\": \"buscar no YouTube por Jordan Belfort official\",\n        \"buscar\": [\n          \"tonality\",\n          \"objection handling\",\n          \"straight line persuasion\"\n        ]\n      },\n      {\n        \"nome\": \"Grant Cardone\",\n        \"url\": \"https://www.youtube.com/@GrantCardone\",\n        \"buscar\": [\n          \"follow up\",\n          \"sales discipline\",\n          \"closing objections\"\n        ]\n      }\n    ],\n    \"brasil_social_selling\": [\n      {\n        \"nome\": \"Camila Porto\",\n        \"url\": \"buscar no YouTube por Camila Porto\",\n        \"buscar\": [\n          \"WhatsApp vendas\",\n          \"Instagram vendas\",\n          \"atendimento WhatsApp\"\n        ]\n      },\n      {\n        \"nome\": \"Leandro Ladeira\",\n        \"url\": \"buscar no YouTube por Leandro Ladeira\",\n        \"buscar\": [\n          \"oferta\",\n          \"copy\",\n          \"vendas online\",\n          \"mensagem de vendas\"\n        ]\n      },\n      {\n        \"nome\": \"Pedro Sobral\",\n        \"url\": \"buscar no YouTube por Pedro Sobral\",\n        \"buscar\": [\n          \"tráfego para WhatsApp\",\n          \"leads\",\n          \"funil\",\n          \"remarketing\"\n        ]\n      },\n      {\n        \"nome\": \"Ícaro de Carvalho\",\n        \"url\": \"buscar no YouTube por Ícaro de Carvalho\",\n        \"buscar\": [\n          \"copywriting\",\n          \"persuasão\",\n          \"storytelling\"\n        ]\n      },\n      {\n        \"nome\": \"Thiago Concer\",\n        \"url\": \"buscar no YouTube por Thiago Concer\",\n        \"buscar\": [\n          \"vendas consultivas\",\n          \"prospecção\",\n          \"objeções\"\n        ]\n      },\n      {\n        \"nome\": \"César Frazão\",\n        \"url\": \"buscar no YouTube por César Frazão\",\n        \"buscar\": [\n          \"técnicas de vendas\",\n          \"atendimento\",\n          \"fechamento\"\n        ]\n      },\n      {\n        \"nome\": \"G4 Educação\",\n        \"url\": \"buscar no YouTube por G4 Educação\",\n        \"buscar\": [\n          \"vendas\",\n          \"growth\",\n          \"atendimento\",\n          \"CRM\"\n        ]\n      }\n    ]\n  },\n  \"day_plan\": {\n    \"segunda\": {\n      \"canal\": \"Patrick Dang\",\n      \"tema\": \"sales scripts + discovery questions\",\n      \"entrega\": \"1 abertura e 1 pergunta SPIN\"\n    },\n    \"terça\": {\n      \"canal\": \"Alex Hormozi\",\n      \"tema\": \"valor percebido + oferta\",\n      \"entrega\": \"1 frase para gerar valor antes de preço\"\n    },\n    \"quarta\": {\n      \"canal\": \"Gong\",\n      \"tema\": \"objection handling + call review\",\n      \"entrega\": \"2 respostas para objeção\"\n    },\n    \"quinta\": {\n      \"canal\": \"Chris Voss / Shep Hyken\",\n      \"tema\": \"perguntas, empatia tática e atendimento premium\",\n      \"entrega\": \"1 pergunta de segurança e 1
```
