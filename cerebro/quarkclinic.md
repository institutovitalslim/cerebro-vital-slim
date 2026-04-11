# Quarkclinic

## Agenda padrão para marcação via API
- Nome: **AGENDA OPENCLAW**
- `agendaId`: `445996589`
- `profissionalId`: `240623016` (Daniely Alves Freitas)
- `clinicaId`: `227138348` (Instituto Vital Slim)

## Regra
- Para novos agendamentos via API, usar a **AGENDA OPENCLAW** como padrão.
- A agenda `240623539` pode retornar horários livres, mas pode falhar no POST com erro de que a agenda não permite agendamentos online.
- Sempre consultar `/horarios-livres` antes de tentar marcar.
- Se o horário solicitado cair no meio do intervalo, usar o início real do slot livre e comunicar isso ao usuário.

## Fluxo recomendado
1. Verificar se o paciente existe; se não, cadastrar.
2. Consultar horários livres da agenda padrão.
3. Criar o agendamento com o início exato do slot.
4. Informar o ID do agendamento e o horário efetivamente usado.
