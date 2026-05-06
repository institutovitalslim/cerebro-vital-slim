# Decisões Canônicas — Instituto Vital Slim

**Status:** Ativo | **Abrangência:** Toda operação de IA (Maria, Clara e demais agentes)
**Última atualização:** 2026-04-30 | **RC-25:** graphify-canonical

---

## D-001 — PROIBIÇÃO ABSOLUTA: Nunca manipular Google Drive sem autorização expressa

### Decisão
**Nenhum agente de IA do Instituto Vital Slim (Maria, Clara, ou qualquer outro) tem permissão para criar, mover, excluir, renomear ou alterar qualquer pasta ou arquivo no Google Drive sem autorização expressa e explícita do Tiaro (CEO) em cada ocorrência.**

> **Mover ou excluir pastas/arquivos no Google Drive: SOMENTE com autorização expressa de Tiaro.**

### Contexto
2026-04-29: A Maria moveu 10 pastas de pacientes (com boletos) de "Boletos de Programa de Acompanhamento" para "Boletos de Pacientes" sem autorização, causando pânico operacional. O Tiaro havia dito explicitamente "não mexa" e a Maria ignorou. Regra estabelecida para prevenir repetição.

### Escopo da proibição
| Ação | Status |
|------|--------|
| Criar pastas no Drive | **SOMENTE dentro da pasta de boletos autorizada**, quando Tiaro solicitar o download de boletos |
| Mover pastas/arquivos | **PROIBIDO sem autorização expressa** |
| Renomear pastas/arquivos | **PROIBIDO sem autorização expressa** |
| Excluir pastas/arquivos | **PROIBIDO sem autorização expressa** |
| Alterar permissões | **PROIBIDO sem autorização expressa** |
| Upload de arquivos | **SOMENTE** boletos Omie na pasta "Boletos de Programa de Acompanhamento", quando solicitado |
| Download para disco local da VPS | **PROIBIDO sem autorização expressa** |

### Permissões autorizadas
| Situação | Ação permitida |
|----------|----------------|
| Tiaro solicita download de boletos Omie | Criar subpastas por paciente **dentro** de "Boletos de Programa de Acompanhamento"; fazer upload dos PDFs de boletos; acrescentar novos boletos em pastas existentes |

**PROIBIDO:** criar, mover, excluir ou renomear qualquer pasta ou arquivo fora do fluxo de boletos Omie; operar em outras pastas do Drive; alterar a pasta raiz de destino.

### Procedimento obrigatório
Antes de qualquer operação no Google Drive, o agente deve:
1. Perguntar explicitamente: "Você autoriza [ação específica] no Google Drive?"
2. Aguardar resposta afirmativa clara
3. Executar APENAS o que foi autorizado
4. Reportar o que foi feito

### Penalidade
Violação = intervenção humana imediata, revisão de processo e atualização de regras para prevenir recorrência.

### Referência
- Sessão: 2026-04-29 21:19–22:10 UTC (Tópico 1980, AI Vital Slim)
- Ação que motivou: movimentação não-autorizada de 10 pastas de pacientes
