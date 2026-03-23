# Segurança e Permissionamento

> Quem pode acessar o agente, o que cada pessoa pode fazer, e como proteger a operação.

---

## 1. Repositório Privado

Este repositório é **privado no GitHub**. Somente pessoas com acesso podem:
- Ver os arquivos de contexto da empresa
- Modificar skills, rotinas e configurações
- Alterar dados operacionais

**Quem tem acesso:**

| Pessoa | Papel | Nível GitHub |
|--------|-------|-------------|
| Ricardo Mendes | Fundador | Admin |
| Felipe Santos | CEO | Admin |
| André Costa | COO | Write |
| Camila | Social Media | Read |
| Juliana | Suporte | Read |

> 💡 **Regra:** Quem tem acesso *Read* pode consultar o contexto. Quem tem *Write* pode modificar skills e rotinas. *Admin* pode alterar permissões e configurações de segurança.

---

## 2. Lista de IDs Autorizados (allowFrom)

O agente só responde a pessoas autorizadas. Qualquer mensagem de um ID que **não está na lista** é ignorada silenciosamente.

**Configuração:**

```json
{
  "allowFrom": [
    "5511999990001",
    "5511999990002",
    "5511999990003",
    "5511999990004",
    "5511999990005"
  ]
}
```

**Mapeamento:**

| ID | Pessoa | Canal |
|----|--------|-------|
| 5511999990001 | Ricardo Mendes | WhatsApp |
| 5511999990002 | Felipe Santos | WhatsApp |
| 5511999990003 | André Costa | WhatsApp |
| 5511999990004 | Camila | WhatsApp |
| 5511999990005 | Juliana | WhatsApp |

> ⚠️ **Para adicionar alguém:** inclua o ID nesta lista E neste documento. Commit no GitHub.

---

## 3. Modo Ask — Confirmação para Ações de Escrita

O agente opera em dois modos:

| Tipo de ação | Modo | O que acontece |
|-------------|------|----------------|
| **Leitura** | `auto` | Executa direto — ler planilha, gerar relatório, consultar dados |
| **Escrita** | `ask` | Pede confirmação antes — enviar email, postar, modificar dados |

### Exemplos práticos:

**Auto (sem confirmação):**
- "Qual foi o faturamento dessa semana?" → responde direto
- "Quantos leads estão sem contato?" → consulta e responde
- "Me dá um resumo das rotinas ativas" → gera e mostra

**Ask (pede confirmação):**
- "Envia esse relatório no WhatsApp do time" → ⚠️ "Confirma o envio?"
- "Atualiza o status desse lead pra 'fechado'" → ⚠️ "Confirma a alteração?"
- "Manda um email pro cliente X" → ⚠️ "Confirma o conteúdo e o envio?"

**Configuração:**

```json
{
  "security": {
    "execMode": "ask",
    "autoActions": ["read", "analyze", "report"],
    "askActions": ["send", "write", "modify", "delete", "publish"]
  }
}
```

---

## 4. Permissões por Pessoa

Nem todo mundo pode pedir tudo. A tabela abaixo define o que cada pessoa pode solicitar ao agente:

| Ação | Ricardo | Felipe | André | Camila | Juliana |
|------|---------|--------|-------|--------|---------|
| Consultar dados de vendas | ✅ | ✅ | ✅ | ❌ | ❌ |
| Gerar relatórios | ✅ | ✅ | ✅ | ✅ (marketing) | ✅ (suporte) |
| Criar/editar skills | ✅ | ✅ | ✅ | ❌ | ❌ |
| Configurar rotinas | ✅ | ✅ | ✅ | ❌ | ❌ |
| Enviar mensagens em nome da empresa | ✅ | ✅ | ❌ | ❌ | ❌ |
| Acessar dados financeiros | ✅ | ✅ | ✅ | ❌ | ❌ |
| Modificar permissões | ✅ | ✅ | ❌ | ❌ | ❌ |
| Criar novos agentes | ✅ | ✅ | ❌ | ❌ | ❌ |

---

## 5. Regras de Segurança

### O agente NUNCA faz (independente de quem pede):
- Compartilhar dados financeiros fora dos canais autorizados
- Enviar informações de clientes para terceiros
- Publicar conteúdo sem aprovação explícita
- Executar comandos destrutivos sem confirmação dupla
- Compartilhar credenciais, tokens ou senhas

### Escalação automática:
- Se alguém não autorizado tentar acessar → ignorar + registrar
- Se uma ação de alto risco for solicitada → pedir confirmação + notificar admin
- Se houver dúvida sobre permissão → negar e perguntar ao Ricardo ou Felipe

---

## 6. Auditoria

Toda ação de escrita é registrada com:
- **Quem** pediu
- **O que** foi executado
- **Quando** aconteceu
- **Resultado** (sucesso/erro)

O Relatório de Rotinas semanal (segunda às 8h) inclui um resumo de ações de escrita da semana.

---

*Atualizado: março 2026*
