# Bloco 7: Multi-agente — De 1 Agente para um Sistema

**Timing:** 9h15–9h45 (30 minutos)

---

## O que cobrir

- A evolução: 1 agente → sistema de agentes
- Criar segundo agente ao vivo com SOUL.md diferente
- Demo: mesma pergunta → respostas diferentes
- Quando faz sentido ter múltiplos agentes

---

## Demos e arquivos

| Demo | Arquivo/Path |
|------|-------------|
| SOUL.md do agente principal | `SOUL.md` |
| SOUL.md do segundo agente | `agentes/suporte/SOUL.md` (criar ao vivo) |
| AGENTS.md atualizado | `AGENTS.md` |
| Demo: mesma pergunta | Telegram: dois grupos lado a lado |

---

## Como fazer

**Passo 1 — O conceito (5 min)**

> "Até agora, temos 1 agente que sabe tudo. Funciona para uma pessoa. Mas quando o time cresce, você precisa de especialização."

Exemplos reais:
- Agente do Bruno: estratégico, acesso total
- Agente da equipe de suporte: foco em atendimento, sem acesso ao financeiro
- Agente de vendas: foco no funil, scripts, CRM

> "Todos compartilham o mesmo repositório. Mas cada um tem uma 'personalidade' e um escopo diferente."

**Passo 2 — Criar segundo agente ao vivo (15 min)**

No terminal, crie a estrutura:
```bash
mkdir -p agentes/suporte
```

Peça ao agente:
> "Crie um SOUL.md para um agente de suporte ao cliente da [empresa demo]. Ele deve ser empático, focado em resolver dúvidas, escalar quando necessário, e NÃO ter acesso a dados financeiros."

Mostre o arquivo criado. Edite 1-2 pontos ao vivo para personalizar.

Atualize `AGENTS.md` com o novo agente e seu escopo.

**Passo 3 — Demo lado a lado (8 min)**

Mostre dois grupos do Telegram (ou dois terminais):

Faça a mesma pergunta nos dois agentes:
> "Como você pode me ajudar hoje?"

Mostre as respostas diferentes:
- Agente principal: resposta estratégica e ampla
- Agente de suporte: resposta focada em atendimento

> "Mesmo repo. Dois agentes. Duas experiências completamente diferentes."

**Passo 4 — Quando usar (2 min)**

> "Use multi-agente quando: time com funções diferentes, clientes que precisam de acesso limitado, ou áreas que não devem se misturar."

---

## NÃO mostrar

- Configuração de múltiplos servidores
- Integração com ferramentas externas de orquestração

---

## Checkpoint

✅ Conceito de multi-agente explicado  
✅ Segundo agente criado ao vivo  
✅ Demo lado a lado executada  
✅ AGENTS.md atualizado  
→ Avançar para `dia2/08-permissionamento.md`
