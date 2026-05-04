# Template: Handoff financeiro (RC-16)

Quando lead aceita fechar agendamento e Clara precisa do link de pre-consulta da InfinityPay (sem API, emitido manualmente por humano).

## Fluxo completo

### T+0: Clara avisa paciente

```
[BLOCO 1]
Show, [Nome]! 💚 
Vou solicitar o link de pagamento a nossa equipe financeira 
e te envio aqui em seguida.
```

### T+0: Clara → Tiaro (mensagem estruturada)

Destinatario: WhatsApp 5571986968887

```
🆕 PRÉ-CONSULTA — solicitar link

Paciente: [Nome completo]
WhatsApp: [+55 71 9XXXX-XXXX]
Valor: R$ 300
Parcelamento: cartão 2x sem juros
Desconto aplicado: [Sim - R$ 100 OFF / Não]
Total final consulta: [R$ 900 ou R$ 1.000]
Origem do lead: [ABRIL A / Instagram / Indicação X / etc]
Observação: [se houver algo relevante]

Aguardando link pra repassar.
```

### T+30 min (sem resposta de Tiaro)

Clara reforca pro paciente:
```
Ja solicitei o link a nossa equipe. 
Em instantes te envio. 🙏
```

### T+2h (Tiaro ainda nao respondeu)

Clara escala automaticamente para Liane (5571991574827):

```
🆕 PRÉ-CONSULTA — escalacao financeiro (T+2h)

Paciente: [Nome] [WhatsApp]
Solicitacao enviada ao Tiaro as [hora] - sem resposta ate agora.

[mesmos dados da solicitacao original]

Pode emitir o link InfinityPay e me enviar?
```

### Quando link chega (de Tiaro OU Liane)

Clara repassa ao paciente em blocos:

```
[BLOCO 1]
Aqui esta o link da pre-consulta, [Nome]! 💳
[link InfinityPay]

[delay 2s]

[BLOCO 2]
Cartao em 2x sem juros. Pode usar no mesmo dia.

[delay 1.5s]

[BLOCO 3]
Assim que voce confirmar o pagamento, eu te envio o questionario 
pre-consulta e os pedidos de exames.
```

## Cenarios excepcionais

### Tiaro responde com instrucao especial
Ex: "Manda link separado pra ela", "Vou ligar direto". Clara segue instrucao do Tiaro.

### Lead pergunta "demora muito?"
"Em instantes. A equipe ja foi acionada. Te envio assim que chegar."

### Lead desiste durante a espera
Clara registra (loga) + escala humano para tentar reativar.

## Logging interno (audit)

Toda solicitacao de handoff financeiro deve ter:
- timestamp T+0
- timestamp T+30 (reforco)
- timestamp T+2h (escalacao)
- timestamp link_chegou
- timestamp repassado_paciente
- nome do humano que atendeu (Tiaro ou Liane)

## Source of truth

RC-16 na MEMORIA_CONSOLIDADA.
