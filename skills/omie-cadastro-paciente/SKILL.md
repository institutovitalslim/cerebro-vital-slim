---
name: omie-cadastro-paciente
description: Cadastrar ou complementar pacientes no Omie a partir de dados do Quarkclinic, com checagem de homônimos, confirmação explícita do usuário e prevenção de duplicidade no ERP. Use quando o pedido for algo como “cadastre a paciente X no Omie”, “busque no Quarkclinic e depois cadastre no Omie”, “complemente cidade/estado do paciente no Omie” ou qualquer fluxo de criação/atualização de paciente entre Quarkclinic e Omie.
---

# Omie Cadastro Paciente

Use esta skill para executar o fluxo seguro de cadastro de pacientes no Omie.

## Fluxo obrigatório
1. Buscar a paciente no Quarkclinic.
2. Mostrar ao usuário os dados encontrados, de preferência mascarados, e pedir confirmação explícita.
3. Antes de criar no Omie, verificar duplicidade por CPF e nome exato no `ListarClientes` paginado.
4. Só então criar o cadastro no Omie.
5. Se faltarem dados importantes, informar isso claramente e complementar depois com `AlterarCliente`.

## Regras críticas
- Nunca inferir identidade da paciente quando houver nome ambíguo.
- Nunca criar cadastro no Omie sem confirmação explícita do usuário.
- Nunca assumir que a busca nominal do Quarkclinic está correta sem revisar o resultado.
- Nunca inferir cidade, estado, CEP ou complemento quando o Quarkclinic vier vazio.
- Se o Omie já tiver cadastro com mesmo CPF ou nome exato, tratar como duplicidade e parar para decisão do usuário.

## Script principal
Use o script desta skill para evitar repetir lógica manual:

```bash
# Buscar candidatas no Quarkclinic
python3 {baseDir}/scripts/cadastro_paciente_omie.py search "Suely"

# Criar no Omie a partir do ID confirmado do Quarkclinic
python3 {baseDir}/scripts/cadastro_paciente_omie.py create --quark-id 449990267 --write-ok

# Criar já com complementos informados pelo usuário
python3 {baseDir}/scripts/cadastro_paciente_omie.py create --quark-id 449990267 --cidade "Lauro de Freitas" --estado BA --write-ok

# Atualizar um cadastro já existente no Omie
python3 {baseDir}/scripts/cadastro_paciente_omie.py update --omie-id 6828819531 --cidade "Lauro de Freitas" --estado BA --write-ok
```

## Como interpretar a saída
- `search` retorna candidatas com score de similaridade e campos mascarados para confirmação.
- `create` retorna `duplicate` se já existir cadastro compatível no Omie.
- `create` retorna os payloads e o resultado do `IncluirCliente` quando a criação for feita.
- `update` retorna o payload final enviado ao `AlterarCliente` e o resultado da alteração.

## Quando ler a referência
Leia `references/mapeamento-e-regras.md` quando precisar:
- revisar o mapeamento Quarkclinic → Omie;
- lembrar os defaults do cadastro;
- confirmar as regras anti-duplicidade e anti-inferência;
- copiar exemplos de comando.

## Resultado esperado
Concluir sempre em um destes estados:
- paciente confirmada e cadastrada no Omie;
- duplicidade encontrada e reportada ao usuário;
- dados insuficientes claramente apontados para complemento;
- bloqueio real de API/credencial informado sem inventar progresso.
