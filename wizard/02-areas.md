# Step 2: Primeira Área

> **Para o agente:** Este step configura a estrutura de pastas e contexto da primeira área. Siga o bloco correspondente à escolha do usuário.

---

## Pergunta inicial

**Diga ao usuário:**
> "Qual área quer configurar primeiro?"
> - **Vendas** — funil, CRM, metas de receita
> - **Marketing** — canais, conteúdo, campanhas
> - **Atendimento** — suporte, FAQ, SLA
> - **Operações** — processos internos, financeiro, time

Aguarde a resposta e siga o bloco correspondente abaixo.

---

## BLOCO VENDAS

**Perguntas:**
1. "Descreva seu funil de vendas — do lead até o fechamento."
2. "Quais ferramentas você usa? (CRM, planilha, WhatsApp...)"
3. "Qual sua meta de receita para os próximos 3 meses?"
4. "Qual etapa do funil você mais perde leads?"

**Criar estrutura:**
```
areas/vendas/contexto/geral.md   ← preencher com as respostas
areas/vendas/rotinas/            ← pasta vazia por agora
areas/vendas/skills/             ← pasta vazia por agora
```

**Conteúdo de `areas/vendas/contexto/geral.md`:**
```markdown
# Vendas — Contexto

## Funil
[etapas descritas pelo usuário]

## Ferramentas
[ferramentas listadas]

## Metas
[meta de receita]

## Principal gargalo
[onde perde mais leads]
```

---

## BLOCO MARKETING

**Perguntas:**
1. "Quais canais você usa? (Instagram, YouTube, email, tráfego pago...)"
2. "Qual sua estratégia principal? (conteúdo orgânico, ads, parceria...)"
3. "Como você descreve o tom de voz da sua marca? (ex: direto, educativo, descontraído)"
4. "O que está funcionando melhor agora?"

**Criar estrutura:**
```
areas/marketing/contexto/geral.md
areas/marketing/rotinas/
areas/marketing/skills/
```

---

## BLOCO ATENDIMENTO

**Perguntas:**
1. "Por onde chegam as dúvidas dos clientes? (WhatsApp, email, chat...)"
2. "Qual seu tempo de resposta esperado (SLA)?"
3. "Quais as 5 dúvidas mais comuns que você recebe?"
4. "Tem alguém dedicado ao suporte ou é você mesmo?"

**Criar estrutura:**
```
areas/atendimento/contexto/geral.md
areas/atendimento/rotinas/
areas/atendimento/skills/
```

**Extra:** Se o usuário tiver um FAQ básico, criar também:
```
areas/atendimento/contexto/faq.md
```

---

## BLOCO OPERAÇÕES

**Perguntas:**
1. "Quais são os processos que mais tomam tempo da equipe?"
2. "Tem algum processo que depende só de você hoje?"
3. "Como você controla financeiro? (planilha, sistema, nada...)"
4. "Qual gargalo operacional você mais quer resolver?"

**Criar estrutura:**
```
areas/operacoes/contexto/geral.md
areas/operacoes/rotinas/
areas/operacoes/skills/
```

---

## Validação

Mostre a estrutura de pastas criada com `tree areas/` (ou liste os arquivos) e diga:

> "Primeira área configurada! Aqui está o que criamos: [mostrar estrutura]. Tudo certo?"

Se OK → diga: "Agora vamos criar as primeiras skills." → Leia `wizard/03-skills.md`.
