# Treinamento Eduardo — Omie Estoque IVS
## 1. Acesso Omie, credenciais e skill/script oficial
Use sempre a skill/script:
`omie-api`
Script oficial:
`/root/.openclaw/workspace/skills/omie-api/scripts/omie_api.py`
Comando de ajuda:
```bash
python3 /root/.openclaw/workspace/skills/omie-api/scripts/omie_api.py --help
```
Teste de conexão:
```bash
python3 /root/.openclaw/workspace/skills/omie-api/scripts/omie_api.py --check
```
Status do rate limit local:
```bash
python3 /root/.openclaw/workspace/skills/omie-api/scripts/omie_api.py --rate-status
```
Credenciais:
- O script carrega automaticamente `OMIE_APP_KEY` e `OMIE_APP_SECRET`.
- Fonte principal local: `/root/.openclaw/secure/omie_api.env`
- Fallback: 1Password, item `Acesso API OMIE`, vault `openclaw`.
- Eduardo NÃO deve abrir, copiar, imprimir, mandar em mensagem ou registrar essas chaves.
- Nunca colocar `app_key` / `app_secret` em relatório, log, print, memória ou prompt.
Formato geral de chamada pelo script:
```bash
python3 /root/.openclaw/workspace/skills/omie-api/scripts/omie_api.py call <endpoint> <metodo> '<json_parametros>'
```
Exemplo seguro, leitura:
```bash
python3 /root/.openclaw/workspace/skills/omie-api/scripts/omie_api.py call geral/produtos ListarProdutos '{"pagina":1,"registros_por_pagina":50}'
```
Observação importante:
- No script, o endpoint é passado sem `/api/v1/`.
- Exemplo correto: `geral/produtos`
- Exemplo errado: `/api/v1/geral/produtos/`
---
## 2. Leitura segura: consultar produtos, saldo e posição de estoque
Leitura é permitida para consulta, auditoria e conferência. Mesmo assim, minimize dados e não exponha credenciais.
### 2.1 Listar produtos
Endpoint Omie:
`geral/produtos`
Método:
`ListarProdutos`
Comando:
```bash
python3 /root/.openclaw/workspace/skills/omie-api/scripts/omie_api.py call geral/produtos ListarProdutos '{"pagina":1,"registros_por_pagina":50}'
```
Listagem resumida, quando bastar uma visão leve:
```bash
python3 /root/.openclaw/workspace/skills/omie-api/scripts/omie_api.py call geral/produtos ListarProdutosResumido '{"pagina":1,"registros_por_pagina":50}'
```
### 2.2 Consultar um produto específico
Por `codigo_produto` interno Omie:
```bash
python3 /root/.openclaw/workspace/skills/omie-api/scripts/omie_api.py call geral/produtos ConsultarProduto '{"codigo_produto":123456789}'
```
Por código exibido/SKU, quando disponível:
```bash
python3 /root/.openclaw/workspace/skills/omie-api/scripts/omie_api.py call geral/produtos ConsultarProduto '{"codigo":"SKU-EXEMPLO"}'
```
Campos comuns úteis:
- `codigo_produto`: ID interno Omie.
- `codigo`: código/SKU exibido.
- `descricao`: nome do produto.
- `unidade`: unidade de medida.
- `ean`: se houver.
- status/bloqueio do cadastro, quando retornado.
### 2.3 Listar locais de estoque
Endpoint:
`estoque/local`
Método:
`ListarLocaisEstoque`
```bash
python3 /root/.openclaw/workspace/skills/omie-api/scripts/omie_api.py call estoque/local ListarLocaisEstoque '{"nPagina":1,"nRegPorPagina":100}'
```
Use o `codigo_local_estoque` retornado para consultas e ajustes por local.
### 2.4 Consultar posição consolidada de estoque de um produto
Endpoint:
`estoque/resumo`
Método:
`ObterEstoqueProduto`
Por ID interno do produto:
```bash
python3 /root/.openclaw/workspace/skills/omie-api/scripts/omie_api.py call estoque/resumo ObterEstoqueProduto '{"nIdProduto":123456789,"dDia":"23/06/2026"}'
```
Por código/SKU:
```bash
python3 /root/.openclaw/workspace/skills/omie-api/scripts/omie_api.py call estoque/resumo ObterEstoqueProduto '{"cCodigo":"SKU-EXEMPLO","dDia":"23/06/2026"}'
```
Por busca dinâmica:
```bash
python3 /root/.openclaw/workspace/skills/omie-api/scripts/omie_api.py call estoque/resumo ObterEstoqueProduto '{"xCodigo":"NOME OU SKU DO PRODUTO","dDia":"23/06/2026"}'
```
Observação:
- `xCodigo` pode buscar por EAN, código/SKU ou descrição.
- Se mais de um produto for encontrado, a API pode retornar lista de produtos em vez do estoque direto.
- Nesse caso, escolha o produto correto e refaça por `nIdProduto`.
### 2.5 Listar posição de estoque geral
Endpoint:
`estoque/consulta`
Método:
`ListarPosEstoque`
```bash
python3 /root/.openclaw/workspace/skills/omie-api/scripts/omie_api.py call estoque/consulta ListarPosEstoque '{"nPagina":1,"nRegPorPagina":50,"dDataPosicao":"23/06/2026","cExibeTodos":"N","codigo_local_estoque":0}'
```
Parâmetros principais:
- `dDataPosicao`: data da posição no formato `DD/MM/AAAA`.
- `cExibeTodos`: `S` ou `N`.
- `codigo_local_estoque`: local específico; `0` costuma indicar padrão/geral conforme API.
### 2.6 Listar movimentos de estoque
Endpoint:
`estoque/consulta`
Método:
`ListarMovimentoEstoque`
```bash
python3 /root/.openclaw/workspace/skills/omie-api/scripts/omie_api.py call estoque/consulta ListarMovimentoEstoque '{"nPagina":1,"nRegPorPagina":50,"codigo_local_estoque":0,"idProd":123456789,"dDtInicial":"01/06/2026","dDtFinal":"23/06/2026"}'
```
Alternativa pelo endpoint de movimentos:
Endpoint:
`estoque/movestoque`
Método:
`ListarMovimentos`
```bash
python3 /root/.openclaw/workspace/skills/omie-api/scripts/omie_api.py call estoque/movestoque ListarMovimentos '{"pagina":1,"registros_por_pagina":50,"codigo_local_estoque":0,"data_inicial":"01/06/2026","data_final":"23/06/2026"}'
```
Use para auditoria antes/depois de qualquer ajuste.
---
## 3. Escrita: movimentação, ajuste e baixa de estoque
Regra IVS:
Toda escrita de estoque altera saldo oficial no Omie. Eduardo não deve executar sem aprovação explícita da Maria/Tiaro conforme impacto.
Antes de escrever:
1. Consultar produto.
2. Confirmar `codigo_produto` / `nIdProduto`.
3. Consultar local de estoque.
4. Consultar saldo atual.
5. Conferir motivo.
6. Montar payload.
7. Pedir aprovação explícita.
8. Executar com `--write-ok`.
9. Consultar saldo depois.
10. Registrar evidência: produto, local, data, quantidade, motivo, ID do ajuste retornado.
O script bloqueia métodos de escrita se não passar `--write-ok`.
Métodos considerados escrita incluem:
- `Incluir...`
- `Alterar...`
- `Excluir...`
- `Upsert...`
- `Faturar...`
- `Gerar...`
- `Cancelar...`
- `Prorrogar...`
### 3.1 Endpoint de ajuste de estoque
Endpoint:
`estoque/ajuste`
Método para incluir ajuste:
`IncluirAjusteEstoque`
Método para listar ajustes:
`ListarAjusteEstoque`
Método para excluir ajuste:
`ExcluirAjusteEstoque`
Atenção:
- `ExcluirAjusteEstoque` também altera o histórico/saldo e exige aprovação.
- Não use exclusão para “corrigir rápido”; prefira novo ajuste rastreável, salvo orientação explícita.
### 3.2 Tipos de ajuste
Campo `tipo`:
- `ENT`: entrada no estoque.
- `SAI`: saída/baixa no estoque.
- `SLD`: ajuste de saldo de estoque.
Campo `origem`:
- `AJU`: ajuste manual de estoque.
- `PDV`: ajuste realizado pelo PDV.
Campo `motivo`:
Entrada:
- `INV`: ajuste por inventário.
- `OPE`: integração com ordem de produção — entrada.
- `PDV`: integração com PDV.
- `INI`: estoque inicial.
Saída:
- `INV`: ajuste por inventário.
- `PER`: baixa por perda ou quebra.
- `OPS`: integração com ordem de produção — saída.
- `PDV`: integração com PDV.
Ajuste de saldo:
- `INV`: ajuste por inventário.
- `INI`: estoque inicial.
- `CMC`: ajuste do valor do CMC.
- `PDV`: integração com PDV.
Transferência entre locais:
- `TPQ`: transferência por perda ou quebra.
- `TRF`: transferência entre locais de estoque.
### 3.3 Exemplo: baixa por perda/quebra
Uso: reduzir saldo por perda, quebra, vencimento, descarte ou divergência física validada.
Payload exemplo:
```json
{
  "codigo_local_estoque": 0,
  "id_prod": 123456789,
  "data": "23/06/2026",
  "quan": "2",
  "obs": "Baixa autorizada por inventário físico IVS - perda/quebra. Aprovado por Maria/Tiaro em DD/MM/AAAA.",
  "origem": "AJU",
  "tipo": "SAI",
  "motivo": "PER",
  "valor": 0
}
```
Comando:
```bash
python3 /root/.openclaw/workspace/skills/omie-api/scripts/omie_api.py call estoque/ajuste IncluirAjusteEstoque '{"codigo_local_estoque":0,"id_prod":123456789,"data":"23/06/2026","quan":"2","obs":"Baixa autorizada por inventario fisico IVS - perda/quebra. Aprovado por Maria/Tiaro em DD/MM/AAAA.","origem":"AJU","tipo":"SAI","motivo":"PER","valor":0}' --write-ok
```
Regra prática:
- Para `SAI`, informe `quan` positivo. O tipo `SAI` indica a saída.
- Não use quantidade negativa sem validação formal da API/tela.
### 3.4 Exemplo: entrada por inventário
Uso: aumentar saldo após conferência física autorizada.
```bash
python3 /root/.openclaw/workspace/skills/omie-api/scripts/omie_api.py call estoque/ajuste IncluirAjusteEstoque '{"codigo_local_estoque":0,"id_prod":123456789,"data":"23/06/2026","quan":"5","obs":"Entrada autorizada por inventario fisico IVS. Aprovado por Maria/Tiaro em DD/MM/AAAA.","origem":"AJU","tipo":"ENT","motivo":"INV","valor":0}' --write-ok
```
### 3.5 Exemplo: ajuste de saldo por inventário
Uso: quando o inventário físico define o saldo correto e a operação quer ajustar a posição.
```bash
python3 /root/.openclaw/workspace/skills/omie-api/scripts/omie_api.py call estoque/ajuste IncluirAjusteEstoque '{"codigo_local_estoque":0,"id_prod":123456789,"data":"23/06/2026","quan":"15","obs":"Ajuste de saldo por inventario fisico IVS. Saldo fisico validado e aprovado por Maria/Tiaro em DD/MM/AAAA.","origem":"AJU","tipo":"SLD","motivo":"INV","valor":0}' --write-ok
```
Cuidado:
- Antes de usar `SLD`, confirme se a intenção é ajustar para o saldo final informado, não apenas movimentar diferença.
- Se a operação for “baixar 2 unidades”, normalmente use `SAI`.
- Se a operação for “saldo correto agora é 15 unidades”, use `SLD`.
### 3.6 Conferência pós-escrita
Depois de qualquer escrita:
Consultar saldo:
```bash
python3 /root/.openclaw/workspace/skills/omie-api/scripts/omie_api.py call estoque/resumo ObterEstoqueProduto '{"nIdProduto":123456789,"dDia":"23/06/2026"}'
```
Listar movimentos do período:
```bash
python3 /root/.openclaw/workspace/skills/omie-api/scripts/omie_api.py call estoque/consulta ListarMovimentoEstoque '{"nPagina":1,"nRegPorPagina":50,"codigo_local_estoque":0,"idProd":123456789,"dDtInicial":"23/06/2026","dDtFinal":"23/06/2026"}'
```
Listar ajustes feitos por API:
```bash
python3 /root/.openclaw/workspace/skills/omie-api/scripts/omie_api.py call estoque/ajuste ListarAjusteEstoque '{"pagina":1,"registros_por_pagina":100,"apenas_importado_api":"S"}'
```
---
## 4. App key / app secret: como usar sem expor
Nunca faça isto:
```json
{
  "app_key": "CHAVE_REAL",
  "app_secret": "SEGREDO_REAL"
}
```
Nunca cole credenciais em:
- Telegram.
- Markdown.
- GitHub.
- Logs.
- Prints.
- Planilhas.
- Memória de agente.
- Prompt para outro agente.
- Arquivos de relatório.
Use sempre o script:
```bash
python3 /root/.openclaw/workspace/skills/omie-api/scripts/omie_api.py call ...
```
Motivo:
- O script injeta `app_key` e `app_secret` internamente.
- O script aplica rate limit.
- O script bloqueia escrita sem `--write-ok`.
- O script evita expor o payload completo com segredo.
Se der erro de credencial:
1. Não imprima o arquivo de env.
2. Não rode `cat /root/.openclaw/secure/omie_api.env`.
3. Avise Pedro/Tiaro: “credencial Omie não resolvida pelo script”.
4. Teste apenas:
```bash
python3 /root/.openclaw/workspace/skills/omie-api/scripts/omie_api.py --check
```
---
## 5. Cuidados e erros comuns
## Segurança operacional
- Leitura: permitida para consulta e auditoria.
- Escrita: só com aprovação explícita.
- Estoque oficial não é rascunho; ajuste errado muda saldo real.
- Nunca “testar” escrita em produto real sem autorização.
- Não excluir ajuste para esconder erro; registrar correção rastreável.
## Antes de ajustar estoque
Checklist mínimo:
```text
[ ] Produto correto confirmado por codigo_produto/nIdProduto
[ ] Descrição confere
[ ] Local de estoque correto confirmado
[ ] Saldo atual consultado
[ ] Movimento/motivo definido: ENT, SAI ou SLD
[ ] Quantidade conferida
[ ] Valor definido quando aplicável
[ ] Observação com origem e aprovação
[ ] Aprovação Maria/Tiaro registrada
[ ] Comando revisado antes de --write-ok
[ ] Saldo pós-ajuste conferido
```
## Erros comuns
1. Confundir `codigo_produto`, `nIdProduto`, `id_prod` e `codigo`.
   - `codigo_produto` / `nIdProduto` / `id_prod`: ID interno Omie.
   - `codigo` / `cCodigo`: código/SKU exibido.
2. Ajustar no local errado.
   - Sempre liste locais com `ListarLocaisEstoque`.
   - Use `codigo_local_estoque` correto.
3. Usar `SLD` quando queria apenas entrada/saída.
   - Entrada: `ENT`.
   - Baixa: `SAI`.
   - Saldo final inventariado: `SLD`.
4. Usar quantidade negativa indevidamente.
   - Para saída, use `tipo: "SAI"` e `quan` positivo.
5. Fazer baixa sem motivo.
   - `motivo` é obrigatório.
   - Para perda/quebra: `PER`.
   - Para inventário: `INV`.
6. Rodar escrita sem aprovação.
   - O script exige `--write-ok`, mas isso não substitui aprovação humana.
   - `--write-ok` é só trava técnica; a autorização precisa existir.
7. Expor segredo.
   - Nunca imprimir env, 1Password ou payload com `app_key/app_secret`.
8. Ignorar rate limit.
   - O script limita localmente.
   - Se receber HTTP 429 / “Too many requests”, pare e aguarde.
   - Não rode múltiplos robôs em paralelo contra Omie sem coordenação.
9. Não conferir depois.
   - Toda escrita exige consulta pós-ajuste.
   - Sem conferência pós-escrita, a tarefa não está concluída.
10. Misturar inventário físico com decisão financeira.
   - Eduardo cuida da operação de estoque.
   - Impacto contábil/financeiro relevante deve ser escalado para Pedro/Maria/Tiaro/contador.
---
## Fluxo padrão para Eduardo
```text
1. Buscar produto
2. Confirmar local
3. Consultar saldo atual
4. Listar movimentos recentes
5. Definir se é leitura, entrada, baixa ou ajuste de saldo
6. Se for escrita: pedir aprovação explícita
7. Executar com omie_api.py e --write-ok
8. Consultar saldo pós-ajuste
9. Registrar evidência objetiva
```
Modelo de evidência pós-ajuste:
```markdown
## Estoque Omie — ajuste executado
- Produto:
- ID Omie:
- Local:
- Data:
- Tipo: ENT / SAI / SLD
- Motivo:
- Quantidade:
- Saldo antes:
- Saldo depois:
- ID ajuste Omie:
- Aprovação:
- Observação:
```
Regra final:
Se altera saldo oficial, não é só “consulta”: é escrita operacional sensível. Execute apenas com aprovação explícita e registre evidência.
