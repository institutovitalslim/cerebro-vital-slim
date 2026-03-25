# Step 3: Primeiras Skills

> **Para o agente:** Skills são mini-programas que o agente executa. Você vai criar 2-3 skills baseadas nas tarefas reais do usuário. Use o template abaixo para cada uma.

---

## Explicação para o usuário

**Diga:**
> "Uma skill é como uma receita: tem uma entrada (o que você fornece), um processo (o que o agente faz) e uma saída (o que você recebe)."
>
> "Exemplo: Skill de relatório semanal → entrada: dados da semana → processo: analisa e formata → saída: relatório pronto no Telegram."

---

## Identificando a primeira skill

**Perguntas (uma de cada vez):**

1. "Qual tarefa repetitiva você faz toda semana — algo que cansa mas você faz do mesmo jeito?"
2. "Quanto tempo isso leva?"
3. "Qual seria o resultado ideal se o agente fizesse isso por você?"

**Anote a tarefa.** Ela vira a Skill #1.

---

## Template de skill

Cada skill fica em `areas/[area]/skills/[nome-da-skill].md`:

```markdown
# Skill: [Nome]

## Objetivo
[O que essa skill faz em 1 frase]

## Quando executar
[Gatilho: "toda segunda às 9h" / "quando solicitado" / "ao receber dados X"]

## Input necessário
- [O que o agente precisa para executar]
- [Fontes de dados, se houver]

## Processo
1. [Passo 1]
2. [Passo 2]
3. [Passo 3]

## Output esperado
[Formato e destino do resultado: "mensagem no Telegram" / "arquivo em X"]

## Exemplo de saída
[Exemplo real ou fictício de como fica o resultado]
```

---

## Criando as skills

**Skill #1:** Baseada na tarefa identificada acima. Crie o arquivo e mostre para o usuário.

**Pergunta para Skill #2:**
> "Tem outra tarefa — talvez de análise ou acompanhamento — que você gostaria de automatizar?"

**Skill #2:** Criar com o mesmo template.

**Pergunta para Skill #3 (opcional):**
> "E comunicação? Você manda relatórios ou atualizações para clientes ou para o time regularmente?"

---

## Transição natural

Após criar 2 skills, pergunte:

> "E se essas skills rodassem **sozinhas**, sem você pedir — toda semana, no horário certo?"

Aguarde a reação. Depois diga:
> "É exatamente isso que vamos configurar agora."

→ Leia `wizard/04-rotinas.md`.

---

## Validação

Antes de avançar, liste as skills criadas:
```
areas/[area]/skills/
├── [skill-1].md  ✅
├── [skill-2].md  ✅
```

Pergunte: "Essas skills refletem bem o que você precisa? Quer ajustar alguma coisa?"
