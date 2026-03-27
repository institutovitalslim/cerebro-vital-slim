# Rotina: Follow-up de Leads Diário

## O que faz

Todo dia às **9h BRT**, identifica leads sem contato há mais de 7 dias e envia alerta no tópico 💰 Vendas.

## Configuração

| Campo | Valor |
|-------|-------|
| **Cron ID** | `378ea390-70cb-40ce-af69-cb766747f817` |
| **Schedule** | `0 12 * * *` (UTC) = 9h BRT |
| **Skill usada** | `cerebro/areas/vendas/skills/leads-esfriando/SKILL.md` |
| **Fonte de dados** | `wizard-imersao/dados-demo/leads.csv` |
| **Entrega** | Tópico 💰 Vendas (topic_id: 4) — HTML como documento + resumo em texto |
| **Session target** | `isolated` |
| **Criado em** | 2026-03-27 |
| **Criado por** | Bruno Okamoto |

## O que é entregue

1. **Texto de resumo** com:
   - Total de leads esfriando
   - Valor total em risco
   - Top 3 leads mais urgentes (dias sem contato + produto)

2. **Arquivo HTML** (`relatorio-leads-esfriando.html`) como documento anexo — dashboard completo com KPIs, distribuição por urgência e tabela detalhada.

3. **Se não houver leads esfriando:** mensagem positiva confirmando que todos estão em dia.

## Critérios de classificação

| Urgência | Critério |
|----------|----------|
| 🔴 Crítico | +14 dias sem contato |
| 🟡 Alto | 10–13 dias |
| 🟠 Médio | 8–9 dias |

Leads com status `fechado` são excluídos automaticamente.

## Como ajustar

- **Mudar o threshold** (ex: 10 dias): editar o prompt do cron no painel ou pedir ao assistente
- **Mudar o horário**: atualizar o schedule via `cron update`
- **Desativar**: `cron disable` com o ID acima

## Histórico de alterações

| Data | Alteração |
|------|-----------|
| 2026-03-27 | Rotina criada (Bruno Okamoto) |
