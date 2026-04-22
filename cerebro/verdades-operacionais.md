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

### Gatilhos psicológicos
- Gap de curiosidade (curiosity gap)
- Pattern interrupt (quebrar padrões)
- Tom de prova social (social proof tone)
- Medo de perder algo (FOMO)
- Ideias contrarianas
- Recompensas rápidas (quick wins)

## Regra de operação
Antes de responder ou executar tarefas recorrentes de GitHub, Quarkclinic, WhatsApp/Z-API, Omie, time da clínica ou tweet-carrossel, consultar os arquivos canônicos correspondentes em `cerebro/`.
