# Clara Concierge WhatsApp - Memoria Operacional

Diretorio com a base de conhecimento da Clara para atuar como concierge comercial do Instituto Vital Slim.

## Arquivos

| Arquivo | Descricao | Tamanho |
|---------|-----------|---------|
| MEMORIA_CONSOLIDADA_2026-04-28.md | Documento autoritativo completo - 21 RCs + voice rules + personas + crons + catalogo | ~17 KB |

## Acesso rapido via memory_search

A memoria foi indexada em:
```
/root/cerebro-vital-slim/cerebro/empresa/conhecimento/pesquisas/2026-04-28_clara-concierge-operacional/
```

Para buscar:
```bash
# Busca por topico
python3 /root/.openclaw/workspace/skills/memoria-cientifica/scripts/memory_search.py \
  --topic clara-concierge

# Busca por keyword
python3 /root/.openclaw/workspace/skills/memoria-cientifica/scripts/memory_search.py \
  --query "regra canonica reembolso" --keyword-only
```

## Estrutura indexada

```
pesquisas/2026-04-28_clara-concierge-operacional/
├── original.md     # Memoria consolidada completa
├── research.md     # Mesmo conteudo (compatibilidade com schema)
├── clinical.md     # Guia pratico - como aplicar cada regra em situacoes reais
├── summary.md      # TL;DR ultra-compacto (1 pagina)
├── source.json     # Metadados de origem
├── metadata.json   # Topic, tags, timestamps
└── embeddings.json # (vazio - regenerar quando Gemini API retornar)
```

## Atalhos

- **Tudo de uma vez**: leia MEMORIA_CONSOLIDADA_2026-04-28.md
- **TL;DR**: leia pesquisas/.../summary.md
- **Como aplicar em situacoes reais**: leia pesquisas/.../clinical.md
- **Regras canonicas (RC-01 a RC-21)**: secao 1 da MEMORIA_CONSOLIDADA

## Regras CRITICAS (top 5)

1. **RC-01**: NUNCA falar valor de programa/medicacao/tratamento pre-consulta
2. **RC-12**: Paciente no WhatsApp deve ser respondido com contexto e escalado quando necessario
3. **RC-06**: R$ 100 OFF imediato + cashback 100% se fechar Programa no dia
4. **RC-14**: Pre-consulta R$ 300 (cartao 2x) - InfinityPay
5. **RC-19**: Situacao sensivel = acolhe + escala paralelo Tiaro+Liane

## Hierarquia de contatos

- Tiaro: 5571986968887 (T+0 financeiro, conflitos, VIP nominal)
- Liane: 5571991574827 (T+2h backup financeiro, atendimento humano)
- Dra. Daniely: nunca direto - via Telegram topico Pacientes

## Status da indexacao

- Indexacao por keywords: OK
- Indexacao por topicos: OK (topico "clara-concierge")
- Indexacao semantica (embeddings): PENDENTE (sistema OpenAI - aguardando integracao - regenerar quando resolvido)

## Versao

v1.0 - 2026-04-28 - Sessao de descoberta com Tiaro
27 conversas reais analisadas + esclarecimentos diretos
