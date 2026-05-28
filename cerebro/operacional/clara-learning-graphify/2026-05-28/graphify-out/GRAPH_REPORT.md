# Graph Report - /root/cerebro-vital-slim/cerebro/operacional/clara-learning-graphify/2026-05-28  (2026-05-28)

## Corpus Check
- 9 files · ~420 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 18 nodes · 14 edges · 6 communities detected
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Clara agendamento e conversão|Clara agendamento e conversão]]
- [[_COMMUNITY_Governança e risco operacional|Governança e risco operacional]]
- [[_COMMUNITY_Governança e risco operacional|Governança e risco operacional]]
- [[_COMMUNITY_Governança e risco operacional|Governança e risco operacional]]
- [[_COMMUNITY_Governança e risco operacional|Governança e risco operacional]]
- [[_COMMUNITY_Governança e risco operacional|Governança e risco operacional]]

## God Nodes (most connected - your core abstractions)
1. `Primeira resposta curta` - 4 edges
2. `Triagem segura sem diagnóstico` - 3 edges
3. `Teste operacional 3 dias` - 3 edges
4. `Reserva assistida para início do mês` - 2 edges
5. `Verificação humana dos logs WhatsApp/Z-API` - 2 edges
6. `RC-25 Graphify` - 2 edges
7. `Clara máquina de agendamento` - 1 edges
8. `Leads com mensagens ultra-curtas` - 1 edges
9. `Pergunta operacional de agenda` - 1 edges
10. `Preço e endereço como gatilhos de abertura` - 1 edges

## Surprising Connections (you probably didn't know these)
- `Primeira resposta curta` --classification--> `Teste operacional 3 dias`  [EXTRACTED]
  /root/cerebro-vital-slim/cerebro/operacional/clara-learning-graphify/2026-05-28/raw/qa-diaria-conversao-20260528-0130.md → /root/cerebro-vital-slim/cerebro/operacional/clara-learning-graphify/2026-05-28/raw/qa-diaria-conversao-20260528-0130.md  _Bridges community 0 → community 1_
- `Triagem segura sem diagnóstico` --registered_in--> `RC-25 Graphify`  [EXTRACTED]
  /root/cerebro-vital-slim/cerebro/operacional/clara-learning-graphify/2026-05-28/raw/qa-diaria-conversao-20260528-0130.md → /root/cerebro-vital-slim/cerebro/operacional/clara-learning-graphify/2026-05-28/raw/qa-diaria-conversao-20260528-0130.md  _Bridges community 2 → community 1_

## Communities

### Community 0 - "Clara agendamento e conversão"
Cohesion: 0.5
Nodes (4): Leads com mensagens ultra-curtas, Pergunta operacional de agenda, Preço e endereço como gatilhos de abertura, Primeira resposta curta

### Community 1 - "Governança e risco operacional"
Cohesion: 0.5
Nodes (4): Objeção financeira por adiamento, RC-25 Graphify, Reserva assistida para início do mês, Teste operacional 3 dias

### Community 2 - "Governança e risco operacional"
Cohesion: 0.67
Nodes (3): Menção espontânea de saúde, Paciente existente ou demanda administrativa, Triagem segura sem diagnóstico

### Community 3 - "Governança e risco operacional"
Cohesion: 0.67
Nodes (3): Não pausar Clara sem ordem explícita do Tiaro, Risco médio: inbound sem outbound no recorte, Verificação humana dos logs WhatsApp/Z-API

### Community 4 - "Governança e risco operacional"
Cohesion: 1.0
Nodes (2): CTA fechado de confirmação, Clara máquina de agendamento

### Community 5 - "Governança e risco operacional"
Cohesion: 1.0
Nodes (2): Discovery antes de empurrar consulta, Lead em pesquisa

## Knowledge Gaps
- **12 isolated node(s):** `Clara máquina de agendamento`, `Leads com mensagens ultra-curtas`, `Pergunta operacional de agenda`, `Preço e endereço como gatilhos de abertura`, `Objeção financeira por adiamento` (+7 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Governança e risco operacional`** (2 nodes): `CTA fechado de confirmação`, `Clara máquina de agendamento`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Governança e risco operacional`** (2 nodes): `Discovery antes de empurrar consulta`, `Lead em pesquisa`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Teste operacional 3 dias` connect `Governança e risco operacional` to `Clara agendamento e conversão`?**
  _High betweenness centrality (0.235) - this node is a cross-community bridge._
- **Why does `Primeira resposta curta` connect `Clara agendamento e conversão` to `Governança e risco operacional`?**
  _High betweenness centrality (0.176) - this node is a cross-community bridge._
- **Why does `RC-25 Graphify` connect `Governança e risco operacional` to `Governança e risco operacional`?**
  _High betweenness centrality (0.154) - this node is a cross-community bridge._
- **What connects `Clara máquina de agendamento`, `Leads com mensagens ultra-curtas`, `Pergunta operacional de agenda` to the rest of the system?**
  _12 weakly-connected nodes found - possible documentation gaps or missing edges._