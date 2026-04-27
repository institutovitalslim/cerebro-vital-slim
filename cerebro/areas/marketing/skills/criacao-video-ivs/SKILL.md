---
name: criacao-video-ivs
description: >
  Framework de criação de vídeo para o Instituto Vital Slim. Gera roteiros completos para reels,
  storyboards, prompts de IA para geração de frames, e variações de criativos para Meta Ads.
  Adaptação do "Claude Video Cheat Code" para a realidade operacional da IVS.
  Trigger: "crie um vídeo sobre [tema]", "roteiro de reel", "variações de criativo para ads".
---

# Criação de Vídeo — IVS

## Origem
Conteúdo adaptado de **"The Claude Video Cheat Code"** (Notion, 2026).
Original focado em **Remotion** (programmatic video via React/Node.js) + Claude Code.

## Análise de Viabilidade para IVS

### ✅ O que FUNCIONA para nós
| Conceito Original | Adaptação IVS |
|------------------|---------------|
| "Instalar um Video Engine no Claude" | Usar `video_generate` + `image_generate` como engine de frames |
| Iteração em segundos, não horas | Geração de frames em lote + montagem rápida |
| "Make 10 versions instantly" | Gerar variações de roteiro/frames para A/B test em ads |
| Zero experiência em software complexo | Prompts prontos, não precisa saber After Effects |
| Kinetic typography | Texto animado via templates ou geração direta |

### ⚠️ O que NÃO funciona (ainda)
| Limitação Original | Impacto IVS |
|-------------------|-------------|
| Requer Claude Code (terminal) | Não temos — usamos OpenClaw |
| Requer Remotion (React/Node.js) | Não instalado — complexidade alta |
| Renderização local de vídeo | Nossa infra não tem GPU para render |
| Curva de aprendizado React | Time não tem dev frontend disponível |

### 🎯 Decisão
**NÃO instalar Remotion/Claude Code.** Em vez disso, criar framework de **geração de conteúdo de vídeo** usando:
- `video_generate` (AI video generation)
- `image_generate` (frames estáticos)
- Scripts Python para montagem simples (FFMPEG)
- Roteiros otimizados para reels Instagram

---

## Framework IVS de Criação de Vídeo

### 1. Input
- **Tema:** assunto médico/comercial (ex: "lipedema", "magnésio", "GLP-1")
- **Objetivo:** Audiência / Desejo / Ação (ver `criacao-carrossel/SKILL.md`)
- **Formato:** Reel (9:16, até 90s) ou Ad (1:1 ou 4:5, 15-30s)
- **Tom:** educativo, autoridade, empático

### 2. Estrutura de Roteiro (3-Act)

#### ATO 1 — HOOK (0-3 segundos)
- Dor direta ou curiosidade aberta
- Texto grande em tela ou fala impactante
- Ex: *"Sua perna incha e dói? Pode não ser obesidade."*

#### ATO 2 — STORYTELLING (3-45 segundos)
- Prova científica (paper, dado)
- Contexto médico explicado simples
- Identificação com a Avatar Mestre
- 3 pilares de prova (igual carrossel)

#### ATO 3 — CTA (últimos 10 segundos)
- Frase de empatia + direcionamento
- "Salve este vídeo" ou "Link na bio"
- Sempre com a Dra. Daniely em frame final

### 3. Storyboard por Tipo

#### Tipo A: Talking Head (Dra. fala)
- Frame 1: Dra. com expressão de autoridade
- Frames 2-5: Cortes com texto animado sobreposto
- Frame final: Dra. + CTA + CRM

#### Tipo B: Kinetic Typography (texto animado)
- Fundo escuro com elementos dourados
- Texto aparece palavra por palavra
- Ícones/ilustrações médicas simples
- Música de fundo épica mas discreta

#### Tipo C: Before/After (compliance CFM)
- NUNCA mostrar resultado quantificado sem protocolo
- Foco em "como a paciente se sente"
- Depoimentos com autorização formal

### 4. Prompts de IA para Frames

#### Para `image_generate` (capa/thumbnail):
```
Formato vertical 9:16. Fundo escuro elegante com 
elementos dourados sutis. Texto grande em branco: 
"[HEADLINE]". Estilo médico premium, clínica de 
emagrecimento. Sem rostos.
```

#### Para `video_generate` (clips):
```
Vídeo vertical 9:16. Close-up de mãos de médica 
explicando. Fundo clínico branco/dourado. 
Movimento suave de câmera. Iluminação profissional. 
Estilo documentário médico.
```

### 5. Variações para A/B Test (Ads)

Gerar automaticamente:
- **V1:** Hook agressivo (dor direta)
- **V2:** Hook curiosidade ("Você sabia que...")
- **V3:** Hook autoridade ("Como médica, vejo isso todo dia")
- **V4:** Hook social proof ("11% das mulheres...")

Mesmo corpo do vídeo, apenas o hook muda. Ideal para teste em Meta Ads.

---

## Dependências
- `video_generate` (OpenClaw nativo)
- `image_generate` (OpenClaw nativo)
- `ffmpeg` (para montagem simples, se necessário)

## Scripts
- `scripts/gerar_roteiro.py` — gera roteiro completo a partir de tema
- `scripts/gerar_variacoes.py` — gera N variações de hook para mesmo vídeo

## Segurança / Compliance
- Todo conteúdo médico passa por filtro CFM/CRM-BA
- Nunca prometer resultado quantificado
- Antes/depois apenas com autorização e protocolo documentado
- Avatar Dra. Daniely: usar apenas foto oficial (`avatar.png`)

---

## Status
🟡 **Skill instalada. Aguardando validação de primeiro roteiro.**
Próximo passo: gerar roteiro de reel sobre tema real da IVS e validar com Tiaro.
