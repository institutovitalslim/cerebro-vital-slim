# Atendimento — Mapa da Área

## Estrutura

```
atendimento/
├── MAPA.md
├── contexto/
│   └── geral.md
├── bot/
│   ├── faq.md
│   └── duvidas.md
├── rotinas/
│   ├── checagem-tickets-diaria.md
│   └── consolidar-faq.md
└── skills/
    └── _index.md
```

## O que tem em cada lugar

| Caminho | O que o agente encontra |
|---------|------------------------|
| `contexto/` | Objetivo da área, KPIs, canais de atendimento, fluxo de escalação |
| `bot/` | FAQ do bot de suporte e registro de dúvidas pendentes |
| `rotinas/` | Crons configurados (checagem de tickets diária, consolidação do FAQ 18h) |
| `skills/` | Skills da área de atendimento (ver `_index.md` dentro da pasta) |
