# Step 5: Multi-agente (Opcional)

> **Para o agente:** Este step só é relevante se o usuário tem um time. Comece com a pergunta de triagem. Se a resposta for "não", pule direto para `wizard/06-validacao.md`.

---

## Pergunta de triagem

**Pergunte:**
> "Tem mais alguém no time que vai usar o agente? (sócio, funcionário, colaborador)"

**Se NÃO** → Diga: "Sem problema — você pode configurar isso depois. Vamos para a validação final." → Leia `wizard/06-validacao.md`.

**Se SIM** → Continue abaixo.

---

## Explicação do conceito

**Diga:**
> "Com múltiplos agentes, cada pessoa pode ter seu próprio agente com personalidade e escopo diferente — mas todos compartilham o mesmo cérebro (o repositório)."
>
> "Exemplo: você tem um agente estratégico e sua equipe de suporte tem um agente focado só em atendimento — sem acesso aos dados financeiros."

---

## Coletando informações

**Perguntas:**
1. "Quem vai ter acesso ao agente? Liste os nomes e cargos."
2. "O agente deles deve ter acesso a tudo, ou só a uma área específica?"
3. "Cada pessoa vai usar pelo Telegram? Qual o ID ou @ de cada uma?"

---

## Criando o segundo agente

**Crie o arquivo SOUL.md específico:**

```
agentes/[nome-do-agente]/SOUL.md
```

Exemplo para agente de suporte:
```markdown
# SOUL.md — [Nome do Agente]

## Quem sou
Sou o assistente de suporte da [Empresa]. Ajudo a equipe a responder dúvidas de clientes com agilidade e consistência.

## Foco
Tenho acesso apenas à área de atendimento: FAQ, histórico de tickets e scripts de resposta.

## Tom
Profissional, empático, direto. Nunca impaciente.

## O que não faço
- Não acesso dados financeiros
- Não tomo decisões estratégicas
- Escalo para o [Nome do responsável] quando necessário
```

---

## Configurando AGENTS.md

Crie ou atualize `AGENTS.md` na raiz do repo:

```markdown
# AGENTS.md

## Agente Principal — [Seu Nome]
- Acesso: total
- Telegram ID: [seu ID]
- Escopo: empresa completa

## [Nome do Agente Secundário]
- Acesso: areas/[area específica]
- Telegram ID: [ID da pessoa]
- Escopo: apenas [área]
- SOUL: agentes/[nome]/SOUL.md
```

---

## Duas arquiteturas — explicar ao usuário

**Opção A — Grupos separados (mais seguro):**
> Cada agente tem seu próprio grupo no Telegram. Informações não vazam entre grupos.

**Opção B — Tópicos no mesmo grupo (mais prático):**
> Um grupo com tópicos por agente. Mais fácil de gerenciar, mas precisa de permissionamento correto.

**Pergunte:** "Qual faz mais sentido para o seu caso?"

---

## Validação

Mostre o que foi criado:
```
✅ SOUL.md do agente secundário
✅ AGENTS.md atualizado com escopo restrito
✅ Arquitetura escolhida: [A ou B]
```

→ Leia `wizard/06-validacao.md`.
