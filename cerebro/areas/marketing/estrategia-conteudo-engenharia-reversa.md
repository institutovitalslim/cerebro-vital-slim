# Estratégia de Conteúdo — Engenharia Reversa de Reels Virais

> Adaptação do framework "Content Strategy" para o Instituto Vital Slim.
> Quando o Tiaro indicar perfis pra monitorar, executar esta metodologia.

## Quando usar

Sempre que o Tiaro mandar um ou mais perfis do Instagram pra "estudar / analisar / extrair conteúdo".

## Voz alvo (não desviar)

**Dra. Daniely Freitas** — médica do Instituto Vital Slim:
- Acolhedora, ancorada em evidência
- Sem promessa de resultado
- Traduz pra realidade da paciente alvo (mulher 30-55, mãe, profissional, frustrada com tentativas)
- Tom: humano, médico-empático, sem jargão excessivo

**Eixos temáticos:**
- Emagrecimento real (sem dieta da moda)
- Hormonal / Menopausa / TPM / Libido
- Energia / Disposição / Cansaço crônico
- Compulsão / Comportamento alimentar / Ciclo sanfona
- Autoestima / Saúde sustentável

## Pipeline técnico

```bash
# 1. Pega top 11 reels do perfil
python3 /root/.openclaw/workspace/skills/tweet-carrossel/scripts/fetch_top_reels.py <username> --enrich
# Output: /tmp/reels/<username>_top.json
```

## Estrutura de entrega para cada perfil analisado

### Bloco 1 — Top 11 reels
Tabela com: posição, link, plays, likes, comments, duração, caption (1ª linha).

### Bloco 2 — Para cada reel, 4 itens

**Por que viralizou** (300-500 chars):
- Hook (primeiros 3 segundos)
- Estrutura (sequência narrativa)
- Retention drivers (o que faz ficar)

**3 scripts originais adaptados** (30-40s cada, na voz da Dra. Daniely):

```
SCRIPT [N]
HOOK (0-3s): [pattern interrupt visual + frase]
DESENVOLVIMENTO (3-25s): [história / insight / dado científico]
CTA (25-35s): [pergunta engajamento OU convite consulta]
LEGENDA: [texto da caption do reel — 100-200 chars]
```

### Bloco 3 — Clusterização em temas
Agrupar os 11 reels em 3-4 temas. Identificar o eixo emocional dominante.

### Bloco 4 — 1 carrossel por tema
Padrão Viral Content Strategy (10 slides):
1. **HOOK** (Pattern Interrupt) — headline ousada, max 5-10 palavras
2. **REHOOK** (Open Loop) — intriga sem resposta
3. **Relatable Pain** / Início da história
4-7. **Valor** (História + Insights) — 1 ideia por slide
8. **Turning Point** (Momento AHA) — insight-chave
9. **Actionable Takeaway** — passos práticos
10. **CTA** (Engagement Trigger) — call-to-action

### Bloco 5 — Plano de publicação sugerido
- Cadência por tema (ex: 1 reel/semana por tema, carrossel quinzenal)
- Melhor horário (basear no histórico do @institutovitalslim)
- Sequenciamento (qual reel libera contexto pra qual carrossel)

## Regras éticas invioláveis (saúde médica)

- **Nunca prometer resultado quantificado** ("você vai perder 10kg")
- **Nunca usar antes-e-depois** sem contexto clínico + autorização explícita
- **Nunca medicalizar conteúdo educativo** (não dizer "você TEM hipotireoidismo" — dizer "esses sintomas podem indicar")
- **Sempre incluir CTA de consulta** quando o conteúdo levanta sintoma/diagnóstico
- **Nunca copiar caption literal** — sempre reescrever na voz da Dra. Daniely
- **Sempre creditar fonte de dado científico** se usar (PubMed/estudos)

## Fluxo operacional

1. Tiaro manda 1+ perfil (`@usuario1 @usuario2 ...`)
2. Para cada perfil, rodar `fetch_top_reels.py <username> --enrich`
3. Análise com Kimi K2.6 via OpenRouter (não usar GPT — Kimi tem voz mais natural em PT-BR)
4. Entregar os 5 blocos por perfil, em ordem
5. Aguardar aprovação do Tiaro antes de publicar / criar imagens
6. Carrosseis aprovados → executar via skill `tweet-carrossel` com NanoBanana 2 pra imagens

## Output final por perfil

Markdown estruturado, salvo em `cerebro/empresa/conteudo/analise-perfil-<username>-<data>.md` e committed no GitHub.
