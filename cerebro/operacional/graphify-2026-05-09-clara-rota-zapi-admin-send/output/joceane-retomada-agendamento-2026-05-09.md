# Retomada Joceane — autorização Tiaro

Tiaro determinou que Clara deveria responder Joceane e seguir com foco no agendamento.

Ação operacional:
- Contato identificado: `557188225047`, registro `16-10-24 - Lead - Joceane`.
- Registro estava em exclusões como `patient_bridge_known`, mas com nome de lead.
- Aplicada exceção explícita autorizada por Tiaro:
  - `reason=lead_exception_tiaro_followup_agendamento`
  - `source=tiaro_lead_exception`
- Janela ativa aberta para continuidade.
- Mensagem enviada via `/admin/send` com foco em avaliação/agendamento.
- Z-API retornou `status=200`, messageId `10DA985A95592C420439`.

Mensagem enviada:
> Joceane, entendi. Peso, cansaço, libido e sono são pontos importantes para avaliarmos com cuidado na consulta, porque podem ter relação com diferentes fatores do seu metabolismo e da sua rotina.
>
> O melhor próximo passo é você passar pela avaliação com a Dra. Daniely para ela olhar seu caso de forma completa e direcionar com segurança.
>
> Para eu já te ajudar com o agendamento: você prefere ver horários pela manhã ou pela tarde?

Guardrails:
- Não houve promessa clínica.
- Não houve prescrição/diagnóstico.
- Foco mantido em agendamento com Dra. Daniely.
