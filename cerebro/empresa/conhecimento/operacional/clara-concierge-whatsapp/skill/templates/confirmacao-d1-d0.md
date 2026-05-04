# Template: Confirmacao D-1 / D-0

Disparado pelos crons CRON-CONFIRM-AM (manha) e CRON-CONFIRM-PM (tarde).

Exemplos reais funcionando: Taina, Larissa, Cintia, Francisco, Silvana Modesto, Erick.

## Estrutura padrao

```
[BLOCO 1]
Oi, [Nome]! Tudo bem? 😊

[BLOCO 2]
Estou passando para confirmar seu atendimento de **[Tipo]** [hoje/amanha], 
as **[hora]**, aqui no Instituto Vital Slim.

[BLOCO 3]
Se estiver tudo certo, pode me responder com **Confirmo**.
Se precisar, voce tambem pode me dizer **Quero remarcar** 
ou **Nao vou conseguir**.
```

## Tipos de atendimento (preencher [Tipo])

- "Consulta Particular"
- "Aplicacao SC - Tirzepatida"
- "Aplicacao IM"
- "Aplicacao EV" (soroterapia)
- "Aplicacao - Protocolo (IM/SC/EV)"
- "Tricologia" (com Dra. Patricia Fabrini)
- "IMPLANTES"
- "Retorno" / "Consulta de retorno"

## Variantes vistas em producao

### Multiplos atendimentos no mesmo dia
Ex: "consulta de hoje, as 16:00 [Tainá] e 17:00 [Cintia]" - Clara separa por turno.

### Caso paciente nao confirma
Cron continua tentando ate o dia. Se nao confirma ate 4h antes, Liane assume manualmente.

### Confirmacao compartilhada com casal/familia
Ex: "Sra. Isabela esta agendada para o horario das 16:00 e o Sr. Aristoteles no horario das 17:00"

## NAO incluir nesta confirmacao

- Valores
- Lembrete de exames (vai em outro template PRE-CONSULTA-D3)
- Mensagem motivacional (vai em CRON-D1-LEAD-FIRST so para primeiro atendimento)

## Pos-confirmacao do paciente

Se paciente responde:
- "Confirmo" / "Sim" / "OK" -> Clara nao responde mais (e paciente, RC-12)
- "Quero remarcar" -> Escala humano (Liane gerencia agenda)
- "Nao vou conseguir" -> Clara: "Tudo bem, [Nome]. A equipe vai entrar em contato pra reagendar." + escala humano
- Pergunta nao-padrao -> Clara nao responde, escala humano (RC-12)
