---
name: omie-estoque
description: "Gestão de estoque IVS no Omie e controle interno: consulta de produtos, posição, saldos, movimentações, tabelas de fornecedores e protocolos injetáveis; leitura autônoma, escrita com aprovação."
category: estoque
tags: [omie, estoque, ivs, fornecedores, injetaveis]
---

# Skill: omie-estoque

Gestão de estoque pelo Omie via skill `omie-api` (script genérico `call <endpoint> <metodo> <json>`).

Treinamento completo do Pedro: `TREINAMENTO-PEDRO-OMIE-ESTOQUE.md`.

## Regra central

- **Leitura** (`ListarProdutos`, posição, movimentos, tabelas arquivadas, controle interno) = Eduardo executa autonomamente e reporta.
- **Movimento/ajuste/baixa/compra** que altera saldo oficial ou gera gasto = confirmar com Tiaro/Maria antes.
- Nunca negar existência ou saldo sem conferir inventário/controle interno/Omie/última contagem disponível.

## Governança Omie — limite operacional seguro IVS

Fontes canônicas: skill `omie-api`, treinamento do Pedro sobre limite operacional Omie e `/root/cerebro-vital-slim/cerebro/areas/financeiro/referencias/omie/mapa_uso_api_omie.md`.

Política segura consolidada:
- Read-only: até **1 req/s**, máximo **45/min** e **1.800/h**.
- Writes: sempre serializados, sem paralelismo, **1 write a cada 2–3s**.
- Lote destrutivo: máximo **10 itens**.
- Lote não destrutivo: máximo **25 itens**.
- Parar lote em `MISUSE_API_PROCESS`, payload inválido, **2 erros consecutivos no método** ou **3 erros no lote**.
- Qualquer write financeiro/sensível exige **preflight**, payload validado e **gate humano explícito** antes da execução.

## Convenção de códigos de estoque IVS no Omie

- `INJ` = injetável.
- `PEL` = pellet.
- `SIL` = silástico.

Use essa convenção para classificar cadastro, validar apresentação, escolher NCM/família equivalente e revisar listas antes de ajustes/exclusões.

## Fluxo padrão — consulta de estoque

1. Identificar o item/protocolo e seus sinônimos/códigos.
2. Consultar controle interno atualizado quando existir.
3. Consultar Omie read-only quando o pedido depender do saldo oficial.
4. Para implantes/pellets, buscar também variações de nome entre controle interno e Omie (ex.: `Pellet - NADH 200mg` no controle pode aparecer como `PEL0004 — PELLET - NAD 200 MG` no Omie).
5. Se `ListarProdutos`/`ListarProdutosResumido` vier vazio, não concluir ausência: consultar `estoque/consulta ListarPosEstoque` com `cExibeTodos:"S"` e filtrar por descrição/código; depois, se achar o produto, confirmar posição com `estoque/resumo ObterEstoqueProduto` por `cCodigo` ou `nIdProduto`.
6. Se houver divergência controle interno × Omie, reportar como divergência; não inventar saldo.
7. Separar: `tem em estoque físico`, `tem cadastro/saldo Omie`, `precisa contagem Liane`, `precisa compra/reposição`.
8. Para saneamento/reset com writes no Omie, seguir `references/reset-cadastro-saldos-apresentacoes.md`: validar apresentações nas tabelas de fornecedores antes de excluir/cadastrar, executar em fases (cadastros → saldos → exclusões), usar payload de exclusão com apenas um identificador, e respeitar a política Pedro/Omie: limite público `4 req/s`, `240/min`, `14.400/h`; limite seguro IVS no cliente `1 req/s`, `45/min`, `1.800/h`; em writes em lote, sem paralelismo, parar no primeiro erro repetido/`MISUSE_API_PROCESS`/425/429 e aguardar o `blocked_until` do `omie_api.py --rate-status` antes de qualquer nova chamada.

## Tabelas de fornecedores e protocolos injetáveis

Quando o usuário perguntar valor de item/protocolo de farmácia de manipulação (Victa, Stin, Health Tech, Central etc.):

1. Procurar em planilhas/PDFs de cotações e tabelas arquivadas.
2. Se o guia clínico/estético tiver composição mas não valor, **não concluir “sem preço” ainda**.
3. Procurar também PDFs/planilhas de **tabela de preço** do mesmo fornecedor; preços podem estar em arquivo separado do guia de composição.
4. Informar fonte e diferenciar:
   - valor do kit/protocolo;
   - valor por ampola/frascos;
   - composição/código;
   - se o preço é de item equivalente ou exatamente o mesmo item.

### Pitfall aprendido — Victa lipedema/gordura

Na Victa, o `Guia Estético` pode trazer “Gordura Localizada”, “Auxiliar de Lipedema” e “Lipodistrofia” com código/composição, mas sem preço visível. O preço relacionado pode aparecer na `Tabela Guia Ortomolecular`/tabela de preços separada. Antes de responder que não há valor, procurar por códigos e termos em todos os PDFs/planilhas Victa arquivados.

Referências rápidas:

- Reset de cadastro/saldos com apresentações validadas em fornecedores e campos fiscais obrigatórios: `references/reset-cadastro-saldos-apresentacoes.md`.
- Deep scrape/manual Omie estoque 2026-07-10: `references/omie-estoque-manual-deep-scrape-20260710.md`.
- Caso “gordura localizada” e tabela Stin/Victa: `references/lipedema-victa-stin-estoque.md`.
- Caso implante/pellet NADH 200mg no controle interno vs NAD 200mg no Omie: `references/implantes-pellets-nadh-omie-controle.md`.

## Reporte recomendado

Para consultas operacionais, responder curto com:

`Status | Evidência | Risco/gate | Próximo passo`

E, quando houver protocolo, usar tabela:

| Fonte | Item/protocolo | Código | Apresentação | Valor/saldo | Observação |
|---|---:|---:|---:|---:|---|
