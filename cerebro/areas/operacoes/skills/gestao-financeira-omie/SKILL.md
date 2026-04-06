---
name: gestao-financeira-omie
description: >
  Orienta e executa tarefas financeiras no Omie ERP do IVS: lançamentos de contas a pagar/receber, verificação de fluxo de caixa, conciliação bancária e consulta de estoque. Trigger: "abra o Omie", "cheque o financeiro", "lançamento no Omie", "fluxo de caixa", "conciliação".
---

# Gestão Financeira — Omie ERP

## Quando usar
Sempre que Tiaro pedir qualquer tarefa financeira, fiscal ou de estoque relacionada ao Omie.

## Acesso
1. Abrir `https://app.omie.com.br/login/`
2. Informar e-mail operacional
3. Clicar em `Continuar`
4. Informar senha (de fonte segura: `/root/.openclaw/secure/omie_credentials.env`)
5. Se pedir código por e-mail → usar o mais recente
6. Se pedir TOTP → solicitar código atual de 6 dígitos ao Tiaro (ou usar Authenticator se disponível)

## Módulos e tarefas principais

### Contas a Pagar
- Menu: Finanças → Contas a Pagar
- Verificar vencimentos dos próximos 7 dias
- Registrar novos lançamentos (fornecedor, valor, vencimento, centro de custo)

### Contas a Receber
- Menu: Finanças → Contas a Receber
- Verificar pagamentos pendentes dos Programas de Acompanhamento
- Registrar recebimentos confirmados
- Gerar boletos quando necessário

### Fluxo de Caixa
- Menu: Finanças → Fluxo de Caixa
- Relatório diário: entradas previstas vs realizadas
- Identificar gaps e alertar Tiaro quando necessário

### Conciliação Bancária
- Via Omie.Cash (conta digital integrada)
- Menu: Finanças → Conciliação Bancária
- Confirmar lançamentos automáticos
- Resolver pendências de conciliação

### Gestão de Estoque
- Menu: Compras e Estoque
- Verificar saldo de medicamentos e insumos
- Registrar entradas de compras
- Alertar quando produto atingir estoque mínimo

## Erros já mapeados
- Código de e-mail inválido → usar o código mais recente emitido
- TOTP inválido → verificar hora automática no celular; usar código no início da janela de 30s
- Se 2FA não disponível → solicitar explicitamente ao Tiaro antes de insistir

## Output esperado
Para cada tarefa: confirmação do que foi feito + resumo dos dados relevantes (totais, vencimentos, alertas).
