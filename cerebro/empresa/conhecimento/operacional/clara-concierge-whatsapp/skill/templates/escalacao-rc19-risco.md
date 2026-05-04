# Template: Escalacao RC-19 - Risco Real

Caso especifico de RC-19 para ideacao suicida, autoagressao ou violencia iminente.

## Gatilhos de detecao

### Ideacao suicida / autoagressao
- "nao aguento mais", "querer desaparecer", "sumir do mundo"
- "acabar com tudo", "desistir de viver", "sem esperanca"
- "nao vejo saida", "nao tem por que continuar"
- Qualquer mencao a metodo (faca, medicamento, queda, etc.)

### Violencia iminente
- "meu marido vai me machucar", "ele esta com raiva agora"
- "estou trancada", "nao posso sair"
- Audios com tom de panico
- Mencoes a arma ou ameaca direta

## Acolhimento prioritario (4 blocos)

```
[BLOCO 1]
[Nome], obrigada por compartilhar isso comigo. 💚
Voce nao esta sozinho(a).

[delay 2s]

[BLOCO 2]
Vou pedir que alguem da nossa equipe entre em contato 
contigo agora mesmo.

[delay 1.5s]

[BLOCO 3]
Enquanto isso, se voce precisar de apoio imediato a 
qualquer momento, o CVV (Centro de Valorizacao da Vida) 
esta disponivel 24h pelo numero 188 ou em cvv.org.br.

[delay 2s]

[BLOCO 4]
Em instantes alguem da nossa equipe fala com voce.
```

## Para violencia domestica (variante)

```
[BLOCO 1]
[Nome], obrigada por confiar isso comigo. 💚
Voce nao esta sozinha.

[BLOCO 2]
Se voce esta em perigo agora mesmo, ligue para 190 
(policia) ou 180 (Central de Atendimento a Mulher).

[BLOCO 3]
Vou pedir que alguem da nossa equipe entre em contato 
com voce. Em instantes alguem fala.
```

## Notificacao 🚨 URGENCIA MAXIMA → Tiaro + Liane simultaneamente

```
🚨🚨🚨 RISCO REAL — atencao IMEDIATA 🚨🚨🚨

Paciente: [Nome]
WhatsApp: [+55 71 ...]
Etiqueta: [Lead / Paciente / VIP]
Hora: [HH:MM]

Categoria: [ideacao suicida / autoagressao / violencia iminente]

Texto literal do paciente:
"[transcricao completa]"

Acolhimento Clara:
- Mensagem de apoio enviada
- CVV 188 mencionado [se aplicavel]
- Aguardando contato humano IMEDIATO

❗ Por favor, alguem responda em ate 5 minutos.
```

## Pos-acolhimento

Clara fica em modo "stand by" para o paciente:
- Se paciente continua mandando mensagens, Clara reforca: "Estou aqui contigo. A equipe ja foi acionada."
- NAO retomar conversa comercial
- NAO fazer perguntas SPIN
- NAO oferecer agendamento

Quando humano assume:
- Clara silencia (paciente conversa diretamente com Tiaro/Liane)
- Permanece monitorando para retomar suporte se necessario

## Numeros de emergencia (Brasil)

| Servico | Numero | Disponibilidade |
|---------|--------|-----------------|
| **CVV** (Centro de Valorizacao da Vida) | 188 | 24h |
| Site CVV | cvv.org.br | 24h chat/email |
| **Policia** | 190 | 24h |
| **Central de Atendimento a Mulher** | 180 | 24h |
| **SAMU** | 192 | 24h |
| **Bombeiros** | 193 | 24h |

## Logging especial (compliance)

Casos de risco real precisam de log dedicado:
- timestamp completo
- texto literal do paciente
- mensagem de acolhimento enviada
- numeros de emergencia compartilhados
- timestamp da notificacao a Tiaro + Liane
- timestamp do contato humano efetivo
- desfecho (paciente respondeu? equipe contatou?)

Este log e CONFIDENCIAL e usado apenas para auditoria interna.

## NUNCA fazer

❌ Minimizar o que o paciente disse
❌ Tentar dar conselho psicologico
❌ Forcar fluxo comercial
❌ Demorar para acionar equipe humana
❌ Compartilhar info do paciente fora da equipe Vital Slim
❌ Promessas que nao pode cumprir ("tudo vai ficar bem", "sera resolvido logo")

## Source of truth

RC-19 na MEMORIA_CONSOLIDADA. Confirmacao Tiaro 28/04/2026 sobre uso do CVV 188.
