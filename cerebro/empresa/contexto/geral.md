# Instituto Vital Slim

## O que fazemos
Clínica médica premium localizada em Lauro de Freitas-BA (região metropolitana de Salvador), especializada em Emagrecimento, Reposição Hormonal, Longevidade e Saúde integral. Atendemos predominantemente através de Programas de Acompanhamento médico de 3, 6 ou 12 meses.

## Produtos e Serviços
- **Programa de Acompanhamento 3 meses** — produto principal de entrada
- **Programa de Acompanhamento 6 meses** — produto intermediário
- **Programa de Acompanhamento 12 meses** — produto de maior valor e comprometimento
- **Consulta médica avulsa** — porta de entrada; não é o foco comercial
- **Bioimpedância** — serviço complementar, sem foco comercial ativo

## Público-alvo (Avatar Mestre)
**"A Mulher Que Não Se Reconhece Mais no Espelho"**

- Mulher, 30–45 anos (core), com personas secundárias até 60 anos
- Casada, com filhos, trabalha muito (emprego + casa)
- Classe média / média-alta
- Chegou ao sobrepeso/obesidade após evento de vida: gravidez, pandemia, estresse, menopausa, ansiedade
- Dor real: **perda de identidade feminina**, não apenas excesso de peso
- Frases que ela pensa: *"Já tentei de tudo."* / *"Meu corpo não responde."* / *"Não me reconheço mais."*
- O que faz ela agendar: **esperança de voltar a ser quem era**
- O IVS não vende emagrecimento para esse avatar — vende **reconexão com a identidade feminina**

**Personas secundárias:**
1. Executiva 35–45 (sobrecarga, cortisol elevado, sem tempo)
2. Mulher 45–60 em menopausa (queda hormonal, sarcopenia, baixa libido)
3. Mãe 25–35 pós-gravidez (não voltou ao corpo anterior)
4. Mulher 40–55 com compulsão alimentar (fome emocional, culpa, vergonha)

## Diferencial Competitivo
1. **Experiência excepcional do paciente** — acolhimento diferenciado como pilar operacional
2. **Atualização científica de ponta** — participação em mentoria com discussões de casos clínicos 5–8x por semana e treinamento nas pesquisas mais atuais em emagrecimento, reposição hormonal e longevidade

## Canais de aquisição
> Distribuição atual (fonte: `cerebro/empresa/contexto/metricas.md`, 2026-04):

| Canal | Participação | Status |
|-------|--------------|--------|
| Google Ads | ~98% | Ativo (canal dominante) |
| Indicação de pacientes | ~2% | Crescendo — sinal de alta satisfação |
| Meta Ads (Facebook/Instagram) | — | Não ativo ainda — alavanca prioritária |
| Instagram orgânico | — | Não ativo ainda — alavanca prioritária |

**Execução de tráfego pago:** mentoria + execução por **Matheus Zappiello** (parceiro externo, ver `people.md`).

**Instagram da clínica:** @institutovitalslim e @dradaniely.freitas.

## Ferramentas
> Stack operacional (fonte: `cerebro/CLAUDE.md` seção "Infraestrutura" + skills instaladas):

**Operação clínica**
- **QuarkClinic** — sistema de agendamento e prontuário (agenda padrão **AGENDA OPENCLAW**, `agendaId 445996589`)
- **Omie** — ERP financeiro (boletos, contas correntes, cadastro de paciente)

**Comunicação com paciente**
- **WhatsApp via Z-API** — bridge em `localhost:8787`, instância `3CF367BB00EB205F87468A74AFBCE7F1`, número conectado `7138388708`
- **ElevenLabs TTS** — respostas em áudio (voice ID `EXAVITQu4vr4xnSDxMaL`, modelo `eleven_multilingual_v2`)
- **Whisper (OpenAI)** — transcrição de áudio recebido do paciente

**Comunicação interna**
- **Telegram** — bot `@VitalSlimBot`, grupo "AI Vital Slim" (`-1003803476669`) com tópicos por área

**Conteúdo e marketing**
- **NanoBanana 2 (Google Gemini Pro Vision)** — geração de imagens via skill `prompt-imagens`
- **Buffer** — agendamento/postagem em redes sociais
- **Google Drive** — conta `medicalemagrecimento@gmail.com` via `gog` CLI (boletos, deliverables, fotos da Dra)

**Agente e cérebro**
- **OpenClaw** — gateway local em `localhost:18789` na VPS (Hostinger `187.77.58.193`, Ubuntu 25.10)
- **Modelo principal:** `openai-codex/gpt-5.4` (OAuth ChatGPT Plus)
- **Fallback:** `anthropic/claude-sonnet-4-6`
- **Cérebro versionado em GitHub:** `institutovitalslim/cerebro-vital-slim`
- **Bridge HTTPS para acesso remoto:** `https://openclaw.institutovitalslim.com.br` (read-only, ver `verdades-operacionais.md`)

**Segurança**
- **1Password** — vault `openclaw` (secrets via service account)

## Momento atual
Crescimento ativo — expansão de pacientes e equipe em andamento. Meta: atingir R$ 1.000.000 em faturamento em um único mês ainda em 2026.

**Alerta operacional 2026-04:** captação de novos pacientes em dificuldade nos últimos 3 meses (principal gargalo). 300 pacientes na base × 32 ativos = grande oportunidade de reativação via skill `alerta-clientes-inativos`.

_Atualizado: 2026-04-23_
