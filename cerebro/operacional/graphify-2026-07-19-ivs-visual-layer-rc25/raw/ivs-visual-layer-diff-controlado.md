# RC-25 — IVS Visual Layer com edição controlada e diff

**Data:** 2026-07-19  
**Origem:** Tiaro / continuação do piloto IVS Visual Layer  
**Contexto:** Tiaro pediu seguir após o primeiro smoke da skill na apresentação V12 de programa de acompanhamento.

## Decisão

Evoluir `ivs-visual-layer` para suportar edição controlada em cópia, com diff explícito e sem sobrescrever o HTML original.

## Escopo implementado

- `--edit-spec` com JSON de operações.
- Operação `text_replace` com `old`, `new` e `count` explícito.
- Operação `add_class` por `id`, para foco/revisão visual.
- Geração de:
  - `*-visual-layer-edited.html`
  - `*-visual-layer-edited.diff`
- Auditoria JSON passa a registrar `edit.operations_requested`, `edit.operations_applied`, erros, arquivos gerados e `original_unchanged`.

## Validação

- Testes unitários criados antes da implementação e rodados por `unittest`.
- RED verificado: testes falharam por ausência de `edit_spec_path`.
- GREEN verificado: 2 testes passaram.
- Smoke real na apresentação V12 de paciente: 2 operações aplicadas, 0 erros, diff gerado, HTML editado carregado no browser sem erro JS, SHA do original preservado.

## Governança

A edição controlada continua sendo QA interno. Não é envio ao paciente, não publica e não muda conteúdo clínico do original. Aplicação definitiva em template canônico exige validação posterior.
