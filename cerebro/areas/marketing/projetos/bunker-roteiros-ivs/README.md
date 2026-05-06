# Projeto — Bunker de Roteiros IVS

Projeto estrutural para transformar bankers/bunkers externos de roteiros em um bunker proprietário do Instituto Vital Slim.

## Estrutura
- `00-fontes/` → mapa de bunkers externos e origem dos lotes
- `01-brutos/` → extrações ainda não filtradas
- `02-filtrados/` → roteiros aprovados por aderência
- `03-bunker-ivs/` → ativos adaptados para IVS
- `04-hooks/` → banco de hooks e aberturas
- `05-objecoes/` → banco por objeção
- `06-campanhas/` → seleções por objetivo comercial
- `07-publicados/` → ativos já usados
- `templates/` → modelos de cadastro e operação
- `logs/` → histórico operacional do projeto

## Regras
1. Nunca copiar literal.
2. Sempre classificar por objetivo, classe IVS e mecanismo.
3. Toda adaptação deve mapear objeção principal.
4. Todo ativo final deve servir ao avatar mestre do IVS.
