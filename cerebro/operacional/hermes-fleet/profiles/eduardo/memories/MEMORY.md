# Memória do Eduardo — Gestão de Estoque
> Inicial (2026-06-23). Domínio: estoque da clínica + área 2, Omie, abatimento por prontuário.

## Controle interno atual (área 2 / clínica)
  "source": "/root/.openclaw/media/inbound/balanco_estoque_ativos_area_2_preencher_2026-06-12---71ed14fd-ed47-4866-91cd-4bc2f391aec9.numbers",
      "item": "ADEK",
      "estoque_clinica": "5",
      "area_2": "10",
      "total": "15",
      "item": "ALA / Ácido Lipóico",
      "estoque_clinica": "21",
      "area_2": "0",
      "total": "21",
      "item": "Beta Alanina",
      "estoque_clinica": "10",
      "area_2": "0",
      "total": "10",
      "item": "Chronic",
      "estoque_clinica": "9",
      "area_2": "0",
      "total": "9",
      "item": "Cloreto de Cromo",
      "estoque_clinica": "3",
      "area_2": "10",
      "total": "13",

## Regras
- NUNCA negar existência de item sem conferir inventário.
- Saldo só do controle interno + Omie + última contagem (Liane).
## TAREFAS ABERTAS
- (configurar) skill de abatimento medicação-por-prontuário; funções de estoque no Omie (movimento/posição/ajuste).

## Skills instaladas
- **omie-estoque** (treinada pelo Pedro): Omie via `omie-api` — ver skills/omie-estoque/TREINAMENTO-PEDRO-OMIE-ESTOQUE.md. Leitura autônoma; ajuste/movimento com confirmação.
- **estoque-baixa-prescricao** (visão): `skills/estoque-baixa-prescricao/eduardo_estoque_baixa.py <imagem>` lê prescrição+rótulos e propõe baixa.
§
Cotações IVS: carrinho “CX C/10 AMPOLAS” + “Valor a pagar” = Central Injetáveis; print “Código Portal/Portal Médico Web/ISABELLA SANTOS” = Health Tech (corrigido por Tiaro).
§
Para compras de injetáveis IVS, Tiaro confirmou em 2026-07-08 que PQQ 5mg/2ml deve ser tratado como o mesmo PQQ solicitado quando aparecer em orçamento.
§
Códigos Omie estoque IVS: prefixo INJ=injetável, PEL=pellet, SIL=silástico. Cotações IVS: usar valor unit.; conferir apresentação; Ác.Lipóico=300mg/10ml; PQQ 5mg/2ml ok; Cafeína 100mg/2ml=Cafeína Benzoica 50mg/ml-2ml; Morusil Booster≠Moro puro/LC+MO.
§
Orçamento separado NADH é da Victa: NADH (Pó Liofilizado), 01 un, 50mg, valor R$63,39 (print Tiaro 2026-07-09).