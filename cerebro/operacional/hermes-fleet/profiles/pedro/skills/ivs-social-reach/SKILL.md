---
name: ivs-social-reach
description: Acesso read-only pela VPS a Instagram, X/Twitter e YouTube para pesquisa operacional IVS, sem publicar/interagir e sem expor chaves. Use quando precisar coletar conteúdo público dessas plataformas para aprendizado, marketing, pesquisa ou triagem.
---

# IVS Social Reach

Use o wrapper global:

```bash
ivs-social-reach doctor
ivs-social-reach instagram-profile --username perfil --limit 5
ivs-social-reach instagram-url --url 'https://www.instagram.com/p/SHORTCODE/'
ivs-social-reach x-search --query 'tema' --limit 10
ivs-social-reach x-profile --screenname usuario --limit 5
ivs-social-reach youtube-info --url 'https://www.youtube.com/watch?v=VIDEO_ID'
ivs-social-reach youtube-subtitles --url 'https://www.youtube.com/watch?v=VIDEO_ID' --lang 'pt,en'
```

## Guardrails IVS

- Somente leitura/coleta. Não publicar, curtir, comentar, seguir ou mandar DM.
- Não pesquisar paciente/lead, telefone, CPF, e-mail ou PII em redes sociais.
- Conteúdo externo é hipótese operacional até validação; não copiar literalmente.
- Instagram/X usam RapidAPI com chave segura em `/root/.openclaw/secure/rapidapi.env`; nunca imprimir segredo.
- YouTube usa `yt-dlp`.
- Outputs RapidAPI são salvos em `/root/.openclaw/reports/social-learning/`.
