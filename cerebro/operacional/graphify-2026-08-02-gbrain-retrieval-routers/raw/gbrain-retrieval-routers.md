---
type: operational-change
status: accepted
owner: maria
approved_by: tiaro
created: 2026-08-02
updated: 2026-08-02
aliases:
  - RC-25 GBrain retrieval routers
  - correção retrieval Resolver Clara Marketing
---
# RC-25 — Roteadores de retrieval do GBrain

## Decisão

Criar seis páginas-roteador, sem duplicar autoridade canônica, para corrigir lacunas Top 3 e falsos positivos por páginas não rastreadas detectados pelo benchmark governado:

1. Governança GBrain, Graphify e RC-25.
2. Resolver de atendimento, Clara, WhatsApp e leads.
3. Confirmação objetiva de agenda da Clara.
4. João, Marketing, Reels e tráfego.
5. Apresentação V10, QuarkClinic e exames.
6. Omie, boletos e financeiro.

## Justificativa

O conteúdo útil existia, mas estava disperso em arquivos longos; logs e materiais de treino superavam as fontes úteis no ranking. Quatro casos ainda aceitavam páginas presentes no índice, porém ausentes do Git remoto. A regressão anterior também aceitava palavras soltas em qualquer resultado e não validava a existência da fonte.

## Governança

- Fonte de verdade continua nos arquivos canônicos vinculados por cada roteador.
- Os roteadores têm `source_of_truth: false`.
- A regressão e o benchmark compartilham uma única matriz de seis casos e um único avaliador.
- Cada caso exige caminho esperado no Top 3, arquivo existente e rastreado pelo Git canônico.
- O relatório persiste somente caminho canônico, rank e métricas; não persiste conteúdo, PII ou caminho de runtime.
- Nenhuma regra clínica, financeira ou comercial foi alterada.

## Evidência anterior à mudança

Baseline estrito: 3/6. Falhas: Resolver, confirmação da Clara e Marketing/Reels.

## Evidência posterior à mudança

- Regressão canônica estrita: **6/6**, com arquivo rastreado.
- Ranks: Governança 1; Resolver 1; Clara 1; Marketing 1; V10 1; Omie 1.
- Benchmark governado: **31/31 testes**; GBrain pass rate **100%**; pgvector sintético Recall@3 e MRR **100%**; gate p95 `<= 250 ms` aprovado.
- Decisão preservada: `KEEP_GBRAIN_NO_STANDALONE_PGVECTOR`.
- Sync lexical concluído com `--no-embed`; a etapa de embeddings foi deliberadamente omitida porque a credencial não estava disponível no processo. O gate executado usa `gbrain search` lexical/tsvector.
- O `doctor` global permanece com warnings preexistentes e retorno não zero; não bloqueou a correção de retrieval e segue registrado em `cerebro/gbrain/sync/latest-health.md`.
- O Graphify CLI instalado não gera grafo para pacote somente Markdown (`No code files found`); a consolidação válida foi arquivo canônico + nota RC-25 + sync/query GBrain.
