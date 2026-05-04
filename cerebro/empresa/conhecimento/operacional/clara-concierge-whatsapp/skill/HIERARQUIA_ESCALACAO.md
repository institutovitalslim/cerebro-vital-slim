# Hierarquia de Escalacao - Clara Concierge

## Equipe e quando contatar

| Pessoa | Funcao | WhatsApp | Quando Clara contata |
|--------|--------|----------|----------------------|
| **Tiaro** | CEO / financeiro | 5571986968887 | T+0 financeiro, casos VIP nominais, conflitos, leads que Liane perde |
| **Liane** | Enfermeira chefe | 5571991574827 | Backup financeiro T+2h, atendimento humano geral, mediacao paciente<->Tiaro |
| **Dra. Daniely** | Medica responsavel | "Amor" no WhatsApp Tiaro / Telegram Pacientes | NUNCA Clara contata diretamente. Recebe agenda diaria + questionarios passivos |

## Regra-chave

**Clara NUNCA contata Dra. Daniely diretamente.** Ela recebe informacoes via:
1. Agenda diaria automatica (WhatsApp pessoal "Amor")
2. Questionarios pre-consulta (Telegram topico "Pacientes")
3. Atendimento presencial

## RC-16 - Handoff financeiro (sequencial)

Quando lead aceita fechar agendamento e precisa de link de pagamento (InfinityPay):

```
T+0 minutos
└─ Clara avisa o paciente: "Vou solicitar o link..."
└─ Clara envia mensagem estruturada → Tiaro (5571986968887)

T+30 minutos (sem resposta de Tiaro)
└─ Clara reforca pro paciente: "Ja solicitei a equipe, em instantes te envio"

T+2 horas (Tiaro ainda nao respondeu)
└─ Clara escala automaticamente → Liane (5571991574827)

QUANDO LINK CHEGA (de Tiaro OU Liane):
└─ Clara repassa imediatamente ao paciente em bloco isolado
```

### Mensagem estruturada para Tiaro/Liane

```
🆕 PRÉ-CONSULTA — solicitar link

Paciente: [Nome completo]
WhatsApp: [+55 71 ...]
Valor: R$ 300
Parcelamento: cartão 2x sem juros
Desconto aplicado: [Sim/Não - R$ 100 OFF]
Total final consulta: [R$ 900 ou R$ 1.000]
Origem do lead: [ABRIL A / Instagram / Indicação X / etc]

Aguardando link pra repassar.
```

## RC-19 - Escalacao nao-financeira (paralela)

Diferente da financeira, em situacoes sensiveis/urgentes a escalacao e PARALELA:

```
Clara → Paciente (acolhimento imediato)
       ↓
       (simultaneamente)
       ↓
Clara → Tiaro (5571986968887) + Liane (5571991574827) - ambos juntos

Quem responder primeiro assume.
```

### Categorias detectaveis

- Crise emocional ("nao aguento mais", "querer desistir")
- Efeito colateral grave ("passei mal depois")
- Conflito ("vou processar", "péssimo atendimento")
- Violencia ("meu marido bate", "agressão")
- Pergunta clinica urgente ("posso tomar [med] hoje?")
- Pedido fora do escopo ("voces tem psicologo?")
- Erro operacional ("medicamento vencido", "boleto errado")

### Notificacao estruturada para equipe

```
🚨 ATENCAO — Paciente precisa de contato humano URGENTE

Paciente: [Nome]
WhatsApp: [+55 71 ...]
Etiqueta: [Lead / Agendou / Paciente / VIP]
Hora do alerta: [HH:MM]

Trecho da conversa que motivou a escalacao:
"[citacao literal do que o paciente disse]"

Categoria detectada: [crise emocional / efeito colateral / 
                      conflito / violencia / outro]

Quem responder primeiro assume e me avisa.
```

### Caso especial: ideacao suicida

Clara acolhe + escala paralelo + sugere CVV 188:

```
[BLOCO 1] [Nome], obrigada por compartilhar isso comigo. 💚
          Voce nao esta sozinho(a).

[BLOCO 2] Vou pedir que alguem da nossa equipe entre em contato 
contigo agora mesmo.

[BLOCO 3] Enquanto isso, se voce precisar de apoio imediato a 
qualquer momento, o CVV (Centro de Valorizacao da Vida) esta 
disponivel 24h pelo numero 188 ou em cvv.org.br.

[BLOCO 4] Em instantes alguem da nossa equipe fala com voce.
```

## Padroes humanos (manter)

### "Tiaro reativa quando Liane perde"
Quando Liane tenta sem sucesso reagendar lead, Tiaro entra pessoalmente:
"Ola [Nome]. Tudo bem com vc? Aqui e o Tiaro do Instituto Vital Slim. Estou passando aqui para reagendarmos o seu atendimento conosco para que vc possa ja iniciar este novo ano com um novo projeto de vida e saude. Vamos la?"

### "Liane medeia paciente <-> Tiaro"
Quando paciente pede algo a Tiaro: paciente fala com Liane -> Liane responde "vou passar a informacao para ele" -> Tiaro envia.
