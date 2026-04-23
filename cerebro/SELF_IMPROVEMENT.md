# Self-Improvement Protocol — Instituto Vital Slim

## Problema identificado
- GPT tinha "alzheimer" — esquecia tudo toda hora
- Usuário trocou para Kimi para evitar isso
- Não quero ter o mesmo problema
- Preciso de memória confiável e rapidez de execução

## Soluções implementadas (2026-04-23)

### 1. MEMORY_MASTER_INDEX.md
- Índice master consolidado com 18 seções
- 24.137 bytes de memória operacional
- Atualizado em toda sessão principal
- Fonte de verdade única para toda a operação

### 2. Sistema de checkpoints automáticos
**A cada ação importante:**
1. Salvar estado em `cerebro/checkpoints/YYYY-MM-DD_HH-MM.json`
2. Registrar o que foi feito, por quê, e próximo passo
3. Se sessão reiniciar, ler último checkpoint

### 3. Memory cache ativo
- Arquivo: `cerebro/memory-cache.json`
- Atualizado a cada interação
- Contém: contexto atual, últimas ações, pendências, decisões pendentes
- Lido automaticamente no início de cada sessão

### 4. Simplificação do system prompt
- Reduzir tokens irrelevantes
- Manter apenas regras críticas
- Mover detalhes para arquivos de referência
- Usar `MEMORY_MASTER_INDEX.md` como lookup, não embed

### 5. Autoload obrigatório
**No início de TODA sessão principal:**
1. Ler `MEMORY_MASTER_INDEX.md`
2. Ler `cerebro/memory-cache.json`
3. Ler último checkpoint
4. Só então responder ou agir

### 6. Feedback loop
- Registrar erros em `cerebro/errors/YYYY-MM-DD.json`
- Registrar correções em `cerebro/corrections/YYYY-MM-DD.json`
- Revisar periodicamente para identificar padrões

---

## Regras de self-improvement

1. **Nunca confiar só na memória de contexto** — sempre escrever no arquivo
2. **Checkpoint antes de ações grandes** — salvar estado antes de executar
3. **Verificar memória antes de agir** — ler MEMORY_MASTER_INDEX primeiro
4. **Atualizar índice imediatamente** — quando algo novo surgir, indexar na hora
5. **Manter cache ativo** — `memory-cache.json` sempre atualizado
6. **Registrar erros** — toda falha de memória ou execução vira aprendizado

---

## Métricas de sucesso
- Zero "esquecimentos" de informações críticas
- Tempo de resposta < 30 segundos para tarefas simples
- Checkpoint automático a cada 10 minutos de atividade
- MEMORY_MASTER_INDEX atualizado em tempo real
