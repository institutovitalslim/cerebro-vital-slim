# Regra canônica — QuarkClinic é fonte de verdade de pacientes para histórico da Clara

Data: 2026-06-24
Responsável: Maria
Origem: incidente de follow-up em lote para pacientes

## Decisão

O histórico operacional da Clara deve ser mantido sincronizado com o QuarkClinic para todos os pacientes que constam no sistema.

## Regra

1. QuarkClinic é a fonte de verdade para identificar paciente.
2. Todo telefone de paciente encontrado no QuarkClinic deve entrar na aba `pacientes` da planilha central de histórico WhatsApp da Clara.
3. Todo telefone de paciente encontrado no QuarkClinic deve entrar também em `clara_exclusions.json` com razão `quarkclinic_patient_rc12` e fonte `quarkclinic_patient_sync`.
4. A Clara não pode fazer follow-up comercial para contato que conste como paciente em qualquer uma destas fontes:
   - QuarkClinic;
   - aba `pacientes` da planilha central;
   - `clara_exclusions.json` com `patient_bridge_known`, `bridge_contexto_paciente` ou `quarkclinic_patient_rc12`;
   - histórico classificado como `paciente_ativo`.
5. Falso negativo temporário do QuarkClinic não libera envio se outra fonte marcar paciente/patient-like.
6. A sincronização é operacional, não clínica: não altera dados médicos nem cadastro do paciente no QuarkClinic; apenas replica a condição de paciente para bloqueio da Clara.

## Implementação

Script canônico:

```bash
python3 /root/cerebro-vital-slim/scripts/sync_quarkclinic_patients_to_clara_history.py --apply --max-pages 80 --workers 10
```

Wrapper cron:

```bash
/root/.hermes/scripts/ivs_sync_quarkclinic_patients_to_clara_history.sh
```

Cron Hermes:

```text
job_id: 99c6856042d6
nome: IVS sync QuarkClinic pacientes para histórico Clara
cadência: every 2h
modo: no_agent
```

## Critério de aceite

Antes de qualquer novo lote de follow-up ativo:

```text
paciente_ativo elegível = 0
patient_bridge_known elegível = 0
quarkclinic_patient_rc12 elegível = 0
kind=frio enviado em lote = 0
duplicidade por telefone/chat = 0
```

## Artefatos de relatório

Último relatório sanitizado:

```text
/root/cerebro-vital-slim/cerebro/operacional/clara-quarkclinic-patient-sync/latest.json
```

Relatório do incidente original:

```text
/root/cerebro-vital-slim/cerebro/operacional/incidente-clara-followup-pacientes-duplicado-2026-06-24.md
```
