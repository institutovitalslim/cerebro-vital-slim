# Checklist — Mutirão Omie janeiro até hoje

## Objetivo
Lançar e conciliar, com Pedro apoiando Maria e Tiaro, as informações financeiras de extratos, pagamentos e recebimentos no Omie de janeiro até a data atual.

## Regra de ouro
Pedro prepara, valida e aponta divergências. Lançamento definitivo no Omie só com confirmação explícita de Maria/Tiaro.

## Fontes necessárias
- Extratos bancários de janeiro até hoje por conta.
- Relatórios de recebimentos: PIX, cartão, boletos, transferências, dinheiro, links de pagamento.
- Contas pagas: comprovantes, notas, recibos, fornecedores.
- Contas a receber: boletos, parcelas, pacientes/contratos quando aplicável.
- Categorias Omie e contas correntes já cadastradas.
- Eventuais planilhas auxiliares usadas desde janeiro.

## Fluxo operacional
1. Separar arquivos por mês: `2026-01`, `2026-02`, `2026-03`, etc.
2. Pedro extrai e normaliza os lançamentos em CSV padrão.
3. Pedro cruza com Omie em modo read-only para identificar o que já existe.
4. Pedro classifica cada linha como:
   - `ja_existe_omie`
   - `novo_lancamento_sugerido`
   - `possivel_duplicidade`
   - `precisa_categoria`
   - `precisa_comprovante`
   - `precisa_decisao_tiaro`
5. Maria revisa lote por mês.
6. Tiaro aprova lotes sensíveis ou regras de categoria.
7. Só então executar inclusão/ajuste controlado no Omie, com log e relatório de auditoria.

## Ordem recomendada
1. Janeiro completo.
2. Fevereiro completo.
3. Março completo.
4. Abril completo.
5. Maio até a data atual.
6. Auditoria geral e fechamento preliminar.

## Saída esperada por mês
- CSV normalizado.
- Relatório de divergências.
- Lista de lançamentos novos sugeridos.
- Lista de duplicidades possíveis.
- Pendências de categoria/comprovante.
- Pacote para lançamento Omie após aprovação.
- Relatório final do mês.
