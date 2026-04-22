# Teste Canônico — GitHub

## Cenário
Usuário pede commit, push, PR, issue, comentário ou validação de CI.

## Entrada típica
- repositório
- branch, issue ou PR alvo
- mudança pretendida

## Ação esperada
- operar no repositório correto
- fazer apenas a mudança necessária
- validar o efeito real no GitHub ou no repositório local conforme o caso

## Evidência mínima de sucesso
- commit/hash real
- push/PR/issue/comentário existente
- CI/status consultado com resultado concreto

## Parar e pedir confirmação quando
- o repositório alvo estiver ambíguo
- a ação for destrutiva
- houver risco de alterar remoto errado
