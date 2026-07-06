---
name: competitor-x-ray-ivs
description: Use quando João/Maria/Conselho Growth precisarem mapear concorrentes do IVS, especialmente Salvador, Lauro de Freitas e Região Metropolitana, com ICP, funil, monetização, números, links, evidence tiers, score IVS e ações recomendadas sem inventar dados.
---

# Competitor X-Ray IVS

Versão IVS-first para inteligência competitiva regional. Sempre separar fato, autorrelato e hipótese.

## Evidence tiers

```text
CONFIRMED = fonte própria/autoritativa: site oficial, landing, perfil oficial, página de preço, anúncio ativo.
REPORTED = autorrelato, snippet, Similarweb/SocialBlade/HypeAuditor, entrevista, diretório de terceiros.
INFERRED = inferência operacional marcada como hipótese.
```

Receita, resultado clínico, número de pacientes e promessas de perda de peso nunca viram fato sem fonte autoritativa.

## Foco geográfico

Priorizar Lauro de Freitas, Vilas do Atlântico, Buraquinho, Salvador, Camaçari, Simões Filho e Região Metropolitana.

## Loop

Carregue `ivs-loop-factory` e use o preset `competitor-xray-market-intel`:

```text
state -> collect targets -> normalize -> fan-out research -> evidence tier -> score -> synthesize -> decide -> improve or stop
```

## Score IVS 0–100

| Dimensão | Peso |
|---|---:|
| Oferta premium clara | 15 |
| Prova social confiável | 15 |
| Funil capturável | 15 |
| Intensidade de aquisição | 15 |
| Diferenciação médica/compliance | 15 |
| Momentum | 10 |
| Ameaça local/regional | 10 |
| Gap explorável pelo IVS | 5 |

## Saída padrão para João

1. HTML executivo.
2. JSON/CSV com matriz.
3. Ranking de ameaça.
4. Fontes e confidence note.
5. Ações para João: hooks, ângulos, gaps, claims que NÃO copiar, hipóteses de teste.

## Template por concorrente

```text
Nome:
Local:
Links próprios:
ICP — audiência:
ICP — comprador provável:
Funil: top -> middle -> bottom
Monetização/oferta:
Números:
Evidence tiers:
Score IVS:
Riscos/compliance:
O que João aprende:
O que NÃO copiar:
```

## Human gates

Não contatar concorrente, não simular paciente, não publicar conteúdo, não copiar claim clínico e não transformar hipótese em regra/campanha externa sem validação.
