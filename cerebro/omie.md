# Omie

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

### Pergunta obrigatória antes de emitir
Se a emissão depender de banco/conta corrente, perguntar explicitamente ao Tiaro qual banco deve ser usado antes de criar a OS ou faturar, sem assumir automaticamente o banco do caso anterior.

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
