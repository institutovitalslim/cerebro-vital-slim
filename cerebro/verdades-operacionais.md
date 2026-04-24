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

## WhatsApp / Z-API
- Detalhes completos: `cerebro/whatsapp-zapi.md`
- ElevenLabs TTS: `cerebro/elevenlabs.md`

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
Antes de responder ou executar tarefas recorrentes de GitHub, Quarkclinic, WhatsApp/Z-API, Omie, time da clínica ou tweet-carrossel, consultar os arquivos canônicos correspondentes em `cerebro/`.

- **Roteamento Omie -> gpt-5.4:** qualquer pedido que envolva a API do Omie (faturamento, OS, boleto, NFe, cadastro, financeiro) roda no modelo gpt-5.4 (provider openai-codex). Kimi K2.6 trava em tool-use longo (stopReason=toolUse com payloads=0). Ver cerebro/omie.md secao Regra de roteamento de modelo.
