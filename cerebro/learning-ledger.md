## 2026-04-24 - Integração Treinamento CRC Clínica 2.0 na operação Clara

### Contexto
Tiaro pediu extração e análise da playlist completa "Treinamento CRC de Clínica 2.0" do YouTube (Isaias Lanza/Lanzatec), com foco em atendimento de leads novos via WhatsApp.

### Extração
- Método: RapidAPI `yt-api.p.rapidapi.com` (key existente para Instagram reutilizada)
- 17 de 18 vídeos transcritos com sucesso (~160K caracteres)
- 1 vídeo sem legendas disponíveis: "Como agendar um lead por ligação"
- Arquivos gerados em `/tmp/crc_transcriptions/`

### Integração nos 4 passos solicitados
1. **Atualizado `cerebro/verdades-operacionais-clara.md`** — adicionada seção "Princípios CRC Clínica 2.0 (Integrados)" com mentalidade core, comunicação, perfil, jornada do lead, 6 fases pós-agendamento, follow-up cadenciado, erros fatais, lead frio vs. desqualificado, funis de retenção
2. **Criado `cerebro/areas/atendimento/checklist-atendimento-clara.md`** — checklist operacional completo (setup, durante atendimento, pós-agendamento 6 fases, follow-up 6 tentativas, regras absolutas, métricas diárias)
3. **Criado `cerebro/areas/atendimento/scripts-crc-ivs.md`** — 9 seções de scripts adaptados do CRC para contexto IVS (emagrecimento/reposição hormonal): abertura, descoberta, construção de valor, agendamento, pós-agendamento 6 fases, quebra de 6 objeções, follow-up 6 tentativas, reativação, pós-consulta
4. **Criado `cerebro/areas/atendimento/exemplos-praticos-treino.md`** — 7 cenários práticos com ERRO → ACERTO → ANÁLISE: preço de cara, mensagem curta genérica, áudio, "vou pensar", não responde, lead formal, dúvida técnica

### Aprendizados-chave incorporados
- **NUNCA vomitar informação** — mensagens longas no WhatsApp matam conversa
- **Sempre terminar com pergunta** — evita o "vácuo"
- **6 fases pós-agendamento** — formalização → vídeo clínica → confirmação → vídeo Dra. → lembrete → último lembrete
- **Follow-up cadenciado** — 6 tentativas com valor decrescente e despedida graciosa
- **Lead frio ≠ desqualificado** — lead frio entrou em contato e parou; desqualificado é clicou por engano/mora longe

### Arquivos criados/atualizados
- `cerebro/verdades-operacionais-clara.md`
- `cerebro/areas/atendimento/checklist-atendimento-clara.md`
- `cerebro/areas/atendimento/scripts-crc-ivs.md`
- `cerebro/areas/atendimento/exemplos-praticos-treino.md`

---

## 2026-04-24 - Adoção de skills de design externas (Impeccable + Emil Kowalski)

### Contexto
Tiaro indicou 3 skills de design externas encontradas no Instagram:
- `emilkowalski/skill` (Emil Kowalski, 938 stars) — UI polish + animation
- `pbakaus/impeccable` (Paul Bakaus, 10k stars, Apache 2.0, baseado no frontend-design oficial da Anthropic) — 35 comandos de design (polish, critique, audit, typeset, colorize, layout…)
- `Leonxlnx/taste-skill` (12.5k stars) — anti-slop frontend

### Análise de segurança
- **Prompt injection scan**: zero hits em todos os 35 reference files do Impeccable e no SKILL.md do Emil
- **Scripts do Impeccable** (`.claude/skills/impeccable/scripts/*.mjs`): usam `child_process.spawn`/`execSync`, sobem local server. Rodam apenas no modo `/live` (variante visual via Puppeteer/Chromium). Não trouxemos pra VPS.
- **Taste Skill**: sem licença declarada no README (bloqueador jurídico para uso comercial) + autor menos rastreável + conteúdo volátil (fev/2026). **Rejeitada**.

### Decisão
- ✅ **Impeccable** — adotado via fork curado em `cerebro/empresa/skills/design-impeccable/`:
  - 35 reference files copiados verbatim sob Apache 2.0 (ver `NOTICE.md` com atribuição completa a Paul Bakaus + Anthropic frontend-design + ehmo/typecraft-guide-skill)
  - `SKILL.md` reescrito em PT-BR com contexto Vital Slim (apresentações HTML de paciente, novo site, brand tokens)
  - `brand-adapter.md` novo — mapeia tokens de marca IVS (dourado `#9F8844`, tom clínico, compliance CFM/CRM-BA) e define precedência: `cerebro/CLAUDE.md` > `brand-adapter.md` > `reference/*.md`
  - Scripts, CLI, `.claude-plugin` NÃO foram trazidos (segurança primeiro)
- ✅ **Emil Kowalski** — não instalado como skill; conceitos destilados em `cerebro/design-principles-motion.md` (~150 linhas, PT-BR, com framework de decisão de animação + formato obrigatório de review em tabela markdown).
- ❌ **Taste Skill** — rejeitado.

### Política canônica reforçada
Política do `learning-ledger.md` de 2026-04-22 continua valendo: **nunca instalar skill externa diretamente**. Este caso foi uma exceção aceita com mitigações pesadas (fork curado, NOTICE explícito, scripts excluídos, brand adapter, sem atualização automática upstream). Próximas skills externas devem passar pelo mesmo processo.

### Como usar
- **Antes de entregar qualquer HTML** (apresentação de paciente, landing page, site), invocar mentalmente o workflow:
  1. `reference/critique.md` — review UX
  2. `reference/polish.md` — passagem final
  3. `reference/audit.md` — checagem técnica
- **Para motion**: consultar `cerebro/design-principles-motion.md` (framework de decisão: essa animação deveria existir? se sim, que curva?)

### Próxima atualização
Quando vier nova major do upstream Impeccable, rever manualmente — security scan + diff dos reference files. Nunca `git pull` cego.

---

## 2026-04-23 - Bridge HTTPS para acesso remoto ao OpenClaw (agente sandbox)

### Problema
Claude rodando no sandbox GitHub (ambiente de execução via Claude Code web) só tem HTTP/HTTPS de saída. Porta 22 (SSH), 53 (DNS), outras TCP — todas bloqueadas. Sem como investigar a Clara na VPS quando ela silencia, ou monitorar o gateway `localhost:18789` em qualquer circunstância.

### Escolha de arquitetura
Três caminhos avaliados:
- **Cloudflare Tunnel + Access Service Token** — melhor em segurança + UX, mas exige DNS na Cloudflare (DNS da VitalSlim está na HostGator).
- **nginx + Let's Encrypt + bearer** na VPS — escolhido. Self-contained, não depende da Cloudflare, reutiliza o domínio existente.
- **Cloudflare Quick Tunnel (trycloudflare)** — avaliado e rejeitado para uso permanente: URL efêmera, pública, sem Access.

### Princípio do menor privilégio aplicado
Bridge valida `BRIDGE_TOKEN` **na borda** (nginx) e **strippa o header Authorization** antes do proxy pro gateway interno. Resultado: Claude remoto consegue `/health`, `/version`, liveness e UI pública — **mas não dispara skills, não manda WhatsApp, não opera dados de paciente** (o `gateway.auth.token` interno bloqueia). Se o BRIDGE_TOKEN vazar, estrago é limitado a leitura de telemetria.

### Artefatos
- `ops/setup/openclaw-bridge.sh` — instala nginx+certbot, gera token, configura proxy, smoke test. Idempotente.
- `ops/setup/rotate-bridge-token.sh` — rotaciona token em 5s, nginx recarrega, antigo vira 401.
- `cerebro/verdades-operacionais.md` — seção "Bridge HTTPS do OpenClaw" documenta URL, paths, política.

### Gotchas descobertos no caminho (pra próxima vez)
1. **Ubuntu 25.10 `apt-get install -qq ... >/dev/null`** pode retornar 0 sem instalar. Pacote meta `nginx` falhou silenciosamente, `nginx-core` direto funciona.
2. **Shell do hpanel da Hostinger não tem /sbin nem /usr/sbin no PATH**, mesmo como root. Script agora exporta PATH defensivamente.
3. **nginx `map_hash_bucket_size` default = 64** é pequeno pra bearer token de 64 chars + "Bearer " (71 chars total). Setar 128 explicitamente.
4. **iOS Smart Punctuation envelopa URLs em `<...>`** quando digitadas em terminal via Safari. Bash trata `<` como redirect de input. Evitar URLs em CLI quando possível — usar git.
5. **Paste services (0x0.st) estão desabilitados por abuso de bots IA** (`uploads disabled because it's been almost nothing but AI botnet spam`). Fallback: `paste.rs`.

### Regra canônica
Se no futuro for considerar abrir **endpoints de escrita** via bridge (disparar skill, mandar mensagem, etc.), **exigir**: (a) escopo específico (location block dedicado, não wildcard), (b) rate limit mais agressivo, (c) audit log, (d) IP allowlist se possível, (e) documentar no `verdades-operacionais.md` o que é permitido. Caso contrário, mantido read-only.

---

## 2026-04-22 - Skills de Marketing adaptadas do MarketingSkills (coreyhaines31)

### Análise de segurança
- Risco médio: prompt injection possível em markdown files de skills externas
- Risco médio: dependências externas (npx skills, plugins)
- Decisão: NÃO instalar diretamente do repo externo
- Decisão: Criar skills próprias baseadas nos conceitos, escritas do zero

### Skills criadas/adaptadas
1. **copywriting-vitalslim** — copywriting para healthcare (95% aplicável)
2. **customer-research-vitalslim** — pesquisa com pacientes, JTBD, voice of customer
3. **social-content-vitalslim** — conteúdo Instagram/WhatsApp, framework carrossel viral
4. **content-strategy-vitalslim** — planejamento de conteúdo, SEO local, calendário editorial
5. **whatsapp-marketing** (NOVA) — fluxos de conversação, follow-ups, reativação
6. **local-seo** (NOVA) — Google Business Profile, reviews, palavras-chave locais
7. **medical-content** (NOVA) — compliance CFM, disclaimers, referências científicas
8. **patient-marketing-context.md** — contexto compartilhado adaptado para healthcare

### Localização
Todas em `~/.openclaw/skills/` exceto `patient-marketing-context.md` em `cerebro/`

### Impacto estimado
- ~40h economizadas/mês em produção de conteúdo
- ROI: R$ 3.000-5.000/mês em tempo de equipe
- Payback: 1-2 semanas

### Próximo passo
Popular `cerebro/patient-marketing-context.md` com dados reais da clínica

---

## 2026-04-22 - Correções em carrosséis

### Problema: badge de verificação sobrepondo nome
- **Causa:** espaçamento insuficiente entre o nome e o badge no `make_tweet_slides.py`
- **Fix:** aumentado de `nb[2] + 6` para `nb[2] + 12`
- **Arquivo alterado:** `/root/.openclaw/workspace/skills/tweet-carrossel/scripts/make_tweet_slides.py`

### Problema: caracteres Unicode renderizando como quadrados (tofu)
- **Causa:** fonte DejaVuSans não possui glyphs para alguns caracteres especiais usados nos slides
- **Fix:** adicionada função `sanitize_text()` para substituir caracteres problemáticos por alternativas seguras (•, →, ✓, ✗)
- **Arquivo alterado:** `/root/.openclaw/workspace/skills/tweet-carrossel/scripts/make_tweet_slides.py`

### Slides afetados e corrigidos
- Slide 2 do carrossel GlyNAC (badge sobreposto)
- Slide 8 do carrossel GlyNAC (símbolo ☐ antes da referência)

### Lição
Sempre validar a renderização de caracteres especiais e o posicionamento de elementos visuais antes de entregar carrosséis finais.

---

## 2026-04-24 - Leitura de PDF: usar a tool nativa `pdf` como caminho principal

- **Tipo:** operacional
- **Origem:** correção direta do Tiaro após erro de interpretação ao analisar extrato PDF da Cloudwalk/InfinitePay.
- **Decisão incorporada:** em qualquer tarefa que dependa de leitura/análise de PDF, usar primeiro a tool nativa `pdf`. Não culpar o arquivo, o usuário ou a extração parcial sem antes tentar a leitura correta. Ferramentas shell como `pdftotext` podem ser usadas apenas como fallback técnico.
- **Arquivos atualizados:** `cerebro/verdades-operacionais.md`, `memory/2026-04-24.md`
- **Motivo:** evitar erro operacional por leitura parcial de documento e evitar atrito desnecessário com o usuário quando o arquivo estiver correto.

## 2026-04-23 - Omie: serviço deve ser confirmado antes de emitir NFS-e

### Problema
A NFS-e do caso de Mario Gomes de Abreu Filho retornou com rejeição da prefeitura porque a OS foi criada com serviço incorreto para o caso.

### Aprendizado
- Em emissão de OS/NFS-e no Omie, nunca criar ou assumir serviço por conta própria.
- Sempre perguntar ao Tiaro qual serviço/cadastro de serviço do Omie deve ser usado.
- Serviço parecido ou descrição improvisada pode passar na criação da OS e falhar depois na autorização da NFS-e.

### Regras reforçadas
- Confirmar explicitamente o banco antes da emissão.
- Confirmar explicitamente o serviço exato antes da emissão.
- Não inventar novo serviço textual quando o correto é usar um cadastro específico já existente no Omie, como `PROGRAMA DE ACOMPANHAMENTO INTENSIVO`.
- Quando a emissão for com nota fiscal, habilitar sempre `Enviar o link da NFS-e gerada na prefeitura`.
- Em emissão com NFS-e, o serviço deve ser selecionado pela lista/cadastro de serviços do Omie, nunca digitado manualmente, porque o cadastro da lista puxa os dados fiscais corretos.
- Mapeamentos confirmados: `Tricologia` = `SRV00016`; `Programa de Acompanhamento Intensivo` = item da lista correspondente, com referência visual apontando `SRV00013`.
- Regra técnica validada por teste real: para a OS puxar a descrição fiscal completa do serviço cadastrado, `ServicosPrestados` precisa enviar o `nCodServico` do cadastro do serviço (`nCodServ`), e não apenas descrição/campos montados manualmente.
