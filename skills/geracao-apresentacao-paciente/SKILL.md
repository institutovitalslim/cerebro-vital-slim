---
name: geracao-apresentacao-paciente
description: Gera apresentações HTML personalizadas para pacientes novos do Instituto Vital Slim, combinando exames laboratoriais do Google Drive, respostas de questionários do Google Forms e dados do Quarkclinic. Use quando for necessário criar apresentações de pacientes, gerar relatórios de exames, automatizar o processo de pré-consulta, ou quando o usuário pedir para gerar apresentação de um paciente específico. Também use para verificar se pacientes têm exames e questionários pendentes.
---

# Geração de Apresentação de Paciente

Automatiza a criação de apresentações HTML personalizadas para pacientes novos do Instituto Vital Slim.

## Quando Usar Esta Skill

- Gerar apresentação HTML para paciente novo
- Verificar se pacientes têm exames e questionários pendentes
- Automatizar o fluxo de pré-consulta
- Processar exames laboratoriais de PDFs
- Criar relatórios clínicos personalizados

## Pré-requisitos

Antes de executar, verificar:
- `gog` CLI autenticado com `medicalcontabilidade@gmail.com` (Drive) e `institutovitalslim@gmail.com` (Forms)
- `quarkclinic-api` skill com credenciais ativas
- Python 3 disponível

Para verificar: `gog auth list` e `python3 scripts/quarkclinic_api.py --check`

## Fluxo Principal

### 1. Buscar Pacientes Novos

```bash
python3 scripts/buscar_pacientes_novos.py <data_dd-MM-yyyy> <turno>
```

- `turno`: `manha` (horário < 12:00) ou `tarde` (horário >= 12:00)
- Horários de execução:
  - **06:40**: busca pacientes da TARDE do mesmo dia
  - **12:00**: busca pacientes da MANHÃ do dia seguinte

O script retorna JSON com lista de pacientes novos (nome, sexo, dataNascimento, telefone, email, pacienteId).

### 2. Para Cada Paciente, Verificar Informações

**A. Exames no Google Drive**
```bash
python3 scripts/buscar_exames_drive.py "Nome do Paciente"
```
- Busca na pasta base `1dCDANfnUcTX-iRFCCNtipQ5a3NWzHzSL`
- Compara nome do paciente com nome da subpasta (case-insensitive)
- Retorna lista de PDFs encontrados ou mensagem de não encontrado

**B. Questionários do Google Forms (ou PDF no Drive)**
```bash
python3 scripts/buscar_questionarios.py "Nome do Paciente" [--sexo FEMININO|MASCULINO]
```
- Busca no formulário de Pré-Consulta (obrigatório para todos)
- Se sexo for FEMININO, também busca no formulário de Análise Hormonal
- Encontra resposta pelo nome do paciente
- **Fallback:** se não encontrar no Forms, verifica se há PDF de questionário na pasta do paciente no Drive (alguns pacientes preenchem em papel)
- Retorna JSON com respostas formatadas, indicador de fonte (`forms` ou `pdf_drive`), ou `não encontrado`

### 3. Verificar Completeness

Para cada paciente, verificar se tem:
- [ ] Exames laboratoriais (PDFs no Drive)
- [ ] Questionário de pré-consulta preenchido
- [ ] Questionário de análise hormonal (apenas mulheres)

**Se faltar informação:**
Enviar mensagem no grupo informando:
```
⚠️ PACIENTE: [NOME]
❌ FALTAM: [lista do que falta]
📞 Contato: [telefone]
```

**Se tudo OK:** prosseguir para geração da apresentação.

### 4. Extrair Dados dos Exames

Para cada PDF de exame:
1. Baixar do Google Drive via `gog drive export <fileId> --out /tmp/exame.pdf`
2. Extrair texto e valores usando a ferramenta `pdf` do OpenClaw
3. Identificar: nome do exame, resultado, valor de referência, flag (normal/alterado)
4. Classificar severidade: ok, warn (leve), alert (grave)

**Foco nos exames alterados.** Exames normais podem ser listados brevemente.

### 5. Gerar Apresentação HTML

**Template base:** `assets/template-apresentacao.html`

**Substituições obrigatórias:**
- Nome do paciente → no título e capa
- Idade → calculada de `dataNascimento` (anos)
- Cards de exames → substituir os cards do template pelos exames reais do paciente
- Texto de implicação → descrever a gravidade do quadro clínico com base nos exames alterados
- Lista "O que esperar em 180 dias" → adaptar aos exames do paciente
- Cards de implicação → substituir pelos órgãos/sistemas afetados
- Texto final CTA → resumir os principais achados
- Idade no bloco central → idade real do paciente

**Tom da apresentação:**
- **NUNCA** transmitir sensação de "está tudo bem"
- Exames alterados devem ser apresentados com **gravidade adequada**
- Enfatizar riscos de não agir
- Manter tom de esperança e reversibilidade
- Frases como "Seus exames não estão bons" ou "Seus exames estão muito comprometidos" são apropriadas quando há alterações significativas

**Salvar em:** `/root/cerebro-vital-slim/deliverables/apresentacao-[nome-paciente].html`

### 6. Enviar Apresentação

- Enviar arquivo HTML gerado no canal configurado
- **Sempre** enviar o arquivo quando houver alteração (regra: nunca esperar pedir)

## Script Orquestrador

Para executar o fluxo completo de uma vez:

```bash
python3 scripts/gerar_apresentacao.py <data_dd-MM-yyyy> <turno>
```

Este script:
1. Busca pacientes novos
2. Para cada um, busca exames e questionários
3. Verifica completeness
4. Gera apresentações para pacientes completos
5. Gera relatório de faltantes
6. Salva relatório em `/root/cerebro-vital-slim/deliverables/relatorio-[data]-[turno].json`

## Agendamento (Cron) — Já Configurado ✅

Os cron jobs já estão ativos no sistema:

| Horário | Comando | Função |
|---------|---------|--------|
| **06:40** | `gerar_apresentacao.py $(date +%d-%m-%Y) tarde` | Busca pacientes novos da **tarde de hoje** |
| **12:00** | `gerar_apresentacao.py $(date -d "+1 day" +%d-%m-%Y) manha` | Busca pacientes novos da **manhã de amanhã** |

Logs: `logs/cron-morning.log` e `logs/cron-noon.log`

## Referências

- **Fluxo operacional detalhado:** [references/fluxo-operacional.md](references/fluxo-operacional.md)
- **IDs, contas e constantes:** [references/configuracao.md](references/configuracao.md)
