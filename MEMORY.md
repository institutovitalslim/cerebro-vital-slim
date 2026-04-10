# MEMORY.md - Long-Term Memory

_Curated knowledge and context. Updated as I learn._

---

## Skills Criadas

### omie-boletos (2026-04-07)
Skill para baixar boletos de faturamentos do Omie ERP e organizar por paciente.

- **Localização:** `/root/.openclaw/workspace/skills/omie-boletos/`
- **Script:** `scripts/omie_boletos.py`

**Uso:**
```bash
# Listar boletos de uma data
python3 scripts/omie_boletos.py --data DD/MM/AAAA --listar

# Baixar para Google Drive
python3 scripts/omie_boletos.py --data DD/MM/AAAA --drive

# Baixar localmente
python3 scripts/omie_boletos.py --data DD/MM/AAAA --local

# Período específico
python3 scripts/omie_boletos.py --de DD/MM/AAAA --ate DD/MM/AAAA --drive
```

**Regras importantes:**
- Sempre verificar pasta existente antes de criar (nunca duplicar)
- Criar subpasta com o nome do paciente
- Dentro da pasta do paciente, salvar os PDFs dos boletos
- Usar `filtrar_por_emissao_de/ate` (NÃO `filtrar_por_data_de/ate`)
- Pular cancelados e parcelas sem boleto gerado
- Rate limit: 0.4s entre chamadas
- Destino local: `C:\Users\tiaro\Documents\## Medical Contabilidade\#Instituto Vital Slim\Boletos de Programa de Acompanhamento\[NOME DO PACIENTE]`
- Destino Drive correto: `## Medical Contabilidade / #Instituto Vital Slim / Boletos de Programa de Acompanhamento / [NOME DO PACIENTE]`
- ID da pasta no Drive: `1hbF8K-wil6NNyQ2PyXZK8PZ1jEZhccOr`
- NÃO criar pasta intermediária `Pacientes` para boletos
- Nomenclatura dos arquivos: `Boleto_P{parcela}_R_Venc{data}.pdf`
- Exemplo: `Boleto_P001-009_R$1115_Venc07-04-2026.pdf`
- Sem flag, o script assume `--drive` como padrão

**Credenciais:**
- Omie: `/root/.openclaw/secure/omie_api.env` (APP_KEY + APP_SECRET)
- Drive: `gog` com conta `medicalemagrecimento@gmail.com`
- `GOG_KEYRING_PASSWORD` via 1Password (item `gog-keyring-pass`)

---

## Skills Criadas

### deep-research-protocol (2026-04-07)
Skill para pesquisa profunda com múltiplas fontes.

- **Localização:** `/root/.openclaw/workspace/skills/deep-research/`
- **Output padrão:** HTML salvo em `/root/.openclaw/workspace/research/`

**Fontes de pesquisa (ordem):**
1. `web_search` (Brave)
2. `web_fetch`
3. Perplexity
4. Knowledge Base (memória)
5. PubMed/Scholar (para conteúdo médico)

**Níveis:**
- **Quick scan:** 5-10 min, 3-5 URLs
- **Standard:** 15-30 min, 8-12 URLs
- **Deep dive:** 30-60 min, 15-20+ URLs (spawnar sub-agent)

**Formato:** HTML com CSS inline, auto-contido, cores da marca (`#d4a84b` dourado).

---

## Skills Criadas

### omie-linha-corte (2026-04-07)
Skill para realizar linha de corte (ponto de corte financeiro) em contas correntes do Omie.

- **Localização:** `/root/.openclaw/workspace/skills/omie-linha-corte/`

### agenda-diaria-whatsapp (2026-04-07)
Skill para envio automático da agenda diária por WhatsApp via Z-API.

- **Localização:** `/root/.openclaw/workspace/skills/agenda-diaria-whatsapp/`
- **Cron ID:** `2ba465d4-3dd0-435b-bb12-1576ed6c0403`
- **Horário:** 06:00 (`America/Sao_Paulo`), todos os dias
- **Destinatários corretos:**
  - Tiaro: `5571986968887`
  - Dra. Daniely: `5571996962059`
  - Liane: `5571991574827`
- **Como enviar:** somente via `curl`/`exec` para Z-API (não usar canal whatsapp do OpenClaw)
- **Z-API:**
  - Instance: `3CF367BB00EB205F87468A74AFBCE7F1`
  - Token: `C26CFC41175FD987513C3202`
  - Client-Token: `F277815dcf4e94be7bc2861e8ae9fc369S`
  - Número conectado: `7138388708`
- **Fonte dos dados:** QuarkClinic API via script `quarkclinic_api.py`

**O que faz:**
- Zera o saldo de uma conta corrente no Omie
- Define novo ponto de partida para controle financeiro
- Cria lançamento de ajuste 1 dia antes da data de corte

**Categorias de ajuste:**
- Saldo positivo → `2.05.98` (AJUSTE DE SALDO - Despesa)
- Saldo negativo → `1.04.96` (AJUSTE DE SALDO - Receita)

**Campos corretos da API:**
- `saldo_inicial` e `saldo_data` (NÃO `nSaldoInicial` ou `dDtSaldoInicial`)
- `AlterarContaCorrente` requer: `nCodCC`, `saldo_inicial`, `saldo_data`, `descricao`, `tipo_conta_corrente`, `codigo_banco`

**Execução já realizada:**
- 2026-04-07: Caixinha (6737587708) — saldo R$40 zerado, corte em 01/01/2026, lançamento 6825963504

**Regra de segurança:** SEMPRE confirmar com o usuário antes de executar

---

## Skills Criadas

### tweet-carrossel v3.0 (2026-04-09)
Atualização obrigatória da skill de carrosséis com fluxo e specs novas.

**Fluxo obrigatório:**
1. Usuário envia tema
2. Clara cria RASCUNHO da copy
3. Clara aciona a skill `llm-council` para avaliar e refinar a copy
4. Clara incorpora o feedback do conselho e gera a COPY FINAL
5. Clara apresenta a copy final para aprovação
6. Usuário aprova ou ajusta
7. Só depois gerar imagens

**Regra crítica:** a skill `llm-council` deve ser acionada antes de apresentar a copy ao usuário.

**Regra crítica:** nunca gerar imagens antes da copy aprovada.

**Regra crítica de imagens:**
- Sempre usar NanoBanana 2 (`google/gemini-3.1-flash-lite-preview`) para gerar imagens
- Nunca usar GPT ou DALL-E para imagens de carrossel
- API key Gemini atualizada em `auth-profiles.json` (`google:manual`)

**Estrutura do carrossel:**
1. Capa: NanoBanana 2 gera foto + Pillow adiciona texto (Montserrat Black, branco + dourado `#9F8844`)
2. Slide 2: formato tweet + screenshot PubMed do paper (quando houver pesquisa)
3. Slides 3+: formato tweet com dois tipos possíveis

**Dra. Daniely na capa:**
- semblante sério (nunca sorrindo)
- blazer escuro (nunca jaleco)
- braços cruzados
- fundo de laboratório com frascos
- cápsulas douradas no canto superior direito

**Slides tweet — tipos obrigatórios:**
- TIPO A (com foto): texto no topo + foto na parte inferior ocupando ~40-45% do slide, `border-radius: 12px`
- TIPO B (sem foto): bloco inteiro centralizado verticalmente com respiro

**Slides tweet — specs obrigatórias:**
- sem ícone de mute
- sem contador de slide
- avatar: `72px`
- nome: `32px`, bold, branco
- handle: `20px`, cinza `#71767B`
- corpo: `38px`, branco `#c8c8c8`
- gap entre parágrafos: `40px`
- margens: `48-64px`

## Operação / Robustez da Clara

### Fortalecimento estrutural de execução, contexto e guardrails (2026-04-10)
Foram criadas camadas permanentes para reduzir dois problemas críticos: (1) parar no meio da execução e (2) falhas de memória/contexto/skills.

**Arquivos canônicos criados no cérebro:**
- `/root/cerebro-vital-slim/OPERATING_RULES.md`
- `/root/cerebro-vital-slim/EXECUTION_CHECKLIST.md`
- `/root/cerebro-vital-slim/CONTEXT_CANON.md`
- `/root/cerebro-vital-slim/PREFLIGHT.md`

**Mudanças no workspace:**
- `AGENTS.md` atualizado para incluir disciplina de execução (`execute until conclusion`) e leitura obrigatória de `OPERATING_RULES.md`, `CONTEXT_CANON.md` e `PREFLIGHT.md` no startup.
- `OPERATING_RULES.md` passou a concentrar regras de execução, resolução de contexto, troca de LLM, bridge e skills críticas.
- `CONTEXT_CANON.md` define a fonte de verdade por domínio e a ordem de precedência quando houver conflito de contexto.
- `EXECUTION_CHECKLIST.md` define o protocolo para tarefas longas/críticas.
- `PREFLIGHT.md` define a pré-checagem obrigatória para tarefas críticas e operacionais.

**Guardrails operacionais implementados fora do cérebro:**
- `/root/.openclaw/workspace/ops/zapi_bridge/FOLLOWUP_CHECKLIST.md`
- `/root/.openclaw/workspace/ops/preflight/preflight_check.py`
- `/root/.openclaw/workspace/ops/llm-audit/audit_llm_overrides_v3.py`
- `/root/.openclaw/workspace/ops/llm-audit/run_audit_with_telegram_alert.sh`

**Comportamento operacional agora esperado:**
- “pode seguir” = executar até conclusão
- não retornar com updates vazios de intenção
- consultar fonte canônica antes de agir em contexto ambíguo
- rodar preflight antes de tarefas críticas
- bloquear bridge se o preflight falhar
- auditar automaticamente overrides de LLM e alertar no Telegram se houver modelo proibido em produção

## Clara / Vendas

### Aprendizados de vendas incorporados à Clara (2026-04-09)
Foram analisados dois perfis de Instagram para aprender técnicas de vendas adaptáveis à Clara Concierge do Instituto Vital Slim:

- **Yuri Barbosa (`@yuribarbosaoficial`)**
  - Aprendizados principais: condução intencional, valor antes de preço, rapport breve e contextual, objeção tratada com clareza, follow-up mais elegante.
  - O que não importar: pressão, manipulação emocional, urgência artificial, linguagem agressiva de closer.

- **Oestevão Souza (`@oestevaosouza`)**
  - Análise feita por triangulação pragmática por limitação pública do Instagram.
  - Aprendizados principais: direção comercial, diagnóstico curto, foco em resultado/processo, microcompromissos claros, postura consultiva.

**Mudança aplicada:** prompt da Clara na bridge foi atualizado para incorporar esses princípios com tom premium e seguro para contexto de saúde.

**Lapidações adicionais aplicadas:**
- bloco de `modo rápido para lead quente`
- bloco de `respostas elegantes e curtas para dúvidas frequentes`
- refinamento de preço, objeções e fechamento para soar menos roteirizado e mais natural
- resposta-padrão mais forte para disponibilidade
- manejo melhor de urgência emocional sem prometer resultado
- bloco padronizado de condições comerciais, reserva e próximo passo
- revisão final com corte de pequenas redundâncias para deixar o prompt mais estável para produção

## Índice

| Data | Evento |
|------|--------|
| 2026-04-07 | Skill `omie-boletos` criada para baixar boletos do Omie ERP |
| 2026-04-07 | Skill `deep-research-protocol` instalada para pesquisa profunda multi-fonte |
| 2026-04-07 | Skill `omie-linha-corte` criada para linha de corte em contas correntes do Omie |
| 2026-04-07 | Skill `agenda-diaria-whatsapp` criada para envio automático da agenda diária por WhatsApp via Z-API |
| 2026-04-09 | Skill `tweet-carrossel` atualizada para v3.0 com fluxo de copy validado por `llm-council` antes da aprovação, NanoBanana 2 obrigatório e specs exatas de slide tweet |
| 2026-04-09 | Prompt da Clara refinado com aprendizados de vendas dos perfis de Yuri Barbosa e Oestevão Souza |
| 2026-04-09 | Regras dos boletos do Omie corrigidas: destino principal em `Boletos de Programa de Acompanhamento`, sem pasta intermediária `Pacientes` |
| 2026-04-10 | Estrutura de robustez criada para Clara: regras canônicas, checklist de execução, contexto canônico, preflight e guardrails automáticos de LLM/bridge |
