# Design Premium IVS — Taste Skill seletivo, Impeccable e Motion

## Pedido
Tiaro autorizou seguir com a incorporação das referências analisadas: Emil Kowalski Motion System, Impeccable e Taste Skill para a operação do Instituto Vital Slim.

## Decisão operacional
- `design-impeccable` permanece como padrão oficial de identidade, hierarquia, polimento e qualidade visual IVS.
- Foi criada a skill canônica IVS `design-premium-ivs` para orquestrar:
  - Impeccable IVS como base;
  - Taste Skill seletivo para evitar frontend genérico;
  - motion sutil, sob demanda, sem exagero em contexto médico.
- Taste Skill foi incorporado de forma seletiva, não como pacote inteiro indiscriminado.

## Skills instaladas localmente
- `taste-skill`
- `gpt-tasteskill`
- `redesign-skill`
- `output-skill`
- `image-to-code-skill`
- `design-premium-ivs` criada internamente

## Agente atualizado
João (`agente-reels-intel`) recebeu:
- `design-premium-ivs`
- `design-impeccable`
- `taste-skill`
- `gpt-tasteskill`
- `redesign-skill`
- `output-skill`
- `image-to-code-skill`

## Regra adicionada ao João
Quando criar ou revisar HTML, landing page, cockpit, pré-consulta, dashboard, apresentação executiva ou protótipo visual do IVS, João deve usar `design-premium-ivs` como regra de orquestração. `design-impeccable` permanece como padrão oficial de identidade/polimento IVS. Taste é seletivo para evitar frontend genérico. Motion deve ser sutil, funcional e compatível com contexto médico.

## Governança
- Não trocar identidade IVS por estética SaaS genérica, neon, roxo/azul de IA ou template externo.
- Não copiar código/ativos proprietários sem validação de licença e decisão explícita.
- Apresentações de paciente devem ser quase estáticas; interfaces vivas podem ter microinterações funcionais.
- Entregas HTML para Tiaro devem respeitar a regra de arquivo/anexo quando aplicável.

## Validação
- Arquivos `SKILL.md` presentes no workspace.
- João atualizado em `/root/.openclaw/openclaw.json`.
- Gateway recarregado via SIGUSR1.
- Healthcheck retornou `{"ok":true,"status":"live"}`.
