# Template: Escalacao RC-19 (situacao sensivel/urgente)

Para situacoes onde Clara NAO pode resolver sozinha. Diferente do handoff financeiro (sequencial), aqui a escalacao e PARALELA.

## Categorias detectaveis

| Categoria | Exemplo |
|-----------|---------|
| Crise emocional | "nao aguento mais", "sem esperanca" |
| Efeito colateral | "passei mal depois da medicacao", "alergia" |
| Conflito | "vou processar", "Procon" |
| Violencia | "meu marido bate", "agressao" |
| Pergunta clinica urgente | "posso tomar Mounjaro hoje?" |
| Pedido fora escopo | "voces tem psicologo? cardiologista?" |
| Erro operacional | "medicamento vencido", "boleto errado" |

## Fluxo

```
Clara → Paciente (acolhimento imediato, em blocos)
       ↓
       (simultaneamente)
       ↓
Clara → Tiaro + Liane (notificacao paralela via WhatsApp)

Quem responder primeiro assume.
```

## Acolhimento ao paciente (genericо)

```
[BLOCO 1]
[Nome], obrigada por compartilhar isso comigo. 💚

[delay 2s]

[BLOCO 2]
Vou pedir que alguem da nossa equipe entre em contato 
contigo agora mesmo pra te ajudar com cuidado.

[delay 1.5s]

[BLOCO 3]
Voce nao esta sozinho(a). Em instantes alguem fala com voce 
por aqui.
```

## Acolhimento por categoria (variantes)

### Efeito colateral
```
[BLOCO 1]
[Nome], obrigada por me avisar imediatamente. 💚

[BLOCO 2]
Vou pedir que a Dra. Daniely ou a Liane entre em contato 
contigo agora mesmo pra te orientar com seguranca.

[BLOCO 3]
Por favor, observe se [sintoma] piora ou se aparecer algo novo. 
Em instantes alguem fala com voce.
```

### Conflito/Reclamacao
```
[BLOCO 1]
[Nome], lamento muito que voce tenha passado por isso.

[BLOCO 2]
Vou avisar imediatamente o Tiaro e a Liane para que possam 
falar diretamente com voce e resolver isso da melhor forma.

[BLOCO 3]
Em instantes alguem da equipe entra em contato.
```

### Pedido fora do escopo
```
[BLOCO 1]
[Nome], obrigada por buscar o Vital Slim para isso.

[BLOCO 2]
[Especialidade pedida] nao e algo que oferecemos diretamente, 
mas vou pedir pra equipe te orientar com algumas indicacoes.

[BLOCO 3]
Em instantes alguem fala com voce.
```

### Erro operacional (boleto, medicamento, agenda)
```
[BLOCO 1]
[Nome], que situacao chata. Lamento muito.

[BLOCO 2]
Vou acionar agora a equipe para resolver isso o mais rapido 
possivel.

[BLOCO 3]
Em instantes alguem fala com voce.
```

## Notificacao paralela para Tiaro + Liane (estruturada)

Destinatarios: 5571986968887 (Tiaro) + 5571991574827 (Liane), simultaneamente.

```
🚨 ATENCAO — Paciente precisa de contato humano URGENTE

Paciente: [Nome]
WhatsApp: [+55 71 ...]
Etiqueta: [Lead / Agendou / Paciente / VIP]
Hora do alerta: [HH:MM]

Trecho da conversa que motivou a escalacao:
"[citacao literal do que o paciente disse]"

Categoria detectada: [crise emocional / efeito colateral / 
                      conflito / violencia / pergunta clinica / 
                      fora do escopo / erro operacional]

Acolhimento ja enviado por Clara: [resumo curto]

Quem responder primeiro assume e me avisa.
```

## Logging interno (audit)

- timestamp da deteccao
- categoria identificada
- texto literal do paciente
- timestamp da notificacao a Tiaro + Liane
- quem respondeu primeiro
- timestamp da resolucao

## Casos especiais

### Risco real (ideacao suicida, autoagressao, violencia iminente)
Ver: `templates/escalacao-rc19-risco.md`

### Paciente VIP nominal
Notificar PRIMEIRO Tiaro (canal direto). Apos 5min sem resposta, escalar Liane.

### Lead em fechamento que pediu link de pagamento
Aplicar RC-16 (sequencial Tiaro → Liane), nao RC-19.

## NAO fazer

❌ Tentar resolver sozinha caso clinico/emocional
❌ Minimizar o problema do paciente
❌ Oferecer pitch comercial em momento sensivel
❌ Ignorar e seguir com fluxo normal

## Source of truth

RC-19 na MEMORIA_CONSOLIDADA. HIERARQUIA_ESCALACAO.md.
