# Governança Comum de Skills

## Objetivo
Criar um padrão mínimo compartilhado para todas as skills do IVS, reduzindo dispersão, melhorando legibilidade e facilitando manutenção, uso e auditoria.

## Estrutura mínima obrigatória de uma skill
Toda skill deve conter, nessa ordem lógica:
1. `name` e `description` no frontmatter
2. título claro
3. quando usar
4. inputs necessários
5. dependências e pré-requisitos
6. fontes canônicas complementares
7. passo a passo de execução
8. critérios de qualidade / quality gate
9. output esperado
10. falhas comuns / fallback

## Dependências: padrão obrigatório
Toda skill deve declarar explicitamente:
- dependências técnicas (scripts, CLIs, APIs, credenciais)
- dependências canônicas (arquivos de regra, playbooks, MAPA, contexto)
- dependências visuais/compliance quando houver saída para paciente ou público

## Critérios mínimos comuns
Toda skill deve atender estes critérios:
- clareza de quando usar
- clareza de input e output
- sequência operacional reproduzível
- dependências explícitas
- fallback quando houver bloqueio
- referência a fontes canônicas quando a skill toma decisão sensível
- linguagem consistente com o contexto IVS

## Classificação sugerida de skills
- **operacional**
- **analítica**
- **criativa**
- **governança**
- **integração**

## Regra de precedência
1. `cerebro/verdades-operacionais*.md`
2. `cerebro/execution-principles.md`
3. `cerebro/success-criteria.md`
4. playbooks e arquivos da área
5. a própria skill

## Governança de mudança
Quando uma skill for criada ou alterada, revisar se precisa atualizar:
- índice da área
- skill index da empresa
- playbook relacionado
- projeto/backlog relacionado
- checklist/quality gate relacionado

## Regra canônica de implantação total
Toda implementação operacional relevante no IVS deve terminar com implantação total até o final da execução, sem depender apenas de runtime temporário e sem depender de autorização posterior do Tiaro para canonização.

Isso significa que, sempre que houver liberação de ferramenta, nova integração, ajuste estrutural de agente, correção operacional relevante ou novo capability necessário para a operação:
- a configuração runtime deve ser aplicada quando couber
- a regra, o uso e as restrições devem ser promovidos imediatamente para a camada canônica do cérebro
- os agentes impactados devem ter seus arquivos operacionais atualizados
- o registro durável deve ser feito via graphify
- a entrega só deve ser tratada como concluída quando runtime e camada canônica estiverem coerentes

Regra prática: não deixar implementação importante funcionando apenas porque o runtime atual aceita; deixar também funcional e explícita nas regras canônicas.
