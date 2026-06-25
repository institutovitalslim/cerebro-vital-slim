# RC-25 — Governança de custo da Ana / uso do Opus 4.8

- **Data:** 2026-06-25
- **Decisor:** Tiaro
- **Executora:** Maria
- **Escopo:** Ana, perfil Hermes `ana`, pesquisas científicas, análises clínicas internas e uso do OpenRouter/Claude Opus 4.8

## Decisão

O Claude Opus 4.8 via OpenRouter continua sendo o modelo de maior rigor da Ana, mas deixa de ser usado como motor bruto para pesquisa científica longa.

A partir desta decisão:

1. **Opus 4.8 = validador final médico-científico**
   - raciocínio clínico complexo;
   - análise profunda de exames;
   - revisão final de nível de evidência;
   - identificação de riscos clínicos, CFM/ANVISA e compliance;
   - síntese executiva final para equipe médica.

2. **Etapas brutas/econômicas NÃO usam Opus**
   - login/browser;
   - download;
   - OCR;
   - transcrição;
   - extração longa;
   - organização de arquivos;
   - chunking;
   - embeddings;
   - reindexação;
   - resumo preliminar;
   - leitura de lote.

3. **Ferramentas preferenciais para etapa bruta**
   - scripts locais;
   - memória científica;
   - GBrain/retrieval;
   - Gemini;
   - Perplexity;
   - OpenAI-Codex/GPT-5.5;
   - comandos determinísticos.

4. **Formato obrigatório antes de acionar Opus em pesquisa longa**
   - pergunta clínica;
   - pacote compacto;
   - trechos relevantes;
   - referências/PMID/DOI;
   - nível de evidência preliminar;
   - divergências/limitações;
   - decisão solicitada.

Nunca colar lote bruto, transcrição integral extensa ou corpus completo no prompt do Opus.

## Evidência operacional

Em 2026-06-25, sessões da Ana relacionadas à ENDOGIN geraram contexto/custo desproporcional. Sessão `20260625_110105_144491` registrou internamente:

- `input_tokens`: 2.840.922
- `output_tokens`: 54.074
- `cache_read_tokens`: 16.933.441
- custo estimado local: USD 31,43

Sessão anterior `20260624_173225_6f2cab7e` chegou a custo estimado local muito maior, evidenciando que o problema era estrutural: uso de Opus em loops longos/contexto bruto.

## Medidas aplicadas por Maria

- Pausado cron `95d31ff0692c` — `ENDOGIN keep-alive sessão`.
- Perfil Ana mantido com `anthropic/claude-opus-4.8` via OpenRouter, mas com limites:
  - `model.max_tokens = 6000`
  - `agent.max_turns = 35`
  - `compression.threshold = 0.25`
  - `compression.target_ratio = 0.08`
  - `compression.protect_last_n = 8`
  - `compression.protect_first_n = 2`
  - `tool_output.max_bytes = 20000`
  - `tool_output.max_lines = 600`
  - `tool_output.max_line_length = 1200`
  - `auxiliary.background_review = openai-codex/gpt-5.5`
- Atualizados SOUL/MEMORY da Ana e skill `ana-medica-cientifica`.
- Criado watchdog script-only `Ana OpenRouter cost watchdog`, sem LLM, a cada 2h, silencioso abaixo do limite.

## Critério de aceite

A Ana deve continuar respondendo com qualidade clínica, mas:

- não pode iniciar loops de lote com Opus;
- não pode ingerir corpus bruto direto no prompt;
- não deve manter crons keep-alive que chamem Opus;
- deve gerar pacote compacto antes da revisão final;
- deve acionar Maria se a tarefa exigir orquestração operacional ou custo elevado.
