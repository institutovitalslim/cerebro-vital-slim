# Graph Report - raw  (2026-05-05)

## Corpus Check
- 6 files · ~6,400 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 25 nodes · 49 edges · 4 communities detected
- Extraction: 84% EXTRACTED · 16% INFERRED · 0% AMBIGUOUS · INFERRED: 8 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Governança e modelo operacional|Governança e modelo operacional]]
- [[_COMMUNITY_Governança e modelo operacional|Governança e modelo operacional]]
- [[_COMMUNITY_Runtime e governança do João|Runtime e governança do João]]
- [[_COMMUNITY_Conteúdo social e vídeo curto|Conteúdo social e vídeo curto]]

## God Nodes (most connected - your core abstractions)
1. `Modelo de subagentes sob demanda` - 20 edges
2. `João como agente principal` - 17 edges
3. `frontend-developer` - 4 edges
4. `ui-designer` - 4 edges
5. `reality-checker` - 4 edges
6. `instagram-curator` - 4 edges
7. `Runtime prompt João — regra de subagentes sob demanda` - 4 edges
8. `Não criar 12 agentes fixos agora` - 3 edges

## Surprising Connections (you probably didn't know these)
- `runtime_prompt_joao_subagentes` --related_to--> `modelo_subagentes_sob_demanda`  [EXTRACTED]
   → 

## Communities

### Community 0 - "Governança e modelo operacional"
Cohesion: 0.31
Nodes (9): agency-agents como referência adaptada, Fontes e Ferramentas do João, frontend-developer, Modelo de subagentes sob demanda, project-shepherd, PROMPT-BASE do João, Regras de Operação do João, ui-designer (+1 more)

### Community 1 - "Governança e modelo operacional"
Cohesion: 0.43
Nodes (7): accessibility-auditor, api-tester, Briefing canônico para subagente, João como agente principal, performance-benchmarker, reality-checker, tool-evaluator

### Community 2 - "Runtime e governança do João"
Cohesion: 0.33
Nodes (6): Critério de promoção para agente fixo, Fluxo Tiaro → João → subagente → João → Tiaro, Guardrails IVS para subagentes, Memória 2026-05-05, Não criar 12 agentes fixos agora, Runtime prompt João — regra de subagentes sob demanda

### Community 3 - "Conteúdo social e vídeo curto"
Cohesion: 0.67
Nodes (3): instagram-curator, short-video-coach, social-media-strategist

## Knowledge Gaps
- **5 isolated node(s):** `Briefing canônico para subagente`, `PROMPT-BASE do João`, `Regras de Operação do João`, `Fontes e Ferramentas do João`, `agency-agents como referência adaptada`
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **A regra de subagentes está no runtime do João?**
  _Valida sincronização de execução._
- **Quando João deve acionar um subagente sob demanda?**
  _Define o gatilho operacional._
- **Quando uma especialidade vira agente fixo?**
  _Evita proliferação prematura._