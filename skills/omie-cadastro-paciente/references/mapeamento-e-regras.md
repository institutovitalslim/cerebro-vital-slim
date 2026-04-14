# Mapeamento e regras do cadastro de paciente no Omie

## Fluxo canônico
1. Buscar a paciente no Quarkclinic.
2. Mostrar dados mascarados ao usuário e pedir confirmação explícita.
3. Antes de criar no Omie, checar duplicidade por CPF e nome varrendo `ListarClientes` paginado.
4. Se não houver duplicidade, criar o cliente no Omie.
5. Se faltarem dados importantes, registrar isso claramente e complementar depois via `AlterarCliente`.

## Regra crítica
- Nunca inferir identidade do paciente com base em nome ambíguo.
- Nunca criar cadastro no Omie sem confirmação explícita do usuário.
- Nunca duplicar paciente no Omie quando já existir cadastro com mesmo CPF ou nome exato.
- Quando o Quarkclinic vier com campos vazios, manter vazio ou pedir complemento ao usuário. Não adivinhar cidade, estado, CEP ou complemento.

## Mapeamento principal Quarkclinic → Omie
- `id` → `codigo_cliente_integracao` com padrão `QC-<id>`
- `nome` → `razao_social` e `nome_fantasia`
- `cpf` → `cnpj_cpf`
- `email` → `email`
- `logradouro` → `endereco`
- `numero` → `endereco_numero`
- `bairro` → `bairro`
- `cidade` → `cidade` (somente se vier preenchido ou se o usuário complementar)
- telefone principal → `telefone1_ddd` + `telefone1_numero`

## Defaults operacionais no Omie
- `pessoa_fisica`: `S`
- `codigo_pais`: `1058`
- `exterior`: `N`
- `bloquear_faturamento`: `N`
- `inativo`: `N`
- `optante_simples_nacional`: `N`
- `enviar_anexos`: `N`
- `tags`: `Cliente`

## Comandos úteis
```bash
# Buscar candidatas no Quarkclinic
python3 {baseDir}/scripts/cadastro_paciente_omie.py search "Suely"

# Criar cadastro após confirmação
python3 {baseDir}/scripts/cadastro_paciente_omie.py create --quark-id 449990267 --write-ok

# Complementar cidade e estado depois
python3 {baseDir}/scripts/cadastro_paciente_omie.py update --omie-id 6828819531 --cidade "Lauro de Freitas" --estado BA --write-ok
```
