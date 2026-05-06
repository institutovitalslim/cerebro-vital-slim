# Providers de Mídia IVS — Mapa Útil + Playbook de Decisão (2026-04-28)

> Documento operacional para escolher provider de imagem, vídeo, voz e experimentação no stack do Instituto Vital Slim.
>
> Índice central relacionado:
> - `cerebro/areas/marketing/governanca-visual-ivs-index.md`

## 1. Objetivo

Evitar duas falhas:
1. instalar ecossistemas grandes sem ganho real
2. escolher provider errado para a tarefa errada

Este documento resume:
- o que realmente presta no stack atual
- o que vale observar em ecossistemas externos como benchmark
- quando usar cada tecnologia

---

## 2. Stack oficial atual do IVS

### Imagem final premium
- **Google / NanoBanana2**
- **OpenAI**

### Imagem rápida / prototipagem
- **Z-Image-Turbo**

### Vídeo
- **Qwen / Wan**

### Voz
- **ElevenLabs**

### Montagem
- **Python + FFMPEG**

### Regra oficial de reel
- **1 cena = 1 clip = 1 fala = 1 legenda**

---

## 3. Mapa útil de providers/modelos observados

## 3.1 Imagem

### Google / NanoBanana2
**Melhor para:**
- análise de imagens
- extração/descrição
- fotos mais realistas
- capas premium
- situações com maior exigência estética

**Forças**
- boa qualidade visual
- bom realismo
- útil para contexto premium da marca

**Fraquezas**
- custo maior que opção gratuita
- não é a opção para prototipagem mais barata

**Status no IVS**
- provider forte para peça final
- obrigatório para análise/extracao/descrição de imagem quando essa regra estiver ativa

### OpenAI
**Melhor para:**
- arte final
- imagem institucional
- outputs consistentes
- produção com maior previsibilidade

**Forças**
- consistência
- bom acabamento
- encaixe bom em produção

**Fraquezas**
- pago
- não é a melhor escolha para exploração barata em volume

**Status no IVS**
- provider premium oficial para material final

### Z-Image-Turbo
**Melhor para:**
- conceito
- mockup
- rascunho
- testes visuais rápidos
- exploração barata

**Forças**
- gratuito
- rápido
- dependência leve
- útil para ideação

**Fraquezas**
- menos previsível
- roda em servidor externo via HuggingFace Space
- não serve para peça médica sensível ou imagem final crítica

**Status no IVS**
- aprovado apenas como provider de prototipagem

---

## 3.2 Vídeo

### Qwen / Wan
**Melhor para:**
- clips com movimento real
- reels com blocos curtos
- base visual para pipeline oficial de reels

**Forças**
- já validado operacionalmente
- bom encaixe com fluxo de 1 clip por bloco
- boa relação custo/resultado no cenário atual

**Fraquezas**
- ainda exige curadoria de prompt e montagem
- nem sempre a primeira geração vira peça final

**Status no IVS**
- provider padrão de vídeo

### Veo / outros premium de vídeo
**Melhor para:**
- testes de qualidade superior quando houver disponibilidade real

**Fraquezas atuais**
- histórico de falhas/instabilidade em parte do fluxo
- não são hoje o caminho mais confiável do pipeline IVS

**Status no IVS**
- secundário, experimental, não padrão

---

## 3.3 Voz

### ElevenLabs
**Melhor para:**
- locução final de reels
- voz natural
- blocos narrativos curtos

**Forças**
- naturalidade melhor
- já validado no pipeline
- resolve limitação do gTTS e do TTS quota-blocked anterior

**Fraquezas**
- exige escolha correta de voz
- custo/uso deve ser racional

**Status no IVS**
- provider oficial de voz

### gTTS
**Melhor para:**
- fallback de emergência

**Fraquezas**
- voz inferior
- não atende padrão premium do IVS

**Status no IVS**
- fallback apenas

---

## 4. Benchmark externo observado, mas não adotado

## Open-Generative-AI

### O que ele oferece que interessa observar
- catálogo amplo de modelos
- radar de providers
- ideias de UX para imagem, vídeo, lip sync e multi-image input
- referência de arquitetura híbrida entre UI e inferência remota/local

### O que NÃO adotamos
- stack inteira do produto
- desktop app em Electron
- monorepo/workspaces/submódulos
- posicionamento "uncensored / no guardrails"
- dependência operacional central desse ecossistema

### Veredito
- **usar como benchmark**, não como base operacional do IVS

---

## 5. Regra de decisão por tipo de tarefa

## 5.1 Se a tarefa é IMAGEM

### Use Z-Image-Turbo quando:
- o objetivo é explorar conceito
- a imagem é só um rascunho
- você quer testar direção criativa sem custo
- ainda não vale gastar com provider premium

### Use Google / NanoBanana2 quando:
- precisa de estética premium
- precisa de melhor realismo
- a peça já está perto do uso final
- a imagem vai sustentar percepção de marca

### Use OpenAI quando:
- precisa de produção final consistente
- quer maior previsibilidade
- a tarefa exige output mais controlado

### Nunca usar Z-Image-Turbo quando:
- houver foto da Dra.
- houver paciente
- houver conteúdo clínico sensível
- a peça for final premium sem revisão rigorosa

---

## 5.2 Se a tarefa é VÍDEO

### Use Qwen / Wan quando:
- precisa de clips curtos com movimento real
- vai montar reel no pipeline oficial
- quer coerência com o fluxo validado

### Estrutura obrigatória
- 1 cena = 1 clip = 1 fala = 1 legenda

### Não fazer
- depender de uma legenda única por cima do vídeo inteiro
- tratar assets isolados como sucesso se o vídeo final estiver ruim

---

## 5.3 Se a tarefa é VOZ

### Use ElevenLabs quando:
- a voz vai para entrega final
- o vídeo precisa soar premium
- o timing precisa casar com os blocos do reel

### Use gTTS quando:
- for apenas contingência
- não houver alternativa imediata

---

## 5.4 Se a tarefa é DESCOBERTA / PESQUISA DE PROVIDER NOVO

### Primeiro filtro
Perguntar:
1. resolve um problema real do IVS?
2. substitui algo fraco do stack atual?
3. reduz custo sem piorar qualidade?
4. reduz tempo sem aumentar risco?
5. cabe como ferramenta pequena ou é outro produto inteiro?

### Sinais de reprovação rápida
- monorepo enorme
- submódulos obrigatórios
- Electron sem necessidade
- branding desalinhado com compliance
- promessa vaga de privacidade
- muita complexidade para ganho marginal

---

## 6. Matriz curta de escolha

### Imagem
- **Protótipo barato:** Z-Image-Turbo
- **Peça final premium:** OpenAI / Google
- **Realismo forte / capa premium:** Google
- **Consistência de produção:** OpenAI

### Vídeo
- **Pipeline oficial de reels:** Qwen / Wan
- **Teste premium extra:** opcional, experimental, não padrão

### Voz
- **Final:** ElevenLabs
- **Emergência:** gTTS

---

## 7. Regra mestra do IVS

Não escolher provider por hype.
Escolher por:
- encaixe na operação
- compliance
- qualidade final percebida
- previsibilidade
- simplicidade de manutenção

Se a ferramenta for maior que o problema que ela resolve, ela não entra.

---

## 8. Próximos usos práticos deste playbook

Este documento deve orientar:
- escolha de provider antes de gerar imagem
- escolha de provider antes de produzir reel
- avaliação de ferramentas externas novas
- futuras comparações de providers de lipsync, vídeo e multi-image edit

## 9. Consulta rápida

Para uso operacional curto antes de gerar, consultar também:
- `cerebro/areas/marketing/providers-midia-checklist-rapido.md`
