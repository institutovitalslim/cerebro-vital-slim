---
name: design-impeccable
description: |
  Use quando o Tiaro pedir para criar, revisar, "polir" ou refinar qualquer
  interface HTML do Instituto Vital Slim — especialmente APRESENTAÇÕES HTML
  de paciente (Mario, Silvana, Francisco, etc.), o novo site institucional,
  landing pages e componentes visuais.
  Também aplicar antes de entregar qualquer HTML: passagem final de "polish"
  checando tipografia, hierarquia, cor, espaçamento, contraste e copy.
  Fonte canônica: skill Impeccable (pbakaus, Apache 2.0), reescrita aqui com
  contexto Vital Slim. Ver NOTICE.md.
user-invocable: true
version: 1.0.0-ivs
license: Apache-2.0 (upstream) + camada Vital Slim
---

# Skill `design-impeccable` — Vital Slim

## Para que serve

Dar à Clara **vocabulário de design** para produzir HTML de qualidade clínica-premium. Evita os anti-patterns conhecidos (Inter em tudo, gradiente roxo, cards com borda grossa, modal abuse, contraste ruim, ícones gigantes).

## Quando disparar

- **Toda apresentação HTML de paciente**, ANTES de enviar o link ao Tiaro
- **Qualquer landing page ou página nova** do instituto
- **Revisão/redesign** de HTML existente
- Quando o Tiaro pedir "polir", "melhorar visual", "revisar o design", "está genérico demais", "parece IA"

## Como invocar

Este arquivo é o ponto de entrada. O fluxo é **consultivo** (advisory) — ler a referência adequada e aplicar.

Não há CLI nem scripts nesta skill. O upstream Impeccable tem um modo `/live` (variante visual em browser via Puppeteer) — **não trouxemos** por superfície de ataque desnecessária. Se um dia for útil, revisar com o Tiaro antes de instalar.

## Workflow padrão (antes de entregar qualquer HTML)

1. **Contexto do projeto** — confirmar o brief com o Tiaro. Não inferir.
2. **Gerar o HTML** seguindo a `brand-adapter.md` (brand tokens do Vital Slim)
3. **Autocrítica** — aplicar os 3 comandos mínimos em ordem:
   - `reference/critique.md` — review de UX (hierarquia, clareza, decisão)
   - `reference/polish.md` — passagem final (detalhes, consistência, pronto para entrega)
   - `reference/audit.md` — checagem técnica (acessibilidade, responsivo, performance)
4. **Enviar link** pro Tiaro (regra operacional 2026-04-23: toda alteração em HTML, link automático, sem esperar pedir)

## Comandos disponíveis (35 references)

Organizados por fase do trabalho:

### Descobrir e planejar
| Comando | Quando usar |
|---|---|
| `reference/shape.md` | Planejar UX/UI **antes** de codar |
| `reference/teach.md` | Primeira vez num projeto — preencher `PRODUCT.md` |
| `reference/document.md` | Gerar `DESIGN.md` a partir de código existente |
| `reference/extract.md` | Extrair componentes e tokens reutilizáveis |
| `reference/personas.md` | Mapear perfis de usuário |

### Refinar
| Comando | Quando usar |
|---|---|
| `reference/craft.md` | Fluxo completo shape→build com iteração |
| `reference/polish.md` | Passagem final antes de entregar |
| `reference/critique.md` | Review crítico de UX |
| `reference/audit.md` | Checagem técnica (a11y, perf, responsivo) |
| `reference/heuristics-scoring.md` | Scorecard de heurísticas |

### Ajuste de tom
| Comando | Quando usar |
|---|---|
| `reference/bolder.md` | Design tímido demais — amplificar |
| `reference/quieter.md` | Design agressivo demais — reduzir |
| `reference/distill.md` | Tirar ruído, deixar só a essência |

### Atributos específicos
| Comando | Quando usar |
|---|---|
| `reference/typography.md` | Fontes, hierarquia, tracking, kerning |
| `reference/typeset.md` | Corrigir escolha e hierarquia de fonte |
| `reference/color-and-contrast.md` | Paleta, contraste, temas |
| `reference/colorize.md` | Introduzir cor estrategicamente |
| `reference/layout.md` | Espaçamento, ritmo, alinhamento |
| `reference/spatial-design.md` | Grid, composição espacial |
| `reference/responsive-design.md` | Comportamento em breakpoints |
| `reference/motion-design.md` | Movimento com propósito |
| `reference/animate.md` | Adicionar animação |
| `reference/interaction-design.md` | Micro-interações, estados |
| `reference/ux-writing.md` | Copy clara, sem ruído |
| `reference/clarify.md` | Melhorar UX copy confusa |

### Edge cases e qualidade
| Comando | Quando usar |
|---|---|
| `reference/harden.md` | Erros, estados vazios, edge cases |
| `reference/onboard.md` | Primeiras telas, ativação |
| `reference/optimize.md` | Performance |
| `reference/adapt.md` | Adaptação pra diferentes devices |
| `reference/delight.md` | Momentos de alegria |
| `reference/overdrive.md` | Efeitos extraordinários |
| `reference/cognitive-load.md` | Reduzir esforço mental do usuário |
| `reference/brand.md` | Aderência à marca |
| `reference/product.md` | Alinhamento com estratégia de produto |
| `reference/live.md` | ⚠️ Modo live — upstream tem via Puppeteer, **não instalado aqui** |

## Anti-patterns críticos (consultar antes de entregar)

Referência viva em `reference/`. Os mais comuns:
- **Inter em tudo** — variar de fonte adiciona craft
- **Gradiente roxo genérico** — sinal de IA preguiçosa
- **Cards com borda grossa** — ruído visual, raramente resolvido
- **Modal abuse** — pro favor, pare
- **Contraste ruim** — acessibilidade + leitura
- **Ícones gigantes** — dispersam atenção
- **UX writing redundante** — "Click here to..." é lixo

## Brand adapter (Vital Slim)

Ver `brand-adapter.md` — traduz a linguagem do Impeccable pros tokens de marca do IVS:
- Cor primária: dourado `#9F8844`
- Tipografia oficial
- Espaçamento padrão
- Logos vetorizados (assets/brand/)

## O que NÃO está incluído (e por quê)

- ❌ **Scripts** (`.mjs`) do upstream — usam `child_process.spawn`, rodam local server. Risco de execução sem controle. Só necessários para o modo `/live` (variante visual em browser).
- ❌ **CLI `npx impeccable detect`** — instala Puppeteer + Chromium (~400MB), superfície grande.
- ❌ **`.claude-plugin/`** — marketplace manifest, irrelevante fora do canal oficial.

## Precedência em caso de conflito

1. **`cerebro/CLAUDE.md`** — regras absolutas (honestidade radical, proibições, compliance CFM/CRM-BA) **sempre vencem**
2. **`brand-adapter.md`** — tokens específicos do IVS
3. **`reference/*.md`** — princípios gerais de design

Se um conselho do Impeccable contradizer uma regra do `cerebro/CLAUDE.md` (ex: "seja ousado" vs "conteúdo médico precisa ser sóbrio"), **vence o CLAUDE.md**.

## Fonte e atribuição

Ver `NOTICE.md`. Conteúdo dos `reference/*.md` vem do projeto **Impeccable** de Paul Bakaus (`pbakaus/impeccable`), distribuído sob Apache 2.0.
