# Fluxo Operacional - Geração de Apresentação de Paciente

## Visão Geral

Esta skill automatiza a geração de apresentações HTML personalizadas para pacientes novos do Instituto Vital Slim. O fluxo executa duas vezes ao dia via cron.

## Horários de Execução

| Horário | Turno Buscado | Dia |
|---------|--------------|-----|
| 06:40 | Tarde | Hoje |
| 12:00 | Manhã | Amanhã |

## Passo a Passo

### 1. Buscar Pacientes Novos no Quarkclinic

**Endpoint:** `GET /v1/agendamentos`
**Parâmetros:**
- `data_agendamento_inicio` e `data_agendamento_fim`: data no formato dd-MM-yyyy
- Filtrar por turno baseado no horário:
  - Manhã: `horaAgendamento < 12:00`
  - Tarde: `horaAgendamento >= 12:00`

**Identificar paciente novo:**
- Verificar `dateCreated` do paciente. Se criado nos últimos 30 dias, considerar novo.
- Alternativa: contar agendamentos anteriores do mesmo `pacienteId` com status de atendimento completo.

**Dados coletados do paciente:**
- `nome`, `sexo`, `dataNascimento`, `telefone`, `email`, `pacienteId`

### 2. Buscar Exames no Google Drive

**Conta:** `medicalcontabilidade@gmail.com`
**Pasta base:** `1dCDANfnUcTX-iRFCCNtipQ5a3NWzHzSL`

**Processo:**
1. Buscar subpastas da pasta base
2. Comparar nome do paciente com nome da pasta (case-insensitive, removendo espaços e caracteres especiais)
3. Se encontrar pasta, listar todos os PDFs dentro dela
4. Se não encontrar, registrar como faltante

### 3. Buscar Questionários do Google Forms

**Conta:** `institutovitalslim@gmail.com`
**Formulários:**
- Pré-Consulta: `1j8h3FUn4riAqSPJoWsRv1Ura_PPcFx4SDG7kafVcX1g`
- Análise Hormonal (apenas mulheres): `1XGIH3MiwVkHWI5FaH9hjsmByMTAS-Td_H2_rm7T7T0s`

**Processo:**
1. Obter estrutura do formulário com `gog forms get <formId>`
2. Identificar campos de nome, email, CPF, data de nascimento
3. Listar todas as respostas com `gog forms responses list <formId>`
4. Encontrar resposta que corresponde ao paciente (match por nome)
5. Se paciente for mulher, repetir para o formulário de análise hormonal

### 4. Verificar Completeness

Para cada paciente, verificar se tem:
- [ ] Exames laboratoriais (PDFs no Drive)
- [ ] Questionário de pré-consulta preenchido
- [ ] Questionário de análise hormonal (apenas mulheres)

**Se faltar alguma informação:**
- Enviar mensagem no grupo informando o que falta
- Incluir nome do paciente e telefone para contato
- NÃO gerar apresentação

### 5. Extrair Dados dos Exames

Para cada PDF de exame:
1. Baixar do Google Drive via `gog drive export`
2. Extrair texto usando análise de PDF (ferramenta nativa de PDF)
3. Identificar valores de referência e resultados
4. Classificar como normal, alterado leve, alterado grave

### 6. Gerar Apresentação HTML

**Template base:** `assets/template-apresentacao.html`

**Substituições obrigatórias:**
- Nome do paciente
- Idade (calculada da `dataNascimento`)
- Cards de exames com valores reais
- Texto de implicação clínica personalizado
- Lista de "O que esperar em 180 dias"

**Tom da apresentação:**
- Nunca transmitir sensação de "está tudo bem"
- Exames alterados devem ser apresentados com gravidade adequada
- Enfatizar riscos de não agir
- Manter tom de esperança e reversibilidade

### 7. Enviar Apresentação

- Enviar arquivo HTML gerado no canal configurado
- Sempre enviar o link/arquivo quando houver alteração

## Estrutura de Diretórios da Skill

```
geracao-apresentacao-paciente/
├── SKILL.md                          # Instruções principais
├── scripts/
│   ├── buscar_pacientes_novos.py     # Busca no Quarkclinic
│   ├── buscar_exames_drive.py        # Busca no Google Drive
│   ├── buscar_questionarios.py       # Busca no Google Forms
│   └── gerar_apresentacao.py         # Orquestrador principal
├── references/
│   ├── fluxo-operacional.md          # Este arquivo
│   └── configuracao.md               # IDs, contas, constantes
└── assets/
    └── template-apresentacao.html    # Template base do HTML
```

## Dependências Externas

- `gog` CLI autenticado com:
  - `medicalcontabilidade@gmail.com` (Drive)
  - `institutovitalslim@gmail.com` (Forms, Sheets)
- `quarkclinic-api` skill com credenciais configuradas
- Python 3 com subprocess
- Acesso à ferramenta `pdf` do OpenClaw para extração de exames
