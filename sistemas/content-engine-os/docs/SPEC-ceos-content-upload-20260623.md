# SPEC-CEOS-CONTENT-UPLOAD-20260623: Ingestão de biblioteca editorial IVS

## Fontes recebidas do Tiaro

- `Instituto Vital - Biblioteca de Hooks.docx`
- `Roteiros Feed.txt`
- `Instituto Vital Slim _Régua de Mídia_.xlsx`
- `Instituto Vital - Roteiros de Stories.docx`
- `Instituto Vital - Biblioteca de Temas.docx`

## Objetivo

Alimentar o Content Engine OS com material editorial aprovado/estruturado do IVS para que os módulos de produção, sprint semanal, banco de roteiros e stories tenham repertório real de marca.

## Script canônico do lote

```bash
python3 scripts/ingest_content_uploads_20260623.py
```

## Origem técnica

Todos os registros deste lote usam prefixo/origem:

```text
ivs-upload-20260623
```

A ingestão é idempotente: antes de recriar o lote, remove apenas registros com essa origem/source_ref/código controlado.

## Mapeamento

| Fonte | Destino no banco | Uso operacional |
|---|---|---|
| Biblioteca de Hooks | `narrative_devices` + `viral_scripts` | hooks reutilizáveis para Reels, Carrossel, Stories e Estáticos |
| Roteiros Feed | `viral_scripts` | roteiros prontos para banco de roteiros |
| Régua de Mídia XLSX | `viral_scripts` + `themes` | peças aprováveis com formato, pilar, hook, copy e legenda |
| Roteiros de Stories | `story_themes` + `viral_scripts` | temas/roteiros para Stories Engine e destaques |
| Biblioteca de Temas | `themes` | temas editoriais e itens de “não falar/evitar” |

## Resultado da ingestão em 2026-06-23

```json
{
  "hooks": 30,
  "feed_scripts": 3,
  "themes": 35,
  "media_sheet_items": 13,
  "story_items": 47,
  "total": 128
}
```

## Endpoints impactados

- `/api/generation/roteiros?tenant_slug=demo`
- `/api/stories/themes?tenant_slug=demo&limit=50`
- `/api/weekly-command/overview?tenant_slug=demo`
- `/banco-roteiros`
- `/stories-engine`
- `/sprint-semanal`

## Governança

- Não publica conteúdo.
- Não envia mensagem.
- Não toca em paciente/lead.
- Não escreve em QuarkClinic, Z-API ou Omie.
- Mantém conteúdo como repertório editorial interno para geração e aprovação.
- Conteúdos com prova social/antes-depois continuam exigindo autorização e revisão humana antes de publicação.

## Validação mínima

```bash
python3 -m py_compile scripts/ingest_content_uploads_20260623.py scripts/content_engine_smoke.py
python3 scripts/content_engine_smoke.py --json
```
