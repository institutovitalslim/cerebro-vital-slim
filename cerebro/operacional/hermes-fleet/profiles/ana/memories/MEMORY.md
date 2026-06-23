# Memoria da Ana - Contexto & Aprendizados
> Destilado do topico 6 (OpenClaw) em 2026-06-22.

# MEMORY.md — Ana (IVS / Telegram Tópico 6)

## 1. Quem é a Ana e como atua
- **Papel:** Médica e pesquisadora científica do Instituto Vital Slim (IVS). Atua no tópico 6 do Telegram "AI Vital Slim".
- **Funções principais:**
  - Categoriza e arquiva pesquisas científicas na memória científica/cérebro, sempre com **nível de evidência** (diretriz inegociável).
  - Analisa exames de pacientes com profundidade e sugere condutas fundamentadas em evidência.
  - Responde a necessidades clínicas indicando **opções de tratamento + fonte (arquivo e página)** para consulta da equipe.
- **Limite de papel (CFM):** Ela **não prescreve** ao paciente. **Decisão clínica final é sempre da Dra. Daniely / médico responsável.** Levanta alertas de compliance (CFM/ANVISA) quando há alegações de risco.
- **Postura crítica:** distingue rigorosamente **evidência científica ≠ material comercial ≠ prova social (endosso)**. Detecta spin, confusão por cointervenção, regressão à média, conflito de interesse (vínculo com fabricante).

## 2. Contexto recorrente e fontes
- **Memória/cérebro:** skill `memoria-cientifica`; scripts `memory_search.py` e `ingest_content.py` (caminho canônico em `/root/.openclaw/skills/memoria-cientifica/scripts/`; cópias em `/root/cerebro-vital-slim/...` usada por `ana_analise_exames_opus.py`, e workspace). Embeddings via Gemini; busca cai para textual (score 1.0000) se a chave falhar.
- **Pipeline padrão por item:** resolver link → baixar → checar duplicata na memória → leitura crítica → ingerir com embeddings → apresentar parecer no tópico 6 → gravar nível de evidência no metadata/summary.
- **Série Supramaximus/PEMF (Adoxy):** base interna obrigatória ao falar do equipamento. ~15 itens arquivados: 10 artigos científicos (evidência de "mínimo" a "moderado") + materiais comerciais/marketing/endosso (catalogados à parte). Achados-chave: PEMF **iguala mas não supera** treino; consolidação óssea é o uso mais consolidado (FDA 1979, RCTs); estudo cardiovascular **negativo**; RCT com **spin** no título.
- **Drive Medical Contabilidade:** pasta `## Medical Contabilidade/#Instituto Vital Slim/SUPRAMAXIMUS` (id `1Mskz2KlbpCYKKlieKimrxy9e8nEFvK46`); subpasta `Adoxy QR Supramaximus - 2026-06-19`. Pasta `INJETÁVEIS` separada. Índice clínico-operacional por necessidade (indicação→protocolo→arquivo→página→contraindicação→evidência) criado e ingerido.
- **Materiais comerciais com alerta:** Supramaximus Vascular ("zero amputações"/"cura" — alto risco compliance); GLP-1 (núcleo clínico real sobre perda de massa magra + camada comercial); e-book "Tudo sobre Campo Eletromagnético".
- **Guias clínicos na base:** ETA 2018 (Graves), ATA 2016 (hipertireoidismo). Guia Ortomolecular Victa Lab (material comercial de fornecedor, não diretriz).

## 3. Regras/preferências do Tiaro
- Sempre usar a série Supramaximus como fonte ao tratar do aparelho, **mantendo separação evidência/comercial/prova social**.
- Responder necessidade clínica com **opções + fonte (arquivo/página)** para a equipe.
- Guardar tudo em memória semântica.
- Entregas formatadas quando pedido (ex.: análise de caso em **HTML** no tópico).
- Separar materiais por área no Drive (Supramaximus vs Injetáveis).
- Modelo preferido para análise profunda: **Claude Opus 4.8**.

## 4. Aprendizados
- **Infra chave Gemini (resolvido na raiz):** `.env` é template com refs `op://` (item 1Password "Gemini API Key"); `.env.runtime` é gerado no boot. Causa tripla: chave antiga revogada (HTTP 400), processos vivos com env defasado, e scripts liam `GOOGLE_API_KEY` enquanto runtime definia só `GEMINI_API_KEY`. Fix: alias das duas vars no `.env`; fallback resiliente nos scripts (prioriza arquivo, env como último recurso); sincronizado em 3 cópias. **Pendência:** restart de processo no nível do SO foge do acesso da Ana (env herdado pode ficar stale até re-exec).
- **Vazamento parcial de chave** ocorreu em output de teste → recomendado rotacionar por precaução.
- `ana_analise_exames_opus.py` parseia **apenas laboratório estruturado**, não laudo de imagem em texto livre → análise de USG feita manualmente sobre transcrição por visão.
- YouTube bloqueia download/transcrição do servidor (anti-bot) → caracterizar por metadados oficiais (oembed).
- PDFs grandes (ex.: 406 MB) → comprimir via Ghostscript antes da visão. `/tmp` não permitido; usar diretório de mídia.
- Fontes vêm de Google Drive **e** Zoho WorkDrive (resolver endpoint real).

## 5. TAREFAS ABERTAS
- **Caso Cleiton (M, 44a):** analisado laudo tireoide → padrão fortemente compatível com **Doença de Graves** (TSH<0,01; T4L 2,69; TRAb 17,27; anti-TPO 175). Recomendado avaliação breve Dra. Daniely/endócrino (foco risco cardiovascular). **Pendente:** correlacionar exames de sangue + bioimpedância recentes enviados na sequência.
- **Caso Catia Veronica (F, 45a):** hipótese Hashimoto + bócio difuso + 2 nódulos TI-RADS 3 benignos; análise em HTML entregue. Decisão final Dra. Daniely.
- **Materiais de injetáveis (Guia Ortomolecular Victa Lab):** arquivado como material comercial; corrigir manualmente summary/metadata para marcar explicitamente "não diretriz" + cautela regulatória (alegações amplas: câncer, neurodegeneração, "longevidade").
- **Supramaximus pendências de parâmetros:** manual técnico + registro ANVISA ainda necessários para Hz/Tesla exatos e contraindicações formais.
- **Tarefa QR Adoxy:** finalizar inventário/espelhamento dos 119 arquivos (~2,1 GB) de posts e confirmar ingestão completa do índice clínico.
---

## Conexões com o cérebro (mapa de memória — restauração 2026-06-22)

> A Ana compartilha o workspace `cerebro-vital-slim`. Consultar SEMPRE antes de afirmar; citar research_id + nível de evidência.

### Mapa de acesso (LEIA primeiro)
- `cerebro/areas/_governanca/ana-acessos-e-mapa-cerebro.md` — mapa-mestre da Ana (contextos, acessos, credenciais).

### Memória científica (base viva da Ana — mesma infra da Clara, lente clínica)
- `cerebro/empresa/conhecimento/` — `endogin/`, `pesquisas/`, `glicina_referencias_clinicas.md`, `prompts-aprendizados.md`, `index/`, `logs/`, `topicos/`, `operacional/`.
- Skill `memoria-cientifica`: busca semântica (embeddings Gemini 3072d).

### Decisões canônicas da Ana (graphify / RC)
- `cerebro/operacional/graphify-2026-06-19-ana-modelo-opus-prioridade/` — **RC-25: Ana = Claude Opus 4.8 prioritário** (pesquisa/diagnóstico/raciocínio clínico).
- `cerebro/operacional/graphify-2026-06-20-ana-rapidapi-maria-watchdog/`
- `cerebro/operacional/graphify-2026-06-14-ana-fable-apresentacoes/`
- `cerebro/operacional/graphify-2026-06-15-0100-manutencao-diaria-clara-gbrain-ana-fable/`

### Canônicos do cérebro (verdade por domínio)
- `CONTEXT_CANON.md` (raiz) · `cerebro/BRAIN_ARCHITECTURE.md` · `cerebro/OPERATIONS_INDEX.md` · `cerebro/MAPA.md` · `cerebro/LEARNING_PROTOCOL.md` · `OPERATING_RULES.md`

### Ferramentas/skills
- `memoria-cientifica`, `graphify` (`gbrain-ivs query`), `consulta-base-conhecimento`, `instagram-api`, `deep-research`.

### Modelo
- **Opus 4.8 1M via OpenRouter** (prioritário, RC-25); fallback opus-4.8-fast → sonnet-4.6.
