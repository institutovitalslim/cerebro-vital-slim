---
name: omie-boletos
description: Baixa boletos dos faturamentos realizados no Omie ERP e organiza por paciente em pastas no Google Drive e/ou disco local. Use quando o usuário pedir para baixar boletos, organizar boletos por paciente, gerar boletos de uma data específica, ou consultar faturamentos com boletos pendentes. Também use para "boletos do dia", "boletos da semana", "salvar boletos no Drive" ou variações similares.
---

# Omie Boletos

Consulta faturamentos no Omie ERP, baixa os boletos em PDF e organiza por paciente em pastas no Google Drive e/ou disco local.

## Fluxo operacional

### 1. Consultar faturamentos

```bash
# Boletos de uma data específica
python3 scripts/omie_boletos.py --data 25/03/2026

# Boletos de um período
python3 scripts/omie_boletos.py --de 01/03/2026 --ate 31/03/2026

# Apenas listar (sem baixar/salvar)
python3 scripts/omie_boletos.py --data 25/03/2026 --listar
```

### 2. Baixar e salvar no Google Drive

```bash
# Baixar e salvar no Drive (pasta Pacientes)
python3 scripts/omie_boletos.py --data 25/03/2026 --drive

# Baixar e salvar no disco local
python3 scripts/omie_boletos.py --data 25/03/2026 --local
```

### 3. Exemplo de execução completa

```bash
python3 scripts/omie_boletos.py --data 25/03/2026 --drive --local
```

## Especificações técnicas

### Destinos de gravação

| Destino | Caminho |
|---------|---------|
| **Google Drive** | Pasta "Pacientes" dentro do Drive da clínica (ID: `1_on_1ABIODqcbpby-EwKHgciT0m4_P9f`) |
| **Disco local** | `C:\Users\tiaro\Documents\## Medical Contabilidade\#Instituto Vital Slim\Boletos de Programa de Acompanhamento\` |

### Estrutura de pastas

```
[Destino]/
├── NOME DO PACIENTE 1/
│   ├── Boleto_P001-009_R$1115_Venc07-04-2026.pdf
│   ├── Boleto_P002-009_R$1115_Venc07-05-2026.pdf
│   └── ...
├── NOME DO PACIENTE 2/
│   ├── Boleto_P001-015_R$966_Venc01-04-2026.pdf
│   └── ...
└── ...
```

### Nomenclatura dos arquivos

```
Boleto_P{parcela}_R${valor}_Venc{data}.pdf
```
- `{parcela}`: número da parcela no formato `NNN-NNN` (ex: `001-009`)
- `{valor}`: valor do documento
- `{data}`: data de vencimento no formato `DD-MM-AAAA`

## Regras de negócio

1. **Verificar antes de criar**: sempre listar pastas existentes antes de criar novas. Se a pasta do paciente já existir, reutilizar o ID — **nunca duplicar**.
2. **Pular parcelas sem boleto**: parcelas com `boleto.cGerado != "S"` (pagamento à vista, PIX, etc.) são ignoradas com log.
3. **Pular cancelados**: títulos com `status_titulo == "CANCELADO"` são ignorados.
4. **Rate limit**: respeitar limite de 3 req/s da API Omie (throttle automático de 0.4s entre chamadas).
5. **Verificar existência do boleto antes de upload**: se o arquivo já existir no destino (mesmo nome), pular para evitar duplicidade.

## Credenciais necessárias

### Omie API
- `OMIE_APP_KEY` e `OMIE_APP_SECRET`
- Fonte: `/root/.openclaw/secure/omie_api.env` ou 1Password (item "Acesso API OMIE")

### Google Drive (gog)
- Conta: `medicalemagrecimento@gmail.com`
- `GOG_KEYRING_PASSWORD`: obtido via 1Password (item "gog-keyring-pass")
- `OP_SERVICE_ACCOUNT_TOKEN`: de `/root/.openclaw/.op.service-account.env`

### Resolução de credenciais

```bash
export OMIE_APP_KEY=6655978677348
export OMIE_APP_SECRET=f6296760f5debd02e40e19c0bb62293a
export OP_SERVICE_ACCOUNT_TOKEN=$(grep OP_SERVICE_ACCOUNT_TOKEN /root/.openclaw/.op.service-account.env | cut -d= -f2-)
export GOG_KEYRING_PASSWORD=$(op item get 'gog-keyring-pass' --vault openclaw --fields password --reveal)
```

## Endpoints Omie utilizados

| Endpoint | Método | Uso |
|----------|--------|-----|
| `financas/contareceber` | `ListarContasReceber` | Listar títulos por data de emissão |
| `financas/contareceberboleto` | `ObterBoleto` | Obter link do PDF do boleto |
| `geral/clientes` | `ConsultarCliente` | Obter nome do paciente pelo código |

### Filtro de data correto

```json
{
  "filtrar_por_emissao_de": "DD/MM/AAAA",
  "filtrar_por_emissao_ate": "DD/MM/AAAA"
}
```
> **Importante**: usar `filtrar_por_emissao_de/ate` (data de emissão), **NÃO** `filtrar_por_data_de/ate` (data de alteração).

## Empresa configurada

- **Razão Social**: Freitas e Fernandes Serviços Médicos LTDA (Instituto Vital Slim)
- **CNPJ**: 40.289.526/0001-58
- **Código Omie**: 6737587523

## Troubleshooting

- **Pasta duplicada no Drive**: verificar se o script rodou mais de uma vez. Sempre usar `--listar` antes para validar.
- **Boleto sem link**: nem todos os títulos geram boleto (PIX, dinheiro, cartão). O script pula automaticamente.
- **Erro de keyring**: reautenticar com `gog auth login -a medicalemagrecimento@gmail.com --services drive --force-consent`.
- **Rate limit Omie**: se receber erro 429, aumentar o delay entre chamadas.
- **Timeout no download**: alguns boletos podem demorar. O script usa timeout de 30s por download.
