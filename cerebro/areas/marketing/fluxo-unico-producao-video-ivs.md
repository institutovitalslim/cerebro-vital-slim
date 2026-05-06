# Fluxo Único de Produção de Vídeo — IVS

## Objetivo
Criar um pipeline único, auditável e simples para qualquer vídeo do IVS, evitando improviso, retrabalho e dispersão entre roteiro, produção, aprovação e reaproveitamento.

## Regra-mãe
- **1 cena = 1 clip = 1 fala = 1 legenda**
- Todo vídeo nasce com objetivo claro: **Audiência, Tempo de Tela, Desejo ou Ação**
- Toda peça deve incluir **quebra de objeções** quando o tema tocar consulta, tratamento, valor, medo, tempo ou insegurança

## Escopo
Este fluxo vale para:
- reels orgânicos
- vídeos curtos de autoridade
- vídeos explicativos para lead/paciente
- criativos de anúncio
- reaproveitamento de conteúdo já gravado

## Pipeline oficial

### 1. Entrada
Registrar obrigatoriamente:
- tema
- objetivo do vídeo
- público-alvo
- origem do material
- formato desejado
- CTA esperado

**Origens possíveis:**
- ideia interna
- referência externa
- vídeo bruto gravado
- fala da Dra. Daniely
- ativo operacional da Clara
- reel de concorrente/benchmark

### 2. Classificação
Definir em até 1 minuto:
- é **orgânico**, **comercial**, **explicativo** ou **ads**?
- entra melhor como **talking head**, **kinetic typography**, **clip guiado** ou **reaproveitamento**?
- precisa de narração?
- precisa da Dra. em cena?
- precisa de compliance médico reforçado?

### 3. Roteiro
Todo vídeo precisa sair com:
- hook
- desenvolvimento em blocos
- quebra de objeções
- CTA
- indicação visual por cena

### 4. Produção
#### Se for vídeo novo com IA
- clips: `video_generate` com Qwen/Wan como padrão
- capa/frame estático: `image_generate`
- voz: ElevenLabs
- trilha: `music_generate` quando necessário

#### Se for vídeo real gravado
- usar o material original como ativo-base
- cortar em blocos curtos
- legendar por fala
- gerar versões derivadas quando fizer sentido

### 5. Montagem
Pipeline de montagem:
1. separar por cenas
2. sincronizar fala e legenda
3. revisar legibilidade
4. ajustar trilha abaixo da voz
5. garantir abertura forte nos 3 primeiros segundos

### 6. Revisão
Checklist obrigatório:
- hook forte?
- 1 ideia por cena?
- legenda sincronizada?
- compliance preservado?
- objeção quebrada?
- CTA claro?
- serve ao objetivo do vídeo?

### 7. Aprovação
Aprovação em 3 estados:
- aprovado
- ajustar
- arquivar

Se ajustar, devolver com comentário objetivo por bloco/cena.

### 8. Saída final
Toda entrega final deve gerar pelo menos:
- vídeo final
- roteiro-base salvo
- observação de uso
- possibilidade de reaproveitamento

### 9. Reaproveitamento obrigatório
De cada vídeo aprovado, avaliar se ele pode virar:
- corte curto
- variação de hook
- carrossel
- roteiro de anúncio
- ativo da Clara
- peça de follow-up

## Portas operacionais

### Porta A — Reel de conteúdo
Entrada: tema ou referência
Saída: roteiro + vídeo curto + CTA

### Porta B — Vídeo comercial
Entrada: objeção, oferta, campanha
Saída: criativo com quebra de objeções e CTA de ação

### Porta C — Vídeo explicativo da Clara
Entrada: ativo operacional de atendimento
Saída: vídeo pronto para envio no WhatsApp com mensagem de apoio

### Porta D — Reaproveitamento
Entrada: vídeo já gravado
Saída: cortes, novos hooks, derivações

## Responsabilidade sugerida
- João: roteiro, análise, hook, quebra de objeções, reaproveitamento
- Clara: uso operacional em atendimento quando for ativo de WhatsApp
- Maria: governança do fluxo e padronização
- Tiaro: aprovação estratégica quando necessário

## Regra de decisão rápida
Se houver dúvida entre começar pela estética ou pela função, começar pela **função**.

Pergunta obrigatória:
**Esse vídeo existe para fazer o quê exatamente?**
