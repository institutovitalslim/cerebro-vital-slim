# Bloco 3: Skills — 🔥 1º AHA MOMENT

**Timing:** 10h00–10h30 (30 minutos)

---

## O que cobrir

- Anatomia de uma skill (input → processo → output)
- O template padrão
- Skill real de vendas criada ao vivo
- Conectar a uma planilha Google Sheets
- Gerar relatório ao vivo e mostrar resultado

---

## Demos e arquivos

| Demo | Arquivo/Path |
|------|-------------|
| Template de skill | `areas/_template/skills/exemplo.md` |
| Skill de vendas pronta | `areas/vendas/skills/relatorio-semanal.md` |
| Planilha de leads (demo) | Google Sheets (link no repo) |
| Resultado gerado | Mensagem no Telegram ao vivo |

---

## Como fazer

**Passo 1 — Anatomia de skill (5 min)**

Mostre o template no terminal:
```
Input: o que você fornece
Processo: o que o agente faz
Output: o que você recebe
```

> "Uma skill é uma receita. Você escreve uma vez, o agente segue sempre do mesmo jeito."

Abra `areas/vendas/skills/relatorio-semanal.md` e leia em voz alta os campos principais.

**Passo 2 — Conectar planilha (8 min)**

Abra o terminal. Mostre como a skill aponta para a planilha:
```markdown
## Input necessário
- Planilha de leads: [URL da planilha]
- Período: semana atual
```

Execute ao vivo: peça ao agente para ler a planilha e extrair os dados.
> "O agente está lendo a planilha agora. Ao vivo."

**Passo 3 — Gerar relatório (10 min)**

Peça ao agente:
> "Execute a skill relatorio-semanal"

Mostre o agente processando. Quando o relatório aparecer no Telegram, grite:
> "Pronto. Relatório completo. Zero prompt. Zero formatação manual. Só pedir."

Pause aqui. Deixe o chat explodir.

**Passo 4 — Mostrar o chat (7 min)**

Leia reações ao vivo. Pegue a pergunta mais comum e responda demonstrando.

---

## NÃO mostrar

- Como criar a planilha do zero
- Configuração de OAuth / credenciais (bastidores)
- Erros de autenticação (testar antes)

---

## Checkpoint

✅ Template de skill explicado  
✅ Planilha conectada ao vivo  
✅ Relatório gerado e enviado no Telegram  
✅ Chat reagiu (AHA moment confirmado)  
→ Avançar para `dia1/pausa.md`
