# Conhecimento - Memória Científica Semântica

Memória de longo prazo da Clara para pesquisas científicas com aplicação clínica no Instituto Vital Slim.

## Como funciona

1. **Tiaro envia conteúdo** (link, PDF, imagem, texto) para Clara pelo Instagram/WhatsApp/Telegram
2. **Clara SEMPRE busca aqui primeiro** (`skill memoria-cientifica` → `memory_search.py`)
3. Se tema novo: **Clara ingere → aprofunda (Perplexity) → aplica clinicamente → armazena aqui**
4. Só DEPOIS cria o material solicitado (carrossel, post, etc.)

## Estrutura

```
conhecimento/
├── pesquisas/              # 1 pasta por pesquisa (YYYY-MM-DD_slug)
│   └── <id>/
│       ├── original.md     # Conteúdo original recebido
│       ├── research.md     # Pesquisa aprofundada (Perplexity/Gemini)
│       ├── clinical.md     # Aplicação clínica IVS (quando/como prescrever)
│       ├── summary.md      # TL;DR 250 palavras
│       ├── embeddings.json # Chunks + vecs (Gemini 3072 dims)
│       ├── metadata.json   # topic, tags, stats, source
│       └── source.json     # URLs originais
├── topicos/                # Links simbólicos por tópico
│   ├── magnesio/
│   ├── creatina/
│   └── ...
├── index/                  # Índice global
│   ├── master.jsonl        # 1 linha/pesquisa: id, topic, tags, summary, keywords
│   ├── embeddings.jsonl    # 1 linha/chunk: research_id, chunk_id, text, vec (3072d)
│   ├── topics.json         # Taxonomia completa
│   └── keywords.json       # Keyword → research_ids (fallback textual)
└── logs/                   # Histórico de uso (append-only)
```

## Busca

```bash
# Semântica (embeddings Gemini)
python3 skills/memoria-cientifica/scripts/memory_search.py --query "<texto>" --top-k 5

# Por tópico
python3 skills/memoria-cientifica/scripts/memory_search.py --topic creatina

# Taxonomia inteira
python3 skills/memoria-cientifica/scripts/memory_search.py --list-topics

# Textual (sem API)
python3 skills/memoria-cientifica/scripts/memory_search.py --query "..." --keyword-only
```

## Thresholds de score (cosseno)

- `>= 0.75`: match forte, usar direto
- `0.55 - 0.75`: considerar, pode ingerir novo para enriquecer
- `< 0.55`: ignorar, tema efetivamente novo

## Como popular

Manual:
```bash
python3 skills/memoria-cientifica/scripts/ingest_content.py \
  --url "https://pubmed.ncbi.nlm.nih.gov/XXX" \
  --topic "<topico>" \
  --tags "tag1,tag2"
```

Via skill (Clara recebe conteúdo e aciona automaticamente).

## Estado atual

Execute \`memory_search.py --list-topics\` para ver inventário.

Seed inicial (2026-04-17):
- **magnesio**: "Deficiência Oculta" (PMID 41504160)
- **creatina**: "Além da Musculação" (PMID 39070254)
