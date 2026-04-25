# Verdades Operacionais

Este arquivo concentra fatos operacionais canônicos que **não podem ser esquecidos**.

Use este arquivo para:
- fatos estáveis do negócio
- IDs, contas, destinos e integrações reais
- regras de domínio que dependem da operação da clínica

Não usar este arquivo para princípios universais de execução.
Para isso, consultar:
- `cerebro/execution-principles.md`
- `cerebro/success-criteria.md`
- `OPERATING_RULES.md`

## GitHub / Cérebro
- Repositório oficial do cérebro: `institutovitalslim/cerebro-vital-slim`
- URL remota correta: `https://github.com/institutovitalslim/cerebro-vital-slim.git`
- Quando Tiaro disser **"commit no cérebro"**, isso significa:
  1. atualizar os arquivos relevantes no workspace do cérebro;
  2. fazer `git commit`;
  3. fazer `git push` para o repositório oficial no GitHub.

<<<<<<< HEAD
## Skills — cérebro é fonte de verdade, workspace é runtime

- **Fonte de verdade (cérebro):** `cerebro/empresa/skills/` no repositório. Aqui ficam as definições canônicas: `SKILL.md`, `reference/`, `scripts/` de cada skill. Versionado no GitHub.
- **Runtime (VPS):** `/root/.openclaw/workspace/skills/` na VPS. É aqui que o OpenClaw/Clara efetivamente **invoca** as skills em tempo de execução.
- **Sincronia:** one-way, cérebro → workspace. Nunca o contrário.
- **Mecanismo:**
  1. **Automático via git hook** — após qualquer `git pull`, `git merge`, `git checkout` ou `git rebase` dentro do cérebro na VPS, o hook `.git/hooks/post-merge` (e irmãos) dispara `ops/skills-sync/sync-skills.sh` e espelha cérebro → workspace.
  2. **Safety-net da Clara** — no startup da sessão (passo 17 do `AGENTS.md`), Clara roda `ops/skills-sync/verify-sync.sh`. Se detectar desalinhamento, pode rodar `--fix` pra corrigir.
  3. **Manual** — qualquer um pode rodar `bash /root/cerebro-vital-slim/ops/skills-sync/sync-skills.sh` a qualquer momento. Idempotente, seguro.
- **Preservação:** o rsync é sem `--delete`, então arquivos runtime-only do workspace (caches, logs, state) **nunca são removidos** pelo sync. Só SKILL.md, reference/, scripts/ são sobrescritos com a versão do cérebro.
- **Exclusões do sync:** `_index.md`, `_templates/`, `.git/`, `logs/`, `state/` — metadados que não pertencem ao runtime.
- **Instalação do hook (uma vez só, na VPS):**
  ```bash
  cd /root/cerebro-vital-slim
  bash ops/skills-sync/install-hook.sh
  ```
- **Logs de sync:** `ops/skills-sync/logs/sync-<timestamp>.log` (gitignored)

## 🚫 Nunca rodar "reset" do onboarding neste cérebro
- Este repositório é **ambiente de produção** do Instituto Vital Slim, não template.
- A **Fase 0 do `onboarding/SETUP.md` foi removida em 2026-04-23** a pedido do Tiaro e **nunca deve ser reintroduzida nem executada** aqui.
- Mesmo que apareça em versão antiga de doc/template, **nenhum agente deve** zerar `cerebro/empresa/contexto/*`, `cerebro/areas/*/contexto/*`, `cerebro/empresa/projetos/*`, criativos de tráfego, relatórios de `gestao/reports/`, nem `cerebro/areas/vendas/bot/conhecimento.md`.
- Se o Tiaro pedir "reset" ou "limpar cérebro", **parar e confirmar por escrito** antes de qualquer ação destrutiva, e só proceder com uma tag git de segurança (`pre-reset-<timestamp>`).

## Bridge HTTPS do OpenClaw (acesso remoto)
- **URL pública:** `https://openclaw.institutovitalslim.com.br`
- **Liveness (sem auth):** `/__bridge_alive` retorna `ok`
- **Propósito:** permitir que agentes Claude rodando **fora da VPS** (ex: sandbox GitHub, Claude web) acessem o gateway OpenClaw sob HTTPS.
- **Arquitetura:** nginx + Let's Encrypt + bearer auth → proxy para `localhost:18789`. O header `Authorization` é strippado antes do upstream, então **endpoints que exigem `gateway.auth.token` do OpenClaw retornam 401 via bridge** — isso é intencional.
- **Escopo aceitável via bridge:** monitoring e leitura — `/health`, `/version`, `/__bridge_alive`, UI pública do OpenClaw Control. **NÃO** expor endpoints que disparam skills, enviam mensagens, ou operam dados de paciente. Se no futuro precisar, abrir com escopo limitado e documentar aqui.
- **Gerenciamento:**
  - Config nginx: `/etc/nginx/sites-available/openclaw-bridge`
  - Token de borda: `/root/.openclaw/secure/bridge-token.env` (permissões 0600, só root)
  - Scripts: `ops/setup/openclaw-bridge.sh` (instalar/reconfigurar) e `ops/setup/rotate-bridge-token.sh` (rotacionar)
- **Rotação de token:** quando suspeitar de vazamento (token em chat, screenshot, log), rodar `bash ops/setup/rotate-bridge-token.sh` na VPS. Nginx recarrega automaticamente e o token antigo vira 401.
- **Desligar o bridge por completo:** `rm /etc/nginx/sites-enabled/openclaw-bridge && nginx -t && systemctl reload nginx` — a URL passa a retornar 404 de default, gateway interno fica inalterado.
- **Cert Let's Encrypt:** renovação automática via `certbot.timer`. Se certbot quebrar, `certbot renew --dry-run` diagnostica.

## WhatsApp
- A comunicação operacional por WhatsApp deve usar a **bridge da Z-API**.
- Não assumir que um fluxo criado a partir de contexto Telegram consegue disparar WhatsApp automaticamente sem estar amarrado ao contexto/caminho correto.
- **ElevenLabs TTS**: respostas em áudio para pacientes que enviarem áudio via WhatsApp.
  - Chave: `/root/.openclaw/secure/elevenlabs.env` (ELEVENLABS_API_KEY)
  - Voice ID padrão: `EXAVITQu4vr4xnSDxMaL` (Rachel)
  - Modelo: `eleven_multilingual_v2`
  - Fluxo: áudio do paciente → transcrição via Whisper (OpenAI) → resposta da Clara → TTS ElevenLabs → envio via Z-API `/send-audio` com `audioBase64`
=======
## WhatsApp / Z-API
- Detalhes completos: `cerebro/whatsapp-zapi.md`
- ElevenLabs TTS: `cerebro/elevenlabs.md`
>>>>>>> 9caaa1a (Deduplicate verdades-operacionais.md and create canonical domain files)

## Quarkclinic
- Detalhes completos: `cerebro/quarkclinic.md`
- Agenda padrão: **AGENDA OPENCLAW** (`agendaId`: `445996589`)

## Omie
- Detalhes completos: `cerebro/omie.md`
- Checklist de emissão: `cerebro/omie-emissao-checklist.md`
- Serviços cadastrados: `cerebro/omie-servicos.md`
- Skill de cadastro: `skills/omie-cadastro-paciente/`
- Mapeamentos: `Tricologia` = `SRV00016`; `Programa de Acompanhamento Intensivo` = `SRV00013`
- Regra crítica: sempre perguntar banco e serviço antes de emitir

## Time da clínica
- Detalhes completos: `cerebro/time-clinica.md`

## Comercial / Leads
- Nunca passar preço antes de o paciente entender o valor do atendimento.
- Em leads, primeiro acolher, entender a necessidade, contextualizar o atendimento e explicar a proposta/avaliação; só depois entrar em preço.
- Quando Tiaro pedir para "chamar o conselho", usar a skill/metodologia canônica de conselho (`llm-council`) quando ela for a referência definida, e não improvisar com subagente genérico.

## Buffer Social Media
- Detalhes completos: `cerebro/buffer.md`

## Tweet-carrossel
- OpenClaw `v2026.4.11` possui sistema nativo de image providers.
- Para gerar imagens de carrossel, preferir provider Google com NanoBanana 2 (`google/gemini-3.1-flash-image-preview` / NanoBanana 2).
- Fallback permitido: OpenAI (`gpt-image-1`).
- Banco central de fotos reais da Dra. Daniely:
  - originais: `/root/.openclaw/workspace/fotos_dra/originais/`
  - avatares: `/root/.openclaw/workspace/fotos_dra/avatares/`
- Acervo disponível inclui looks e poses em blazer branco, vestido branco longo, blazer branco com blusa preta e saia preta, macacão vermelho e composições com Bio Meds, seringa e modelos corporais.
- Para TODA capa de carrossel, usar obrigatoriamente o pipeline `compose_cover.py` (v4).
- O sistema usa `photo_selector.py` para escolher a foto real mais adequada ao tema do acervo catalogado.
- Se nenhuma foto for adequada (score < 0.55), gerar uma **VARIAÇÃO via NanoBanana 2** usando a foto mais próxima como base:
  - Preserva identidade facial (rosto, cabelo)
  - Altera cenário, iluminação e roupas conforme o tema
  - Incluir no prompt a instrução canônica de consistência facial estrita:
    `Enable strict facial consistency mode. Prioritize the facial features from the provided reference image for all subsequent generations. Maintain the subject's identity accurately while only adapting the pose, lighting, and background. Do not alter the core facial structure.`
- Essa instrução serve para reforçar preservação de identidade, mas não substitui validação visual do resultado final.
- Gerar a IMAGEM DO CÍRCULO via NanoBanana 2 com contexto do tema.
- NUNCA gerar rosto da Dra. via IA sem referência real.
- NUNCA gerar a capa inteira com texto via image tool.
- Se a geração distorcer a fisionomia da Dra., refazer com referências mais fortes ou usar foto real original com fundo escuro.

### Estrutura de conteúdo (10 slides — Viral Content Strategy)
- Slide 1: HOOK (Pattern Interrupt) — headline ousada, max 5-10 palavras
- Slide 2: REHOOK (Open Loop) — aumenta intriga sem dar resposta
- Slide 3: Relatable Pain / Início da História — situacao identificavel
- Slides 4-7: Valor (História + Insights) — 1 ideia-chave por slide, storytelling + valor acionavel
- Slide 8: Turning Point (Momento AHA) — insight-chave, momento "salvavel"
- Slide 9: Actionable Takeaway — passos claros e praticos
- Slide 10: CTA (Engagement Trigger) — call-to-action direto no texto

### Especificações visuais dos slides
- Fundo: **branco #FFFFFF**
- Texto: **preto #000000** (cor única, sem bold, sem destaques)
- Fontes aumentadas em **20%** em relação ao padrão anterior:
  - Texto corpo: ~46px (v3) / 60px (v4)
  - Nome: ~38px (v3) / 58px (v4)
  - Handle: ~24px (v3) / 41px (v4)
- Selo verificado: azul #1D9BF0 (mantido)

### Gatilhos psicológicos
- Gap de curiosidade (curiosity gap)
- Pattern interrupt (quebrar padrões)
- Tom de prova social (social proof tone)
- Medo de perder algo (FOMO)
- Ideias contrarianas
- Recompensas rápidas (quick wins)

## Regra de operação
Antes de responder ou executar tarefas recorrentes de GitHub, Quarkclinic, WhatsApp/Z-API, Omie, time da clínica, PDF ou tweet-carrossel, consultar os arquivos canônicos correspondentes em `cerebro/`.

- **Leitura de PDF:** quando a tarefa depender de análise de PDF, usar primeiro a tool nativa `pdf`. Não assumir limitação do arquivo ou do usuário sem tentar a leitura correta. Extração por shell (ex.: `pdftotext`) é fallback técnico, não caminho principal.
- **Roteamento Omie -> gpt-5.4:** qualquer pedido que envolva a API do Omie (faturamento, OS, boleto, NFe, cadastro, financeiro) roda no modelo gpt-5.4 (provider openai-codex). Kimi K2.6 trava em tool-use longo (stopReason=toolUse com payloads=0). Ver cerebro/omie.md secao Regra de roteamento de modelo.

## Portal de Pré-Consulta IVS
- **URL:** `preconsulta.institutovitalslim.com.br`
- **Runtime:** Next.js em `localhost:3001` (PM2 gerenciado)
- **Código-fonte:** `/root/ivs-preconsulta/`
- **Dados submetidos:** `/root/ivs-preconsulta-data/` (JSONs com timestamp)
- **Envio de resumo:** síncrono no submit via `notifyTelegram()` em `src/app/api/submit/route.ts`
- **Destino:** grupo AI Vital Slim, tópico 271 (Pacientes)
- **Fallback manual:** `python3 skills/geracao-apresentacao-paciente/scripts/notificar_resumos_portal_ivs.py --force-file ARQUIVO.json`
- **Problema comum:** build do Next.js desatualizado causa erro "Could not find a production build". Solução: PM2 reinicia automaticamente ou rodar `cd /root/ivs-preconsulta && npm run build && pm2 restart ivs-preconsulta`

## Template de Apresentação de Paciente
- **Skill:** `skills/geracao-apresentacao-paciente/`
- **Template:** `assets/template-apresentacao.html` — Jinja2, dark theme, baseline aprovado do Erick (2026-04-25)
- **Script:** `scripts/gerar_apresentacao.py` — renderiza Jinja2 com placeholders dinâmicos
- **Placeholders principais:** `nome_paciente`, `idade_paciente`, `crm_medico`, `stats_section`, `diagnostico_section`, `history_section`, `exams_section`, `timeline_section`, `contexto_section`, `references_section`
- **Seções do questionário:** history e contexto são geradas automaticamente a partir dos dados do pré-consulta
- **Seções clínicas:** stats, diagnostico, exams são placeholders para preenchimento após análise dos PDFs de exames
- **Pendente:** trocar logo no template para versão oficial do brand kit (`assets/brand/logo-vital-slim-vetorizado-rgb.pdf`)
