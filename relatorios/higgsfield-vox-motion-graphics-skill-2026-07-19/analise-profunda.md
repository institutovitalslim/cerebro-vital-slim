# Análise profunda — skill Vox Motion Graphics para Higgsfield

**Fonte:** Google Drive informado pelo Tiaro  
**Arquivo baixado:** `vox-motion-graphics.skill`  
**SHA-256:** `765c946d78bf114907e96da8be4ac749e36ef8009fa273eb65f2133b9ca83053`  
**Arquivos internos:** 3  
**Segredos detectados:** não

## Veredito

A skill é realmente valiosa. Ela não é só um prompt: é um pipeline completo para gerar vídeos explicativos narrados, no estilo editorial/motion graphics, com pesquisa, roteiro, prompts por bloco, geração de clipes, voiceover e montagem final.

Para o IVS, o valor maior não é copiar “Vox” literalmente; é internalizar a estrutura: **tema → pesquisa → tese → roteiro em blocos de 10s → estilo visual travado → clipes paralelos → narração consistente → montagem com legenda**.

## Inventário extraído

| Arquivo | Linhas | Bytes | Modelos/ferramentas citados |
|---|---:|---:|---|
| `SKILL.md` | 321 | 16872 | explainer_video, gemini_omni, generate_audio, generate_image, generate_video, job_status, list_voices, nano_banana_pro, resolve_explainer_preset, seed_audio, seedance_2_0, show_generations |
| `references/diorama-doc.md` | 164 | 7389 | gemini_omni, generate_audio, generate_image, generate_video, nano_banana_pro, seedance_2_0 |
| `references/vox-prompts.md` | 159 | 7674 | generate_image, nano_banana_pro |

## Pipeline operacional identificado

1. **Topic discovery** — se não houver tema, pesquisar tendências atuais com potencial visual.
2. **Research** — buscar 2–3 fontes, coletar números, datas e reversões; nunca roteirizar de memória.
3. **Style key** — usar preset Mixed Media vertical ou gerar key própria 16:9.
4. **Script** — N blocos de ~20–24 palavras, cada bloco = 10 segundos.
5. **Block prompts** — um prompt por bloco, com STYLE, SCENE, MOTION, AUDIO e NEGATIVE.
6. **Clips** — gerar cada vídeo com style key anexada.
7. **Voiceover** — uma voz documental consistente, um take por bloco.
8. **Assemble** — juntar vídeo + áudio + legenda; entregar MP4 final.

## Dois estilos da skill

### 1. Mixed Media collage — padrão

Visual: recortes fotográficos, papel, halftone, cores chapadas, gráficos abstratos, mapas, setas e círculos desenhados.

Melhor uso IVS:
- “Por que emagrecer e manter é tão difícil?”
- “O que os exames mostram antes do corpo mudar?”
- “Como músculo protege o resultado?”
- “Por que sono, tireoide e resistência insulínica travam evolução?”

Regra crítica: **não colocar texto legível nos clipes**; a legenda entra na montagem.

### 2. Paper-diorama documentary

Visual: diorama de jornal envelhecido, recortes, luz cinematográfica, prop lettering curto, câmera FPV/fake-oner.

Melhor uso IVS:
- vídeos dramáticos de mecanismo/metáfora;
- explicações sobre indústria do emagrecimento;
- temas “dinheiro, poder, sistema”, com cuidado para não parecer sensacionalista médico.

## Técnicas narrativas mais importantes

- **Objeto-metáfora único** atravessando todos os blocos.
- **Pergunta no começo, resposta só no final.**
- **Impacto a cada ~3 segundos.**
- **Alternância macro/wide** para manter retenção.
- **Reveal shot memorável.**
- **Blocos de 10s** com uma única ideia por bloco.

## Riscos e adaptações obrigatórias para IVS

| Risco | Adaptação IVS |
|---|---|
| A skill original manda prosseguir antes de aprovação de gasto | No IVS, geração paga exige gate do Tiaro/João antes do primeiro job pago |
| Linguagem “Vox” pode virar cópia de estilo de terceiro | Usar como gramática editorial, não copiar identidade, logo, paleta ou assinatura Vox |
| Conteúdo médico pode virar promessa | Ana/Dra. Daniely validam claims clínicos; sem promessa de resultado |
| Clipes com texto podem sair ilegíveis | Texto só em legenda ou props curtos controlados no estilo diorama |
| Políticos/rostos/nuclear podem acionar moderação | Para IVS, evitar temas sensíveis; usar metáforas clínicas abstratas |
| Voz/legenda podem desalinha | Medir duração real de cada take antes da montagem |

## Oportunidade para o João

Criar uma skill IVS derivada: `ivs-motion-graphics-higgsfield`, com três formatos:

1. **Reel 60s vertical educativo** — 6 blocos.
2. **Short 90s autoridade** — 9 blocos.
3. **Vídeo 3 min manifesto/explicativo** — 18 blocos.

Cada execução deve gerar: briefing, fontes, roteiro, prompts, lista de jobs, MP4 final, legenda/caption Instagram e checklist de compliance.

## Prompt-base IVS recomendado

```text
Criar motion graphics editorial premium para o Instituto Vital Slim, vertical 9:16, sem rosto de paciente, sem promessa de resultado.
Tema: <tema>.
Tese: <tese>.
Estilo: mixed-media editorial médico-premium, recortes de papel, gráficos abstratos, mapas metabólicos, linhas douradas sutis, fundo creme/café, movimento elegante.
Estrutura: 6 blocos de 10 segundos, uma ideia por bloco, narração documental em português brasileiro, legendas queimadas na montagem.
Negativo: texto ilegível no vídeo bruto, promessa de cura/emagrecimento garantido, antes/depois, dados de paciente, tom sensacionalista.
```

## Próximo passo recomendado

Transformar esta análise em uma skill IVS operacional governada e rodar um smoke sem gasto: gerar roteiro + prompts de 6 blocos para um tema de IVS, sem submeter jobs pagos ainda.
