# Teste Canônico — Omie

## Cenário
Usuário pede cadastro ou emissão recorrente envolvendo paciente, proposta, OS ou boleto.

## Entrada típica
- nome do paciente
- contexto de faturamento ou emissão
- eventual referência a dados vindos do Quarkclinic

## Ação esperada
- localizar a fonte canônica do fluxo
- evitar duplicidade
- validar banco/categoria/campos estruturados quando houver emissão
- executar o fluxo correto ou parar para confirmação objetiva se faltar banco/identidade

## Evidência mínima de sucesso
- cadastro/emissão validado no ambiente correto; ou
- bloqueio explícito com motivo concreto; ou
- artefato derivado entregue quando fizer parte do fluxo

## Parar e pedir confirmação quando
- houver ambiguidade de identidade
- faltar banco/conta corrente
- houver risco de duplicidade
- houver impacto financeiro sem confirmação suficiente
