---
name: geracao-apresentacao-paciente
description: Cria apresentações HTML premium para pacientes dos Programas de Acompanhamento do Instituto Vital Slim, consolidando evolução antropométrica, exames mais recentes, fotos comparativas e identidade visual da clínica. Use quando for necessário montar devolutiva individual de evolução para paciente específico, revisar material para reunião clínica/comercial, ou gerar arquivo único em HTML para envio interno.
category: operacional
status: ativo
owner: operacao-ivs
---

# Geração de Apresentação de Paciente

## Quando usar
- Quando Tiaro ou equipe autorizada pedir uma apresentação de evolução de paciente de programa de acompanhamento
- Quando for necessário consolidar peso, medidas, exames e fotos em uma devolutiva visual
- Quando precisar gerar um HTML único, com imagens incorporadas, pronto para compartilhamento
- Quando for necessário localizar exames e fotos do paciente no Google Drive da conta operacional da clínica

## Inputs necessários
- Nome completo do paciente
- Material de evolução disponível: medidas, pesos, datas ou imagem da tabela de evolução
- Acesso à pasta do paciente no Google Drive
- Se houver, objetivo da apresentação e contexto de uso

## Dependências e pré-requisitos
### Técnicas
- `gog` CLI autenticado, preferencialmente com `medicalcontabilidade@gmail.com`
- Acesso aos arquivos da skill em `skills/geracao-apresentacao-paciente/`
- Capacidade de leitura de PDFs e imagens no ambiente
- Diretório de entrega em `/root/deliverables/`

### Canônicas
- `cerebro/empresa/skills/GOVERNANCA-SKILLS.md`
- `cerebro/LEARNING_PROTOCOL.md`
- `MEMORY.md`
- identidade visual disponível em `cerebro/assets/identidade-visual/`
- fotos da Dra. Daniely em `cerebro/assets/fotos-dra-daniely/`

### Compliance
- Não inventar dado clínico, laboratorial ou operacional
- Não afirmar interpretação clínica final sem base nos exames localizados
- Em caso de dúvida clínica sensível, sinalizar necessidade de validação da Dra. Daniely
- A skill monta material de apresentação; não substitui conduta médica

## Passo a passo
1. Identificar o paciente corretamente pelo nome e confirmar a pasta correspondente no Google Drive.
2. Localizar os exames mais recentes, priorizando os arquivos com data mais nova e nome do paciente.
3. Localizar a pasta de fotos e selecionar um comparativo coerente de antes e depois.
4. Extrair da evolução enviada os dados de peso e medidas, preservando datas e marcando qualquer campo duvidoso para revisão.
5. Consolidar os principais indicadores da jornada:
   - peso inicial e atual
   - redução absoluta e percentual
   - cintura, quadril e demais medidas relevantes
   - linha do tempo resumida da evolução
6. Extrair dos exames os achados principais úteis para devolutiva:
   - glicemia, hemoglobina glicada, insulina, HOMA-IR
   - perfil lipídico
   - enzimas hepáticas
   - marcadores inflamatórios
   - vitaminas, minerais e hormônios relevantes
7. Gerar a apresentação em HTML com:
   - logomarca do Instituto Vital Slim
   - foto da Dra. Daniely quando aplicável
   - bloco de resumo executivo
   - comparativo inicial x atual
   - tabela consolidada de medidas
   - comparativo fotográfico
   - bloco de exames recentes
8. Sempre que o destino for compartilhamento externo ou facilidade operacional, incorporar imagens no próprio HTML em base64 para produzir arquivo único.
9. Salvar a saída final em `/root/deliverables/apresentacao-[slug-paciente]-inline.html` quando for versão autônoma.
10. Enviar o arquivo final ao solicitante assim que estiver pronto.

## Critérios de qualidade
- paciente corretamente identificado
- nenhuma informação inventada
- exames realmente extraídos da pasta do paciente
- fotos coerentes com antes e depois
- identidade visual da clínica aplicada
- HTML funcional em arquivo único quando solicitado
- leitura clara no celular e no desktop
- tom executivo, objetivo e premium

## Output esperado
- arquivo HTML de apresentação do paciente
- preferencialmente uma versão inline, com imagens incorporadas no próprio arquivo
- conteúdo pronto para revisão interna ou apresentação ao paciente

## Falhas comuns / fallback
- se as imagens não carregarem, substituir referências externas por imagens embutidas em base64
- se houver mais de uma pasta ou homônimo, confirmar o paciente correto antes de fechar a apresentação
- se não localizar exames recentes, entregar a versão parcial e sinalizar exatamente a lacuna
- se os dados da tabela vierem por imagem e algum campo estiver duvidoso, marcar para conferência antes da versão final
- se houver interpretação hormonal ou clínica sensível, incluir como ponto de atenção e não como conclusão fechada

## Arquitetura — Pipeline de extração de exames (atualizada 2026-05-05)

A extração de valores dos PDFs de laudos laboratoriais usa **LLM (OpenAI gpt-4o)** com Structured Outputs + **validador multi-layer** com refs canônicas armazenadas em `assets/refs_canonicas.json`.

### Fluxo
```
PDF do paciente (Drive)
  → pdftotext extrai texto
  → gpt-4o (Structured Outputs strict) extrai {nome, valor, unidade}
  → validador classifica status usando refs canônicas (sexo + idade)
  → renderer v9 gera HTML
```

### Componentes
- `scripts/extrair_exames_llm.py` — extrator LLM (gpt-4o)
- `scripts/validador_exames.py` — 6 camadas de validação (L0-L6)
- `scripts/extrair_exames_pdf.py` — wrapper de download Drive + parser legacy (fallback)
- `scripts/gerar_apresentacao.py` — orchestrator (chama `extrair_todos_exames_llm`)
- `scripts/gerar_apresentacao_v9.py` — renderer v9 (light cream luxury, 7 seções)
- `assets/refs_canonicas.json` — catálogo único de refs por exame + sexo + idade

### Camadas do validador
| Layer | O que valida |
|-------|--------------|
| L0 | Pre-check: sexo do paciente obrigatório (RC-01) |
| L1 | Schema: campos obrigatórios |
| L2 | Catálogo: nome canônico está em refs_canonicas.json |
| L3 | Plausibilidade: valor dentro do range fisiológico absoluto |
| L4 | Sex+age lookup: ref aplicável encontrada |
| L5 | Cross-check lipídico: LDL ≈ Total − HDL − VLDL |
| L6 | Status recalc: status final usando refs canônicas |

### Atualizar referências clínicas
Editar `assets/refs_canonicas.json`. Cada exame tem array `ranges` com objetos:
```json
{
  "sexo": "M",
  "idade_min": 17,
  "idade_max": 40,
  "ref_min": 400,
  "ref_max": 916,
  "fonte": "IVS conservador — Testo Total >400 ng/dL"
}
```
A próxima apresentação gerada usa as refs atualizadas.

### Auditoria por paciente
Cada execução salva em `state/auditoria/<paciente-slug>_<timestamp>.json`:
- exames extraídos pelo LLM
- exames validados (entram na apresentação)
- exames em revisão manual com motivo (NÃO entram)
- cross-check warnings

### Regras canônicas
Ver `REGRAS_CANONICAS.md`:
- **RC-01**: sexo do paciente é obrigatório
- **RC-02**: validação multi-layer obrigatória antes do render
- **RC-03**: hemograma diferencial usa valor absoluto (/mm³)
- **RC-04**: Plaquetas com multiplicador x10³

### Custo e latência
- gpt-4o: ~$0,06 por laudo (16k tokens input, 2k tokens output)
- Latência: 10-20s por laudo
- Validador: instantâneo (lookup em JSON em memória)
