# Bloco 5: Rotinas Automáticas (Crons)

**Timing:** 11h15–11h35 (20 minutos)

---

## O que cobrir

- O que é um cron e por que importa
- Configurar um cron ao vivo baseado na skill do bloco anterior
- Mostrar o heartbeat como segundo cron
- Demonstrar o agente rodando sem ser solicitado

---

## Demos e arquivos

| Demo | Arquivo/Path |
|------|-------------|
| Arquivo de rotina | `areas/vendas/rotinas/relatorio-semanal.md` |
| Configuração de cron | `openclaw.json` (seção crons) |
| Heartbeat | `rotinas/heartbeat.md` |

---

## Como fazer

**Passo 1 — O conceito (5 min)**

> "Tudo que fizemos até agora, você precisou pedir. Agora vamos mudar isso."

Analogia: "É como programar o agente para entrar no trabalho todo dia às 8h, checar o que tem pra fazer, e te mandar o relatório. Sem você lembrar de pedir."

**Passo 2 — Criar rotina ao vivo (8 min)**

No terminal:
1. Abra `areas/vendas/rotinas/` (pasta vazia)
2. Crie `relatorio-semanal.md` com o agente:
   > "Crie uma rotina para executar a skill de relatório toda segunda-feira às 8h e enviar o resultado no Telegram"
3. Mostre o arquivo criado
4. Adicione o cron ao `openclaw.json`

Mostre o formato cron:
```
0 8 * * 1   ← segunda às 8h
0 7 * * *   ← todo dia às 7h
0 9 * * 5   ← sexta às 9h
```

**Passo 3 — Heartbeat (5 min)**

> "Tem um cron que recomendo pra todo mundo: o heartbeat. Todo dia de manhã, o agente acorda, checa se está tudo ok e manda uma mensagem confirmando que está vivo."

Mostre `rotinas/heartbeat.md`. Se possível, acione manualmente para mostrar a mensagem no Telegram.

**Passo 4 — Fechar o ponto (2 min)**

> "A partir de hoje, você não precisa mais lembrar de pedir esse relatório. Ele vai aparecer na segunda de manhã. Na sua caixa. Pronto."

---

## NÃO mostrar

- Sintaxe complexa de cron expressions
- Configuração de timezone no servidor
- Múltiplos crons encadeados

---

## Checkpoint

✅ Arquivo de rotina criado ao vivo  
✅ Cron adicionado ao openclaw.json  
✅ Heartbeat explicado e mostrado  
→ Avançar para `dia1/06-seguranca.md`
