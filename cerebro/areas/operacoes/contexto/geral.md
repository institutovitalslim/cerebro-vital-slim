# Operações — Contexto

## Como funciona
A gestão operacional e financeira do IVS é feita via **Omie ERP** (app.omie.com.br). O acesso é feito com login `medicalemagrecimento@gmail.com` + senha + TOTP (Google Authenticator).

## Áreas financeiras a estruturar (prioridade atual)
1. **Contas a pagar** — lançamentos e vencimentos
2. **Contas a receber** — controle de pagamentos dos programas
3. **Fluxo de caixa** — previsões e relatórios diários
4. **Conciliação bancária** — via Omie.Cash (conta digital integrada)
5. **Gestão de estoque** — medicamentos e insumos da clínica

## Ferramentas
- **Omie ERP** — sistema principal: financeiro, fiscal, estoque, CRM, serviços
- **Omie.Cash** — conta digital integrada para conciliação automática
- **R Leiro Contabilidade** — escritório contábil parceiro

## Módulos Omie relevantes para o IVS
| Módulo | Uso |
|--------|-----|
| Gestão Financeira | Contas a pagar/receber, fluxo de caixa, boletos |
| Conciliação bancária | Via Omie.Cash automaticamente |
| Gestão de Serviços | Controle de contratos (Programas de Acompanhamento), NFS-e |
| Estoque e Compras | Controle de medicamentos e insumos |
| Emissão Fiscal | NFS-e de consultas e programas |

## Acesso Omie
- Login: `https://app.omie.com.br/login/`
- Treinamentos: `https://portal.omie.com.br/treinamentos`
- 2FA: TOTP via Google Authenticator (se código não disponível, solicitar ao Tiaro)
- Credenciais seguras: armazenadas em `/root/.openclaw/secure/omie_credentials.env`

## Principais desafios
1. Lançamentos financeiros ainda não totalmente estruturados no Omie
2. Fluxo de caixa sem visibilidade consistente
3. Estoque sem controle sistemático
4. Integração com a contabilidade (R Leiro) a formalizar

_Atualizado: 2026-04-06_
