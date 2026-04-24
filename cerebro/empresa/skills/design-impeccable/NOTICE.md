# Notice — Atribuição

Esta skill (`cerebro/empresa/skills/design-impeccable/`) é uma **adaptação curada** do projeto open-source **Impeccable** para uso no cérebro do Instituto Vital Slim.

## Fonte original
- **Projeto:** Impeccable
- **Repositório:** https://github.com/pbakaus/impeccable
- **Autor:** Paul Bakaus
- **Copyright:** 2025-2026 Paul Bakaus
- **Licença:** Apache License 2.0
- **Ancestralidade:** O Impeccable é baseado no skill `frontend-design` original da Anthropic (Apache 2.0, Copyright 2025 Anthropic, PBC — https://github.com/anthropics/skills/tree/main/skills/frontend-design). A referência `typography.md` incorpora contribuições de `ehmo/typecraft-guide-skill` mergeadas no upstream.

## O que foi adotado verbatim (sob Apache 2.0)
Os 35 arquivos em `reference/` foram copiados como-estão do diretório `.claude/skills/impeccable/reference/` do repositório upstream no commit HEAD de 2026-04-24.

## O que foi adicionado/modificado pelo Instituto Vital Slim
- `SKILL.md` — ponto de entrada em **português brasileiro**, com workflow específico pro contexto IVS (apresentações HTML de paciente, novo site, brand tokens, regras canônicas do `cerebro/CLAUDE.md` como precedência).
- `brand-adapter.md` — mapeamento explícito para tokens de marca do Vital Slim (dourado `#9F8844`, tipografia, logos vetorizados, regras de tom clínico).
- Esta `NOTICE.md`.

## O que foi intencionalmente NÃO adotado
- `scripts/*.mjs` e `.js` do upstream — usam `child_process.spawn`/`execSync` e fazem spawn de servidor local. Segurança-primeiro: não trouxemos.
- CLI (`bin/cli.js`, `package.json`, `npx impeccable detect`) — depende de Puppeteer/Chromium, superfície de ataque grande por pouco valor no nosso caso de uso (apresentações HTML estáticas e páginas simples).
- `.claude-plugin/marketplace.json` — manifest de distribuição, irrelevante fora do marketplace oficial.

## Política de atualização
Esta skill é uma **fork curada**, não sincronização contínua. Novas versões do upstream serão revisadas manualmente (security review + ajuste de contexto) antes de qualquer atualização. Documentar no `cerebro/learning-ledger.md`.

## Licença desta adaptação
Apache License 2.0 (mesma do upstream). Arquivo `LICENSE` nesta pasta.

_Adaptação datada: 2026-04-24. Revisor: Claude (agente remoto GitHub) sob autorização do Tiaro._
