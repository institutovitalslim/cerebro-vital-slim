---
name: ivs-design-qa
description: Use when validating IVS HTML sites, internal reports, patient-presentation shells, responsive behavior, visual evidence, placeholders, broken assets, or pre-publication quality gates.
version: 1.0.0
author: Instituto Vital Slim
license: Proprietary
metadata:
  hermes:
    tags: [html, qa, playwright, design, ivs]
    related_skills: [ivs-visual-layer]
---

# IVS Design QA

## Overview

Executar uma única rotina de QA em artefatos HTML do Instituto Vital Slim, sem alterar o original e sem autorizar publicação ou envio a paciente.

## When to Use

- Antes de publicar uma landing ou site IVS.
- Antes de aprovar o casco ou a renderização de uma apresentação.
- Quando houver suspeita de overflow, asset quebrado, erro de navegador ou placeholder.
- Para produzir evidências desktop/mobile e um contrato JSON redigido.

Não usar como substituto de validação clínica, autorização de publicação ou aprovação de envio ao paciente.

## Pré-requisitos

- Linux com Python 3.11+;
- Node.js 20+;
- Chromium em `/snap/bin/chromium` ou `CHROMIUM_PATH` definido;
- `ivs-site` disponível para artefatos do tipo `site`;
- dependências instaladas com `npm ci --ignore-scripts --no-audit --no-fund` dentro da skill.

O wrapper `scripts/ivs-design-qa` instala somente o lockfile pinado quando `node_modules/playwright-core` estiver ausente.

## Uso

### Landing ou site

```bash
/root/cerebro-vital-slim/skills/ivs-design-qa/scripts/ivs-design-qa \
  --input /caminho/landing.html \
  --out-dir /root/deliverables/qa-landing \
  --artifact-type site \
  --data-mode anonymous
```

### Casco anônimo de apresentação

```bash
/root/cerebro-vital-slim/skills/ivs-design-qa/scripts/ivs-design-qa \
  --input /caminho/casco.html \
  --out-dir /root/deliverables/qa-apresentacao \
  --artifact-type patient-presentation \
  --data-mode anonymous
```

### Apresentação real, apenas local

```bash
/root/cerebro-vital-slim/skills/ivs-design-qa/scripts/ivs-design-qa \
  --input /caminho/apresentacao-local.html \
  --out-dir /caminho/local/restrito/qa \
  --artifact-type patient-presentation \
  --data-mode sensitive-local
```

## Contrato de saída

Arquivos gerados no `--out-dir`:

- `ivs-design-qa.report.json` — contrato de automação redigido;
- `ivs-design-qa.report.html` — leitura executiva;
- `browser/desktop.png` e `browser/mobile.png`;
- `visual-layer/*-visual-layer.html` e `*.audit.json` — apenas em `anonymous`; o componente é deliberadamente omitido em `sensitive-local` para não serializar título, headings, IDs ou classes sensíveis.

Códigos de saída:

- `0`: `PASS` ou `PASS_WITH_CONCERNS`;
- `2`: `BLOCKED`;
- `1`: falha interna.

## Bloqueios mínimos

- HTML inexistente ou sem estrutura essencial;
- viewport ausente;
- placeholder técnico real (`TODO`, `FIXME`, lorem ipsum ou marcador entre colchetes);
- overflow horizontal;
- erro de JavaScript/console;
- imagem quebrada;
- falha no `ivs-site` para sites;
- dado identificável em apresentação declarada anônima;
- qualquer alteração do hash do HTML original.

## Governança

1. O original é somente leitura; `ivs-visual-layer` recebe cópia de saída.
2. Relatórios não serializam texto da página, e-mail, CPF ou telefone.
3. `sensitive-local` oculta o caminho de origem no relatório e marca screenshots como sensíveis.
4. O gate nunca define `patient_send_ready=true` e nunca publica conteúdo.
5. `PASS` técnico não substitui revisão humana de copy, clínica ou compliance.
6. Para apresentação real, a validação clínica canônica continua obrigatória antes de qualquer revisão do Tiaro.

## Testes

```bash
cd /root/cerebro-vital-slim
python3 -m unittest discover -s skills/ivs-design-qa/tests -v
```

## Pilotos homologados

- `fixtures/landing-piloto.html` — landing institucional sintética;
- `fixtures/apresentacao-anonima-piloto.html` — casco anônimo com dados não clínicos e sintéticos.

## Common Pitfalls

1. **Tratar `PASS` como autorização externa:** o gate mantém `patient_send_ready=false` e `external_publish=false`.
2. **Rodar apresentação real como `anonymous`:** use `sensitive-local`; identificadores em modo anônimo bloqueiam.
3. **Abrir HTML por `file://`:** o probe usa servidor efêmero em `127.0.0.1`, resolve caminhos canônicos e rejeita traversal/symlinks fora da raiz para compatibilidade segura com Chromium Snap e assets relativos.
4. **Permitir recursos remotos no navegador:** o probe intercepta e bloqueia requisições fora do servidor local, registrando `external_request_blocked` sem serializar a URL.
5. **Contornar bloqueios editando a régua:** corrija o artefato ou crie teste de regressão para falso positivo comprovado.
6. **Copiar texto clínico para logs:** use somente códigos, contagens e hashes; screenshots sensíveis permanecem locais.

## Verification Checklist

- [ ] `python3 -m unittest discover -s skills/ivs-design-qa/tests -v` termina com todos os testes em `OK`.
- [ ] `ivs-design-qa.report.json` existe e contém `status` válido.
- [ ] Screenshots desktop e mobile existem e foram revisados visualmente.
- [ ] O hash do original permaneceu igual e `original_unchanged=true`.
- [ ] Nenhum texto identificável aparece no relatório JSON.
- [ ] `patient_send_ready=false` e `external_publish=false` permanecem invariantes.
