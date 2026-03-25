# SKILL — Relatório de Ads

## O Que Faz
Puxa dados da Meta Ads API, analisa performance de criativos e campanhas, e gera relatório formatado com métricas, alertas e recomendações.

---

## Input
- Período desejado (padrão: últimas 24h ou última semana)
- Nível de análise: campanha, conjunto de anúncios ou criativo
- Opcional: CPL alvo e ROAS mínimo da empresa

## Processo

### 1. Autenticação e Coleta
```
META_ADS_TOKEN e META_ADS_ACCOUNT_ID do ambiente
Endpoint: https://graph.facebook.com/v21.0/{account_id}/insights
Parâmetros: date_preset, level, fields
```

### 2. Campos Coletados
- `spend` — investimento
- `impressions` — impressões
- `clicks` — cliques no link
- `ctr` — CTR
- `cpc` — custo por clique
- `actions` (leads) — conversões
- `cost_per_action_type` (CPL)
- `frequency` — frequência média
- `reach` — alcance único

### 3. Cálculos
- **CPL** = spend ÷ leads
- **ROAS** = receita atribuída ÷ spend (se conversão de venda configurada)
- **CPA** = spend ÷ conversões totais
- **Taxa de conversão** = leads ÷ cliques × 100

### 4. Análise de Criativos
- Ranquear por CTR (decrescente)
- Identificar frequência > 4 (saturação)
- Comparar CPL atual vs média histórica

### 5. Geração do Relatório
- Formatar conforme template em `rotinas/meta-ads-report.md`
- Aplicar alertas automáticos (CPL > R$60, zero leads, freq > 4)
- Incluir top 3 criativos e candidatos a pausar

## Output

Relatório em markdown formatado:
```
📊 Report Meta Ads — {DATA/PERÍODO}
💰 Investimento: R$ X
🎯 Leads: N | CPL: R$ X | ROAS: Xx
🏆 Top criativo: [nome] CTR X%, CPL R$ X
⚠️ [Alertas se houver]
```

---

## Referências
- Contexto de tráfego: `areas/marketing/sub-areas/trafego-pago/MAPA.md`
- Learnings: `areas/marketing/sub-areas/trafego-pago/learnings/resumo.md`
- Template de relatório: `areas/marketing/sub-areas/trafego-pago/rotinas/meta-ads-report.md`
