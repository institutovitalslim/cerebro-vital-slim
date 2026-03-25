# Bloco 9: Deep Dive — Sistema de Criativos (Marketing)

**Timing:** 10h05–10h40 (35 minutos)

---

## O que cobrir

- O ciclo completo de criativos com IA
- 3 skills de marketing (relatório, análise, criação)
- 3 crons para rodar o ciclo automaticamente
- Pipeline visual do processo
- Demo: "Qual próximo criativo faz sentido?"

---

## Demos e arquivos

| Demo | Arquivo/Path |
|------|-------------|
| Pasta de formatos | `areas/marketing/criativos/formatos/` |
| Pasta de criativos | `areas/marketing/criativos/` |
| Skill de relatório | `areas/marketing/skills/relatorio-ads.md` |
| Skill de análise | `areas/marketing/skills/analise-performance.md` |
| Skill de criação | `areas/marketing/skills/gerar-criativo.md` |
| Daily report (dados fake) | `areas/marketing/reports/daily-2026-03-27.md` |

---

## Como fazer

**Passo 1 — O ciclo (5 min)**

Desenhe (ou mostre diagrama) o ciclo:

```
HIPÓTESE → CRIATIVO → TESTE → DADO → CONCLUSÃO → NOVA HIPÓTESE
    ↑_______________________________________________|
```

> "Hoje a maioria das equipes faz isso manualmente. Coletam dados de um lado, analisam em outro, criam em outro. O agente fecha esse loop."

**Passo 2 — Estrutura de pastas (5 min)**

Mostre ao vivo:
```
areas/marketing/
├── criativos/
│   ├── formatos/          ← templates por formato (carrossel, reels, story)
│   │   ├── carrossel.md
│   │   └── reels.md
│   └── 2026-03/           ← criativos do mês
├── skills/
│   ├── relatorio-ads.md
│   ├── analise-performance.md
│   └── gerar-criativo.md
└── reports/
    └── daily-2026-03-27.md
```

**Passo 3 — As 3 skills (10 min)**

Abra cada skill rapidamente e explique:

1. **relatorio-ads.md:** "Conecta na API de ads, puxa os dados, formata o relatório diário."
2. **analise-performance.md:** "Compara criativos, identifica padrões, aponta o que está funcionando."
3. **gerar-criativo.md:** "Com base na análise, gera o próximo criativo — texto, hook, call-to-action."

**Passo 4 — Daily report ao vivo (8 min)**

Abra `reports/daily-2026-03-27.md` (com dados fake preparados). Leia em voz alta os números.

Depois, peça ao agente:
> "Com base neste relatório de performance, qual o próximo criativo que faz mais sentido testar?"

Mostre a resposta do agente. Ela deve ser específica: formato, hook sugerido, por quê.

> "Isso é o agente fechando o loop. Dos dados → para a próxima ação."

**Passo 5 — Os 3 crons (5 min)**

Mostre rapidamente os 3 crons configurados:
- `0 7 * * *` → relatório diário às 7h
- `0 8 * * 1` → análise de semana toda segunda às 8h
- `0 9 * * 1` → sugestão de criativo logo depois

---

## NÃO mostrar

- Configuração real de API do Meta Ads (bastidores)
- Processo de aprovação de criativos
- Ferramenta de design (Canva, etc.)

---

## Checkpoint

✅ Ciclo HIPÓTESE→CRIATIVO→TESTE→DADO explicado  
✅ Estrutura de pastas navegada  
✅ 3 skills mostradas  
✅ Daily report + resposta do agente executados ao vivo  
✅ 3 crons apresentados  
→ Avançar para `dia2/pausa.md`
