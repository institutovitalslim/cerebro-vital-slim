# MEMORY.md - Long-Term Memory

_Curated knowledge and context. Keep only the essential index._

---

## Camada estrutural do cérebro

### Princípios universais
- `cerebro/execution-principles.md`
- `cerebro/success-criteria.md`
- `OPERATING_RULES.md`

### Fontes canônicas por domínio
- índice geral: `cerebro/OPERATIONS_INDEX.md`
- fatos operacionais do negócio: `cerebro/verdades-operacionais.md`
- protocolo de aprendizado: `cerebro/LEARNING_PROTOCOL.md`
- ledger de mudanças estruturais: `cerebro/learning-ledger.md`
- rubrica de skills: `cerebro/skill-design-rubric.md`

---

## Skills e operações canônicas

### omie-boletos
- Local: `/root/.openclaw/workspace/skills/omie-boletos/`
- Script: `scripts/omie_boletos.py`
- Regras e credenciais críticas já consolidadas em `cerebro/verdades-operacionais.md` e nos artefatos da skill

### omie-linha-corte
- Local: `/root/.openclaw/workspace/skills/omie-linha-corte/`
- Regra crítica: sempre confirmar com o usuário antes de executar

### agenda-diaria-whatsapp
- Local: `/root/.openclaw/workspace/skills/agenda-diaria-whatsapp/`
- Cron: `2ba465d4-3dd0-435b-bb12-1576ed6c0403`
- Envio somente via Z-API

### historico-conversas
- Local: `/root/.openclaw/workspace/skills/historico-conversas/`
- Script validado: `scripts/consultar_historico.py`
- Conta correta: `institutovitalslim@gmail.com`
- Planilha: `ZAPI_Historico_Pacientes`

### tweet-carrossel
- Skill central de carrosséis, com copy antes de imagem
- Sempre consultar `memoria-cientifica` antes de conteúdo científico
- Para imagens, seguir a camada canônica atual:
  - `cerebro/verdades-operacionais.md`
  - `/root/.openclaw/workspace/skills/tweet-carrossel/scripts/make_cover.py`
  - `/root/.openclaw/workspace/fotos_dra/originais/`
  - `/root/.openclaw/workspace/skills/prompt-imagens/`
- Documento de lições maiores da sessão 2026-04-20:
  - `cerebro/empresa/conhecimento/logs/LICOES_SESSAO_2026-04-20.md`

### prompt-imagens
- Local: `/root/.openclaw/workspace/skills/prompt-imagens/`
- Caminho obrigatório para criação de imagem guiada
- Orquestrador oficial: `scripts/clara_create_image.py`

### memoria-cientifica
- Local: `/root/cerebro-vital-slim/cerebro/empresa/skills/memoria-cientifica/`
- Clara consulta antes de criar conteúdo científico ou responder paciente

### deep-research
- Local: `/root/.openclaw/workspace/skills/deep-research/`
- Saída padrão: `/root/.openclaw/workspace/research/`
- Consultar o índice da pasta `research/`

---

## Instituto Vital Slim

### Equipe médica
- **Dra. Daniely Freitas**
  - CRM-BA 27588
  - Instagram: `@dradaniely.freitas`
- **Dra. Patrícia Fabrini**
  - Instagram: `@patriciafabrini.dra`
  - Responsável Técnica do Centro de Tricologia Avançada
  - Dermatologista SBD desde 1999
  - Desenvolvedora da metodologia Nutroboost

### Centro de Tricologia Avançada
- Parte do Instituto Vital Slim
- Especialista de referência: Dra. Patrícia Fabrini

---

## Clara / vendas
- Nunca passar preço antes de o paciente entender o valor
- Postura: consultiva, premium, sem pressão artificial
- Frase de ativação para nova conversa/reativação:
  - “Oi, eu estava olhando o seu site e queria tirar uma dúvida...”

---

## Índice resumido
- 2026-04-07: skills `omie-boletos`, `omie-linha-corte`, `agenda-diaria-whatsapp`, `deep-research`
- 2026-04-09: `tweet-carrossel` consolidado com `llm-council`, NanoBanana 2 e capa obrigatória via `make_cover.py`
- 2026-04-10: estrutura de robustez criada (`OPERATING_RULES`, `CONTEXT_CANON`, `PREFLIGHT`, `EXECUTION_CHECKLIST`)
- 2026-04-10: regra absoluta de honestidade operacional consolidada
- 2026-04-10: `historico-conversas` validado com conta correta e planilha confirmada
- 2026-04-10: equipe médica atualizada com Dra. Patrícia Fabrini e contexto de tricologia
- 2026-04-11: regra crítica de continuidade e prazo consolidada
- 2026-04-14: image providers nativos, fotos reais da Dra. e montagem de capa consolidados
- 2026-04-20: cérebro ganhou camada explícita de princípios de execução, critérios de sucesso e rubrica de skills
- 2026-04-20: `verdades-operacionais.md` foi separado da camada universal e passou a concentrar fatos do negócio
- [Argumentos de venda — ligações](cerebro/leads-argumentos-venda-ligacoes.md) — Lições condensadas de 15 reels do @vitoroliveiraconsultor (comercial para clínicas médicas) aplicadas à Clara: follow-up 5x, velocidade de resposta, objeção de preço = objeção escondida, recuperação de lead silenciado, 4 pilares de conversão. Fonte de verdade para ligações/atendimento de paciente.
