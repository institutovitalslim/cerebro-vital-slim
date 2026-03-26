# Permissionamento — Pessoas & Agentes

> Quem pode o quê, tanto para pessoas quanto para agentes.

---

## Visão Geral

O sistema tem duas camadas de permissão:

1. **Pessoas** → quais agentes podem acionar + quais dados podem pedir
2. **Agentes** → quais pastas do cérebro acessam + qual tópico operam

```
┌─────────────────────────────────────────────────┐
│                    PESSOAS                       │
│  Ricardo (tudo), Felipe (tudo), André (tudo)     │
│  Camila (marketing), Juliana (vendas+atend.)     │
├─────────────────────────────────────────────────┤
│                    AGENTES                       │
│  Assistente Geral  →  empresa/ + todas as áreas │
│  Marcos (Vendas)   →  empresa/ + vendas/        │
│  Beatriz (Mkt)     →  empresa/ + marketing/     │
│  Clara (Atend.)    →  empresa/ + atendimento/   │
├─────────────────────────────────────────────────┤
│                    CÉREBRO                       │
│  empresa/ │ areas/ │ dados/ │ agentes/           │
└─────────────────────────────────────────────────┘
```

---

## Permissões de Pessoas

### Quem aciona qual agente

| Pessoa | Papel | Agentes que aciona | Pode ver dados de |
|--------|-------|-------------------|-------------------|
| Ricardo Mendes | Fundador | Todos | Tudo |
| Felipe Santos | CEO | Todos | Tudo |
| André Costa | COO | Todos | Tudo |
| Camila | Social media | Assistente Geral, Beatriz (Mkt) | Marketing, métricas gerais |
| Juliana | Suporte + vendas | Assistente Geral, Marcos (Vendas), Clara (Atend.) | Vendas, atendimento, métricas gerais |
| Lucas / Patrícia | Tráfego pago | Beatriz (Mkt) | Marketing (ads), métricas gerais |
| Marcos (designer) | Freelancer | Beatriz (Mkt) | Marketing (briefings), métricas gerais |

### O que cada nível de acesso significa

**Acesso total (liderança):**
- Pode pedir qualquer relatório, de qualquer área
- Pode ver dados financeiros, pipeline de leads, métricas de todas as áreas
- Pode alterar configurações de agentes e permissões
- `allowFrom: ["ricardo", "felipe", "andre"]`

**Acesso à área (equipe):**
- Pode pedir relatórios e dados da sua área
- Pode interagir com o agente da sua área
- Pode pedir métricas gerais da empresa (sem financeiro detalhado)
- NÃO pode ver pipeline de leads de vendas (se for de marketing)
- NÃO pode alterar configurações de agentes

### Configuração no OpenClaw

```json
{
  "agents": {
    "defaults": {
      "allowFrom": {
        "users": [
          { "id": "ricardo_id", "name": "Ricardo", "level": "admin" },
          { "id": "felipe_id", "name": "Felipe", "level": "admin" },
          { "id": "andre_id", "name": "André", "level": "admin" },
          { "id": "camila_id", "name": "Camila", "level": "area", "areas": ["marketing"] },
          { "id": "juliana_id", "name": "Juliana", "level": "area", "areas": ["vendas", "atendimento"] }
        ]
      }
    }
  }
}
```

---

## Permissões de Agentes

### Qual agente acessa o quê

#### Agentes internos (falam com o time)

| Agente | Mentes de referência | Acesso ao cérebro | Canal |
|--------|---------------------|-------------------|-------|
| Agente Geral | Generalista | `empresa/` + todas as `areas/` + `dados/` + `seguranca/` | Telegram (tópicos internos) |
| Agente de Vendas | Hormozi, Belfort, Ziglar | `empresa/` + `areas/vendas/` + `dados/` | Telegram (💰 Vendas) |
| Agente de Marketing | Brunson, Hormozi, Halbert, Schwartz | `empresa/` + `areas/marketing/` | Telegram (📢 Marketing) |
| Agente de Atendimento | Hsieh (Zappos), Hyken, Disney | `empresa/` + `areas/atendimento/` | Telegram (🎧 Atendimento) |

#### Agentes externos (falam com clientes)

| Agente | Mentes de referência | Acesso ao cérebro | Canal |
|--------|---------------------|-------------------|-------|
| Bot Leads | Chet Holmes, Chris Voss, Ziglar | `empresa/contexto/` + `areas/vendas/skills/` + `dados/leads.csv` (write) | WhatsApp |

> ⚠️ **Bot Leads tem acesso MÍNIMO.** Não vê métricas, decisões, learnings, marketing, ou atendimento interno. Só sabe o necessário pra atender o lead: produtos, preços e processo de qualificação.

### Por que o Assistente Geral tem acesso total?

O Assistente Geral é o "gerente" dos outros agentes. Ele:
- Responde perguntas cross-área (que envolvem mais de uma área)
- Roda o heartbeat (precisa ver tudo pra checar saúde)
- Gerencia o repositório (sync, consolidação de memória)
- Faz o relatório de rotinas (monitora todos os crons)
- É o fallback quando um agente de área não está configurado

### Escopo limitado na prática

O agente de vendas (Marcos), por exemplo:
- ✅ Pode ler `empresa/contexto/empresa.md` (precisa saber os produtos)
- ✅ Pode ler `empresa/contexto/equipe.md` (precisa saber quem é quem)
- ✅ Pode ler `areas/vendas/` inteiro (é a área dele)
- ✅ Pode ler e escrever `dados/vendas.csv` e `dados/leads.csv`
- ❌ NÃO lê `areas/marketing/` (não é da conta dele)
- ❌ NÃO lê `areas/atendimento/` (mesmo que seja sobre um cliente)
- ❌ NÃO lê `seguranca/permissoes.md` (não precisa saber as regras globais)

Se um agente de área precisa de informação de outra área, ele pede ao Assistente Geral.

---

## Matriz Completa: Pessoa × Agente × Área

### Agentes internos (time)

| Pessoa | Agente Geral | Ag. Vendas | Ag. Marketing | Ag. Atendimento |
|--------|:---:|:---:|:---:|:---:|
| Ricardo (Fundador) | ✅ | ✅ | ✅ | ✅ |
| Felipe (CEO) | ✅ | ✅ | ✅ | ✅ |
| André (COO) | ✅ | ✅ | ✅ | ✅ |
| Camila (Social) | ✅ | ❌ | ✅ | ❌ |
| Juliana (Suporte) | ✅ | ✅ | ❌ | ✅ |
| Lucas (Tráfego) | ❌ | ❌ | ✅ | ❌ |
| Marcos (Design) | ❌ | ❌ | ✅ | ❌ |

### Agente externo (Bot Leads)

| Quem fala | Acesso |
|-----------|--------|
| Qualquer lead (WhatsApp) | Bot Leads |

O Bot Leads é **aberto** (`allowFrom: *`) — qualquer pessoa que mande mensagem no WhatsApp da empresa é atendida. Não há restrição de quem pode falar, porque o público é externo.

---

## Mapeamento de Agentes — Tópicos ou Grupos

Existem dois cenários para mapear agentes no Telegram. Escolha o que faz sentido pra sua empresa:

### Cenário A: Um grupo com tópicos (fórum)

Ideal para equipes pequenas (3-10 pessoas). Um único grupo, cada área é um tópico.

```
Grupo: Imersão OpenClaw nos Negócios
├── General              → Assistente Operacional (Agente Geral)
├── 📢 Marketing         → Assistente de Marketing
├── 💰 Vendas            → Agente de Vendas
├── 🎧 Atendimento       → Agente de Atendimento
├── ⚙️ Operações         → Assistente Operacional (Agente Geral)
├── 🤖 Debug             → (testes e comandos)
└── [topic 8]            → Assistente de Marketing
```

| Agente | Tópico | topic_id | Quem fala ali |
|--------|--------|----------|---------------|
| Assistente Operacional (Agente Geral) | General | 1 | Liderança, qualquer um |
| Assistente de Marketing | 📢 Marketing (topic 8) | 8 | Camila, Lucas, liderança |
| Agente de Vendas | 💰 Vendas | a criar | Juliana, André, liderança |
| Agente de Atendimento | 🎧 Atendimento | a criar | Juliana, André, liderança |
| Assistente Operacional (Agente Geral) | ⚙️ Operações | a criar* | André, liderança |

> *Tópico ⚙️ Operações ainda não criado — bot precisa de permissão "Gerenciar tópicos" no grupo.

### ⚠️ Policy de Responsabilidade por Tópico

**Regra inviolável:** cada agente responde SOMENTE no(s) tópico(s) que são seus. Nunca cruzar tópicos.

| Agente | Responde em | NÃO responde em |
|--------|-------------|-----------------|
| Assistente Operacional | General (1), ⚙️ Operações (a criar) | Marketing (8), Vendas, Atendimento |
| Assistente de Marketing | 📢 Marketing (topic 8) | General e qualquer outro |
| Agente de Vendas | 💰 Vendas | Qualquer outro |
| Agente de Atendimento | 🎧 Atendimento | Qualquer outro |

> **Decisão registrada (2026-03-26, Cayo Syllos):** O tópico 8 (Marketing) é de responsabilidade exclusiva do Assistente de Marketing. O Assistente Operacional responde somente no General e no tópico Operações (quando criado). Cada agente não deve responder fora do seu tópico.

**Vantagem:** tudo num lugar só, fácil de gerenciar.
**Desvantagem:** qualquer pessoa do grupo pode ver todos os tópicos (permissão é por agente, não por visualização).

### Cenário B: Grupos separados por área

Ideal para equipes maiores (10+ pessoas) ou quando a separação de dados é crítica.

```
Grupo: Vendas           → Agente de Vendas
Grupo: Marketing         → Agente de Marketing
Grupo: Atendimento       → Agente de Atendimento
Grupo: Liderança         → Agente Geral
```

| Agente | Grupo | Quem participa |
|--------|-------|----------------|
| Agente de Vendas | Vendas | Juliana, André, Felipe, Ricardo |
| Agente de Marketing | Marketing | Camila, Lucas, Patrícia, Marcos, Ricardo |
| Agente de Atendimento | Atendimento | Juliana, André, Ricardo |
| Agente Geral | Liderança | Ricardo, Felipe, André |

**Vantagem:** separação real — quem não está no grupo, não vê nada. Mais seguro.
**Desvantagem:** mais grupos pra gerenciar, mais agentes pra configurar.

### Qual escolher?

| Critério | Cenário A (tópicos) | Cenário B (grupos) |
|----------|:---:|:---:|
| Equipe pequena (< 10) | ✅ | ➖ |
| Equipe grande (10+) | ➖ | ✅ |
| Dados sensíveis por área | ➖ | ✅ |
| Simplicidade de setup | ✅ | ➖ |
| Separação real de acesso | ❌ | ✅ |
| Custo (agentes rodando) | ✅ Menor | ❌ Maior |

> 💡 **Recomendação:** comece com Cenário A (tópicos). Quando a equipe crescer ou dados sensíveis justificarem, migre para Cenário B.

---

## Modo Ask (Ações Sensíveis)

Independente do nível de acesso, algumas ações SEMPRE pedem confirmação:

| Ação | Quem pode aprovar |
|------|-------------------|
| Enviar email para cliente | Ricardo, Felipe, André |
| Publicar em rede social | Ricardo, Camila |
| Aprovar reembolso > R$ 200 | André |
| Alterar preço de produto | Ricardo, Felipe |
| Criar campanha de ads | Ricardo, Lucas/Patrícia |
| Alterar permissões de agentes | Ricardo, Felipe |

Configuração:
```
Modo: ask (pede confirmação antes de executar)
Ações em modo ask: envio de email, post público, reembolso, alteração de preço
```

---

## Evolução: Quando Adicionar Mais Agentes

A estrutura de permissionamento é escalável:

1. **Fase 1 (início):** Só o Assistente Geral → acesso total, uma pessoa configura
2. **Fase 2 (equipe de 5+):** Adicionar 1-2 agentes de área → menos gargalo
3. **Fase 3 (equipe de 10+):** Agente por área + sub-agentes especializados
   - Ex: Beatriz (Mkt) pode spawnar sub-agente só pra copywriting
   - Ex: Marcos (Vendas) pode spawnar sub-agente só pra qualificação de leads

Para adicionar um novo agente:
1. Criar pasta em `agentes/[nome-do-agente]/`
2. Criar `SOUL.md` com a persona especialista
3. Criar `AGENTS.md` com escopo e permissões
4. Atualizar este arquivo com as novas permissões
5. Configurar no OpenClaw apontando pro tópico correto

---

*Atualizado: março 2026*
