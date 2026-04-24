# Brand Adapter — Vital Slim ↔ Impeccable

Traduz o vocabulário genérico do Impeccable para os **tokens de marca do Instituto Vital Slim**. Sempre consultar antes de seguir uma recomendação do `reference/`.

## Identidade visual

### Cor primária
- **Dourado oficial**: `#9F8844`
- Uso: títulos de destaque, CTAs primários, acentos, borda de cards-chave
- **Nunca**: gradiente dourado-roxo, dourado puro em texto corrido (contraste baixo sobre branco)

### Cores de suporte
- **Texto principal**: `#1a1a1a` (preto quase-puro para legibilidade)
- **Texto secundário**: `#4a4a4a` (cinza 70%)
- **Fundo**: branco `#ffffff` ou off-white `#fafafa` (escolher por superfície)
- **Sucesso clínico** / **Alerta** / **Erro**: definir caso a caso em consulta com o Tiaro antes de aplicar. Evitar verde/vermelho/amarelo hardcoded — conteúdo médico usa semântica específica.

### Tipografia
- **Referência institucional**: definir com o Tiaro (verificar brand kit em `assets/brand/`)
- **Princípio**: seguir `reference/typography.md` — variar de fonte (nem sempre Inter), ajustar tracking, letter-spacing, peso
- **Para apresentações clínicas**: tom sóbrio, médico. **Evitar fontes display dramáticas**; preferir serif elegante (Lora, Playfair, Cormorant) ou sans-serif clássica (Söhne, Inter bem-usada, Work Sans).

### Logos
- Vetorizados disponíveis em `assets/brand/`:
  - `logo-vital-slim-vetorizado-rgb.pdf` — digital
  - `logo-assinatura-simplificada-cmyk.pdf` — impressão
- **Nunca** inventar logo, reconstruir de screenshot, ou usar placeholder "LOGO HERE"

## Tom de voz (sobrepõe `reference/ux-writing.md`)

- **Português brasileiro**, sempre
- **Médico sem ser frio** — acolhimento clínico, seriedade respeitosa
- **Nunca** transmitir "está tudo bem" em apresentações com exames alterados — exames com problema devem ser apresentados com gravidade adequada, elevando consciência do paciente (regra reforçada pelo Tiaro em 2026-04-23)
- **Nunca** prometer resultado — compliance CFM/CRM-BA. Usar "contribuir", "apoiar", "ajudar a"; nunca "garante", "cura", "elimina"
- **Evitar** exagero comercial em copy médica. Linguagem calma e confiante

## Regras de "polish" obrigatórias (sobrepõem o default)

Antes de fechar qualquer HTML:

1. **Conferir logo** em posição correta, tamanho adequado (usar SVG/PDF vetorial, não PNG downscaled)
2. **Conferir dourado `#9F8844`** em acentos — não overprint, não em fundo colorido sem fallback
3. **Conferir CFM do médico** quando aparecer nome (Dra. Daniely Freitas CRM-BA 27588; Dra. Patrícia Fabrini quando for tricologia)
4. **Conferir contato oficial** do IVS (não usar placeholder)
5. **Conferir que exames alterados têm tom grave** — não minimizar achados clínicos na copy
6. **Conferir responsividade** — apresentações são vistas em celular pelo paciente, não só desktop
7. **Conferir acessibilidade básica** — contraste AA mínimo em texto, semântica HTML correta (`<h1>`, `<h2>`, `<strong>` — não `<div class="bold">`)
8. **Conferir nenhuma informação inventada** — nomes, números, telefones, especialidades. Na dúvida, perguntar ao Tiaro.

## O que sempre respeitar

- **Regras absolutas de `cerebro/CLAUDE.md`** vencem sempre (honestidade radical, proibições absolutas, compliance CFM/CRM-BA)
- **`cerebro/verdades-operacionais.md`** — fatos canônicos do negócio
- **Padrões da skill `prompt-imagens`** quando houver imagem da Dra. Daniely ou Dra. Patrícia — nunca gerar rosto do zero, sempre referência do acervo

## Quando o Impeccable contradiz

Exemplo: `reference/bolder.md` sugere "amplificar o timid design com cor vibrante". Se isso entrar em conflito com "apresentação de paciente precisa ser sóbria" — **vence a sobriedade clínica**. Ousadia visual pode ser aplicada em landing page ou site institucional; **não em apresentação clínica individual**.

Sempre que perceber conflito entre Impeccable e regras do IVS: **ignora o Impeccable naquele ponto específico e registra a decisão em comentário** no HTML gerado.

_Atualizado: 2026-04-24._
