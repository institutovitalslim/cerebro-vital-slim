# 🧠 Repositório Empresa Exemplo — Cérebro da Operação

> Este repositório é o **cérebro da Empresa Exemplo**. O agente de IA lê esses arquivos automaticamente para entender o contexto da empresa, tomar decisões e executar tarefas com autonomia.

## O que é isso?

Este repo centraliza todo o conhecimento operacional da **Empresa Exemplo** — uma EdTech que vende cursos online de marketing digital. Aqui ficam:

- Contexto da empresa e da equipe
- Regras e objetivos por área
- Skills (automações prontas para usar)
- Dados operacionais (vendas, leads)
- Rotinas automáticas (crons)
- Configurações de segurança

**Por que no GitHub?** Porque o agente de IA precisa de uma fonte de verdade versionada, auditável e acessível. Qualquer membro da equipe pode atualizar um arquivo aqui e o agente vai se comportar diferente na próxima execução — sem precisar reprogramar nada.

---

## Estrutura de Pastas

```
imersao-openclaw-negocios/
│
├── README.md                   ← Você está aqui
├── TEMPLATE-SKILL.md           ← Esqueleto para criar novas skills
│
├── contexto/
│   ├── empresa.md              ← O que é a Empresa Exemplo, produtos, métricas
│   └── equipe.md               ← Quem é quem, papéis e responsabilidades
│
├── areas/
│   ├── vendas/
│   │   └── contexto.md         ← Objetivos, KPIs e ferramentas de vendas
│   ├── marketing/
│   │   └── contexto.md         ← Objetivos, KPIs e ferramentas de marketing
│   ├── atendimento/
│   │   └── contexto.md         ← Objetivos, KPIs e ferramentas de atendimento
│   └── operacoes/
│       └── contexto.md         ← Objetivos, KPIs e ferramentas de operações
│
├── skills/
│   ├── relatorio-vendas/
│   │   └── SKILL.md            ← Gera relatório semanal de vendas
│   ├── follow-up-leads/
│   │   └── SKILL.md            ← Identifica leads sem contato há 3+ dias
│   └── relatorio-rotinas/
│       └── SKILL.md            ← Monitora status de todas as rotinas ativas
│
├── dados/
│   ├── vendas.csv              ← Histórico de vendas (março 2026)
│   └── leads.csv               ← Pipeline de leads atual
│
├── rotinas/
│   └── README.md               ← O que são crons, como configurar, exemplos
│
└── seguranca/
    └── permissoes.md           ← Modelo de segurança, quem pode o quê
```

---

## Como o Agente Usa Esse Repositório

1. **Ao iniciar qualquer tarefa**, o agente lê este README para entender a estrutura
2. **Para contexto da empresa**, lê `contexto/empresa.md` e `contexto/equipe.md`
3. **Para executar uma automação**, lê o `SKILL.md` correspondente em `skills/`
4. **Para acessar dados**, lê os arquivos em `dados/`
5. **Para rotinas agendadas**, segue as instruções em `rotinas/README.md`

> 💡 **Dica:** Sempre que atualizar um arquivo aqui, faça um commit com uma mensagem clara. O histórico de versões é o log de evolução da inteligência da empresa.

---

## Começando

### Para a equipe:
- Edite `contexto/empresa.md` para manter métricas atualizadas
- Edite `contexto/equipe.md` quando alguém entrar ou sair
- Crie novas skills usando o `TEMPLATE-SKILL.md` como base

### Para o agente:
- Leia este README primeiro
- Consulte `contexto/` para entender o negócio
- Use as skills em `skills/` para executar tarefas recorrentes
- Respeite as permissões definidas em `seguranca/permissoes.md`

---

*Mantido pela equipe da Empresa Exemplo | Atualizado: março 2026*
