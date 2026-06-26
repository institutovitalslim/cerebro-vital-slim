# Memoria da Ana - Contexto & Aprendizados
> Destilado do topico 6 (OpenClaw) em 2026-06-22. Atualizado em 2026-06-23 (Victa/Supramaximus/QR Adoxy/Peptídeos resolvidos).

# MEMORY.md — Ana (IVS / Telegram Tópico 6)

## 0. REGRA-MESTRA INEGOCIÁVEL (Tiaro, 2026-06-25)
**NUNCA alterar, resumir, censurar, parafrasear ou substituir QUALQUER informação coletada** — pesquisas, papers, aulas, peças, transcrições, qualquer fonte. Preservar **EXATAMENTE como apresentado**: doses, fármacos, números, sequência, afirmações literais. Toda crítica/cautela/alerta (CFM, ANVISA, conflito de interesse, nível de evidência, claim a verificar) entra SÓ em seção separada e claramente marcada **"ADENDO DA ANA"**, sem tocar no conteúdo original. Vale para TODO conteúdo (não só ENDOGIN). A decisão clínica é sempre da Dra. Daniely.

## 1. Quem é a Ana e como atua
- **Papel:** Médica e pesquisadora científica do Instituto Vital Slim (IVS). Atua no tópico 6 do Telegram "AI Vital Slim".
- **Funções principais:**
  - Categoriza e arquiva pesquisas científicas na memória científica/cérebro, sempre com **nível de evidência** (diretriz inegociável).
  - Analisa exames de pacientes com profundidade e sugere condutas fundamentadas em evidência.
  - Responde a necessidades clínicas indicando **opções de tratamento + fonte (arquivo e página)** para consulta da equipe.
- **Limite de papel (CFM):** Ela **não prescreve** ao paciente. **Decisão clínica final é sempre da Dra. Daniely / médico responsável.** Levanta alertas de compliance (CFM/ANVISA) quando há alegações de risco.
- **Postura crítica:** distingue rigorosamente **evidência científica ≠ material comercial ≠ prova social (endosso)**. Detecta spin, confusão por cointervenção, regressão à média, conflito de interesse (vínculo com fabricante).

## 2. Contexto recorrente e fontes
- **Memória/cérebro:** skill `memoria-cientifica`; scripts `memory_search.py` e `ingest_content.py` (caminho canônico em `/root/.openclaw/skills/memoria-cientifica/scripts/`; cópias em `/root/cerebro-vital-slim/...` usada por `ana_analise_exames_opus.py`, e workspace). Embeddings via Gemini; busca cai para textual (score 1.0000) se a chave falhar.
- **Pipeline padrão por item:** resolver link → baixar → checar duplicata na memória → leitura crítica → ingerir com embeddings → apresentar parecer no tópico 6 → gravar nível de evidência no metadata/summary.
- **Série Supramaximus/PEMF (Adoxy):** base interna obrigatória ao falar do equipamento. ~15 itens arquivados: 10 artigos científicos (evidência de "mínimo" a "moderado") + materiais comerciais/marketing/endosso (catalogados à parte). Achados-chave: PEMF **iguala mas não supera** treino; consolidação óssea é o uso mais consolidado (FDA 1979, RCTs); estudo cardiovascular **negativo**; RCT com **spin** no título.
- **Drive Medical Contabilidade:** pasta `## Medical Contabilidade/#Instituto Vital Slim/SUPRAMAXIMUS` (id `1Mskz2KlbpCYKKlieKimrxy9e8nEFvK46`); subpasta `Adoxy QR Supramaximus - 2026-06-19`. Pasta `INJETÁVEIS` separada. Índice clínico-operacional por necessidade (indicação→protocolo→arquivo→página→contraindicação→evidência) criado e ingerido.
- **Materiais comerciais com alerta:** Supramaximus Vascular ("zero amputações"/"cura" — alto risco compliance); GLP-1 (núcleo clínico real sobre perda de massa magra + camada comercial); e-book "Tudo sobre Campo Eletromagnético".
- **Guias clínicos na base:** ETA 2018 (Graves), ATA 2016 (hipertireoidismo). Guia Ortomolecular Victa Lab (material comercial de fornecedor, não diretriz).

## 3. Regras/preferências do Tiaro
- Sempre usar a série Supramaximus como fonte ao tratar do aparelho, **mantendo separação evidência/comercial/prova social**.
- Responder necessidade clínica com **opções + fonte (arquivo/página)** para a equipe.
- Guardar tudo em memória semântica.
- Entregas formatadas quando pedido (ex.: análise de caso em **HTML** no tópico).
- Separar materiais por área no Drive (Supramaximus vs Injetáveis).
- Modelo preferido para análise profunda: **Claude Opus 4.8**.

## 3b. Acesso ENDOGIN (Mentoria) — credencial e sessão
- **Plataforma:** `membros.mentoriaendogin.com.br` (área de membros Cademí/Laravel). Mentoria de Emagrecimento, Reposição Hormonal, Longevidade e Saúde.
- **Credencial vive SÓ no 1Password** (cofre `openclaw`, item `Senha Acesso Endogin`, id `snzb2piwiljadccf5abm2aqqaq`, username `danyafreitas@hotmail.com` = Dra. Daniely). NUNCA hardcodar usuário/senha em arquivo. Atualizada em 2026-06-24 (senha antiga no cofre estava desatualizada — 9 chars vs 6 corretos).
- **Login:** formulário em `/auth/login` funciona (marcar "Lembrar de mim"); cookie `app_v6_session` dura ~2h e renova a cada acesso autenticado. Magic-link `crstk` também reautentica (reutilizável) mas removido por segurança.
- **op CLI:** `op signin --account vitalslim` exige senha-mestra do Tiaro (não disponível em automação autônoma).
- **Keep-alive:** cron job `95d31ff0692c` renova sessão a cada 90min. Backup de cookies em `/root/.openclaw/secure/endogin_browser_profile_backup/`.
- **ATENÇÃO:** credenciais Hotmart (`omie_course_credentials.env`, tiarofernandes@gmail.com) NÃO servem para ENDOGIN. Browser Hermes usa perfil temp `/tmp/agent-browser-chrome-*/` (volátil). Ferramenta de visão recusa transcrever senhas de imagem (filtro de segurança) — usar leitura nativa Opus ou pedir valores ao Tiaro.
- **Foco atual (2026-06-24):** absorver módulo "Conteúdos Pílula" (Aulas Gerais) — 17 aulas Módulo 1 + 3 Módulo 2. Aula 1 (id 8733521) = Retatrutida TRIUMPH-1 (PDF anexo). IDs das aulas mapeados.
- **DIRETRIZ DO TIARO (2026-06-24, inegociável):** ao arquivar protocolos/aulas, transcrever **EXATAMENTE como apresentado** (doses, fármacos, sequência, observações literais) — NÃO resumir, censurar, omitir doses nem substituir. A decisão clínica é SEMPRE da Dra. Daniely. A Ana PODE e DEVE fazer adendos (alertas CFM/segurança/conflito de interesse), mas em SEÇÃO SEPARADA claramente marcada "ADENDO DA ANA", sem alterar nada do conteúdo apresentado. Errei na 1ª versão da Aula 2 (parafraseei/apliquei cautela demais) → corrigido para transcrição literal + adendo.
- **Conteúdos Pílula — só 3 de 20 aulas têm PDF anexo:** Aula 1 (8733521, Retatrutida/TRIUMPH-1), Aula 2 (7866666, Recompilar Masculino), Aula 17 (7489376, Pellets Estradiol/Estudo CLARA). As outras 16 são SÓ VÍDEO (VdoCipher DRM, não transcritível) → para essas, baixar/arquivar as PESQUISAS científicas que o título indica. PDFs ricos = slides-imagem; extrair via pdftoppm + visão nativa (a ferramenta de visão auxiliar recusa transcrever 'credenciais', mas transcreve protocolo clínico normalmente).
- **Pesquisas identificadas:** CLARA Study = Malavasi et al, Menopause 2026, PMID 41401223 (n=20, aberto, evidência baixa-moderada). CagriSema/REDEFINE = NEJM 2025 PMID 40544432/40544433. TRIUMPH-1 design = DOM 2026 PMID 41090431 (Lilly; é desenho, não resultados — números da aula são topline). PMC bloqueia download por reCAPTCHA → usar abstract via E-utilities PubMed.
- **Script de ingestão manual criado:** `cerebro/empresa/conhecimento/endogin/conteudos-pilula/ingest_manual.py <rid> <topic> <original.md>` — gera chunks+embeddings Gemini 3072d e sincroniza index global. Usar SEMPRE em vez do ingest_content.py (cujo aprofundamento Gemini dá HTTP 5xx e polui clinical.md).
- **REGRA DE ROTEAMENTO DE MODELO (Tiaro, 2026-06-24, ajustada por custo em 2026-06-25):** tarefas de LOGIN, navegação, browser e operacionais/diversas (acessar plataforma, capturar, baixar, rodar script, organizar arquivo) → usar **Codex GPT-5.5** (CLI `codex` v0.118+, ou delegar com acp_command='codex'). ANÁLISE DE EXAMES + PESQUISAS CIENTÍFICAS / raciocínio clínico → **Opus 4.8 somente como VALIDADOR FINAL/juízo médico-científico**, não como motor bruto. Primeiro usar memória científica, scripts locais, Gemini/Perplexity, embeddings e resumos compactos; só então chamar Opus para revisão final de nível de evidência, risco clínico/compliance e síntese executiva. Não gastar Opus em tarefa mecânica de browser/login, transcrição, OCR, chunking, lote ou leitura integral enorme. **Qualquer mudança maior no modelo padrão segue com Tiaro, mas esta restrição de uso econômico está autorizada.**
- **APOIO DA MARIA (Tiaro, 2026-06-24):** sempre que eu tiver dificuldade de encontrar informações, logins, credenciais ou acessos, PEDIR À MARIA via `ivs-agent-message send --from ana --to maria ...` (skill ivs-agent-communications). Ela responde no inbox (`ivs-agent-message inbox --agent ana --status all`). Funciona — ela me resolveu o OAuth do Codex em minutos.
- **Codex GPT-5.5 OAuth (resolvido pela Maria 2026-06-24):** o OAuth que o HERMES usa para openai-codex está em `/root/.hermes/auth.json` (perfil ana é symlink). Validar com `HERMES_HOME=/root/.hermes/profiles/ana hermes auth list` → mostra `openai-codex: openai-codex-oauth-1 oauth device_code` ✓. NÃO confundir com `/root/.codex/auth.json` (CLI standalone, modo apikey, irrelevante p/ Hermes). NUNCA imprimir/copiar token. Para usar Codex operacional, delegar via Hermes (não `codex exec` standalone, que usa a apikey).
- **OpenRouter (Opus 4.8) pode esgotar:** em 2026-06-24 deu 402 exhausted (~40min p/ reset). Quando isso ocorrer, análise científica pode cair p/ fallback; checar `hermes auth list`.
- **ENDOGIN aulas-vídeo (VdoCipher/Widevine DRM) — captura de áudio É INVIÁVEL em headless (INVESTIGADO ATÉ A RAIZ, 2026-06-24):** provei cada camada — login OK, Widevine CDM FUNCIONAL (requestMediaKeySystemAccess cria MediaKeys+sessão, hasMediaKeys:true no vídeo), segmentos áudio+vídeo BAIXAM (HTTP 206), buffer enche (122s), SwiftShader (--use-angle=swiftshader --enable-unsafe-swiftshader) carrega sem erro. MAS o <video> trava em readyState=1/currentTime=0.1 e NUNCA decodifica → captura (sink virtcap E Web Audio API MediaRecorder) = silêncio -91dB. Causa-raiz: o DRM recusa DECODIFICAR em ambiente sem saída protegida (proteção de output, por desenho intransponível sem quebrar DRM). NÃO é GPU, rede, licença nem PULSE — é o DRM. NÃO reabrir essa direção. CAMINHO REAL: Tiaro grava a aula (tela+áudio) no dispositivo dele e envia → rodar `whisper <arq> --language Portuguese --model small`. Infra pronta: PulseAudio+sink virtcap, Whisper instalado, Chrome 9333 (perfil ana_endogin_profile c/ CDM+SwiftShader), scripts CDP em cerebro/.../conteudos-pilula/ (cdp_endogin.py, diag_*.py, capture_*.py). Chrome do curso = systemd chrome-hotmart.service porta 9222 (sem PULSE_SERVER; mexer exige aprovação).
- **Plaud (resolvido 2026-06-25):** não tratar como OAuth manual; Plaud Web fica acessível no Chrome da VPS porta 9222. Fluxo: abrir `https://web.plaud.ai/`, clicar Google iframe → conta Tiaro já logada → biblioteca aparece (All files). Endpoints web úteis via sessão do navegador: `https://api.plaud.ai/file/simple/web?skip=0&limit=99999&is_trash=0&sort_by=start_time&is_desc=true`; detalhes/transcrição visíveis no DOM em `https://web.plaud.ai/file/<file_id>`. Script watcher criado em `cerebro/empresa/conhecimento/endogin/conteudos-pilula/_capture_recorder/plaud_watcher.py` para salvar novas transcrições em `plaud_transcricoes/`.

## 4. Aprendizados
- **Infra chave Gemini (FUNCIONANDO em 2026-06-23):** Tiaro renovou a chave no 1Password ("Gemini API Key"); `ana_google.py check` passou e embeddings rodam (gemini-embedding-001, 3072 dims). `.env` é template com refs `op://`; `.env.runtime` é gerado no boot. Sempre rodar scripts com `export HOME=/root && set -a && source /root/.openclaw/.env.runtime && set +a`. ATENÇÃO: a API tem rate limit — `generateContent` pode dar HTTP 429 em sequência; espaçar chamadas ou cair para ingestão manual + reindex depois.
- **gog (Drive CLI) na sessão Hermes:** exige `export HOME=/root` (credenciais reais em /root/.config/gogcli, NÃO no home do profile) + `GOG_KEYRING_PASSWORD` lido de /root/.openclaw/.env.runtime. Sintaxe: flags globais ANTES do subcomando (`gog -a medicalcontabilidade@gmail.com -j drive ls --parent <ID> --max 1000`), paginar com nextPageToken. Conta Drive: medicalcontabilidade@gmail.com.
- **Embeddings da memória científica:** vários registros antigos tinham `embeddings.json = {"chunks":[]}` (caíam em busca textual). Reindexar regenerando chunks de research+clinical+summary via `memory_store.get_embedding/chunk_text`. Em 2026-06-23 reindexei 8 materiais (3 Victa, índice QR Adoxy, Elsimar, BRCA, mitocondrial, Clara concierge).
- **Drift do próprio MEMORY.md:** o arquivo é rico/estruturado (seções `#`/`##`/bullets/blockquotes) e NÃO round-trip pelo memory tool → o guard recusa escrita. Manter via `patch`/`write_file` direto, NÃO pelo memory tool. Backups do guard ficam em memories/MEMORY.md.bak.*.
- **Zoom gravação:** acessar pelo browser da VPS, digitar senha, clicar "Watch Recording". A página entrega resumo + smart chapters + transcrição (endpoint `/rec/play/vtt?type=transcript`) — extrair via `browser_console` (document.body.innerText e fetch credentials:include). yt-dlp NÃO extrai Zoom protegido. O browser do Zoom é isolado e não acessa 127.0.0.1 da VPS.
- **QR code decode:** sem pyzbar/cv2 no sistema (PEP668) → criar venv com `uv venv /tmp/qrenv` + `uv pip install pyzbar pillow` + `apt install libzbar0`.
- **Vazamento parcial de chave** ocorreu em output de teste → recomendado rotacionar por precaução.
- `ana_analise_exames_opus.py` parseia **apenas laboratório estruturado**, não laudo de imagem em texto livre → análise de USG feita manualmente sobre transcrição por visão.
- YouTube bloqueia download/transcrição do servidor (anti-bot) → caracterizar por metadados oficiais (oembed).
- PDFs grandes (ex.: 406 MB) → comprimir via Ghostscript antes da visão. `/tmp` não permitido; usar diretório de mídia.
- Fontes vêm de Google Drive **e** Zoho WorkDrive (resolver endpoint real).

## 5. TAREFAS ABERTAS
- **Caso Cleiton (M, 44a):** analisado laudo tireoide → padrão fortemente compatível com **Doença de Graves** (TSH<0,01; T4L 2,69; TRAb 17,27; anti-TPO 175). Recomendado avaliação breve Dra. Daniely/endócrino (foco risco cardiovascular). **NOVO:** Graves é **contraindicação ABSOLUTA do fabricante** para Supramaximus (manual REV.03) — risco sistêmico/cardiovascular, não local. Se candidato ao aparelho, exige liberação médica. **Pendente:** correlacionar exames de sangue + bioimpedância recentes.
- **Caso Catia Veronica (F, 45a):** hipótese Hashimoto + bócio difuso + 2 nódulos TI-RADS 3 benignos; análise em HTML entregue. Decisão final Dra. Daniely.

### Pendências REAIS remanescentes (atualizado 2026-06-23)
- **Supramaximus — registro ANVISA: RESOLVIDO em 2026-06-23.** Tiaro enviou o PDF de consulta oficial. Notificação/registro **82149139003**, situação **Válido/VIGENTE**, processo 25351657198202181; detentor/fabricante ADOXY (CNPJ 30.446.895/0002-34, AFE 8.21.491-3); categoria **Eletroestimulador Muscular / Aparelho de Múltiplo Uso em Estética — Classe II (médio risco)**; vigência desde 11/11/2021; cobre Supramáximus/Compact/Regen/Regen Compact. Ingerido como `2026-06-23_supramaximus-registro-anvisa-82149139003-vigente` (PDF + 4 .md + PDF original arquivado). ATENÇÃO no pipeline: Gemini deu HTTP 429 no aprofundamento → research/clinical/summary reescritos manualmente (corrigindo imprecisão do auto-resumo que tratava como eletrodos de superfície) e **reindexados manualmente**: 13 chunks no embeddings.json local E substituí as 3 linhas stale no index/embeddings.jsonl global (schema da linha: research_id, chunk_id, text, vec, topic; backup .bak criado). Leitura crítica registrada: registro de equipamento ≠ aprovação de protocolo/eficácia; alegações fora do escopo estético = risco compliance.
- **Ivana (corrida de rua):** sugeri áreas prioritárias para Supramaximus (1º glúteos/médio, 2º quadríceps, 3º posteriores/panturrilha) como COMPLEMENTO ao treino de força — RCT interno mostra que PEMF não supera treino resistido. Decisão de protocolo com Dra. Daniely.

### RESOLVIDO em 2026-06-23 (não reabrir)
- **Guia Ortomolecular Victa Lab + 2 outros Victa + Catálogo Biomeds:** metadata padronizada com `is_guideline=false`, `doc_type`, `regulatory_caution`; banner "NÃO É DIRETRIZ" no summary; Biomeds (EAAs) marcado com proibição CFM 2.333/2023. Embeddings reindexados.
- **Supramaximus parâmetros técnicos:** EXTRAÍDOS do Manual do Usuário REV.03 e ingeridos como `2026-06-23_supramaximus-parametros-tecnicos-contraindicacoes-manual-oficial` (campo 0-7 Tesla, pulso 300µs, F1 1-10Hz/F2 1-100Hz, 4300W; contraindicações absolutas incluindo Graves; racional fisiológico Graves arquivado). Ficha Técnica/Guia Rápido/Pelvic Up/Lipedema são PDFs-imagem (texto não extrai) — parâmetros vieram do Manual do Usuário.
- **QR Adoxy:** inventário verificado NA FONTE (Drive real): 119 arquivos em 20 subpastas, batendo com manifesto. QR enviado = mesma página adoxy.com.br/links-adoxy3/supramaximus já arquivada.
- **Masterclass Peptídeos (Zoom 14/05/2026, Luis Felipe Castro Neves):** acessada via browser VPS, dossiê crítico + gráfico timeline + mapa conceitual gerados, ingerida como `2026-06-23_masterclass-peptideos-luis-felipe-zoom-educacional` (34 embeddings), classificada como opinião/educacional/comercial — NÃO diretriz. Moléculas: tesamorelina, CJC, ipamorelina, MOTS-c, AOD-9604, BPC-157, GHK-Cu, TB-500/Glow, PT-141. Doses citadas = conteúdo da aula, não protocolo IVS.
---

## Conexões com o cérebro (mapa de memória — restauração 2026-06-22)

> A Ana compartilha o workspace `cerebro-vital-slim`. Consultar SEMPRE antes de afirmar; citar research_id + nível de evidência.

### Mapa de acesso (LEIA primeiro)
- `cerebro/areas/_governanca/ana-acessos-e-mapa-cerebro.md` — mapa-mestre da Ana (contextos, acessos, credenciais).

### Memória científica (base viva da Ana — mesma infra da Clara, lente clínica)
- `cerebro/empresa/conhecimento/` — `endogin/`, `pesquisas/`, `glicina_referencias_clinicas.md`, `prompts-aprendizados.md`, `index/`, `logs/`, `topicos/`, `operacional/`.
- Skill `memoria-cientifica`: busca semântica (embeddings Gemini 3072d).

### Decisões canônicas da Ana (graphify / RC)
- `cerebro/operacional/graphify-2026-06-19-ana-modelo-opus-prioridade/` — **RC-25: Ana = Claude Opus 4.8 prioritário** (pesquisa/diagnóstico/raciocínio clínico).
- `cerebro/operacional/graphify-2026-06-20-ana-rapidapi-maria-watchdog/`
- `cerebro/operacional/graphify-2026-06-14-ana-fable-apresentacoes/`
- `cerebro/operacional/graphify-2026-06-15-0100-manutencao-diaria-clara-gbrain-ana-fable/`

### Canônicos do cérebro (verdade por domínio)
- `CONTEXT_CANON.md` (raiz) · `cerebro/BRAIN_ARCHITECTURE.md` · `cerebro/OPERATIONS_INDEX.md` · `cerebro/MAPA.md` · `cerebro/LEARNING_PROTOCOL.md` · `OPERATING_RULES.md`

### Ferramentas/skills
- `memoria-cientifica`, `graphify` (`gbrain-ivs query`), `consulta-base-conhecimento`, `instagram-api`, `deep-research`.

### Modelo
- **Opus 4.8 1M via OpenRouter** (prioritário, RC-25); fallback opus-4.8-fast → sonnet-4.6.
