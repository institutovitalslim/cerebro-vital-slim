# Omie

## Regra de roteamento de modelo (obrigatória)

**Todo pedido relacionado ao Omie deve ser processado pelo modelo `gpt-5.4` (provider `openai-codex`).**

- Motivo: Kimi K2.6 via openai-completions tem bug recorrente em tool-use + reasoning longo (stopReason=toolUse com payloads=0), que trava operações Omie complexas (faturamento, OS, boletos, NFe, ListarClientes paginado).
- Escopo: faturar orçamento/OS, emitir NFe, gerar boleto, cadastrar/alterar cliente, consultar financeiro, baixar títulos, qualquer coisa que chame tools da API Omie.
- Como garantir: a sessão do tópico precisa estar com `model = gpt-5.4` / `modelProvider = openai-codex`. Se um tópico novo começar em Kimi e o pedido for Omie, trocar o modelo **antes** de responder.
- Kimi K2.6 continua padrão só pra conversas da Clara no WhatsApp (Z-API bridge), onde não há tool-use pesado.
- Histórico do bug: incidente 2026-04-23 19:52 UTC, tópico 1980 (MARIO GOMES DE ABREU FILHO, R$ 45.500), backup `sessions.json.bak-omie-fix-20260423-*`.

## Cadastro de pacientes a partir do Quarkclinic

### Skill canônica
- `skills/omie-cadastro-paciente/SKILL.md`
- Script principal: `skills/omie-cadastro-paciente/scripts/cadastro_paciente_omie.py`
- Referência: `skills/omie-cadastro-paciente/references/mapeamento-e-regras.md`

### Fluxo obrigatório
1. Buscar a paciente no Quarkclinic.
2. Mostrar os dados encontrados ao usuário e pedir confirmação explícita.
3. Antes de criar no Omie, checar duplicidade por CPF e nome exato no `ListarClientes` paginado.
4. Só então criar o cadastro no Omie.
5. Se faltarem dados importantes, registrar isso claramente e complementar depois via `AlterarCliente`.

### Regras críticas
- Não inferir identidade da paciente quando o nome for ambíguo.
- Não criar cadastro no Omie sem confirmação explícita do usuário.
- Não inferir cidade, estado, CEP ou complemento se o Quarkclinic vier com campo vazio.
- Se a paciente já existir no Omie, parar e informar a duplicidade antes de qualquer ação.

### Convenções
- `codigo_cliente_integracao` deve seguir o padrão `QC-<id do paciente no Quarkclinic>`.
- `razao_social` e `nome_fantasia` devem usar o nome vindo do Quarkclinic.
- Para pessoa física, usar `pessoa_fisica = S`.
- Tag padrão do cadastro: `Cliente`.

## Emissão de proposta / OS com cobrança por boleto

### Regra operacional do caso Francisco
Ao emitir proposta/OS no Omie com cobrança por boleto bancário, os campos críticos precisam ser definidos explicitamente na criação para evitar ajuste manual posterior.

### Campos que devem sair corretos
- Categoria compatível com o serviço real do caso, por exemplo `Tricologia`.
- Conta corrente correta, por exemplo `Bradesco` quando o boleto for do Bradesco.
- `Gerar boleto = Sim`.
- `Enviar também o boleto de cobrança = Sim`.
- Tipo de pagamento/documento das parcelas = `Boleto`.
- Meio de pagamento das parcelas = `Boleto Bancário`.
- Quando o caso exigir, manter a observação comercial/fiscal: emitir `recibos` em vez de `nota fiscal`.

### Perguntas obrigatórias antes de emitir
- Se a emissão depender de banco/conta corrente, perguntar explicitamente ao Tiaro qual banco deve ser usado antes de criar a OS ou faturar, sem assumir automaticamente o banco do caso anterior.
- Se a emissão depender de serviço/cadastro de serviço no Omie, perguntar explicitamente ao Tiaro qual serviço exato deve ser usado. Nunca inventar descrição de serviço e nunca assumir serviço parecido, porque isso pode rejeitar a NFS-e na prefeitura.

### Regra de serviço para orçamento, OS e nota fiscal
Em orçamento, criação de OS e emissão com NFS-e, o serviço deve ser selecionado pela lista/cadastro de serviços do Omie, nunca digitado manualmente. O item da lista é o que carrega os dados operacionais e fiscais corretos e evita divergência entre proposta, OS e nota.

Fonte canônica da lista de serviços:
- `cerebro/omie-servicos.md`

Mapeamentos já confirmados:
- `Tricologia` → `SRV00016`
- `Programa de Acompanhamento Intensivo` → `SRV00013`

### Regra técnica do payload da OS
Para o Omie realmente puxar a descrição fiscal completa do serviço cadastrado, o item em `ServicosPrestados` deve referenciar o `nCodServico` do cadastro do serviço listado em `ListarCadastroServico` / `ConsultarCadastroServico`.

Exemplo validado:
- `SRV00016` (Tricologia) → `nCodServ = 6831167233`
- Quando a OS foi criada enviando `ServicosPrestados: [{"nCodServico": 6831167233, "nQtde": 1, "nSeqItem": 1, "nValUnit": 8100}]`, o Omie puxou automaticamente a descrição completa: `SERVIÇO MÉDICO DE PROCEDIMENTO COM APLICAÇÃO DE MEDICAÇÃO SC`.

Regra prática:
- não montar manualmente os campos fiscais do serviço quando existir cadastro canônico;
- primeiro mapear o código comercial (`SRV00016`, `SRV00013`, etc.), depois consultar/usar o `nCodServ` correspondente;
- só então incluir a OS.

### Comportamento assíncrono do faturamento NFS-e
Depois de `FaturarOS`, o Omie pode ainda não marcar imediatamente `cFaturada = "S"` em `ConsultarOS`.

Interpretação correta confirmada pelo Tiaro:
- isso pode ocorrer porque a prefeitura demora um pouco para devolver a NFS-e autorizada;
- enquanto esse retorno não volta, a OS pode permanecer temporariamente sem status final de faturada;
- esse estado transitório não deve ser tratado automaticamente como falha se o `FaturarOS` já retornou sucesso.

Caso validado:
- Mario Gomes de Abreu Filho, OS `6832443045` / número `000000002025699`, serviço da lista `SRV00013`, teve a nota emitida com sucesso após esse fluxo assíncrono.

### Regra de envio para nota fiscal
Quando a emissão for com nota fiscal, habilitar sempre a opção `Enviar o link da NFS-e gerada na prefeitura`.

### Armadilha já observada
Não confiar apenas na observação textual da OS para registrar `boleto bancário Bradesco`. Esses dados precisam estar refletidos também nos campos estruturados da OS e das parcelas, senão a proposta pode nascer com configuração financeira incorreta.

### Regra de entrega dos boletos
Depois que a OS for faturada e os boletos estiverem gerados, baixar todos os PDFs e enviar pelo próprio tópico do Telegram no mesmo fluxo operacional, sem depender de pedido adicional do usuário.

### Comandos úteis
```bash
python3 skills/omie-cadastro-paciente/scripts/cadastro_paciente_omie.py search "Suely"
python3 skills/omie-cadastro-paciente/scripts/cadastro_paciente_omie.py create --quark-id 449990267 --write-ok
python3 skills/omie-cadastro-paciente/scripts/cadastro_paciente_omie.py update --omie-id 6828819531 --cidade "Lauro de Freitas" --estado BA --write-ok
```
