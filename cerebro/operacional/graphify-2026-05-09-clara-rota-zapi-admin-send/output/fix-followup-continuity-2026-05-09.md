# Fix — Continuidade de follow-up Clara/Z-API

Problema reportado por Tiaro: Clara disparava follow-up, o lead respondia, mas Clara não respondia depois.

Causa operacional identificada:
- o envio ativo via `/admin/send` não abria janela ativa de continuidade do lead;
- o eco outbound da Z-API (`fromMe=true`, `fromApi=true`) era ignorado sem registrar continuidade;
- em alguns casos a Z-API devolve telefone com normalização diferente (com/sem nono dígito), então o lead respondia em uma chave diferente e caía em `existing_lead_requires_manual_release`.

Correção:
- criado `mark_followup_outbound(phone, source)`;
- `/admin/send` agora abre janela ativa quando o envio Z-API tem sucesso;
- webhook `fromApi` também abre janela ativa usando o telefone que a Z-API enviou;
- backfill aplicado nos outbounds recentes dos logs para reduzir perda de continuidade imediata.

Validação:
- teste unitário confirmou que lead conhecido/inativo antes bloqueava e, após outbound, passa para `active_lead_window`;
- teste live com webhook `fromApi` fake confirmou registro `source=zapi_from_api_outbound`;
- bridge reiniciada e `/healthz` OK.

Guardrails preservados:
- exclusões/pacientes continuam bloqueados por `should_pause_clara` e QuarkClinic;
- não houve envio real de WhatsApp em teste.
