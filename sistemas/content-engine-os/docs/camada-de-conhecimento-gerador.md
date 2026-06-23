# Camada de Conhecimento do Gerador — Content Engine OS

> Tudo que o **orquestrador de geração** deve consultar antes de criar uma peça (aproveitar o aprendizado IVS já existente). Ordem: contexto do workspace → bibliotecas estruturadas → GBrain (retrieval) → regras canônicas → render.

## 1. No banco (content_engine, por workspace + acervo global IVS)
- **narrative_devices** — 38 dispositivos de engenharia social (Stories 10x) com lógica + exemplo + instrução p/ IA. (seed global)
- **viral_scripts** — biblioteca de roteiros virais (bunker IVS): objetivo, classe_ivs, mecanismo, hook_base, tese, objeção, adaptacao_ivs, uso. (seed: IVS-BKR-0001..0005; cresce via importer do bunker)
- **ctas** — 7 tipos de CTA.
- **themes / personas / products / scientific_sources** — por workspace.
- **brand_kits** — design system derivado dos uploads do cliente (`derive_design_system.py`).

## 2. No GBrain (retrieval semântico — `gbrain-ivs query`)
- **30 hooks** prontos — `cerebro/areas/marketing/performance-5x/biblioteca-hooks`.
- **Biblioteca de temas por pilar** + o que NÃO falar — `performance-5x/biblioteca-temas`.
- **Posicionamento, persona (Marina/Camila), arquétipos (Sábio+Cuidador), 5 pilares** — `performance-5x/posicionamento-persona-arquetipos`.
- **Roteiros dos 8 destaques** (banco de Reels) — `performance-5x/roteiros-destaques`.
- **Aprendizados de Reels** (varredura Instagram) — `cerebro/areas/marketing/reels-sistema-aprendizados...`.
- **Regras canônicas** (todas no GBrain): estratégia por formato (Reels=engajamento CTA salvar/compartilhar; Carrossel feed=salvar/compartilhar+autoridade, Meta Ads=lead p/ agendamento; Stories=conexão); formato 4:5 feed / 9:16 reels-stories + zona segura; capa sempre com a Dra.; figurino de grife sem jaleco; foto-led; alvo declarado; validação visual obrigatória.

## 3. Bunker vivo (fonte de roteiros que cresce)
`cerebro/areas/marketing/projetos/bunker-roteiros-ivs/bunker.db` (CLI `bunker_cli.py`). Importer `scripts/seed_viral_scripts.py` puxa o núcleo md → `viral_scripts`. Conforme o bunker é alimentado (5 fontes externas + classificador), re-rodar o importer atualiza o acervo do SaaS.

## 4. Científico (autoridade médica — motor A e B)
Skill `memoria-cientifica` (embeddings Gemini + Perplexity) + PubMed/SciELO (fase 3). Claims sempre com fonte + nível de evidência. Tabela `scientific_sources`.

## 5. Render (peça final)
`render_worker/render_creative.py` (design-system-ivs + Higgsfield + Soul `3dc66ac7` + voz ElevenLabs `XS8ZgYWcmuEDV1DWLp57`). `derive_design_system.py` para o brand kit por upload.

## Como o orquestrador usa (motor A)
1. Recebe: workspace + objetivo/funil + rede + formato + (tema OU persona OU produto).
2. Puxa contexto: tema (DB) + persona/dores (DB) + posicionamento (GBrain) + hooks (GBrain) + dispositivos relevantes (DB) + roteiro viral análogo (viral_scripts por objetivo/classe) + científica (se claim).
3. Gera roteiro/legenda/título/hashtags via OpenRouter, no dispositivo certo, respeitando regras canônicas + compliance.
   - Regra canônica de legenda: toda legenda/caption deve terminar com `Dra Daniely Freitas`, `Médica, Farmacêutica e Professora de Medicina`, `CRM-BA 27.588` e o disclaimer `(Este conteúdo tem caráter meramente educativo e não substitui uma consulta médica.)`.
   - O backend aplica esse rodapé de forma determinística antes de persistir `caption`/`legenda`, mesmo se o LLM esquecer.
4. Auto-avalia (checklists pontuados) → só passa acima do score.
5. Renderiza a peça visual (render_creative) → `creatives.asset_url` + quality_score.
