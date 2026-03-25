---
name: leads-esfriando
description: >
  Analisa a planilha de leads e identifica quais estão esfriando — leads que
  entraram há mais de 7 dias sem nenhum follow-up registrado. Use quando alguém
  perguntar "quais leads estão esfriando?", "tem lead sem follow-up?",
  "quem a gente tá deixando pra trás?" ou similar.
---

# Leads Esfriando

## O que faz

Lê a planilha de leads, cruza a data de entrada com a data do último follow-up e identifica leads que estão esfriando — ou seja, entraram há mais de 7 dias e não receberam nenhum contato ou o último contato foi há mais de 7 dias.

---

## Input

- Arquivo CSV ou planilha de leads com as colunas:
  - `nome` — nome do lead
  - `email` — email do lead
  - `data_entrada` — data em que o lead entrou (formato YYYY-MM-DD)
  - `ultimo_followup` — data do último follow-up (formato YYYY-MM-DD ou vazio)
  - `canal` — canal de origem (Meta Ads, YouTube, Indicação, etc.)
  - `status` — status atual (novo, em_contato, qualificado, perdido, convertido)

---

## Processo

1. **Ler o arquivo de leads** — usar `imersao/dados-demo/leads.csv` (demo) ou o arquivo configurado para produção
2. **Filtrar leads ativos** — excluir leads com status `convertido` ou `perdido`
3. **Calcular dias sem contato:**
   - Se `ultimo_followup` está vazio → dias desde `data_entrada`
   - Se `ultimo_followup` tem data → dias desde `ultimo_followup`
4. **Identificar leads esfriando** — dias sem contato > 7
5. **Ordenar por urgência** — quem está há mais tempo sem contato primeiro
6. **Classificar por gravidade:**
   - 🔴 **Crítico** — mais de 14 dias sem contato
   - 🟡 **Atenção** — entre 8 e 14 dias sem contato
7. **Gerar relatório** com lista priorizada e sugestão de ação

---

## Output esperado

```
🧊 LEADS ESFRIANDO
Relatório gerado em: 25/03/2026
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total de leads ativos: 42
Leads esfriando: 8 (19%)

🔴 CRÍTICOS (>14 dias sem contato)

1. João Silva — joao@empresa.com
   Entrada: 05/03 · Último contato: 08/03 (17 dias atrás)
   Canal: Meta Ads · Status: em_contato
   → Sugestão: contato urgente ou marcar como perdido

2. Maria Santos — maria@corp.com
   Entrada: 02/03 · Sem follow-up registrado (23 dias)
   Canal: YouTube · Status: novo
   → Sugestão: primeiro contato imediato

🟡 ATENÇÃO (8-14 dias sem contato)

3. Pedro Lima — pedro@startup.io
   Entrada: 14/03 · Último contato: 15/03 (10 dias atrás)
   Canal: Indicação · Status: qualificado
   → Sugestão: reengajar com conteúdo relevante

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Resumo: 2 críticos, 1 atenção
Ação recomendada: priorizar os 🔴 críticos hoje
```

---

## Notas

- Leads com status `convertido` ou `perdido` são excluídos da análise
- O threshold padrão é 7 dias, mas aceita parâmetro customizado
- Se não houver coluna `ultimo_followup`, usa apenas `data_entrada`
- Pode ser combinada com um cron para rodar toda segunda-feira automaticamente
