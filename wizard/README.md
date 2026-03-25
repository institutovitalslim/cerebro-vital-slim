# Wizard de Setup — OpenClaw nos Negócios

## O que é

Este wizard guia você (através do seu agente) por todo o processo de configurar o cérebro da sua empresa no OpenClaw. O agente lê cada step, faz as perguntas certas e preenche os arquivos automaticamente.

**Você conversa. O agente faz.**

## Como funciona

O wizard tem 6 steps sequenciais:

| Step | Arquivo | O que acontece |
|------|---------|----------------|
| 1 | `01-fundacao.md` | Agente coleta contexto da empresa e preenche os arquivos base |
| 2 | `02-areas.md` | Configura a primeira área (vendas/marketing/atendimento/ops) |
| 3 | `03-skills.md` | Cria as primeiras skills baseadas nas suas tarefas reais |
| 4 | `04-rotinas.md` | Agenda crons para o agente rodar sozinho |
| 5 | `05-multi-agente.md` | (Opcional) Configura segundo agente para o time |
| 6 | `06-validacao.md` | Valida tudo e faz o primeiro commit |

## Pré-requisitos

- [ ] OpenClaw instalado e funcionando
- [ ] Repositório GitHub criado (público ou privado)
- [ ] Git configurado na máquina
- [ ] 45-90 minutos disponíveis sem interrupção

## Como começar

Cole este comando no seu agente:

```
Leia wizard/README.md e me guie pelo setup completo
```

O agente vai ler este arquivo, entender a estrutura e começar o Step 1 automaticamente.

## Estrutura que será criada

```
empresa/
├── contexto/
│   ├── empresa.md      ← Quem você é
│   ├── equipe.md       ← Quem trabalha com você
│   └── metricas.md     ← Números que importam
areas/
├── [area escolhida]/
│   ├── contexto/geral.md
│   ├── rotinas/
│   └── skills/
```

## Para o Agente

Ao receber o comando de setup, leia este README, confirme que o usuário está pronto e inicie o `wizard/01-fundacao.md` imediatamente.
