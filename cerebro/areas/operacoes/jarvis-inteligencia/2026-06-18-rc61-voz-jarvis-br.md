# RC-61 — Voz Jarvis BR para agente Jarvis

Data: 2026-06-18
Responsável: Maria — Gerência Geral IVS
Autoridade: Tiaro

## Decisão

Jarvis deve ter voz falada própria no Telegram, com persona `jarvis-br`.

## Configuração operacional

- Agente: `jarvis-inteligencia`
- TTS: habilitado no agente
- Auto TTS: `always`
- Provider: ElevenLabs
- Persona: `jarvis-br`
- Modelo: `eleven_multilingual_v2`
- Voz selecionada: masculina grave, calma, executiva e levemente tecnológica.

## Guardrail de identidade vocal

A voz deve ser inspirada no arquétipo de mordomo digital cinematográfico em português brasileiro, sem clonar nem se passar por ator, dublador ou personagem protegido específico.

## Tom desejado

- Masculina
- Grave
- Calma
- Precisa
- Sofisticada
- Levemente tecnológica
- Português brasileiro impecável
- Ritmo executivo
- Baixa teatralização

## Arquivo operacional alterado

`/root/.openclaw/openclaw.json`

Backup criado antes da alteração: `/root/.openclaw/openclaw.json.bak-jarvis-voice-20260618T011455Z`

---

## Atualização RC-25 — 2026-06-21 — Voz aprovada por Tiaro

Tiaro aprovou a amostra **"Jarvis PT-BR — opção 2: português brasileiro mais neutro e calmo"** como voz operacional do Jarvis.

Frase de aprovação registrada no Telegram:

> "Vamos usar este com o nosso Jarvis"

Configuração operacional vigente:

- Agente: `jarvis-inteligencia`
- Persona: `jarvis-br`
- TTS: habilitado
- Auto TTS: `always`
- Provider operacional no OpenClaw: `tts-local-cli`
- Wrapper: `/usr/local/bin/ivs-tts-jarvis-br`
- Voz: clone interno ElevenLabs a partir de referência fornecida por Tiaro
- Direção: português brasileiro neutro, calmo, executivo, dicção limpa, baixa teatralização

Registro RC-25 correspondente:

`/root/cerebro-vital-slim/cerebro/operacional/graphify-2026-06-21-jarvis-ptbr-voz-aprovada/raw/rc25_manifest.md`

---

## Atualização RC-25 — 2026-06-21 — Resposta em áudio para áudio

Tiaro determinou que, sempre que ele mandar áudio no Telegram, Jarvis deve responder também em áudio.

Configuração mantida/garantida:

- TTS habilitado
- `auto=always`
- `mode=final`
- persona `jarvis-br`
- voz Jarvis PT-BR opção 2 aprovada

Registro RC-25 correspondente:

`/root/cerebro-vital-slim/cerebro/operacional/graphify-2026-06-21-jarvis-responder-audio-para-audio/raw/rc25_manifest.md`

---

## Atualização RC-25 — 2026-06-21 — Correção de fallback para voz feminina

Problema reportado por Tiaro: Jarvis ainda estava usando voz feminina após aprovação da voz PT-BR opção 2.

Correção aplicada:

- `messages.tts.provider` em `/root/.openclaw/openclaw.json` alterado de `elevenlabs` para `tts-local-cli`.
- `/root/.openclaw/settings/tts.json` alterado de `provider=elevenlabs` para `provider=tts-local-cli`.
- Mantida wrapper `/usr/local/bin/ivs-tts-jarvis-br` com a voz Jarvis PT-BR opção 2 aprovada.

Registro RC-25 correspondente:

`/root/cerebro-vital-slim/cerebro/operacional/graphify-2026-06-21-jarvis-correcao-voz-feminina/raw/rc25_manifest.md`

---

## Atualização RC-25 — 2026-06-21 — Correção de parada por timeout inválido

Problema reportado por Tiaro: Jarvis parou de responder após ajuste de TTS.

Causa: `timeoutMs=180000` excedia o limite do schema OpenClaw (`<=120000`), gerando falha de startup do gateway.

Correção aplicada:

- `agents.list.7.tts.timeoutMs = 120000`
- `messages.tts.timeoutMs = 120000`
- Provider preservado em `tts-local-cli`
- Voz preservada: Jarvis PT-BR opção 2 aprovada

Registro RC-25 correspondente:

`/root/cerebro-vital-slim/cerebro/operacional/graphify-2026-06-21-jarvis-timeout-fix/raw/rc25_manifest.md`

---

## Atualização RC-25 — 2026-06-25 — Voz VoxCPM aprovada e ElevenLabs desativado para Jarvis

Tiaro aprovou a voz **Jarvis VoxCPM BR**, baseada no arquivo `jarvis_voxcpm_clone_teste_denoised_ref.mp3`, como nova voz operacional do Jarvis e determinou cancelar o uso do ElevenLabs para o Jarvis.

Configuração operacional vigente:

- Agente: `jarvis-inteligencia`
- Persona: `jarvis-br`
- TTS habilitado
- Provider operacional no OpenClaw/Hermes: `tts-local-cli`
- Wrapper: `/usr/local/bin/ivs-tts-jarvis-br`
- Backend primário da wrapper: VoxCPM local (`/opt/ivs/voxcpm-lab/venv/bin/voxcpm`)
- Referência VoxCPM aprovada: `/opt/ivs/voxcpm-lab/reference/jarvis_voxcpm_approved_20260625.mp3`
- ElevenLabs desativado para Jarvis; a wrapper atual não chama API ElevenLabs.
- Fallback permitido somente para Supertonic local, sem ElevenLabs, para evitar Jarvis mudo se VoxCPM falhar.

Observação operacional: neste host a geração VoxCPM roda em CPU, portanto a latência pode ser maior que ElevenLabs. Para alto volume, preferir GPU/CUDA.

Registro RC-25 correspondente:

`/root/cerebro-vital-slim/cerebro/operacional/graphify-2026-06-25-jarvis-voxcpm-voz-aprovada/raw/rc25_manifest.md`
