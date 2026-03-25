# Bloco 10: Deep Dive — Bot de Suporte que Aprende — 🔥 3º AHA MOMENT

**Timing:** 10h50–11h25 (35 minutos)

---

## O que cobrir

- O loop de aprendizado: FAQ → dúvida nova → humano → consolidação → FAQ evolui
- Arquitetura do bot de suporte
- Demo: conversar com o bot ao vivo
- Demo: o bot escalando uma dúvida nova
- Demo: consolidar FAQ e o bot já sabe responder

---

## Demos e arquivos

| Demo | Arquivo/Path |
|------|-------------|
| FAQ atual | `areas/atendimento/contexto/faq.md` |
| Dúvidas novas | `areas/atendimento/contexto/duvidas.md` |
| Skill de consolidação | `areas/atendimento/skills/consolidar-faq.md` |
| Bot ao vivo | Telegram (grupo/conversa de demo) |

---

## Como fazer

**Passo 1 — O loop (5 min)**

Mostre o diagrama:
```
FAQ existente
    ↓
Usuário pergunta
    ↓
Bot responde (se souber) ── SE não souber ──→ Escala para humano
    ↓                                              ↓
Fim                                          Humano responde
                                                   ↓
                                           Registra em duvidas.md
                                                   ↓
                                           Skill consolida no FAQ
                                                   ↓
                                           Bot já sabe responder ✅
```

> "O bot não fica estagnado. A cada dúvida nova que o humano resolve, ele fica mais inteligente."

**Passo 2 — Estrutura de arquivos (5 min)**

Abra os 3 arquivos:

`faq.md` → "Aqui ficam as perguntas que o bot já sabe responder"  
`duvidas.md` → "Aqui caem as dúvidas que ele ainda não conhece"  
`consolidar-faq.md` → "Essa skill move as dúvidas respondidas para o FAQ"

**Passo 3 — Demo ao vivo: bot responde (8 min)**

Abra o Telegram. Faça uma pergunta que está no FAQ:
> "Qual o prazo de entrega?"

Bot responde corretamente com base no `faq.md`.

Faça uma pergunta que NÃO está no FAQ:
> "Vocês aceitam permuta?"

Bot reconhece que não sabe, escala:
> "Boa pergunta! Não tenho essa informação no momento. Vou registrar e um humano vai te responder em breve."

Mostre que a dúvida foi registrada em `duvidas.md` automaticamente.

**Passo 4 — Humano responde e consolida (10 min)**

No terminal, "responda" a dúvida — adicione a resposta em `duvidas.md`:
```markdown
## Dúvida: Vocês aceitam permuta?
Resposta: Sim, aceitamos permuta para contratos acima de R$5.000. Falar com comercial.
Status: respondida
```

Agora execute a skill de consolidação:
> "Execute a skill consolidar-faq"

Mostre o agente movendo a dúvida para `faq.md`.

Faça a mesma pergunta de novo no Telegram:
> "Vocês aceitam permuta?"

Bot responde corretamente agora. 

> "O bot aprendeu. Sem retreinar modelo. Sem atualizar código. Só editando um arquivo de texto."

**Passo 5 — Deixe o chat explodir (7 min)**

Pausa intencional. Leia reações. Responda perguntas rápidas.

---

## NÃO mostrar

- Configuração de webhook
- Integração com CRM externo
- Casos de edge com erros

---

## Checkpoint

✅ Loop de aprendizado explicado visualmente  
✅ Bot respondeu dúvida conhecida ao vivo  
✅ Bot escalou dúvida desconhecida ao vivo  
✅ Dúvida consolidada no FAQ e bot respondeu corretamente  
✅ AHA moment confirmado pelo chat  
→ Avançar para `dia2/11-proximos-30-dias.md`
