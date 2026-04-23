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

## Quarkclinic
- Agenda padrão para novos agendamentos via API: **AGENDA OPENCLAW**
- `agendaId`: `445996589`
- `profissionalId`: `240623016` (Daniely Alves Freitas)
- `clinicaId`: `227138348` (Instituto Vital Slim)
- A agenda `240623539` pode listar horários livres, mas pode bloquear criação via endpoint com erro de agenda não permitir agendamentos online.
- Ao marcar consulta, sempre consultar `/horarios-livres` da agenda padrão primeiro.
- Quando o horário exato não existir, usar o início real do slot livre mais próximo e informar isso claramente.

## Omie
- Para cadastrar paciente no Omie a partir de um nome solto, usar o fluxo canônico da skill `skills/omie-cadastro-paciente/`.
- `codigo_cliente_integracao` do cadastro vindo do Quarkclinic deve seguir o padrão `QC-<id do paciente>`.
- Não inferir cidade, estado, CEP ou complemento quando esses dados não vierem preenchidos no Quarkclinic; pedir complemento ao usuário ou manter vazio.
- Ao emitir proposta/OS no Omie com cobrança por boleto, não basta escrever isso em observação: é obrigatório preencher corretamente os campos estruturados de categoria, conta corrente, `Gerar boleto = Sim`, `Enviar também o boleto de cobrança = Sim`, tipo de pagamento `Boleto` e meio de pagamento `Boleto Bancário`.
- Quando o caso exigir recibo em vez de nota fiscal, isso deve coexistir com a configuração correta de boleto nas parcelas; uma coisa não substitui a outra.
- Depois da emissão/faturamento e geração dos boletos de paciente, baixar todos os PDFs e enviar os boletos pelo próprio tópico do Telegram, sem esperar novo pedido, sempre que o usuário tiver solicitado a emissão naquele fluxo.
- Em qualquer emissão/faturamento no Omie que dependa de conta corrente ou banco, perguntar explicitamente ao Tiaro qual banco deve ser escolhido antes de emitir, mesmo quando houver um banco usado em caso anterior.
- Em qualquer emissão de OS/NFS-e no Omie, nunca inventar ou assumir descrição de serviço. Sempre perguntar explicitamente ao Tiaro qual serviço exato/cadastro de serviço do Omie deve ser usado antes de criar a OS, especialmente quando a emissão for para nota fiscal.
- Em orçamento, OS e emissão com NFS-e no Omie, o serviço deve ser selecionado pela lista/cadastro de serviços do Omie, nunca digitado manualmente, porque é esse cadastro que puxa os dados corretos e evita divergência operacional/fiscal.
- A lista canônica de serviços do Omie deve ser mantida em `cerebro/omie-servicos.md`.
- Mapeamentos já confirmados pelo Tiaro: `Tricologia` = `SRV00016`; `Programa de Acompanhamento Intensivo` = `SRV00013`.
- Regra técnica obrigatória: para o Omie puxar a descrição fiscal completa do serviço, `ServicosPrestados` na OS deve referenciar o `nCodServico` do cadastro do serviço (`nCodServ` retornado por `ListarCadastroServico` / `ConsultarCadastroServico`), em vez de montar a descrição manualmente.
- Em NFS-e, após `FaturarOS`, a OS pode demorar para refletir `cFaturada = "S"` em `ConsultarOS` porque a prefeitura ainda não devolveu a nota autorizada. Se `FaturarOS` retornou sucesso, tratar esse intervalo como estado assíncrono normal, não como erro automático.
- Quando a emissão for com nota fiscal, habilitar sempre `Enviar o link da NFS-e gerada na prefeitura`.

## Time da clínica
- **Dra. Daniely Alves Freitas**
  - WhatsApp: `+55 71 99696-2059`
  - E-mail: `danyafreitas@hotmail.com`
- **Liane (enfermeira)**
  - WhatsApp: `+55 71 99157-4827`
  - E-mail: `enfermagem.vitalslim@gmail.com`

## Comercial / Leads
- Nunca passar preço antes de o paciente entender o valor do atendimento.
- Em leads, primeiro acolher, entender a necessidade, contextualizar o atendimento e explicar a proposta/avaliação; só depois entrar em preço.
- Quando Tiaro pedir para "chamar o conselho", usar a skill/metodologia canônica de conselho (`llm-council`) quando ela for a referência definida, e não improvisar com subagente genérico.

## Buffer Social Media
- Skill criada: `~/.openclaw/workspace/skills/buffer-social/`
- Script: `scripts/post_buffer.py`
- API key do Buffer (OIDC) salva em `/root/.openclaw/secure/buffer.env`
- Endpoint GraphQL: `https://api.buffer.com/`
- Organização: `69e90408151436756ee2629a` (Instituto Vital Slim)
- Funcionalidade: criação de posts via mutation `CreateIdea` na GraphQL API
- Testado e funcionando: criou post de teste com sucesso (`id: 69e9275415b2e6acbd361053`)

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
Antes de responder ou executar tarefas recorrentes de GitHub, Quarkclinic, WhatsApp/Z-API, Omie, time da clínica ou tweet-carrossel, consultar os arquivos canônicos correspondentes em `cerebro/`.

- **Roteamento Omie -> gpt-5.4:** qualquer pedido que envolva a API do Omie (faturamento, OS, boleto, NFe, cadastro, financeiro) roda no modelo gpt-5.4 (provider openai-codex). Kimi K2.6 trava em tool-use longo (stopReason=toolUse com payloads=0). Ver cerebro/omie.md secao Regra de roteamento de modelo.
