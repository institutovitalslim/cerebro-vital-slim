# 🧠 Cérebro — TechFlow Solutions

> Repositório central de conhecimento e configuração dos agentes IA da TechFlow Solutions.

## O que é o Cérebro?

O Cérebro é o **repositório GitHub que serve como memória persistente** dos agentes de IA da empresa. Enquanto o agente "pensa" em tempo real, o cérebro guarda tudo que importa: contexto da empresa, processos, resultados de testes, base de conhecimento, rotinas.

**Sem o cérebro, o agente esquece tudo ao fechar a sessão.**  
**Com o cérebro, o agente aprende, evolui e fica cada vez mais eficiente.**

---

## Como Funciona

```
┌─────────────────────────────────────────────────────────────┐
│                     FLUXO DO CÉREBRO                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   GitHub Repo (cerebro/)                                    │
│         │                                                   │
│         ▼ clone/pull                                        │
│   Servidor do Agente                                        │
│         │                                                   │
│         ▼ lê contexto, skills, rotinas                      │
│   Agente IA em execução                                     │
│         │                                                   │
│         ├── lê arquivos → entende contexto                  │
│         ├── executa skills → produz output                  │
│         ├── escreve resultados → atualiza arquivos          │
│         └── commit + push → sincroniza com GitHub           │
│                                                             │
│   GitHub Repo ← outros agentes, ferramentas, equipe        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Estrutura de Pastas

```
cerebro/
├── README.md                    ← Este arquivo
│
├── empresa/                     ← Contexto global da empresa
│   ├── contexto/
│   │   ├── empresa.md           ← Missão, visão, produto, stack
│   │   ├── equipe.md            ← Pessoas e responsabilidades
│   │   └── metricas.md          ← KPIs e metas
│   ├── skills/
│   │   ├── _templates/          ← Templates de skills
│   │   └── _index.md            ← Índice de todas as skills
│   └── rotinas/
│       └── README.md            ← Como crons funcionam
│
├── areas/                       ← Áreas da empresa
│   ├── vendas/
│   │   ├── contexto/geral.md
│   │   ├── rotinas/
│   │   ├── skills/
│   │   └── bot/conhecimento.md
│   ├── marketing/
│   │   ├── contexto/geral.md
│   │   ├── sub-areas/trafego-pago/
│   │   └── skills/
│   ├── atendimento/
│   │   ├── contexto/geral.md
│   │   ├── bot/
│   │   ├── rotinas/
│   │   └── skills/
│   └── operacoes/
│       ├── contexto/geral.md
│       └── rotinas/
│
├── agentes/                     ← Config de cada agente
│   ├── COMO-CONECTAR.md
│   ├── assistente/
│   ├── marketing/
│   └── bot-suporte/
│
├── seguranca/                   ← Permissões e acesso
│   └── permissoes.md
│
├── dados/                       ← Dados e integrações
│   ├── README.md
│   └── vendas.csv
│
└── guias/                       ← Documentação e roadmap
    └── roadmap-90-dias.md
```

---

## Como o Agente Usa o Cérebro

1. **Ao iniciar** — o agente lê `empresa/contexto/` para entender onde está
2. **Ao executar tarefa** — busca a skill correspondente em `areas/*/skills/`
3. **Ao rodar rotina** — lê o arquivo de rotina correspondente e executa
4. **Ao aprender** — escreve learnings nos arquivos da área correspondente
5. **Ao finalizar** — faz commit + push para sincronizar com GitHub

---

## Primeiros Passos

```bash
# 1. Clonar o repositório
git clone https://github.com/suaempresa/cerebro.git

# 2. Configurar o agente para apontar para esta pasta
# (ver agentes/COMO-CONECTAR.md)

# 3. Personalizar empresa/contexto/empresa.md com seus dados reais

# 4. Ativar as rotinas (ver empresa/rotinas/README.md)
```

---

*Versão: 1.0 | Empresa: TechFlow Solutions (exemplo fictício)*
