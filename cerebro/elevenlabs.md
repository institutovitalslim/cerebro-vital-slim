# ElevenLabs TTS

Integração ElevenLabs para respostas de áudio no WhatsApp.

---

## Configuração

| Item | Valor |
|------|-------|
| API Key | `/root/.openclaw/secure/elevenlabs.env` |
| Voice ID | `EXAVITQu4vr4xnSDxMaL` (Rachel) |
| Modelo | `eleven_multilingual_v2` |

## Fluxo de Áudio (WhatsApp)

1. Paciente envia áudio no WhatsApp
2. Z-API bridge recebe o áudio
3. Transcrição via **Whisper (OpenAI)**
4. Clara processa a mensagem e gera resposta
5. **ElevenLabs TTS** converte resposta para áudio
6. Envio via Z-API (`/send-audio` com `audioBase64`)

## Regras

- Só responder em áudio quando o paciente enviar áudio
- Fallback para texto se TTS falhar
- Voice ID padrão: Rachel (voz feminina, profissional)

## Status

✅ Operacional — teste de áudio realizado com sucesso
