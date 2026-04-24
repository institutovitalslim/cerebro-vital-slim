# Operations Index

## Camada estrutural

- arquitetura do cérebro: `cerebro/BRAIN_ARCHITECTURE.md`
- política de compactação de memória: `cerebro/memory-compaction-policy.md`
- protocolo de aprendizado: `cerebro/LEARNING_PROTOCOL.md`
- ledger de aprendizados: `cerebro/learning-ledger.md`
- princípios universais: `cerebro/execution-principles.md`
- critérios de sucesso: `cerebro/success-criteria.md`
- rubrica de skills: `cerebro/skill-design-rubric.md`
- padrão de evidência de saída: `cerebro/evidence-output-standard.md`

## Fontes canônicas por domínio

### GitHub
- `cerebro/github.md`
- `cerebro/verdades-operacionais.md`

### Quarkclinic
- `cerebro/quarkclinic.md`
- `cerebro/verdades-operacionais.md`

### Omie
- `cerebro/omie.md`
- `cerebro/omie-emissao-checklist.md`
- `cerebro/omie-servicos.md`
- `cerebro/verdades-operacionais.md`
- `skills/omie-cadastro-paciente/SKILL.md`
- Emissões de proposta/OS com boleto devem seguir os campos estruturados documentados em `cerebro/omie.md`
- Emissões com NFS-e devem consultar o cadastro de serviços em `cerebro/omie-servicos.md` e o checklist em `cerebro/omie-emissao-checklist.md`

### WhatsApp / Z-API
- `cerebro/whatsapp-zapi.md`
- `cerebro/elevenlabs.md`
- `cerebro/verdades-operacionais.md`
- ElevenLabs TTS para respostas de áudio: `cerebro/elevenlabs.md`

### Time da clínica
- `cerebro/time-clinica.md`
- `cerebro/verdades-operacionais.md`

### Aprendizagem / manutenção do cérebro
- `cerebro/BRAIN_ARCHITECTURE.md`
- `cerebro/memory-compaction-policy.md`
- `cerebro/LEARNING_PROTOCOL.md`
- `cerebro/learning-ledger.md`
- `cerebro/verdades-operacionais.md`
- `cerebro/execution-principles.md`
- `cerebro/success-criteria.md`
- `cerebro/skill-design-rubric.md`
- `cerebro/evidence-output-standard.md`

### Tweet-carrossel
- `cerebro/verdades-operacionais.md`
- `MEMORY.md`
- `/root/.openclaw/workspace/skills/tweet-carrossel/scripts/make_cover.py`
- `/root/.openclaw/workspace/fotos_dra/originais/`
- `/root/.openclaw/workspace/fotos_dra/avatares/`
- OpenClaw image providers nativos: preferir Google/NanoBanana 2, fallback OpenAI
- Para fotos da Dra. com NanoBanana 2 Pro e referência real, usar também a cláusula canônica de `strict facial consistency mode`

### Atendimento / Clara (WhatsApp)
- `cerebro/verdades-operacionais-clara.md` — princípios, objeções, regras de ouro + integração CRC Clínica 2.0
- `cerebro/areas/atendimento/checklist-atendimento-clara.md` — checklist operacional completo (setup, atendimento, pós-agendamento, follow-up, métricas)
- `cerebro/areas/atendimento/scripts-crc-ivs.md` — scripts adaptados do CRC para IVS (9 seções: abertura, descoberta, valor, agendamento, pós-agendamento 6 fases, quebra de objeções, follow-up, reativação, pós-consulta)
- `cerebro/areas/atendimento/exemplos-praticos-treino.md` — 7 cenários práticos: ERRO → ACERTO → ANÁLISE

### Marketing (skills adaptadas do MarketingSkills)
- `cerebro/patient-marketing-context.md` — contexto compartilhado de pacientes
- `cerebro/buffer.md` — postagem automática em redes sociais
- `~/.openclaw/skills/copywriting-vitalslim/SKILL.md` — copywriting para healthcare
- `~/.openclaw/skills/customer-research-vitalslim/SKILL.md` — pesquisa com pacientes
- `~/.openclaw/skills/social-content-vitalslim/SKILL.md` — conteúdo social
- `~/.openclaw/skills/content-strategy-vitalslim/SKILL.md` — estratégia de conteúdo
- `~/.openclaw/skills/whatsapp-marketing/SKILL.md` — marketing via WhatsApp
- `~/.openclaw/skills/local-seo/SKILL.md` — SEO local (Google Maps)
- `~/.openclaw/skills/medical-content/SKILL.md` — compliance médico

### Campanhas ativas / prontas para execução
- `cerebro/areas/marketing/campanhas/follow-up-leads-whatsapp.md` — sequência 7 mensagens para leads não agendados
- `cerebro/areas/marketing/campanhas/reativacao-300-pacientes.md` — reativação de 300 pacientes inativos (45 dias)
- `cerebro/areas/marketing/campanhas/google-business-otimizacao.md` — otimização completa do Google Business Profile

### Contexto intertópicos (Telegram)
- `cerebro/telegram-topics.md`
- `cerebro/cross-topic-memory.md`
- `cerebro/cross-topic-protocol.md`
- `cerebro/cross-topic-promotion-rules.md`

## Navegação por tipo de tarefa

- se a tarefa for sobre arquitetura, memória ou organização do cérebro, começar por:
  - `cerebro/BRAIN_ARCHITECTURE.md`
  - `cerebro/memory-compaction-policy.md`
  - `cerebro/LEARNING_PROTOCOL.md`
- se a tarefa for operacional recorrente, começar por:
  - `CONTEXT_CANON.md`
  - arquivo canônico do domínio
  - checklist/skill do fluxo
  - `cerebro/evidence-output-standard.md` se houver execução verificável
- se a tarefa for estrutural em skill, começar por:
  - `cerebro/skill-design-rubric.md`
  - `cerebro/execution-principles.md`
  - `cerebro/success-criteria.md`

## Diretório de testes canônicos

- base: `ops/tests/`
- domínios já cobertos:
  - `ops/tests/github.md`
  - `ops/tests/quarkclinic.md`
  - `ops/tests/omie.md`
  - `ops/tests/whatsapp-zapi.md`
  - `ops/tests/tweet-carrossel.md`
  - `ops/tests/cerebro.md`

## Regras
- Antes de responder ou executar uma tarefa operacional recorrente, consultar primeiro os arquivos do domínio correspondente.
- Para fluxos de cadastro de paciente no Omie, usar a skill canônica `skills/omie-cadastro-paciente/`.
- Sempre que houver novo aprendizado relevante, consultar `cerebro/LEARNING_PROTOCOL.md` e registrar a incorporação em `cerebro/learning-ledger.md`.
- Em grupos com múltiplos tópicos, consultar a estrutura intertópicos antes de tratar o contexto do tópico atual como suficiente.

- `cerebro/leads-argumentos-venda-ligacoes.md` — argumentos de venda para ligações/atendimento de paciente (base Vitor Oliveira, 15 reels)
