# Imersão OpenClaw nos Negócios

**📅 28-29/03/2026 · 2 dias · 3h cada**

Workshop intensivo para PMEs implementarem agentes de IA nos seus negócios usando OpenClaw. Em dois dias, os participantes saem com um Cérebro funcional — contexto, áreas, skills, rotinas e agentes configurados para a sua empresa.

---

## Estrutura do Repositório

```
imersao-openclaw-negocios/
├── cerebro/          ← Template do Cérebro (empresa fictícia TechFlow Solutions)
│   ├── empresa/      ← Contexto geral, decisões, gestão, skills corporativas
│   ├── areas/        ← Marketing, Vendas, Atendimento, Operações
│   ├── agentes/      ← Configuração de cada agente (SOUL, AGENTS, TOOLS)
│   ├── dados/        ← CSVs de exemplo (leads, vendas)
│   ├── guias/        ← Roadmap 90 dias, use cases, checklists
│   └── seguranca/    ← Permissões e políticas de acesso
│
├── wizard/           ← Guia passo a passo para implementação (agente conduz)
│   ├── README.md     ← Ponto de entrada — leia aqui primeiro
│   ├── 01-fundacao.md
│   ├── 02-areas.md
│   ├── 03-skills.md
│   ├── 04-rotinas.md
│   ├── 05-multi-agente.md
│   └── 06-validacao.md
│
└── imersao/          ← Roteiro operacional do facilitador
    ├── README.md
    ├── dia1/         ← Problema, arquitetura, tour, skills, rotinas, segurança
    ├── dia2/         ← Multi-agente, permissionamento, deep dives, próximos 30 dias
    ├── apresentacao-imersao.html
    └── apresentacao-imersao-v3.html
```

---

## As 3 Pastas

### 🧠 `cerebro/`
Template completo de um Cérebro empresarial. Baseado na empresa fictícia **TechFlow Solutions** — uma empresa de SaaS B2B com time de marketing, vendas e atendimento.

Serve como ponto de partida para o participante adaptar à sua própria empresa durante a imersão. Contém:
- Contexto da empresa, equipe e métricas
- Áreas com MAPA.md, contexto, skills, rotinas e sub-áreas
- Agentes configurados (assistente geral, marketing, vendas, atendimento, bot-suporte)
- Dados de exemplo e guias de implementação

### 🧙 `wizard/`
6 steps guiados que o **agente conduz** com o participante para construir o Cérebro personalizado. O agente lê `wizard/README.md` e passa por cada etapa com perguntas e ações concretas.

Sequência: Fundação → Áreas → Skills → Rotinas → Multi-agente → Validação

### 📋 `imersao/`
Roteiro operacional para o **facilitador** conduzir os 2 dias ao vivo. Cada arquivo é um bloco da agenda com objetivo, script, demos e exercícios.

---

## Como Começar

### Para participantes
1. Clone o repositório: `git clone https://github.com/pixel-educacao/imersao-openclaw-negocios`
2. Conecte seu agente OpenClaw ao repositório
3. Peça pro seu agente: **"Leia wizard/README.md e me guie pelo processo"**

### Para o facilitador
- Siga os arquivos em `imersao/dia1/` e `imersao/dia2/` em ordem
- Abra a apresentação `imersao/apresentacao-imersao-v3.html` no navegador
- O `cerebro/` é a demo ao vivo — use como exemplo antes de pedir aos participantes para criar o deles

---

*Imersão OpenClaw nos Negócios · Pixel Educação · 2026*
