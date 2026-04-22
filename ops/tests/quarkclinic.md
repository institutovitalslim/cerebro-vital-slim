# Teste Canônico — Quarkclinic

## Cenário
Usuário pede consulta de agenda, horário livre ou agendamento.

## Entrada típica
- data ou janela de horário
- profissional ou contexto de agenda
- paciente ou intenção de marcar consulta

## Ação esperada
- consultar a agenda canônica correta
- validar slot real pelo endpoint correto
- usar o horário real do slot quando o horário exato não existir
- deixar claro qualquer ajuste feito

## Evidência mínima de sucesso
- agenda/slot consultado com dados reais; ou
- agendamento criado/validado; ou
- bloqueio explícito com causa real

## Parar e pedir confirmação quando
- houver conflito entre agenda listável e agenda realmente agendável
- faltar dado essencial do paciente
- houver divergência entre horário pedido e slot real disponível
