# RC-25 — Criação da skill IVS Visual Layer

**Data:** 2026-07-19  
**Origem:** Tiaro  
**Contexto:** Após reverse do repositório `onlook-dev/onlook`, Tiaro pediu seguir e testar a nova skill em uma apresentação V12 de programa de acompanhamento.

## Decisão

Criar a skill `ivs-visual-layer` como versão IVS-first, local e governada, inspirada funcionalmente em editores visuais tipo Onlook, sem copiar código externo e sem instalar o repositório inteiro.

## Escopo da primeira versão

- Instrumentar uma cópia HTML, nunca o original.
- Detectar seções/layers.
- Adicionar painel visual interno de QA.
- Gerar auditoria JSON redigida.
- Não publicar, não enviar a paciente e não aplicar alteração definitiva.

## Evidência do piloto

Piloto executado sobre uma apresentação V12 já existente de programa de acompanhamento. Resultado: cópia instrumentada criada, 22 seções/layers detectadas, browser abriu sem erro JS, original preservado.

## Arquivos criados

- `skills/ivs-visual-layer/SKILL.md`
- `skills/ivs-visual-layer/scripts/ivs_visual_layer.py`

## Próxima evolução

Adicionar edição controlada de texto/classes com geração de diff e preview antes/depois, mantendo aprovação humana antes de aplicar em template canônico ou publicar.
