# SPEC-CEOS-BI-001: BI Instagram via RapidAPI — Dra. Daniely

## Goal
Criar, em fase seguinte, uma seção de BI (Business Intelligence) no Content Engine OS para coletar diariamente a performance das publicações do Instagram da Dra. Daniely e alimentar decisões de conteúdo, Stories Engine e criativos vencedores.

## Fonte autorizada
- Perfil: `@dradaniely.freitas`
- Operador: João
- Canal técnico: RapidAPI
- Frequência desejada: diária

## Escopo futuro
- Criar seção `BI - Business Intelligence` no Content Engine OS.
- Coletar métricas diárias de publicações via RapidAPI.
- Persistir métricas por publicação, formato, tema, data e CTA.
- Cruzar com Stories Engine, criativos campeões e calendário editorial.
- Gerar ranking de conteúdos por retenção/engajamento/intenção.

## Métricas candidatas
- data da publicação;
- formato: reels, carrossel, foto, stories quando disponível;
- legenda/título;
- visualizações/reach quando disponível;
- curtidas;
- comentários;
- compartilhamentos;
- salvamentos;
- taxa de engajamento;
- crescimento relativo;
- tema/cluster IVS;
- possível relação com leads/agendamentos quando houver `origin_tag`.

## Governança
- Usar RapidAPI como rota padrão para Instagram, conforme preferência do Tiaro.
- Não solicitar print enquanto RapidAPI funcionar.
- Não coletar nem expor PII de seguidores/comentários.
- Tratar dados como agregados operacionais.
- Não publicar, responder ou alterar nada no Instagram por esse fluxo.

## Integração esperada
```text
Instagram Dra. Daniely → RapidAPI → BI Content Engine OS → ranking/insights → Stories Engine/Criativos/Calendário
```

## Acceptance Criteria futura
- [ ] endpoint de ingestão diária idempotente;
- [ ] tabela de métricas por publicação;
- [ ] dashboard BI no menu principal;
- [ ] relatório semanal HTML;
- [ ] smoke sem PII;
- [ ] commit + push.
