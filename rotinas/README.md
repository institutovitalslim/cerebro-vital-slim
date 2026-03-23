# Rotinas — Automações Agendadas (Crons)

> Rotinas são tarefas que o agente executa automaticamente em horários definidos.
> Cada rotina referencia uma **skill** — a skill define *o que fazer*, a rotina define *quando fazer*.

---

## O que é uma rotina?

Uma rotina (ou cron) é uma instrução para o agente executar uma tarefa automaticamente, sem ninguém precisar pedir. Funciona como um despertador inteligente:

- **Horário definido** → o agente acorda
- **Executa a skill referenciada** → faz o trabalho
- **Entrega o resultado** → manda no WhatsApp, Telegram, ou onde estiver configurado

---

## Diferença entre Skill e Rotina

| Conceito | O que é | Exemplo |
|----------|---------|---------|
| **Skill** | Capacidade — o que o agente *sabe fazer* | "Sei gerar relatório de vendas" |
| **Rotina** | Execução — *quando* o agente faz | "Gero relatório todo dia às 8h" |

Uma skill pode existir sem rotina (executada sob demanda).
Toda rotina precisa de uma skill ou instrução clara.

---

## Rotinas Ativas

### 1. Relatório de Vendas Diário
- **Horário:** Todos os dias às 8h (BRT)
- **Skill:** `skills/relatorio-vendas/SKILL.md`
- **Canal de entrega:** WhatsApp — grupo da equipe
- **O que faz:** Lê a planilha de vendas, calcula faturamento do dia anterior, compara com média da semana, destaca produto mais vendido
- **Configuração do cron:**
  ```
  Prompt: "Execute a skill de relatório de vendas e envie o resultado no WhatsApp"
  Frequência: Diária às 8h BRT
  ```

### 2. Follow-up de Leads
- **Horário:** Todos os dias às 9h (BRT)
- **Skill:** `skills/follow-up-leads/SKILL.md`
- **Canal de entrega:** WhatsApp — responsável de vendas
- **O que faz:** Verifica planilha de leads, identifica quem está sem contato há 3+ dias, gera lista priorizada com próximos passos
- **Configuração do cron:**
  ```
  Prompt: "Execute a skill de follow-up de leads e envie o resultado no WhatsApp"
  Frequência: Diária às 9h BRT
  ```

### 3. Relatório de Rotinas (Monitoramento)
- **Horário:** Toda segunda-feira às 8h (BRT)
- **Skill:** `skills/relatorio-rotinas/SKILL.md`
- **Canal de entrega:** Telegram — canal de operações
- **O que faz:** Lista todas as rotinas ativas, mostra última execução, próxima execução e se houve erros
- **Configuração do cron:**
  ```
  Prompt: "Execute a skill de relatório de rotinas e envie o resultado no Telegram"
  Frequência: Semanal — segunda-feira às 8h BRT
  ```

---

## Como Criar uma Nova Rotina

1. **Tenha uma skill pronta** — se não existe, crie primeiro (use o `TEMPLATE-SKILL.md` ou peça ao Gerador de Skills)
2. **Defina a frequência** — diária? semanal? a cada hora?
3. **Defina o canal de entrega** — onde o resultado deve chegar (WhatsApp, Telegram, email)
4. **Configure o cron** no OpenClaw:
   ```
   /cron create "nome-da-rotina" --schedule "8h BRT diário" --prompt "Execute a skill X e envie no WhatsApp"
   ```
5. **Teste** — dispare manualmente para validar antes de automatizar
6. **Documente aqui** — adicione neste arquivo para referência da equipe

---

## Boas Práticas

- **Não exagerar nas rotinas** — comece com 2-3 e vá adicionando conforme necessidade
- **Horários estratégicos** — relatórios de manhã cedo, antes do expediente começar
- **Monitorar erros** — use o Relatório de Rotinas semanal para acompanhar se tudo está funcionando
- **Uma rotina = uma tarefa** — não misture "relatório de vendas + follow-up" numa só rotina

---

*Atualizado: março 2026*
