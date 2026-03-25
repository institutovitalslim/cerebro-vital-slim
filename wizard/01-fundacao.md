# Step 1: Fundação

> **Para o agente:** Leia este arquivo completamente antes de começar. Siga a sequência exata. Não pule etapas. Não invente respostas — pergunte e espere.

---

## Objetivo

Preencher os 3 arquivos base do contexto da empresa:
- `empresa/contexto/empresa.md`
- `empresa/contexto/equipe.md`
- `empresa/contexto/metricas.md`

---

## BLOCO A — Empresa

**Diga ao usuário:**
> "Vamos começar pela fundação. Preciso entender sua empresa para que o agente tenha contexto real. Pode responder em texto livre — eu organizo."

**Perguntas (fazer uma de cada vez, em sequência):**

1. "Qual o nome da sua empresa e o que ela faz em 1-2 frases?"
2. "Qual seu produto ou serviço principal? Como você cobra (mensalidade, projeto, produto)?"
3. "Quem é seu cliente ideal? Descreva o perfil."
4. "Qual seu principal diferencial frente aos concorrentes?"
5. "Em que momento a empresa está? (pré-receita / crescimento / escala)"

**Após coletar as respostas, criar o arquivo:**

```
empresa/contexto/empresa.md
```

Com o formato:
```markdown
# [Nome da Empresa]

## O que fazemos
[resposta da pergunta 1 e 2]

## Cliente ideal
[resposta da pergunta 3]

## Diferenciais
[resposta da pergunta 4]

## Momento atual
[resposta da pergunta 5]
```

---

## BLOCO B — Equipe

**Diga ao usuário:**
> "Agora a equipe. Quem trabalha com você?"

**Perguntas:**

1. "Liste as pessoas da equipe com nome e cargo (pode ser informal: 'João — cuida do suporte')."
2. "Tem alguém externo (freela, agência, parceiro)? Quem faz o quê?"

**Criar o arquivo:**

```
empresa/contexto/equipe.md
```

Com o formato:
```markdown
# Equipe

## Time interno
[lista: Nome — Cargo — Responsabilidades principais]

## Externos / Parceiros
[lista ou "nenhum por enquanto"]
```

---

## BLOCO C — Métricas

**Diga ao usuário:**
> "Por último: os números que importam. Não precisa ser preciso — uma estimativa já ajuda."

**Perguntas:**

1. "Qual sua receita mensal atual (MRR ou faturamento médio)?"
2. "Quantos clientes ativos você tem?"
3. "Qual seu principal canal de aquisição de leads?"
4. "Qual métrica você mais monitora no dia a dia?"

**Criar o arquivo:**

```
empresa/contexto/metricas.md
```

Com o formato:
```markdown
# Métricas-chave

## Receita
- MRR / Faturamento: [valor]
- Clientes ativos: [número]

## Aquisição
- Canal principal: [canal]
- [outras métricas mencionadas]

## O que monitoramos
[métrica mais acompanhada]

_Atualizado: [data de hoje]_
```

---

## Validação

Após criar os 3 arquivos, **mostre o conteúdo de cada um** ao usuário e pergunte:

> "Está correto? Quer ajustar alguma coisa antes de continuarmos?"

Se OK → diga: "Fundação completa! Agora vamos configurar a primeira área da empresa." → Leia `wizard/02-areas.md`.
