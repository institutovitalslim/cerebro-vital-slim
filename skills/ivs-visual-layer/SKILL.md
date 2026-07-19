---
name: ivs-visual-layer
description: Camada visual IVS-first inspirada no Onlook para auditar, navegar e editar com segurança apresentações HTML/Next do IVS sem tocar no original; gera cópia instrumentada, relatório JSON e checklist visual.
category: tecnologia
status: piloto
owner: Maria
---

# IVS Visual Layer

## Objetivo

Criar uma camada visual governada para páginas e apresentações do Instituto Vital Slim, inspirada funcionalmente no Onlook, mas sem copiar código externo e sem instalar o repositório inteiro.

A primeira versão é local/read-only por padrão: recebe um HTML IVS existente, cria uma cópia instrumentada e adiciona:

- mapa de seções/layers;
- painel visual interno;
- IDs e metadados `data-ivs-layer`;
- checklist de design/compliance;
- relatório JSON com evidências;
- modo seguro sem alteração no arquivo original.

## Quando usar

- Testar/polir apresentações V10/V11/V12 de pacientes.
- Auditar landing pages e funis antes de publicação.
- Criar camada de navegação/QA visual para Tiaro revisar.
- Preparar uma próxima versão com diff controlado.

## Regras de governança

1. Nunca sobrescrever o HTML original.
2. Nunca publicar automaticamente.
3. Nunca expor dados sensíveis em relatório; usar contagens, IDs de seção e caminhos locais.
4. Para arquivo de paciente, gerar cópia interna de QA por padrão.
5. Mudança clínica/conteúdo médico não é função desta skill; só estrutura visual, navegação e auditoria.
6. Qualquer aplicação definitiva em template canônico exige validação posterior e commit.

## Comando básico

```bash
python3 /root/cerebro-vital-slim/skills/ivs-visual-layer/scripts/ivs_visual_layer.py \
  --input /caminho/apresentacao.html \
  --out-dir /root/cerebro-vital-slim/deliverables/ivs-visual-layer-smoke \
  --mode presentation-v12
```

## Comando com edição controlada + diff

Crie um JSON de operações:

```json
{
  "operations": [
    {"type": "text_replace", "old": "texto atual", "new": "texto novo", "count": 1},
    {"type": "add_class", "id": "final-cta", "class": "ivs-review-focus"}
  ]
}
```

Rode:

```bash
python3 /root/cerebro-vital-slim/skills/ivs-visual-layer/scripts/ivs_visual_layer.py \
  --input /caminho/apresentacao.html \
  --out-dir /root/cerebro-vital-slim/deliverables/ivs-visual-layer-smoke \
  --mode presentation-v12 \
  --edit-spec /caminho/edit.json
```

Operações suportadas no piloto:

- `text_replace`: substitui texto em cópia, com `count` explícito.
- `add_class`: adiciona classe CSS em elemento por `id`, útil para foco/revisão visual.

A saída editada continua sendo QA interno e não substitui o original.

## Saídas

- `*-visual-layer.html`: cópia HTML instrumentada para revisão interna.
- `*-visual-layer.audit.json`: relatório estrutural redigido.
- `*-visual-layer-edited.html`: cópia editada quando `--edit-spec` é usado.
- `*-visual-layer-edited.diff`: diff unificado da camada visual base para a cópia editada.

## Critérios de aceite do piloto

- O arquivo original permanece intacto.
- A cópia HTML existe e abre como documento standalone.
- O relatório JSON lista seções detectadas, classes principais e riscos.
- A apresentação mantém conteúdo e assets embutidos.
- A camada visual aparece apenas como QA interno e não substitui versão paciente.

## Roadmap

1. Piloto read-only/instrumentado.
2. Seleção visual de seção e edição de texto/classes com diff.
3. Preview antes/depois.
4. Aplicação em branch/cópia.
5. Integração com templates oficiais e design system IVS.
