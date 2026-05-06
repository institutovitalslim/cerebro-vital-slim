# Auditoria executiva — Clara implementação 2026-05-06

Status: APROVADA

Checks: 15 aprovados / 0 falhas.

## Checks
- [OK] RapidAPI Social Learning tem endpoint x-profile para timelines do X — social_learning.py contém def x_profile e timeline.php
- [OK] Lista priorizada de perfis X foi colocada no learning da Clara — clara_learning.py contém X_PROFILES com Gong_io, close, Outreach_io, Patrick Dang, Hormozi, Hyken, Salesforce, Zocdoc
- [OK] Script de estudo de conversas atuais do WhatsApp existe — whatsapp_clara_learning.py suporta --mode current
- [OK] Script de estudo histórico do WhatsApp existe — whatsapp_clara_learning.py suporta --mode historical e janela de 180 dias
- [OK] Aprendizado WhatsApp atual gerou JSON latest — {'total_messages': 8, 'unique_leads': 4, 'total_inbound': 8, 'total_outbound': 0, 'wins': 0, 'drops': 0}
- [OK] Aprendizado WhatsApp histórico gerou JSON latest — {'total_messages': 5060, 'unique_leads': 322, 'total_inbound': 2150, 'total_outbound': 2910, 'wins': 23, 'drops': 5}
- [OK] Relatório atual está no cérebro — /root/cerebro-vital-slim/cerebro/logs/clara-whatsapp-learning/latest-whatsapp-current.md
- [OK] Relatório histórico está no cérebro — /root/cerebro-vital-slim/cerebro/logs/clara-whatsapp-learning/latest-whatsapp-historical.md
- [OK] Pipeline Graphify diário da Clara existe — graphify_clara_learning.py gera graph.json/html/GRAPH_REPORT.md
- [OK] Graphify diário de hoje está no cérebro — /root/cerebro-vital-slim/cerebro/operacional/clara-learning-graphify/2026-05-06/graphify-out/graph.json
- [OK] Graphify diário inclui slots WhatsApp atual e histórico — labels do graph.json contêm whatsapp-current e whatsapp-historical
- [OK] Esta auditoria Graphify está sendo gravada no cérebro — /root/cerebro-vital-slim/cerebro/operacional/graphify-2026-05-06-auditoria-implementacao-clara
- [OK] Cron WhatsApp atual 2/2h está ativo no OpenClaw — 375d74ed — 15 8-22/2 * * * America/Bahia
- [OK] Cron WhatsApp histórico semanal está ativo no OpenClaw — cba17d20 — 30 6 * * 1 America/Bahia
- [OK] Cron Graphify RC-25 diário está ativo no OpenClaw — 0161e7ec — 5 22 * * * America/Bahia

## Saídas Graphify
- `/root/cerebro-vital-slim/cerebro/operacional/graphify-2026-05-06-auditoria-implementacao-clara/graphify-out/graph.json`
- `/root/cerebro-vital-slim/cerebro/operacional/graphify-2026-05-06-auditoria-implementacao-clara/graphify-out/graph.html`
- `/root/cerebro-vital-slim/cerebro/operacional/graphify-2026-05-06-auditoria-implementacao-clara/graphify-out/GRAPH_REPORT.md`
- Raw: `/root/cerebro-vital-slim/cerebro/operacional/graphify-2026-05-06-auditoria-implementacao-clara/raw`

---

# Graph Report - /root/cerebro-vital-slim/cerebro/operacional/graphify-2026-05-06-auditoria-implementacao-clara  (2026-05-06)

## Corpus Check
- 18 files · ~0 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 27 nodes · 48 edges · 4 communities detected
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Auditoria Graphify implementação Clara 2026-05-06  Cérebro Vital Slim  cerebrologsclar|Auditoria Graphify implementação Clara 2026-05-06 / Cérebro Vital Slim / cerebro/logs/clar]]
- [[_COMMUNITY_cerebrooperacionalclara-learning-graphify2026-05-06  Esta auditoria Graphify está send|cerebro/operacional/clara-learning-graphify/2026-05-06 / Esta auditoria Graphify está send]]
- [[_COMMUNITY_Relatório histórico está no cérebro  Aprendizado WhatsApp histórico gerou JSON latest  S|Relatório histórico está no cérebro / Aprendizado WhatsApp histórico gerou JSON latest / S]]
- [[_COMMUNITY_Relatório atual está no cérebro  Aprendizado WhatsApp atual gerou JSON latest  Script de|Relatório atual está no cérebro / Aprendizado WhatsApp atual gerou JSON latest / Script de]]

## God Nodes (most connected - your core abstractions)

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Communities

### Community 0 - "Auditoria Graphify implementação Clara 2026-05-06 / Cérebro Vital Slim / cerebro/logs/clar"
Cohesion: 0.33
Nodes (9): Auditoria Graphify implementação Clara 2026-05-06, Cérebro Vital Slim, cerebro/logs/clara-whatsapp-learning, RapidAPI Social Learning tem endpoint x-profile para timelines do X, Lista priorizada de perfis X foi colocada no learning da Clara, Clara WhatsApp, clara-learning-orchestrator/clara_learning.py, Clara aprende com perfis X/Twitter priorizados (+1 more)

### Community 1 - "cerebro/operacional/clara-learning-graphify/2026-05-06 / Esta auditoria Graphify está send"
Cohesion: 0.29
Nodes (7): cerebro/operacional/clara-learning-graphify/2026-05-06, Esta auditoria Graphify está sendo gravada no cérebro, Graphify diário de hoje está no cérebro, Pipeline Graphify diário da Clara existe, Graphify diário inclui slots WhatsApp atual e histórico, clara-learning-orchestrator/graphify_clara_learning.py, Aprendizados entram no cérebro via Graphify/RC-25

### Community 2 - "Relatório histórico está no cérebro / Aprendizado WhatsApp histórico gerou JSON latest / S"
Cohesion: 0.33
Nodes (6): Relatório histórico está no cérebro, Aprendizado WhatsApp histórico gerou JSON latest, Script de estudo histórico do WhatsApp existe, Clara estuda conversas antigas do WhatsApp, zapi_bridge/whatsapp_clara_learning.py, latest-whatsapp-historical.json

### Community 3 - "Relatório atual está no cérebro / Aprendizado WhatsApp atual gerou JSON latest / Script de"
Cohesion: 0.4
Nodes (5): Relatório atual está no cérebro, Aprendizado WhatsApp atual gerou JSON latest, Script de estudo de conversas atuais do WhatsApp existe, Clara estuda conversas atuais do WhatsApp, latest-whatsapp-current.json