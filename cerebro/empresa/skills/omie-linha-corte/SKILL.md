---
name: omie-linha-corte
description: >
  Realiza linha de corte (ponto de corte financeiro) em contas correntes do Omie ERP.
  Zera o saldo da conta e define um novo ponto de partida para o controle financeiro.
  Use quando: "linha de corte", "ponto de corte", "zerar saldo", "iniciar controle financeiro",
  "corte financeiro", "resetar conta", "novo saldo inicial".
metadata:
  version: 1.0.0
  domain: financeiro
  owner: main
---

# Omie Linha de Corte — Ponto de Corte Financeiro

## O que é

Procedimento que zera o saldo de uma conta corrente no Omie ERP e define um novo ponto de partida para o controle financeiro. Usado quando se deseja iniciar um novo período contábil sem arrastar saldos anteriores.

## Quando usar

- Início de ano fiscal
- Migração de sistema contábil
- Correção de saldos divergentes
- Novo início de controle financeiro

## Pré-requisitos

### Categorias de Ajuste de Saldo (já cadastradas)

| Categoria | Código | Uso |
|-----------|--------|-----|
| AJUSTE DE SALDO (Receita) | `1.04.96` | Quando saldo está negativo (lançamento positivo para zerar) |
| AJUSTE DE SALDO (Despesa) | `2.05.98` | Quando saldo está positivo (lançamento negativo para zerar) |

### Credenciais
- `OMIE_APP_KEY`: 6655978677348
- `OMIE_APP_SECRET`: via `/root/.openclaw/secure/omie_api.env` ou 1Password (item "Acesso API OMIE")

## Contas Correntes Disponíveis

| Conta | ID | Tipo |
|-------|-----|------|
| Caixinha | 6737587708 | CX |
| Omie.CASH | 6737590387 | - |
| Bradesco | 6737642153 | - |
| Santander | 6737645884 | - |
| Banco Inter | 6737869298 | - |
| Cloudwalk IP LTDA | 6737869936 | - |
| Glosas | 6740282183 | - |
| Coparticipação | 6740293850 | - |
| Cartão Santander - MasterCard | 6748905537 | - |
| Cartão Bradesco - Elo | 6753386082 | - |
| Tarifa de Cartão | 6753839138 | - |
| Cartão Inter - MasterCard | 6764103227 | - |

## Protocolo de Execução

### Passo 1 — Calcular saldo atual da conta

```bash
python3 /root/.openclaw/workspace/skills/omie-api/scripts/omie_api.py call financas/contacorrentelancamentos ListarLancCC '{"nPagina":1,"nRegPorPagina":50}'
```

Filtrar os lançamentos pela conta desejada (`cabecalho.nCodCC`) e calcular:
- Natureza `R` (Receita) → somar ao saldo
- Natureza `P` (Pagamento) → subtrair do saldo

### Passo 2 — Definir Saldo Inicial e Data na Conta Corrente

```python
api_call("geral/contacorrente", "AlterarContaCorrente", {
    "nCodCC": ID_DA_CONTA,
    "saldo_inicial": 0,
    "saldo_data": "DD/MM/AAAA",        # Data do novo início (ex: 01/01/2026)
    "descricao": "NOME_DA_CONTA",       # Manter o nome original
    "tipo_conta_corrente": "TIPO",      # Manter o tipo original (CX, CC, etc.)
    "codigo_banco": "CODIGO"            # Manter o código original
})
```

**Campos obrigatórios**: `nCodCC`, `saldo_inicial`, `saldo_data`, `descricao`, `tipo_conta_corrente`, `codigo_banco`

> Consultar dados atuais da conta com `ConsultarContaCorrente` antes de alterar para preservar campos existentes.

### Passo 3 — Criar lançamento de ajuste para zerar o saldo

```python
api_call("financas/contacorrentelancamentos", "IncluirLancCC", {
    "cabecalho": {
        "nCodCC": ID_DA_CONTA,
        "dDtLanc": "DD/MM/AAAA",        # 1 dia ANTES da Data do Saldo Inicial
        "nValorLanc": VALOR_ABSOLUTO     # Valor absoluto do saldo (sem sinal)
    },
    "detalhes": {
        "cCodCateg": "CATEGORIA",        # 2.05.98 se positivo, 1.04.96 se negativo
        "cObs": "Ajuste de saldo - Linha de corte DD/MM/AAAA",
        "cTipo": "99999"
    }
})
```

### Regras de decisão

| Saldo atual | Categoria a usar | Efeito |
|-------------|-----------------|--------|
| **Positivo** (ex: R$ 500) | `2.05.98` (Despesa) | Gera lançamento negativo → zera |
| **Negativo** (ex: -R$ 500) | `1.04.96` (Receita) | Gera lançamento positivo → zera |
| **Zero** | Nenhuma ação necessária | Apenas definir saldo_data |

### Regras de segurança

1. **SEMPRE confirmar com o usuário** antes de executar — mostrar conta, saldo atual, valor do ajuste e data
2. **NUNCA executar sem confirmação explícita**
3. **Consultar dados da conta antes de alterar** para não sobrescrever campos existentes
4. **Data do lançamento = Data do Saldo Inicial - 1 dia**
5. **Registrar a operação na observação** do lançamento para rastreabilidade
6. **Verificar o saldo após execução** para confirmar que zerou corretamente

## Verificação pós-execução

```python
# Confirmar que a conta foi atualizada
r = api_call("geral/contacorrente", "ConsultarContaCorrente", {"nCodCC": ID_DA_CONTA})
print(f"Saldo Inicial: {r['saldo_inicial']}")
print(f"Data: {r['saldo_data']}")
# Ambos devem refletir os valores configurados
```

## Histórico de execuções

| Data | Conta | Saldo anterior | Ajuste | Categoria | ID Lançamento |
|------|-------|----------------|--------|-----------|---------------|
| 2026-04-07 | Caixinha (6737587708) | R$ 140,00 | R$ 140,00 | 2.05.98 | 6825963504 |

## Empresa

- **Razão Social**: Freitas e Fernandes Serviços Médicos LTDA (Instituto Vital Slim)
- **CNPJ**: 40.289.526/0001-58
- **Código Omie**: 6737587523

## Troubleshooting

- **Erro "Tag não faz parte da estrutura"**: verificar nomes dos campos. Usar `saldo_inicial` e `saldo_data` (não `nSaldoInicial` ou `dDtSaldoInicial`).
- **Saldo não zerou**: verificar se a natureza do lançamento está correta (despesa para saldo positivo, receita para negativo).
- **Conta não encontrada**: listar contas com `ListarContasCorrentes` e confirmar o `nCodCC`.
