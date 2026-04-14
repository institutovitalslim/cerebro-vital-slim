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

### Comandos úteis
```bash
python3 skills/omie-cadastro-paciente/scripts/cadastro_paciente_omie.py search "Suely"
python3 skills/omie-cadastro-paciente/scripts/cadastro_paciente_omie.py create --quark-id 449990267 --write-ok
python3 skills/omie-cadastro-paciente/scripts/cadastro_paciente_omie.py update --omie-id 6828819531 --cidade "Lauro de Freitas" --estado BA --write-ok
```
