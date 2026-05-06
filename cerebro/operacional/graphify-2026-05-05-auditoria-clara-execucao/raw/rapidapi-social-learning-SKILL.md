---
name: rapidapi-social-learning
description: Coleta conteúdos públicos via RapidAPI de Instagram e X/Twitter para aprendizado operacional da Clara e João, sem expor chaves.
---

# rapidapi-social-learning

Use quando Tiaro pedir que Clara/João aprendam com Instagram ou X/Twitter via RapidAPI.

## Segurança
- Nunca exibir `RAPIDAPI_KEY`.
- A chave fica em `/root/.openclaw/secure/rapidapi.env`.
- Usar apenas conteúdo público e apenas para aprendizado/copywriting/atendimento, sem responder diretamente a pacientes com conteúdo externo sem validação.

## Script principal

```bash
python3 /root/.openclaw/workspace/skills/rapidapi-social-learning/scripts/social_learning.py daily-plan
python3 /root/.openclaw/workspace/skills/rapidapi-social-learning/scripts/social_learning.py instagram-profile --username camilaporto --limit 5
python3 /root/.openclaw/workspace/skills/rapidapi-social-learning/scripts/social_learning.py instagram-url --url 'https://www.instagram.com/p/SHORTCODE/'
python3 /root/.openclaw/workspace/skills/rapidapi-social-learning/scripts/social_learning.py x-top --period Daily --type Likes
```

## Regra para Clara
Clara não deve navegar aleatoriamente. Ela deve buscar conteúdo conforme rotina RC-27: manhã para aula curta, meio-dia para objeções/linguagem, fim do dia para revisão de padrões.
