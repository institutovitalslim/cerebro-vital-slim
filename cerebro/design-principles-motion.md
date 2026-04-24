# Princípios de Motion & Craft — destilação

Arquivo curto com os princípios de motion e "craft" absorvidos da skill de **Emil Kowalski** (`emilkowalski/skill`, https://github.com/emilkowalski/skill). Não instalamos a skill inteira porque o conteúdo cabe em uma página curada — princípios universais, não um comando dinâmico.

Fonte: Emil Kowalski, Design Engineer, autor da lib `vaul` e do curso [animations.dev](https://animations.dev/). Conteúdo original Apache-inspired (licença upstream não especificada; princípios gerais de design são não-copyrighteable).

---

## Princípios centrais

### 1. Gosto é treinado, não inato
Bom gosto visual não é preferência pessoal — é instinto treinado. Desenvolver estudando trabalho excelente, perguntando *por que* algo parece certo. Para IVS: estudar referências de clínicas premium (Parsley Health, Forward, Eight Sleep site, Function Health) antes de criar.

### 2. Detalhes invisíveis acumulam
O ótimo não se anuncia. O usuário não nota; só percebe que "funciona como deveria". Meta: que o paciente abra a apresentação HTML e não pense no HTML, só absorva o conteúdo clínico.

### 3. Beleza é alavanca
Em software comoditizado, **gosto é o diferenciador**. Para o IVS em concorrência com outras clínicas de emagrecimento, a apresentação visual importa tanto quanto o protocolo clínico.

---

## Framework de decisão de animação

### Perguntar PRIMEIRO: "Isso deve animar?"

| Frequência de uso | Decisão |
|---|---|
| 100+ vezes/dia (ex: atalho de teclado, comando) | **Nunca animar** |
| Dezenas de vezes/dia (hover, navegação de lista) | Remover ou minimizar |
| Ocasional (modal, drawer, toast) | Animação padrão OK |
| Raro/primeira vez (onboarding, celebração) | Pode ter delight |

**Regra dura**: nunca animar ação iniciada por teclado. Faz parecer lento e desconectado.

### Se vai animar, escolher curva certa

| Ação | Curva |
|---|---|
| Elemento entrando (modal abrindo, dropdown) | `ease-out` — resposta imediata, acomoda no final |
| Elemento saindo | `ease-in` ou `ease-in-out` |
| Loading | Linear |
| Delight moment | Curva custom (spring, bezier) |

**`ease-in` em dropdown dá sensação de lentidão** — só usar em elementos saindo.

### Especificar propriedades (não usar `all`)

❌ `transition: all 300ms`
✅ `transition: transform 200ms ease-out`

`all` força o browser a observar mudanças em tudo — caro e imprevisível. Listar só o que muda.

### Nada aparece do nada

❌ `transform: scale(0)` — elemento some/aparece do nada
✅ `transform: scale(0.95); opacity: 0` — simula "vinha de perto"

No mundo real objetos não surgem do zero. Use `0.95` + `opacity: 0` para entrada, reverso para saída.

### Estado `:active` em botão é obrigatório

Todo botão interativo precisa de feedback visual quando pressionado:

```css
button:active { transform: scale(0.97); }
```

Sem isso, o botão não "sente" responsivo ao toque/clique.

### Origem da transformação

Popover/dropdown devem escalar **a partir do gatilho**, não do centro:

```css
transform-origin: var(--radix-popover-content-transform-origin);
```

Modal é exceção — fica centralizado.

---

## Formato de review de UI (obrigatório)

Quando revisar HTML/CSS existente, entregar no formato:

| Antes | Depois | Por quê |
|---|---|---|
| `transition: all 300ms` | `transition: transform 200ms ease-out` | Especificar propriedade + ease-out mais responsivo |
| `scale(0)` | `scale(0.95); opacity: 0` | Nada aparece do nada |
| Sem `:active` em botão | `transform: scale(0.97)` no `:active` | Feedback tátil obrigatório |

Não usar formato "Before:/After:" em linhas separadas. Tabela markdown sempre.

---

## Aplicação no IVS

### Apresentações HTML de paciente
- Motion **baixa**: paciente lê o conteúdo, não admira animação. Transições sutis entre slides, micro-interações em botões/CTAs. Nada de animação no carregamento inicial (paciente pode abrir várias vezes).
- Usar `prefers-reduced-motion` quando o usuário preferir parado.

### Novo site institucional (em dev com Matheus Zappiello)
- Hero com motion estratégica (1 animação marcante, não 5 medianas)
- Scroll-triggered moderado
- Tipografia com weight transitions sutis
- **Nunca** gradiente roxo, nunca "AI-generated vibe"

### CTAs (marcar consulta, agendar retorno)
- `:hover` sutil (transform ou cor, não ambos)
- `:active` com `scale(0.97)`
- Loading state quando clicado (antes de redirecionar)

---

## Regras de precedência

1. **`cerebro/CLAUDE.md`** sempre vence (compliance, honestidade, tom clínico)
2. **`cerebro/empresa/skills/design-impeccable/brand-adapter.md`** — tokens IVS
3. **Este arquivo** — princípios de motion/craft

Se o princípio de motion aqui conflitar com a seriedade clínica de uma apresentação médica, **vence a sobriedade clínica**. Motion é leverage, não obrigação.

_Destilado em 2026-04-24 por Claude (agente remoto GitHub) a partir de `emilkowalski/skill` (Apache-compatible use of general design principles)._
