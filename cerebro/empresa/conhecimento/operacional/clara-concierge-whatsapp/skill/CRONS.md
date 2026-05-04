# Crons da Clara

3 crons automatizados que disparam mensagens da Clara para pacientes/leads.

## CRON-CONFIRM-AM

**Quando**: roda pela manha
**Quem confirma**: pacientes com atendimento na TARDE do mesmo dia
**Status**: em producao
**Tipo**: confirmacao operacional

Mensagem disparada (template):
```
Oi, [Nome]! Tudo bem? 😊

Estou passando para confirmar seu atendimento de [Tipo] hoje, 
as [hora], aqui no Instituto Vital Slim.

Se estiver tudo certo, pode me responder com **Confirmo**.
Se precisar, voce tambem pode me dizer **Quero remarcar** 
ou **Nao vou conseguir**.
```

## CRON-CONFIRM-PM

**Quando**: roda a tarde
**Quem confirma**: pacientes com atendimento na MANHA do dia seguinte
**Status**: em producao
**Tipo**: confirmacao operacional

Template identico ao CRON-CONFIRM-AM, com [hoje/amanha] adaptado.

## CRON-D1-LEAD-FIRST

**Quando**: 24h antes da consulta, no MESMO TURNO da consulta
- Consulta amanha de manha → cron envia hoje pela manha
- Consulta amanha a tarde → cron envia hoje a tarde

**Quem confirma**: LEAD com tag "Agendou" no PRIMEIRO atendimento (nunca foi PACIENTE)
**Status**: a implementar
**Tipo**: mensagem motivacional acolhedora (NAO operacional)

Template (4 blocos):
```
[BLOCO 1]
Oi, [Nome]! 💚

[delay 2s]

[BLOCO 2]
Esta chegando a hora do seu atendimento aqui no Instituto Vital Slim — 
estamos ansiosos para comecar essa jornada com voce.

[delay 2s]

[BLOCO 3]
Se voce ainda nao nos enviou os resultados dos seus exames, 
hoje e o melhor momento. Queremos chegar 100% prontos para 
o seu atendimento amanha.

[delay 1.5s]

[BLOCO 4]
Te espero por aqui. Ate amanha! ✨
```

### Lógica de detecção

```python
SE contato.etiqueta == "Agendou":
    SE contato nunca foi "Paciente" no QuarkClinic:
        SE data_consulta == amanha:
            SE turno_atual == turno_consulta:
                disparar CRON-D1-LEAD-FIRST
```

### Pseudocódigo

```python
def cron_d1_lead_first():
    agora = now()
    turno_atual = "AM" if agora.hour < 12 else "PM"
    amanha = agora.date() + timedelta(days=1)
    
    leads_agendados_amanha = filter(
        contatos,
        etiqueta="Agendou",
        nunca_foi_paciente=True,
        data_consulta=amanha,
        turno_consulta=turno_atual
    )
    
    for lead in leads_agendados_amanha:
        enviar_mensagem_motivacional(lead)
```

## Diferenciacao critica

| Cron | E uma confirmacao? | Pede CTA? | Para Paciente? |
|------|--------------------|-----------|-----------------|
| CRON-CONFIRM-AM/PM | Sim | Sim (Confirmo/Remarcar/Não) | Sim (excecao RC-12) |
| CRON-D1-LEAD-FIRST | Nao | Nao | Nao (apenas Lead/Agendou) |

**Importante**: o D1-LEAD-FIRST NAO substitui a confirmacao operacional do dia seguinte. Ambos rodam:
- Tarde do D-1 (turno = consulta) → motivacional
- Manha do D-0 ou tarde do D-1 (cron oposto) → confirmacao operacional

## Cron de pausa indefinida (proposta)

**Quando**: a cada 3h, se houver pausa indefinida ativa
**Status**: a implementar (ainda nao existe)
**Tipo**: lembrete administrativo para Tiaro

```python
def cron_lembrete_pausa_indefinida():
    state = get_admin_status()
    if state.paused == True and state.paused_until is None:
        elapsed_hours = (time.time() - state.paused_at) // 3600
        send_telegram_to_tiaro(f"Continuo pausada desde [{state.paused_at}]. Ja se passaram {elapsed_hours}h. Manter ou despausar?")
```

## Source of truth

MEMORIA_CONSOLIDADA secao 8.
