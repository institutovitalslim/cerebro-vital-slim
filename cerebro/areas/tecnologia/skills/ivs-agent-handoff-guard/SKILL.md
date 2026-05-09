---
name: ivs-agent-handoff-guard
description: Cria pacotes seguros de handoff entre Maria, Clara, João, Pedro e conselhos, com escopo, guardrails e próximo passo.
---

# IVS Agent Handoff Guard

Skill para transferência operacional entre agentes IVS sem perda de contexto e sem vazar bastidores para leads/pacientes.

## Uso

```bash
python3 /root/.openclaw/workspace/skills/ivs-agent-handoff-guard/scripts/handoff_packet.py \
  --from maria-gerente --to clara-whatsapp \
  --subject "Retomar lead" \
  --context "Lead respondeu dor principal" \
  --next-action "Conduzir para agendamento" \
  --sensitivity lead \
  --md-out /root/deliverables/handoff.md
```

## Guardrails

- Não envia a mensagem; só cria pacote de handoff.
- Se `to=clara-whatsapp`, saída deve ser texto seguro para atendimento, sem ferramenta/bastidor.
- Se o assunto envolver paciente, diagnóstico ou prescrição, o pacote exige escala clínica/humana.
- Financeiro/contrato exige Tiaro/Pedro conforme escopo.
