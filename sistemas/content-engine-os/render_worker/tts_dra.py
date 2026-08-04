#!/usr/bin/env python3
"""TTS com a VOZ CLONADA da Dra. Daniely (ElevenLabs PVC) para o Content Engine OS.

Voz padrão: PVC "Dra Daniely Freitas IVS PVC" (cHeeSDYHphU2IdW1IA0G) — a profissional.
Configurável por env: CONTENT_OS_VOICE_ID, CONTENT_OS_TTS_MODEL.
"""
import os, json, urllib.request

DRA_PVC = "cHeeSDYHphU2IdW1IA0G"            # Dra Daniely Freitas IVS PVC (profissional)
DRA_V4 = "yGClPIVS8u4IOh10hmuf"             # fallback: v4 dataset limpo (cloned)
VOICE = os.environ.get("CONTENT_OS_VOICE_ID", DRA_PVC)
MODEL = os.environ.get("CONTENT_OS_TTS_MODEL", "eleven_multilingual_v2")

def _key():
    for p in ("/root/.openclaw/secure/elevenlabs.env", "/root/.hermes/.env"):
        try:
            for ln in open(p):
                if ln.startswith("ELEVENLABS_API_KEY="):
                    return ln.split("=", 1)[1].strip().strip('"').strip("'")
        except Exception:
            pass
    return os.environ.get("ELEVENLABS_API_KEY", "")

def narrate(text, out_path, voice_id=None):
    """Gera MP3 da narração na voz da Dra. Retorna out_path ou None (texto vazio)."""
    text = (text or "").strip()
    if not text:
        return None
    key = _key()
    if not key:
        raise RuntimeError("ELEVENLABS_API_KEY ausente")
    body = json.dumps({
        "text": text, "model_id": MODEL,
        "voice_settings": {"stability": 0.45, "similarity_boost": 0.9, "style": 0.15, "use_speaker_boost": True},
    }).encode()
    last = ""
    for vid in [voice_id or VOICE, DRA_V4]:   # PVC primário; v4 como fallback
        try:
            req = urllib.request.Request(
                f"https://api.elevenlabs.io/v1/text-to-speech/{vid}", data=body,
                headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/mpeg"},
                method="POST")
            audio = urllib.request.urlopen(req, timeout=180).read()
            if audio and len(audio) > 1000:
                with open(out_path, "wb") as f:
                    f.write(audio)
                return out_path
            last = f"voz {vid}: resposta vazia"
        except Exception as e:
            last = f"voz {vid}: {e}"
    raise RuntimeError("TTS Dra falhou — " + last[:200])

if __name__ == "__main__":
    import sys
    t = sys.argv[1] if len(sys.argv) > 1 else "Oi, aqui é a Dra. Daniely. Esse é um teste da minha voz no Content Engine OS."
    o = sys.argv[2] if len(sys.argv) > 2 else "/tmp/dra_tts.mp3"
    print("ok ->", narrate(t, o), f"(voz {VOICE})")
