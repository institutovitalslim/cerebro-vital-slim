# RC-25 Manifest — Jarvis VoxCPM BR aprovado e ElevenLabs desativado

Data: 2026-06-25
Solicitante: Tiaro
Executor: Jarvis — Assessor Pessoal de Inteligência

## Decisão

Tiaro aprovou a voz `jarvis_voxcpm_clone_teste_denoised_ref.mp3` como nova voz operacional do Jarvis e determinou cancelar o uso de ElevenLabs para o Jarvis.

## Mudança operacional

- Agente: `jarvis-inteligencia`
- Persona: `jarvis-br`
- Provider operacional no OpenClaw/Hermes: `tts-local-cli`
- Wrapper operacional mantida: `/usr/local/bin/ivs-tts-jarvis-br`
- Backend primário da wrapper: VoxCPM local em `/opt/ivs/voxcpm-lab/venv/bin/voxcpm`
- Referência VoxCPM aprovada: `/opt/ivs/voxcpm-lab/reference/jarvis_voxcpm_approved_20260625.mp3`
- Cache/modelo: `/opt/ivs/voxcpm-lab/cache`, modelo `openbmb/VoxCPM2`
- ElevenLabs removido do fluxo do Jarvis; não há chamada à API ElevenLabs na wrapper atual.
- Fallback preservado apenas para Supertonic local, sem ElevenLabs, para evitar Jarvis mudo se VoxCPM falhar.

## Arquivos operacionais alterados

- `/usr/local/bin/ivs-tts-jarvis-br`
- `/root/.openclaw/openclaw.json`
- `/opt/ivs/voxcpm-lab/reference/jarvis_voxcpm_approved_20260625.mp3`

## Backups

- Wrapper anterior com ElevenLabs copiada para `/root/.openclaw/backups/jarvis-tts/ivs-tts-jarvis-br.bak-voxcpm-20260625T104350`
- `openclaw.json` copiado para `/root/.openclaw/openclaw.json.bak-jarvis-voxcpm-20260625T104441Z` e backup adicional de persona.

## Evidência de smoke test

Arquivo gerado pela nova wrapper VoxCPM:

`/root/.openclaw/media/outbound/jarvis/jarvis-voxcpm-production-smoke-20260625.mp3`

Propriedades: MP3, mono, 48 kHz, duração aproximada 7.08 s.

## Guardrails

- Não usar ElevenLabs para Jarvis enquanto esta decisão estiver vigente.
- Não usar clonagem de voz para pacientes/leads sem consentimento e autorização específica.
- Alteração futura de voz do Jarvis exige nova aprovação de Tiaro e novo RC-25.
- Rodando em CPU neste host; latência pode ser maior que ElevenLabs. Preferir GPU/CUDA se a voz VoxCPM virar produção de alto volume.
