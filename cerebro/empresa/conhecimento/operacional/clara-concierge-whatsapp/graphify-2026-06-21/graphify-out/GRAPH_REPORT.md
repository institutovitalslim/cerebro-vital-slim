# Graph Report - raw  (2026-06-21)

## Corpus Check
- Corpus is ~1,495 words - fits in a single context window. You may not need a graph.

## Summary
- 16 nodes · 16 edges · 4 communities detected
- Extraction: 81% EXTRACTED · 19% INFERRED · 0% AMBIGUOUS · INFERRED: 3 edges (avg confidence: 0.78)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Aprendizado Externo Governado|Aprendizado Externo Governado]]
- [[_COMMUNITY_Governanca Interna e Cerebro|Governanca Interna e Cerebro]]
- [[_COMMUNITY_Conversao Premium e SPIN|Conversao Premium e SPIN]]
- [[_COMMUNITY_Envio Real WhatsApp e Curadoria|Envio Real WhatsApp e Curadoria]]

## God Nodes (most connected - your core abstractions)
1. `RC-60 Governança do aprendizado externo` - 5 edges
2. `RC-57 Conversão Premium WhatsApp (Conselho Growth)` - 3 edges
3. `RC-65 Conselhos internos (Growth + LLM Council)` - 3 edges
4. `Classificação de promoção (aplicar/testar/descartar/propor RC-25)` - 3 edges
5. `RC-25 atualização via graphify (governança canônica)` - 3 edges
6. `RC-61 Autonomia evolutiva governada` - 2 edges
7. `RC-62 Operação Telegram tópico Concierge Clara` - 2 edges
8. `RC-63 Rota real WhatsApp Z-API` - 2 edges
9. `RC-64 Curadoria Maria em falha de envio` - 2 edges
10. `RC-58 Aprendizado RapidAPI Instagram/X` - 1 edges

## Surprising Connections (you probably didn't know these)
- `RC-65 Conselhos internos (Growth + LLM Council)` --rationale_for--> `RC-57 Conversão Premium WhatsApp (Conselho Growth)`  [INFERRED]
  raw/APRENDIZADOS_2026-06-21.md → raw/APRENDIZADOS_2026-06-21.md  _Bridges community 2 → community 1_
- `RC-62 Operação Telegram tópico Concierge Clara` --conceptually_related_to--> `RC-63 Rota real WhatsApp Z-API`  [EXTRACTED]
  raw/APRENDIZADOS_2026-06-21.md → raw/APRENDIZADOS_2026-06-21.md  _Bridges community 1 → community 3_
- `Classificação de promoção (aplicar/testar/descartar/propor RC-25)` --references--> `RC-25 atualização via graphify (governança canônica)`  [EXTRACTED]
  raw/APRENDIZADOS_2026-06-21.md → raw/APRENDIZADOS_2026-06-21.md  _Bridges community 0 → community 1_

## Hyperedges (group relationships)
- **Aprendizado externo governado (RapidAPI + YouTube + orchestrator + autonomia)** — aprendizados_rc58_rapidapi, aprendizados_rc59_youtube, aprendizados_rc60_governanca_externa, aprendizados_rc61_autonomia_evolutiva [EXTRACTED 0.90]
- **Operação interna Telegram + envio real + curadoria + conselhos** — aprendizados_rc62_telegram_concierge, aprendizados_rc63_zapi_envio_real, aprendizados_rc64_curadoria_maria, aprendizados_rc65_conselhos_internos [EXTRACTED 0.90]

## Communities

### Community 0 - "Aprendizado Externo Governado"
Cohesion: 0.4
Nodes (6): Classificação de promoção (aplicar/testar/descartar/propor RC-25), Filtro anti-guru, RC-58 Aprendizado RapidAPI Instagram/X, RC-59 Aprendizado YouTube, RC-60 Governança do aprendizado externo, RC-61 Autonomia evolutiva governada

### Community 1 - "Governanca Interna e Cerebro"
Cohesion: 0.5
Nodes (4): RC-25 atualização via graphify (governança canônica), RC-62 Operação Telegram tópico Concierge Clara, RC-65 Conselhos internos (Growth + LLM Council), RC-66 GBrain memory-bridge

### Community 2 - "Conversao Premium e SPIN"
Cohesion: 0.67
Nodes (3): RC-57 Conversão Premium WhatsApp (Conselho Growth), Regra de ouro: não dar preço cedo, SPIN curto para WhatsApp

### Community 3 - "Envio Real WhatsApp e Curadoria"
Cohesion: 0.67
Nodes (3): Maria (curadoria/governança de envio), RC-63 Rota real WhatsApp Z-API, RC-64 Curadoria Maria em falha de envio

## Knowledge Gaps
- **7 isolated node(s):** `RC-58 Aprendizado RapidAPI Instagram/X`, `RC-59 Aprendizado YouTube`, `RC-66 GBrain memory-bridge`, `SPIN curto para WhatsApp`, `Filtro anti-guru` (+2 more)
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RC-65 Conselhos internos (Growth + LLM Council)` connect `Governanca Interna e Cerebro` to `Conversao Premium e SPIN`?**
  _High betweenness centrality (0.648) - this node is a cross-community bridge._
- **Why does `RC-25 atualização via graphify (governança canônica)` connect `Governanca Interna e Cerebro` to `Aprendizado Externo Governado`?**
  _High betweenness centrality (0.590) - this node is a cross-community bridge._
- **Why does `Classificação de promoção (aplicar/testar/descartar/propor RC-25)` connect `Aprendizado Externo Governado` to `Governanca Interna e Cerebro`?**
  _High betweenness centrality (0.476) - this node is a cross-community bridge._
- **What connects `RC-58 Aprendizado RapidAPI Instagram/X`, `RC-59 Aprendizado YouTube`, `RC-66 GBrain memory-bridge` to the rest of the system?**
  _7 weakly-connected nodes found - possible documentation gaps or missing edges._