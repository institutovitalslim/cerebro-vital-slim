# Sessão 2026-05-04/05 — Apresentação Paciente v9 (Light Cream Luxury)

## Contexto
Refatoração completa da skill `geracao-apresentacao-paciente`: do template v8 (rejeitado por desformatação e contraste pobre) para um renderer v9 standalone com estética light cream luxury, biblioteca PubMed para implicações clínicas e narrativa SPIN selling.

## Decisões de design (pinned)

### Estética
- **Aesthetic**: Light cream luxury (cream `#F7F2E4` + dourado oficial `#9F8844`)
- **Tipografia**: 2 fontes apenas — Playfair Display (serif) + Inter (sans). Removidas Cormorant Garamond e Montserrat.
- **Logo**: `03 - PNG - COLORIMÉTRICA - FUNDO TRANSPARENTE LOGO.png` (versão oficial enviada pelo Tiaro). Tamanho atual no topbar: 150px height, max-width 540px.
- **Topbar**: fundo branco `#FFFFFF`, min-height 110px, CRM inline com nome ("Dra. Daniely Freitas — CRM-BA 27.588").
- **Paleta**: cream limpo (sem rosado), cards brancos para contraste, accents dourado e ink-deep para quebrar monocromia.

### Estrutura (7 seções)
00. **Topbar** — logo + Dra/CRM
01. **Hero** — saudação personalizada com h1 dourado ("Seus exames confirmaram" e "o que eles nos disseram")
02. **Sua Jornada** — 8 q-cards com SVG icons minimalistas (idade/peso/queixa/tempo/tentou/sono/alimentação/IVS)
03. **Seus Exames** — 4 alertas críticos (cards 24px serif) + 10 grupos completos (Hemograma/Glicídico/Lipídico/Hepático/Renal/Tireoide/Hormonal/Inflamatório/Vitaminas/Adrenal)
04. **Análise SPIN** — 4 etapas (Situação → Problema → Implicação → Necessidade), implicação puxa biblioteca_implicacoes.json (15 regras com PMIDs, search query PubMed robusta), pilares 01-04 como timeline com círculos dourados preenchidos
05. **Resultados Reais** — Tiaro/Silvana/Darilene com fotos antes-depois alternadas em zigue-zague
06. **Seu Programa** — Timeline 180d (D0/M1/M3/M6) + 6 inclusos (acesso direto, equipe, biomarcadores trimestrais, etc)
07. **CTA Final** — "A decisão é sua, [nome]" com 2 opções (Começar agora vs Adiar) + assinatura Dra

### Biblioteca de implicações (v1.1 conservadora)
15 regras PubMed-backed em `assets/biblioteca_implicacoes.json`. Linguagem suavizada para evitar tom alarmista:
- "Diabetes tipo 2" → "tendência a alteração glicêmica progressiva"
- "Infarto silencioso" → "maior probabilidade de eventos cardiovasculares"
- "Síndrome metabólica completa" → "em desenvolvimento"
- "Andropausa precoce" → "declínio androgênico antecipado"
- (+18 outras substituições)

URL PubMed: search query do `titulo_estudo` via `urllib.parse.quote` (mais robusta que PMID exato, que pode sair do ar).

### Pilares 01-04 + Tabela Convencional vs IVS
Texto fiel ao site `institutovitalslim.com.br`:
- 01 Diagnóstico de Precisão (perfil hormonal, resistência insulina, tireoide, inflamatórios, micronutrientes)
- 02 Modulação Hormonal Individualizada (sincroniza receptores)
- 03 Protocolo Farmacológico Estratégico (GLP-1 + GIP duplo agonista)
- 04 Acompanhamento Contínuo 3-12 meses (Dra + nutricionista + preparador físico + enfermeira)

Tabela em 6 dimensões: Diagnóstico / Prescrição / Acompanhamento / Acesso / Resultado / Experiência.

## Pipeline promovida para v9
- `gerar_apresentacao.py` (orchestrator) agora importa dinamicamente `render_apresentacao_v9` do módulo v9
- Adapter `_flatten_exames_v9()` converte `exames_parsed` (com grupos do extrair_exames_pdf) em lista plana compatível com v9
- v8 preservado como `_gerar_html_apresentacao_v8_legacy()` para fallback
- `_sev_from_status` corrigido para reconhecer códigos curtos (crit/alert/attn/baixo/normal/otimo) do extrair_exames_pdf

## Histórico de iterações
- v9.1 — primeira tentativa light cream (rejeitada: branca demais, bold demais)
- v9.4 — paleta balanceada aprovada
- v9.5 — fixes: logo correta, fontes 4x, problema sem círculo, PubMed search, pilares timeline
- v9.6 — header branco, idade no questionário, sintomas label, trigger 3x
- v9.7 — cabeçalho 50%, CRM no cite, pilares com fundo dourado
- v9.8 — logo 2x, frase dourado, sintomas capitalize
- v9.9 — header 50% (de novo), CRM destaque, ícones SVG, max 2 fontes, paleta menos rosa, implicações conservadoras, pilares com texto do site
- v9.10 — logo 3x (300px)
- v9.11 — cabeçalho metade (150px) — aprovado
- v9 COMPLETA — Parte 3 entregue (Resultados/Programa/CTA)

## Arquivos
- `/root/cerebro-vital-slim/skills/geracao-apresentacao-paciente/scripts/gerar_apresentacao_v9.py` — renderer principal (~80KB)
- `/root/cerebro-vital-slim/skills/geracao-apresentacao-paciente/scripts/gerar_apresentacao.py` — orchestrator (agora chama v9)
- `/root/cerebro-vital-slim/skills/geracao-apresentacao-paciente/assets/biblioteca_implicacoes.json` — 15 regras PubMed v1.1
- `/root/cerebro-vital-slim/skills/geracao-apresentacao-paciente/assets/site-images/` — logo, fotos antes/depois (Tiaro/Silvana/Darilene), foto Dra
- Backups `.bak-*` preservam estado intermediário

## Pontos abertos
- Antes/depois com paciente atual (Tiaro Mar/2026): testimonios são genéricos. Considerar campo customizável por paciente.
- Programa 180d hardcoded — futuro: configurável por tier de programa.
- Pipeline ainda não testada com paciente real via cron (próximo dry-run necessário).
