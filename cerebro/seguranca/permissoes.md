# Permissionamento

> Duas tabelas simples: onde cada agente responde, e quem pode falar com quem.

---

## 1. Mapeamento Grupo → Agente

Cada agente responde **somente** no(s) grupo(s) listados. Mensagem fora do mapeamento = ignora.

| Grupo | group_id | Agente que responde | Bot |
|-------|----------|---------------------|-----|
| Ops - Imersão OpenClaw nos Negócios | `-1003617656481` | Assistente Geral | @agente_geral_imersao_bot |
| Mkt - Imersão OpenClaw nos Negócios | `-5124164895` | Assistente de Marketing | @agente_marketing_imersao_bot |

> Novos grupos serão adicionados aqui conforme forem criados.

---

## 2. Acesso ao Repositório (cerebro/) por Agente

| Agente | Leitura | Escrita |
|--------|---------|---------|
| **Assistente Geral** | `cerebro/` inteiro | `cerebro/` inteiro |
| **Agente de Marketing** | `cerebro/empresa/` + `cerebro/areas/marketing/` | `cerebro/empresa/` + `cerebro/areas/marketing/` |
| **Agente de Vendas** *(futuro)* | `cerebro/empresa/` + `cerebro/areas/vendas/` | `cerebro/empresa/` + `cerebro/areas/vendas/` |
| **Agente de Atendimento** *(futuro)* | `cerebro/empresa/` + `cerebro/areas/atendimento/` | `cerebro/empresa/` + `cerebro/areas/atendimento/` |

**Regra:** Agente de área nunca lê nem escreve em `cerebro/seguranca/`, `cerebro/dados/` ou pastas de outras áreas.

---

## 3. Mapeamento Pessoa → Agentes Permitidos

O agente verifica o `telegram_id` de quem mandou a mensagem. Se a pessoa não tem permissão, **ignora**.

### Exemplo (dados fictícios)

| telegram_id | Nome | Papel | Agentes que pode acionar |
|-------------|------|-------|--------------------------|
| 111111111 | Ana Souza | Fundadora | Todos |
| 222222222 | Bruno Lima | CEO | Todos |
| 333333333 | Carlos Reis | COO | Todos |
| 444444444 | Diana Rocha | Social Media | Assistente Geral, Marketing |
| 555555555 | Eduardo Silva | Suporte | Assistente Geral, Atendimento |
| 666666666 | Visitante / Aluno | — | Nenhum (somente leitura) |

### Níveis de acesso

- **Todos** → pode falar com qualquer agente
- **Área específica** → só interage com agentes da(s) sua(s) área(s) + Assistente Geral
- **Nenhum** → está no grupo mas o agente ignora suas mensagens

### Onde isso é configurado no OpenClaw

No `openclaw.json`, dentro de cada account do Telegram:

```json
"allowFrom": ["111111111", "222222222", "333333333"]
```

---

## 4. Regras Gerais

1. **Um grupo = um agente responsável** — nunca cruza
2. **Agente de área não acessa dados fora do seu escopo** — lê só o que precisa
3. **Assistente Geral é o único com acesso irrestrito** ao repositório
4. **Ações sensíveis pedem confirmação** (emails, posts públicos, alterações de config) independente do nível de acesso

---

*Atualizado: 26 de março de 2026*
