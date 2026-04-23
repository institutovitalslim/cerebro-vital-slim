# Yarn.co — Busca de trechos de vídeo por frase

**URL:** https://yarn.co/

## O que é

Ferramenta web que indexa falas de filmes, séries e desenhos animados, permitindo buscar **frases específicas** e retornar o **trecho exato do vídeo** onde aquela fala aparece (geralmente 2-6 segundos). Cada resultado vem como clipe curto pronto para download ou embed.

## Quando usar

- **B-roll pra Reels da Dra. Daniely** quando quero ilustrar uma ideia com referência cultural reconhecível (ex: frase de filme que casa com o ponto do script).
- **Transições cômicas / reações** em carrosséis ou stories, quando a linguagem da marca permitir leveza.
- **Hook inicial** de Reel pegando frase icônica de filme/série que o público IVS (mulher 30-55) reconheça imediatamente (ex: cenas de "A Escolha", "Divertida Mente", "Sex and the City", "Grey's Anatomy").
- **Referência visual** pra brief de edição quando preciso comunicar o *tom* de um corte específico que tenho na cabeça.

## Limitações / cuidados

- **Direitos autorais:** trechos são fair-use-ish (curtos, citação), mas **Instagram pode detectar áudio** e silenciar ou reduzir alcance. Testar com 1 post antes de escalar.
- **Voz da marca IVS:** Dra. Daniely é médica acolhedora e baseada em evidência. Frases de filme só entram quando o *tom* combina — não forçar humor que quebre o posicionamento clínico.
- **Ética médica:** não usar trechos que banalizem obesidade, compulsão alimentar, ou sofrimento das pacientes. Nunca usar trechos com crianças (regra canônica IVS — ver `cerebro/omie.md` e regras éticas).
- **Idioma:** busca funciona melhor em inglês. Pra referências dubladas em PT-BR, testar ambas as formas da frase.

## Fluxo sugerido no pipeline de conteúdo

1. Ao escrever um script pra Reel, se a ideia pedir um **hook referencial** ou **B-roll emocional**, pensar em frase de filme/série que case.
2. Buscar no yarn.co.
3. Baixar clipe + anotar no roteiro (Bloco HOOK ou CORPO, indicando ponto exato: *"clip yarn.co 0:02-0:04 de <filme>"*).
4. Passar pro editor junto com as imagens.

## Alternativas

- **Getyarn.io** (mesmo projeto, URL antiga que às vezes funciona quando yarn.co está fora)
- **Playphrase.me** (similar, costuma ter catálogo diferente)
- **Cinematic.gif** (menor, específico pra GIF)

## Observação operacional

Não tem API pública documentada. Uso é manual via browser. Pra automação futura, considerar scraping — mas respeitando ToS (não há permissão explícita).
