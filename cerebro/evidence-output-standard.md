# Evidence Output Standard

Padrão obrigatório de fechamento para tarefas executivas, operacionais ou com efeito verificável.

## Objetivo
Evitar conclusões narrativas sem prova.

## Regra principal
Sempre que uma tarefa envolver execução real, o fechamento deve incluir evidência explícita do efeito produzido.

## Formato padrão
Usar, quando aplicável, estas quatro seções no fechamento:

### Ação executada
- o que foi feito de fato
- sem intenção, sem promessa, sem resumo genérico

### Evidência
- prova objetiva de que o efeito ocorreu
- exemplos:
  - status validado
  - arquivo criado/alterado
  - caminho final existente
  - ID retornado
  - log/doctor/output relevante
  - mensagem enviada com retorno real

### IDs / Arquivos
- IDs, paths, URLs, nomes de arquivo, tickets, PRs, commits ou artefatos relevantes

### Pendências
- o que ficou pendente
- ou explicitar que não há pendências

## Quando usar
Usar obrigatoriamente em:
- configurações e gateway
- automações
- GitHub
- Quarkclinic
- Omie
- WhatsApp / Z-API
- geração de entregáveis
- mudanças estruturais no cérebro

## Quando pode ser simplificado
Em tarefas pequenas e internas, a estrutura pode ser mais curta, desde que a evidência continue explícita.

## O que NÃO conta como evidência
- "rodei o comando"
- "aparentemente funcionou"
- "deve estar certo"
- "já deixei ajustado"
- qualquer frase sem artefato, status ou validação concreta

## Exemplos

### Exemplo bom
**Ação executada**
- Atualizei `CONTEXT_CANON.md` e `cerebro/OPERATIONS_INDEX.md` para incluir a nova camada estrutural.

**Evidência**
- Os arquivos foram editados com sucesso e o novo conteúdo aponta para `cerebro/BRAIN_ARCHITECTURE.md` e `cerebro/memory-compaction-policy.md`.

**IDs / Arquivos**
- `/root/cerebro-vital-slim/CONTEXT_CANON.md`
- `/root/cerebro-vital-slim/cerebro/OPERATIONS_INDEX.md`

**Pendências**
- Nenhuma.

### Exemplo ruim
- "Organizei a arquitetura e deixei tudo alinhado."

## Regra de qualidade
Se o fechamento não permite auditoria rápida, ele ainda está fraco.
