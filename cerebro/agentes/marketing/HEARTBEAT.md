# HEARTBEAT.md — Agente de Marketing

A cada heartbeat (verificação periódica), fazer:

### 1. Monitoramento de ROAS
- Verificar campanhas ativas em `cerebro/areas/marketing/sub-areas/trafego-pago/`
- Se ROAS < 1.0 por 3 dias consecutivos → **alertar imediatamente** no tópico 📢 Marketing (topic_id: 8)

### 2. Pendências de marketing
- Ler `cerebro/empresa/gestao/pendencias.md` (filtrar itens de marketing)
- Se item aguarda resposta há mais de 3 dias → alertar

### 3. Calendário de conteúdo
- Verificar `cerebro/areas/marketing/sub-areas/conteudo/`
- Se alguma publicação agendada não foi confirmada → alertar Camila

### 4. Consolidação de memória
- Ler notas diárias em `memory/`
- Se houver notas com mais de 3 dias → consolidar no cerebro/ e deletar as notas
