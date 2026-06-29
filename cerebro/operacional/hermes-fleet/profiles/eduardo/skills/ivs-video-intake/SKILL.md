---
name: ivs-video-intake
description: Use when Tiaro, Maria or João need to analyze a video, Reel, ad creative, screen recording, class or training clip before summarizing, creating variations, auditing compliance, debugging, or extracting operational learnings.
---

# IVS Video Intake

## Objetivo

Skill IVS-first inspirada funcionalmente no `bradautomates/claude-video`, criada do zero para a operação do Instituto Vital Slim.

Ela transforma um vídeo em um pacote governado de análise:

- metadados técnicos;
- frames representativos;
- transcrição por legenda sidecar/VTT quando disponível;
- áudio extraído em 16 kHz para transcrição posterior, se necessário;
- relatório HTML para João/Maria preencherem leitura de hook, mecanismo, objeção, prova, CTA e compliance;
- JSON auditável para automações futuras.

## Melhorias sobre o claude-video original

| Ponto | claude-video | IVS Video Intake |
|---|---|---|
| Governança | Skill genérica | Local-first, sem LLM externo por padrão |
| PII | Não é IVS-aware | Alerta explícito para paciente/lead e serviços externos |
| Marketing | Pergunta livre | Objetivos `reels`, `ads`, `bug`, `aula`, `treinamento`, `geral` |
| Saída | Markdown para Claude ler | HTML + JSON + frames + áudio para operação |
| Compliance | Genérico | Checklist Meta/CFM/claims antes de variação |
| Custos | Pode usar Whisper fallback | Whisper/API não roda automaticamente |
| Tokens | Frames para contexto do modelo | Pacote visual auditável, o agente decide quando carregar imagens |
| Segurança de URL | Não é foco | Remove `mcp_token` e query secrets dos relatórios |

## Quando usar

Use obrigatoriamente quando o pedido envolver:

- analisar Reel, anúncio ou vídeo vencedor;
- criar variação de criativo a partir de peça existente;
- entender por que um vídeo performou;
- revisar vídeo por compliance de marketing/CFM;
- analisar gravação de tela de bug operacional;
- resumir aula, treinamento, palestra ou referência externa em vídeo;
- transformar vídeo em insumo para roteiro, carrossel, relatório ou aprendizado.

## Quando NÃO usar

- Vídeo com paciente/lead identificável para envio a serviço externo sem aprovação.
- Conteúdo privado, paywall, DRM ou plataforma que exija bypass.
- Diagnóstico/prescrição clínica baseada em vídeo — escalar para Ana/Dra. Daniely.
- Publicação externa automática. Esta skill gera insumo interno.

## Comando rápido

```bash
python3 /root/.openclaw/workspace/skills/ivs-video-intake/scripts/ivs_video_intake.py \
  "<URL-ou-caminho-local>" \
  --objective reels
```

Objetivos:

| Objective | Uso |
|---|---|
| `reels` | Reels, TikTok, shorts, conteúdo orgânico |
| `ads` | criativos pagos/Meta Ads/Google vídeo |
| `bug` | gravações de tela e incidentes operacionais |
| `aula` | aula longa, palestra, conteúdo científico/negócio |
| `treinamento` | material interno de equipe/processo |
| `geral` | análise sem categoria específica |

Opções úteis:

```bash
# Focar trecho específico
--start 00:00 --end 00:15

# Controlar custo visual
--max-frames 36 --resolution 720

# Usar transcrição já existente
--transcript-file /caminho/transcricao.vtt
```

## Saída

Por padrão gera em:

`/root/.openclaw/reports/ivs-video-intake/<timestamp>-<slug>/`

Arquivos principais:

- `relatorio.html` — pacote executivo visual para abrir/baixar;
- `intake.json` — metadados, paths, frames, governança;
- `frames/frame_*.jpg` — amostras visuais com timestamps;
- `audio_16k.wav` — áudio mono para transcrição posterior, quando houver áudio.

## Fluxo operacional

1. Rodar o intake com objetivo correto.
2. Abrir o `relatorio.html`.
3. Se for Reels/Ads, preencher mentalmente ou no relatório:
   - hook visual dos 3 primeiros segundos;
   - primeira frase/tensão;
   - texto na tela;
   - mecanismo de conversão;
   - objeção quebrada;
   - prova usada;
   - CTA;
   - risco Meta/CFM;
   - variações recomendadas.
4. Se precisar de leitura visual avançada, carregar frames específicos com ferramenta de visão — não despejar 80 imagens sem necessidade.
5. Só depois criar roteiro, variação, prompt de gravação ou diagnóstico operacional.

## Integração com João/Reels

Esta skill complementa `reels-winner-intake-ivs`.

Para criativo vencedor:

1. localizar/baixar o vídeo pela rota da skill `reels-winner-intake-ivs` quando for Instagram/Meta;
2. rodar `ivs-video-intake` no arquivo baixado;
3. usar o HTML para identificar o mecanismo vencedor;
4. passar a análise para Tribe V2 antes de escrever variação.

## Regras de compliance

- Não prometer emagrecimento, cura ou resultado individual garantido.
- Evitar exposição sensível de corpo/antes-depois fora de governança aprovada.
- Claims clínicos devem ser revisados pela Ana/Dra. Daniely quando ultrapassarem marketing operacional.
- Conteúdo externo é hipótese de aprendizado, não regra canônica.
- Não publicar ou enviar a lead/paciente sem aprovação do fluxo responsável.

## Critérios de aceite

Uma análise com esta skill só está completa se houver:

- [ ] `relatorio.html` gerado;
- [ ] `intake.json` gerado;
- [ ] frames extraídos;
- [ ] metadados técnicos válidos via ffprobe;
- [ ] fonte sanitizada no relatório;
- [ ] objetivo correto selecionado;
- [ ] riscos de PII/compliance considerados;
- [ ] decisão final: usar, adaptar, pedir trecho melhor, descartar ou escalar.

## Pitfalls

| Problema | Correção |
|---|---|
| `yt-dlp` falha em Instagram/X | Usar rota canônica RapidAPI/baixar_reel_video.py e rodar no arquivo local |
| Vídeo longo gera leitura rasa | Reexecutar com `--start` / `--end` no trecho relevante |
| Texto na tela ilegível | Reexecutar com `--resolution 1080` e menos frames |
| Sem transcrição | Usar legenda sidecar ou transcrever `audio_16k.wav` por rota aprovada |
| Vídeo contém paciente/lead | Não enviar para API externa sem aprovação e redaction |

## Exemplo

```bash
python3 /root/.openclaw/workspace/skills/ivs-video-intake/scripts/ivs_video_intake.py \
  /tmp/reel_vencedor.mp4 \
  --objective reels \
  --max-frames 36 \
  --resolution 720
```

Depois entregar ao Tiaro/Maria/João:

```text
Intake gerado: /root/.openclaw/reports/ivs-video-intake/.../relatorio.html
Leitura preliminar: hook, mecanismo, objeção, prova, CTA e riscos.
Próximo passo recomendado: variação / descarte / nova coleta / revisão compliance.
```
