# Verdades Operacionais

Este arquivo concentra fatos operacionais canônicos que **não podem ser esquecidos**.

## GitHub / Cérebro
- Repositório oficial do cérebro: `institutovitalslim/cerebro-vital-slim`
- URL remota correta: `https://github.com/institutovitalslim/cerebro-vital-slim.git`
- Quando Tiaro disser **"commit no cérebro"**, isso significa:
  1. atualizar os arquivos relevantes no workspace do cérebro;
  2. fazer `git commit`;
  3. fazer `git push` para o repositório oficial no GitHub.

## WhatsApp
- A comunicação operacional por WhatsApp deve usar a **bridge da Z-API**.
- Não assumir que um fluxo criado a partir de contexto Telegram consegue disparar WhatsApp automaticamente sem estar amarrado ao contexto/caminho correto.

## Quarkclinic
- Agenda padrão para novos agendamentos via API: **AGENDA OPENCLAW**
- `agendaId`: `445996589`
- `profissionalId`: `240623016` (Daniely Alves Freitas)
- `clinicaId`: `227138348` (Instituto Vital Slim)
- A agenda `240623539` pode listar horários livres, mas pode bloquear criação via endpoint com erro de agenda não permitir agendamentos online.
- Ao marcar consulta, sempre consultar `/horarios-livres` da agenda padrão primeiro.
- Quando o horário exato não existir, usar o início real do slot livre mais próximo e informar isso claramente.

## Time da clínica
- **Dra. Daniely Alves Freitas**
  - WhatsApp: `+55 71 99696-2059`
  - E-mail: `danyafreitas@hotmail.com`
- **Liane (enfermeira)**
  - WhatsApp: `+55 71 99157-4827`
  - E-mail: `enfermagem.vitalslim@gmail.com`

## Comercial / Leads
- Nunca passar preço antes de o paciente entender o valor do atendimento.
- Em leads, primeiro acolher, entender a necessidade, contextualizar o atendimento e explicar a proposta/avaliação; só depois entrar em preço.
- Quando Tiaro pedir para "chamar o conselho", usar a skill/metodologia canônica de conselho (`llm-council`) quando ela for a referência definida, e não improvisar com subagente genérico.

## Regra de operação
Antes de responder ou executar tarefas recorrentes de GitHub, Quarkclinic, WhatsApp/Z-API ou time da clínica, consultar os arquivos canônicos correspondentes em `cerebro/`.
