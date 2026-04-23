# Configuração - Geração de Apresentação de Paciente

## Contas Google

| Serviço | Conta | Uso |
|---------|-------|-----|
| Google Drive | `medicalcontabilidade@gmail.com` | Buscar pastas e PDFs de exames |
| Google Forms | `institutovitalslim@gmail.com` | Buscar respostas de questionários |

## IDs do Google Drive

| Recurso | ID | Descrição |
|---------|-----|-----------|
| Pasta base de pacientes | `1dCDANfnUcTX-iRFCCNtipQ5a3NWzHzSL` | Pasta raiz onde estão as subpastas dos pacientes |

## IDs do Google Forms

| Formulário | ID | Público |
|------------|-----|---------|
| Pré-Consulta | `1j8h3FUn4riAqSPJoWsRv1Ura_PPcFx4SDG7kafVcX1g` | Todos os pacientes |
| Análise Hormonal | `1XGIH3MiwVkHWI5FaH9hjsmByMTAS-Td_H2_rm7T7T0s` | Apenas mulheres |

## API Quarkclinic

- **Base URL:** `https://api.quark.tec.br/clinic/ext`
- **Endpoint de agendamentos:** `GET /v1/agendamentos`
- **Endpoint de pacientes:** `GET /v1/pacientes/{id}`
- **Formato de data:** `dd-MM-yyyy`

## Diretórios

| Diretório | Caminho | Uso |
|-----------|---------|-----|
| Deliverables | `/root/cerebro-vital-slim/deliverables` | Onde os HTMLs gerados são salvos |
| Skill | `/root/cerebro-vital-slim/skills/geracao-apresentacao-paciente` | Raiz da skill |

## Constantes de Negócio

- **Turno manhã:** horários antes de 12:00
- **Turno tarde:** horários a partir de 12:00
- **Janela de paciente novo:** `dateCreated` nos últimos 30 dias
- **Duração do programa:** 180 dias
