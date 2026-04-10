# Quarkclinic — Operação

## Agenda padrão para marcação

Usar como padrão de marcação a agenda:

- **AGENDA OPENCLAW**
- **agendaId:** `445996589`
- **profissionalId:** `240623016` (Daniely Alves Freitas)
- **clinicaId:** `227138348` (Instituto Vital Slim)

## Regra operacional

- Para novos agendamentos via API do Quarkclinic, priorizar a **AGENDA OPENCLAW (`445996589`)**.
- A agenda antiga `240623539` pode aparecer com horários livres, mas pode bloquear criação via endpoint com erro de que a agenda não permite agendamentos online.
- Sempre consultar `/horarios-livres` da agenda padrão antes do POST.
- Quando o horário solicitado não existir exatamente, usar o início real do slot livre mais próximo e informar isso ao usuário.
