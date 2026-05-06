---
name: youtube-learning-ivs
description: Busca e resume vídeos/canais do YouTube para aprendizado comercial da Clara, transformando conteúdo em scripts premium de WhatsApp.
---

# youtube-learning-ivs

Use quando Tiaro pedir que Clara aprenda com canais do YouTube sobre vendas consultivas, SPIN, objeções, follow-up, atendimento premium e WhatsApp/social selling.

## Script

```bash
python3 /root/.openclaw/workspace/skills/youtube-learning-ivs/scripts/youtube_learning.py plan
python3 /root/.openclaw/workspace/skills/youtube-learning-ivs/scripts/youtube_learning.py search --topic "objection handling whatsapp" --limit 5
python3 /root/.openclaw/workspace/skills/youtube-learning-ivs/scripts/youtube_learning.py transcript --url "https://www.youtube.com/watch?v=..."
```

## Regras
- Não copiar conteúdo literalmente.
- Transformar aulas em comportamento WhatsApp: abertura, pergunta, objeção, follow-up, fechamento.
- Não usar promessa clínica.
- Se não conseguir coletar transcript/resultado, registrar falha e sugerir busca manual pelo canal/tema.
