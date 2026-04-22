# Empresa — Mapa

## Estrutura

```
empresa/
├── MAPA.md
├── contexto/
│   ├── geral.md          ← Quem é a empresa, missão, produtos
│   ├── people.md          ← Equipe, cargos, estrutura de decisão
│   ├── metricas.md        ← KPIs e números atuais
│   ├── decisions.md       ← Decisões estratégicas registradas
│   └── lessons.md         ← Lições aprendidas
├── conhecimento/          ← MEMÓRIA CIENTÍFICA SEMÂNTICA (NOVO)
│   ├── pesquisas/         ← Pesquisas armazenadas (1 pasta por tema)
│   ├── topicos/           ← Links simbólicos por tópico (navegação)
│   ├── index/             ← Indices: master.jsonl, embeddings.jsonl, topics.json
│   └── logs/              ← Histórico de uso
├── rotinas/
├── skills/
└── projetos/
    ├── README.md          ← Projetos ativos e concluídos
    └── pendencias.md      ← Pendências abertas
```

## O que tem em cada lugar

| Caminho | O que o agente encontra |
|---------|------------------------|
| `contexto/geral.md` | Missão, produtos, canais, modelo de negócio |
| `contexto/people.md` | Quem trabalha aqui, papéis e estrutura de decisão |
| `contexto/metricas.md` | MRR, clientes, CAC, ROAS — números atuais |
| `contexto/decisions.md` | Decisões estratégicas com contexto e status |
| `contexto/lessons.md` | Lições aprendidas com erros e acertos |
| `rotinas/` | Rotinas automáticas (crons) |
| `skills/` | Skills cross-área (ver `_index.md`) |
| `skills/memoria-cientifica/` | Memoria semantica de pesquisas cientificas (Perplexity+Gemini embeddings). Clara consulta SEMPRE antes de gerar conteudo |
| `skills/prompt-imagens/` | Cria imagens via NanoBanana 2 Pro com 7 dimensoes do prompt + 15 estilos. SEMPRE valida prompt com Tiaro antes de gerar |
| `projetos/` | Projetos em andamento e concluídos |
