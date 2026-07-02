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

## Fluxo padrão — consulta de estoque

1. Identificar o item/protocolo e seus sinônimos/códigos.
2. Consultar controle interno atualizado quando existir.
3. Consultar Omie read-only quando o pedido depender do saldo oficial.
4. Se houver divergência controle interno × Omie, reportar como divergência; não inventar saldo.
5. Separar: `tem em estoque físico`, `tem cadastro/saldo Omie`, `precisa contagem Liane`, `precisa compra/reposição`.

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

Referência rápida da sessão: `references/lipedema-victa-stin-estoque.md`.

## Reporte recomendado

Para consultas operacionais, responder curto com:

`Status | Evidência | Risco/gate | Próximo passo`

E, quando houver protocolo, usar tabela:

| Fonte | Item/protocolo | Código | Apresentação | Valor/saldo | Observação |
|---|---:|---:|---:|---:|---|
