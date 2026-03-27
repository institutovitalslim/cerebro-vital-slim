# Rotinas — Operações

| Rotina | Frequência | O que faz |
|--------|-----------|-----------|
| `heartbeat` | A cada 1h | Verificação de saúde do sistema: pendências, prazos, crons com erro, memória não consolidada |
| `sync-github` | A cada 6h | Sincroniza alterações locais com o repositório GitHub |
