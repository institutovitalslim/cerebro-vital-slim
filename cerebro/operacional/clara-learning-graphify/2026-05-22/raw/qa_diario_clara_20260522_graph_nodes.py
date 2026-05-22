class ClaraQADiarioConversao20260522:
    """Graphify seed for Clara daily conversion QA 2026-05-22 01:30 UTC."""

    def evidencia_zero_outbound(self):
        return "current window has 6 inbound messages, 2 unique leads and 0 outbound messages; operational risk requires human runtime check"

    def melhoria_sla_primeira_resposta(self):
        return "new inbound lead messages need objective first response within 5 minutes without clinical claims"

    def melhoria_abertura_vaga(self):
        return "vague openings should receive a closed intent question: schedule, reschedule, or ask a question; avoid generic how can I help in cold leads"

    def melhoria_espera_sem_previsao(self):
        return "mentions of order of arrival, waiting or no appointment forecast should trigger immediate recovery with schedule check or two concrete reschedule windows"

    def guardrail_operacional(self):
        return "Maria must not contact leads or pause Clara autonomously; human intervention is runtime verification only unless Tiaro explicitly orders pause"
