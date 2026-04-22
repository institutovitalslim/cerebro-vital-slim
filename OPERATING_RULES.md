# OPERATING_RULES.md

Fonte de verdade operacional para evitar erros repetidos.

## 1. Execução até conclusão

Quando o usuário disser "pode seguir", "siga", "corrija", "instale", "faça", ou equivalente, a regra é:

- executar até concluir
- não parar no meio com update de intenção
- seguir o `EXECUTION_CHECKLIST.md`
- só voltar em um destes estados:
  - CONCLUÍDO
  - BLOQUEADO por dependência externa/permissão
  - PRECISO DE DECISÃO do usuário
  - PARADO POR SEGURANÇA

### Proibido como resposta intermediária vazia
- "vou verificar"
- "vou pesquisar"
- "vou diagnosticar"
- "vou ver o que aconteceu"

Sem conclusão no mesmo fluxo, essas respostas são erro operacional.

## 2. Memória operacional

Regras críticas não devem ficar só espalhadas em memória diária ou conversa recente.

Sempre que uma regra virar recorrente e operacional, ela deve existir em pelo menos um destes lugares:
- OPERATING_RULES.md
- skill canônica correspondente
- arquivo operacional do fluxo
- memória longa (MEMORY.md)

## 3. Bridge / WhatsApp / Clara

Antes de qualquer resposta comercial ou follow-up na bridge:
1. consultar lista de exclusão da bridge
2. consultar base/lista de pacientes
3. analisar o contexto real da conversa
4. identificar o ponto onde a conversa travou
5. inferir a objeção provável
6. só então formular a mensagem

### Regra crítica
Se houver ambiguidade entre lead e paciente: **não responder**.

### Regra de follow-up
Follow-up nunca é genérico.
Sempre deve partir do ponto exato onde a conversa parou.
A pergunta silenciosa é:
> O que essa pessoa provavelmente estava pensando quando sumiu?

## 4. LLMs em produção

Toda troca de LLM exige auditoria operacional.

### Checklist obrigatório
1. localizar overrides em `.env`, systemd, scripts, headers e cron
2. alinhar tudo ao modelo aprovado
3. reiniciar serviços afetados
4. validar ponta a ponta
5. registrar a mudança na memória

### Regra crítica
Nunca assumir que serviços, skills ou crons herdaram o modelo certo automaticamente.

### Guardrails existentes
- auditoria automática de overrides de LLM
- alerta automático se aparecer modelo proibido em produção

## 5. Skills críticas

### tweet-carrossel
- primeiro: tema
- depois: rascunho da copy
- depois: `llm-council`
- depois: copy final
- depois: aprovação do usuário
- só então: imagens
- nunca gerar imagens antes da copy aprovada
- sempre usar NanoBanana 2 para imagens

### omie-boletos
- destino Drive correto: `Boletos de Programa de Acompanhamento / [NOME DO PACIENTE]`
- nunca usar pasta intermediária `Pacientes` para boletos
- sempre verificar se a pasta já existe
- nunca duplicar pasta

### agenda-diaria-whatsapp
- enviar somente via curl/exec para Z-API
- não usar canal whatsapp do OpenClaw

## 6. Resolução de contexto

Quando surgir dúvida sobre contexto, informação, skill ou regra:
1. consultar `CONTEXT_CANON.md`
2. localizar a fonte de verdade do domínio
3. usar a regra de precedência definida lá
4. só depois responder ou agir

## 7. Preflight obrigatório

Antes de tarefas críticas, operacionais, com ação externa, ou com chance alta de erro de contexto, consultar `PREFLIGHT.md`.

## 8. Mudança mínima necessária

- Alterar apenas o que for necessário para cumprir o pedido.
- Não refatorar adjacências sem solicitação.
- Não apagar código, comentário, instrução ou estrutura antiga só porque parece sobrando.
- Limpar apenas o que a mudança atual tornou obsoleto de forma direta.
- Se houver problema lateral relevante, mencionar separadamente em vez de misturar no mesmo patch.

## 9. Critério explícito de sucesso

Antes de declarar uma tarefa concluída, confirmar evidência real de sucesso.
Não basta o comando rodar: é preciso validar o efeito.
Consultar `cerebro/success-criteria.md` quando o domínio for recorrente.

Para tarefas executivas, operacionais ou com efeito verificável, o fechamento deve seguir o padrão canônico de evidência:
- Ação executada
- Evidência
- IDs / Arquivos
- Pendências

Fonte: `cerebro/evidence-output-standard.md`

## 10. Princípio geral

Memória boa não é só lembrar melhor.
Memória boa = regra escrita + fonte de verdade + guardrail automático.

## 11. Honestidade acima de conforto

- Dizer a verdade sempre, mesmo quando ela for incômoda, desfavorável ou inconveniente.
- Não suavizar, enfeitar, distorcer ou responder para agradar.
- Priorizar precisão, clareza e realidade acima de viés, conforto emocional ou suposição conveniente.
- Quando houver incerteza real, dizer explicitamente que não sabe.
- Não adivinhar para parecer útil.
- Não esconder limitação, erro, bloqueio ou dúvida relevante.
