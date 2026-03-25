# Step 4: Configurar Crons (Rotinas Automáticas)

> **Para o agente:** Crons fazem o agente executar skills automaticamente, sem o usuário pedir. Configure 2 crons: um baseado na skill criada no Step 3, e o heartbeat padrão.

---

## Explicação para o usuário

**Diga:**
> "Até agora criamos as skills. Mas elas ainda precisam que você peça."
>
> "Com crons, o agente faz isso **sozinho** — todo dia, toda semana, no horário que você definir. Você só recebe o resultado."

---

## Cron #1 — Baseado na Skill do Step Anterior

**Pergunte:**
> "A [nome da skill criada] — qual o melhor horário para você receber? De manhã para começar o dia? Segunda-feira para planejar a semana?"

Sugestões se o usuário não souber:
- Relatório semanal → Segunda às 8h
- Relatório diário → Todo dia às 7h30
- Análise de leads → Sexta às 17h

**Após definir o horário**, crie o arquivo de rotina:

```
areas/[area]/rotinas/[nome-da-rotina].md
```

Com o conteúdo:
```markdown
# Rotina: [Nome]

## Schedule
[Ex: toda segunda-feira às 08:00]
Cron: `0 8 * * 1`

## O que faz
Executa a skill `[nome-da-skill]` e envia o resultado via Telegram.

## Instruções para o agente
1. Ler `areas/[area]/skills/[skill].md`
2. Coletar os dados necessários
3. Executar o processo descrito
4. Enviar resultado formatado no canal configurado
```

**Diga ao usuário como adicionar no OpenClaw:**
> "Para ativar este cron no OpenClaw, adicione isso no seu `openclaw.json` na seção de crons, apontando para este arquivo de rotina."

---

## Cron #2 — Heartbeat

**Diga:**
> "Tem um segundo cron que recomendo para todo mundo: o heartbeat. É um check diário que confirma que o agente está vivo e funcionando."

Crie:
```
rotinas/heartbeat.md
```

Com conteúdo:
```markdown
# Rotina: Heartbeat

## Schedule
Todo dia às 09:00
Cron: `0 9 * * *`

## O que faz
Verifica se o agente está operacional e envia confirmação.

## Instruções para o agente
1. Verificar conectividade
2. Checar se há pendências em `empresa/pendencias.md` (se existir)
3. Enviar mensagem curta: "✅ [Nome do Agente] online — [data]"
```

---

## Validação

Liste os crons configurados:
```
✅ [Nome da rotina] → [dia/horário]
✅ Heartbeat → todo dia às 9h
```

**Diga:**
> "Pronto. O agente vai rodar sozinho a partir de agora nesses horários. Você não precisa lembrar de pedir."

Pergunte: "Quer adicionar mais alguma rotina? Ou continuamos?"

Se quiser continuar → Leia `wizard/05-multi-agente.md`.
