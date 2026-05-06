---
name: stitch-mcp-operacao
description: Homologa, opera e valida o Stitch via MCP no ambiente OpenClaw do IVS usando mcporter na VPS. Use quando for preciso listar projetos, validar conectividade, gerar telas ou auditar a disponibilidade operacional do Stitch no ambiente real.
category: integracao
status: ativo
owner: operacoes
---

# Stitch MCP — Operação canônica no IVS

## Quando usar
- quando for preciso validar se o Stitch está operacional na VPS do OpenClaw
- quando a equipe precisar listar projetos ou testar tools reais do Stitch
- quando houver necessidade de integrar ou revalidar o servidor MCP do Stitch após mudança de ambiente
- quando for necessário distinguir presença de skill versus operação real do runtime MCP

## Inputs necessários
- acesso shell à VPS
- `mcporter` disponível no ambiente
- diretório do servidor MCP: `/root/.openclaw/workspace/tools/stitch-mcp-server`
- autenticação Google válida no host via `gcloud`

## Dependências e pré-requisitos
### Técnicas
- `node`
- `npm`
- `mcporter`
- `gcloud`
- servidor MCP buildado em `/root/.openclaw/workspace/tools/stitch-mcp-server/dist/index.js`
- registro mcporter em `/root/cerebro-vital-slim/config/mcporter.json`

### Canônicas
- `cerebro/empresa/skills/GOVERNANCA-SKILLS.md`
- `cerebro/empresa/skills/_index.md`
- `memory/2026-05-03.md`

### Compliance
- não declarar o Stitch como operacional apenas porque a skill existe
- não usar Claude Desktop como destino operacional do IVS
- homologação exige teste real de tool, não só leitura de schema

## Passo a passo
1. Confirmar que o servidor MCP existe no host:
   - `/root/.openclaw/workspace/tools/stitch-mcp-server`
2. Se necessário, preparar runtime:
   - `npm install`
   - `npm run build`
3. Confirmar autenticação do host:
   - `gcloud auth print-access-token`
4. Registrar ou revisar o servidor no `mcporter`:
   - `mcporter config add stitch --stdio 'node /root/.openclaw/workspace/tools/stitch-mcp-server/dist/index.js'`
5. Validar exposição do schema:
   - `mcporter list stitch --schema`
6. Validar operação real com chamada funcional:
   - `mcporter call stitch.list_projects --output json`
7. Só após retorno real classificar o Stitch como operacional na VPS/OpenClaw

## Critérios de qualidade
- o servidor precisa estar buildado sem erro
- o host precisa autenticar via `gcloud`
- o `mcporter` precisa listar o schema do servidor `stitch`
- pelo menos uma tool real precisa responder com dados válidos
- o parecer final precisa separar claramente:
  - skill instalada
  - runtime MCP instalado
  - autenticação válida
  - tool real homologada

## Output esperado
- confirmação objetiva do status operacional do Stitch no OpenClaw
- caminho canônico do runtime e do registro MCP
- comando de validação rápida para futuras auditorias

## Falhas comuns / fallback
- skill instalada sem runtime MCP: instalar e buildar `stitch-mcp-server`
- runtime presente sem auth: corrigir `gcloud`
- schema aparece mas tool real falha: não homologar; investigar credencial, projeto ou conectividade
- tentativa de configurar no Claude Desktop: corrigir o rumo e registrar no `mcporter` da VPS
