# Preset: competitor-xray-market-intel

## Owner
João + Maria + Conselho Growth

## Goal
Mapear concorrentes do IVS em Lauro de Freitas, Salvador e Região Metropolitana com ICP, funil, monetização, números, evidence tiers, score IVS e ações recomendadas.

## Source of truth
Fontes públicas/read-only: sites oficiais, landings, Instagram público/snippets, link-in-bio, Doctoralia, Google Maps/OSM, entrevistas e diretórios. Não simular paciente e não contatar concorrentes.

## Allowed autonomous actions
- Buscar fontes públicas.
- Classificar concorrentes e normalizar nomes/links.
- Gerar HTML/JSON/CSV interno.
- Marcar claims como CONFIRMED, REPORTED ou INFERRED.

## Human gates
- Enviar mensagem, preencher formulário, publicar conteúdo, copiar claim clínico ou transformar hipótese em regra/campanha externa.

## Evaluation
- Cada concorrente precisa ter pelo menos 1 fonte real.
- Toda afirmação sensível precisa de evidence tier.
- Ranking precisa usar score IVS e não “vibes”.
- Saída precisa incluir ações para João e riscos de compliance.

## Stop conditions
Success:
- HTML + JSON/CSV + fontes + score IVS + next actions.

Partial:
- Alguns concorrentes têm fonte fraca ou só snippet.

Blocked:
- Fontes essenciais indisponíveis sem fallback público.

Budget/plateau:
- Parar após 5 iterações ou 2 rodadas sem novas fontes úteis.
