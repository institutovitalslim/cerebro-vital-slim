---
name: memoria-cientifica
description: >
  Estrutura de memória semântica científica da Clara. Quando o Tiaro envia qualquer
  conteúdo (link, PDF, imagem, texto) pelo Instagram/WhatsApp/Telegram para criar
  material (carrossel, post, conteúdo), Clara PRIMEIRO lê e aprofunda o conteúdo via
  Perplexity/Gemini, apresenta resumo com aplicação clínica prática no Instituto Vital
  Slim, e SÓ DEPOIS cria o material solicitado — armazenando tudo com embeddings para
  busca semântica futura. Use SEMPRE antes de gerar carrossel, post ou responder paciente
  sobre tratamentos. Acionar quando: recebe link científico, PDF de paper, material de
  ensino, pergunta clínica complexa, ou antes de qualquer criação de conteúdo.
metadata:
  version: 1.0.0
  domain: clinical-research
  owner: main
---

# Memória Científica - Pipeline de Ingestão, Pesquisa e Recuperação

## OBJETIVO

Clara NUNCA responde sobre tratamentos ou cria conteúdo sem:
1. **Buscar na memória** se já tem pesquisa sobre o tema
2. Se for novo: **ler → pesquisar → aplicar clinicamente → aprovar → armazenar** ANTES de produzir qualquer material

## FLUXO OBRIGATÓRIO (4 ETAPAS)

### ETAPA 1 — Recebeu conteúdo (link/PDF/imagem/texto)

**SEMPRE rode primeiro:**
```bash
export GOOGLE_API_KEY=$GOOGLE_API_KEY
python3 /root/cerebro-vital-slim/cerebro/empresa/skills/memoria-cientifica/scripts/memory_search.py \
  --query "<TEMA_ENVIADO>" --top-k 3
```

- **Se encontrou ≥ 1 resultado com score > 0.75**: apresentar ao Tiaro "Já temos pesquisa sobre isso em `<research_id>`. Quer que eu use essa base ou aprofunde com novo conteúdo?"
- **Se não encontrou ou score baixo**: prosseguir para ETAPA 2

### ETAPA 2 — Ingestão + Pesquisa + Aplicação Clínica

```bash
python3 /root/cerebro-vital-slim/cerebro/empresa/skills/memoria-cientifica/scripts/ingest_content.py \
  --url "<URL>" \        # OU --file <path>  OU --text "..."
  --topic "<TOPICO>" \   # ex: creatina, magnesio, vitamina-d
  --tags "<TAGS>"        # opcional
```

O pipeline automaticamente:
1. Extrai texto (URL/PDF/imagem via OCR/PubMed eutils)
2. Aprofunda via **Perplexity API** (fallback: Gemini)
3. Gera **aplicação clínica** prática para Dra. Daniely (quando prescrever, dose, monitoramento, etc.)
4. Gera **resumo executivo** (TL;DR)
5. Indexa com **embeddings Gemini** (gemini-embedding-001, 768 dims)
6. Salva no cérebro sob `/root/cerebro-vital-slim/cerebro/empresa/conhecimento/pesquisas/`

### ETAPA 3 — Apresentação ao Tiaro (OBRIGATÓRIA antes de criar material)

Clara apresenta ao Tiaro:
- **Resumo executivo** (TL;DR de 250 palavras)
- **Aplicação clínica no Instituto Vital Slim**:
  - Quando prescrever
  - Como prescrever (dose, forma, horário, duração)
  - Combinações sinérgicas
  - Monitoramento (exames)
  - Sinais de alerta
  - Como explicar ao paciente
  - Critérios de exclusão
- **Pergunta**: "Posso prosseguir com a criação do material usando esta base?"

### ETAPA 4 — Criação do material (carrossel/post)

Só APÓS aprovação do Tiaro, Clara chama a skill `tweet-carrossel` (ou outra) USANDO o conteúdo da memória armazenada como base da copy.

---

## ESTRUTURA DE MEMÓRIA (Cérebro)

```
/root/cerebro-vital-slim/cerebro/empresa/conhecimento/
├── pesquisas/
│   └── YYYY-MM-DD_<slug>/
│       ├── original.md      # Conteúdo original recebido
│       ├── source.json      # URLs, metadata
│       ├── research.md      # Pesquisa Perplexity/Gemini
│       ├── clinical.md      # Aplicação clínica IVS
│       ├── summary.md       # TL;DR 250 palavras
│       ├── embeddings.json  # Chunks + vecs (Gemini 768d)
│       └── metadata.json    # topic, tags, stats
├── index/
│   ├── master.jsonl         # 1 linha/pesquisa: id, topic, tags, summary, keywords
│   ├── embeddings.jsonl     # 1 linha/chunk: research_id, chunk_id, text, vec, topic
│   ├── topics.json          # taxonomia: topic -> [pesquisas]
│   └── keywords.json        # keyword -> [research_ids] (fallback textual)
├── topicos/                 # links simbólicos por tópico (navegação)
│   ├── creatina/
│   ├── magnesio/
│   └── ...
└── logs/                    # histórico de uso
```

---

## BUSCA SEMÂNTICA

### Uso típico:

```bash
# Busca por significado (embeddings cosseno)
python3 memory_search.py --query "creatina ajuda no cérebro?"

# Busca filtrada por tópico
python3 memory_search.py --query "dosagem para idosos" --topic creatina

# Lista tudo de um tópico
python3 memory_search.py --topic creatina

# Taxonomia inteira
python3 memory_search.py --list-topics

# Resultado JSON (para scripts)
python3 memory_search.py --query "..." --format json

# Fallback textual (sem API)
python3 memory_search.py --query "..." --keyword-only
```

### Integração obrigatória nos outros fluxos:

**Antes de sugerir tratamento ao paciente:**
```bash
memory_search.py --query "<sintoma_ou_tema_do_paciente>" --top-k 5
```

**Antes de criar carrossel/post sobre um tema:**
```bash
memory_search.py --query "<tema>" --top-k 3
# Use o clinical.md e research.md das top matches como fonte da copy
```

---

## APIs USADAS

| API | Uso | Auth |
|-----|-----|------|
| Gemini `gemini-2.5-flash` | Síntese clínica + resumos | env `GOOGLE_API_KEY` |
| Gemini `gemini-embedding-001` | Embeddings 768d | env `GOOGLE_API_KEY` |
| Perplexity `sonar-pro` | Deep research científica | 1Password "Perplexity API" |
| NCBI eutils | PubMed metadata + abstracts | Livre |

---

## REGRAS CRÍTICAS

- **NUNCA** criar carrossel/post sobre tema novo sem rodar o pipeline completo
- **SEMPRE** armazenar a pesquisa ANTES de entregar o material
- **SEMPRE** buscar na memória ANTES de responder perguntas clínicas de pacientes
- Perplexity é obrigatória se disponível (fallback: Gemini)
- Embedding com Gemini (`gemini-embedding-001`, 768 dims)
- Score semântico > 0.75 = match forte; entre 0.55 e 0.75 = considerar; < 0.55 = ignorar
- Logs em `/root/cerebro-vital-slim/cerebro/empresa/conhecimento/logs/`

---

## TÓPICOS JÁ CATALOGADOS

Execute `memory_search.py --list-topics` para ver taxonomia atualizada.

Seed inicial (ver `seed_knowledge.sh`):
- `magnesio` — deficiência global e suas consequências
- `creatina` — benefícios cognitivos além da musculação

---

## TROUBLESHOOTING

- **`[Perplexity key nao disponivel]`**: verificar `op` CLI e token 1Password
- **Embeddings vazios**: verificar `$GOOGLE_API_KEY` e quota
- **`master.jsonl` crescendo demais**: considerar dedup por `id` (nunca duplica, mas valida)
- **Score baixo em busca**: pode ser novo tema — prosseguir com ingestão
- **PDF não extrai**: `apt install poppler-utils` (pdftotext)
- **Imagem não OCR**: `apt install tesseract-ocr tesseract-ocr-por`


## REGRA OBRIGATORIA — Resumo pratico de cada paper analisado

Quando Clara analisar papers cientificos (via PubMed, DOI, Perplexity) para montar
carrossel, ela DEVE apresentar ao Tiaro, para CADA paper:

**Formato obrigatorio:**
```
📄 Paper: [TITULO] (PMID XXXXX, DOI XXXXX)

📊 O que o estudo mostrou:
- [principais achados em bullets, maximo 5]
- [com numeros quando relevante]

🏥 Aplicacao pratica na clinica IVS:
- Perfil de paciente que se beneficia: [X]
- Como conectar com atendimento: [Y]
- O que o paper NAO prova (limitacoes): [Z]

💡 Uso para o carrossel:
- Slide que citara este paper: [numero]
- Ponto narrativo: [ligacao com tese do carrossel]
```

Sem esse resumo pratico para CADA paper, Clara NAO prossegue para gerar o carrossel.
