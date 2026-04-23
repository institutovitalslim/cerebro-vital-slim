# Vendas — Contexto

> Conteúdo derivado de fatos canônicos: `cerebro/empresa/contexto/metricas.md`, `cerebro/leads-spin-selling.md`, `cerebro/leads-argumentos-venda-ligacoes.md`, `cerebro/empresa/contexto/people.md`, skills `areas/vendas/skills/`.

## Como funciona

**Funil canônico:**

1. **Atração** — paciente vê anúncio (Google Ads, ~98% do volume) ou recebe indicação (~2%) e chega no WhatsApp da clínica.
2. **Primeiro contato** — Clara responde no WhatsApp via Z-API (regra: responder em até 5 min — diferença de ~70% na taxa de agendamento). Antes de qualquer resposta, **consultar planilha de histórico de conversas** pelo número (Apps Script, ver `cerebro/CLAUDE.md`).
3. **Qualificação SPIN** — antes de mencionar preço, Clara conduz pelo menos 1 pergunta de **Situação** + 1 de **Problema** (ver `cerebro/leads-spin-selling.md`). Regra de ouro: **dor antes de preço, contexto antes de proposta, valor percebido antes de investimento**.
4. **Acolhimento da objeção** — objeção de preço cedo geralmente NÃO é sobre preço; é insegurança ou experiência anterior frustrada (ver `cerebro/leads-argumentos-venda-ligacoes.md`).
5. **Agendamento** — quando o lead está pronto, Clara consulta `/horarios-livres` da AGENDA OPENCLAW no QuarkClinic (`agendaId 445996589`, `profissionalId 240623016` Dra. Daniely) e cria o agendamento com o início real do slot mais próximo.
6. **Cadastro** — paciente novo é cadastrado no Omie via skill `omie-cadastro-paciente/`.
7. **Follow-up** — 80% das vendas acontecem **depois do 5º contato**. Cadência mínima de follow-up: 1h de silêncio, 24h, 3 dias, 7 dias, 15 dias. Cada follow-up retoma o **ponto exato** onde a conversa parou — nunca genérico.

**Produtos vendidos:** Programa de Acompanhamento 3, 6 ou 12 meses (ver `cerebro/empresa/contexto/geral.md`). Consulta avulsa e bioimpedância existem mas não são o foco comercial.

**Quem fecha:** o agendamento da consulta inicial é o "fechamento" operacional do funil de aquisição. A conversão consulta → programa fica com a Dra. Daniely no atendimento clínico.

## Ferramentas

- **WhatsApp via Z-API** — canal principal de aquisição (`localhost:8787`, instância `3CF367BB00EB205F87468A74AFBCE7F1`)
- **QuarkClinic** — agenda e cadastro de paciente (AGENDA OPENCLAW)
- **Omie** — cadastro financeiro e cobrança
- **Planilha Apps Script** — histórico canônico de conversas com cada número (URL em `cerebro/CLAUDE.md`)
- **Telegram** — escalação Clara → Tiaro quando há dúvida (Protocolo de Dúvida)
- **Skills da área** (`areas/vendas/skills/`):
  - `relatorio-vendas` — relatório diário (8h) com vendas, ticket médio, breakdown por canal
  - `follow-up-leads` — gerencia cadência de follow-up automatizada
  - `bot/conhecimento.md` — base de conhecimento do bot de vendas (atualmente em reset, a popular)

## Principais desafios

1. **Captação em dificuldade nos últimos 3 meses (2026-04)** — alerta operacional canônico em `metricas.md`. Causa em investigação; alavanca prioritária = ativar **Meta Ads** e **Instagram orgânico** (hoje zerados).
2. **Reativação de inativos** — 300 pacientes na base × 32 ativos. Skill `alerta-clientes-inativos` existe e roda; falta loop comercial fechado pra converter alerta em conversa de reativação.
3. **Velocidade de resposta fora do horário comercial** — paciente decide quando decide; mensagem parada por 2h pode ser paciente perdido pro concorrente. Clara automatiza, mas escalação humana fora de horário ainda é manual.
4. **Honestidade na qualificação** — risco recorrente de "atalho comercial": pular SPIN e ir direto pra preço quando o lead pergunta "quanto custa". Regra dura: **nunca**. Toda vez que isso acontecer, virá reclamação de Tiaro.

_Atualizado: 2026-04-23_
