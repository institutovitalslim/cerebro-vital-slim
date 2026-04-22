# Testes Canônicos Operacionais

Este diretório guarda cenários mínimos de regressão para fluxos recorrentes.

## Objetivo
Evitar que mudanças em regras, skills ou estrutura quebrem comportamentos operacionais já validados.

## Estrutura
Cada arquivo deve conter:
- contexto
- entrada típica
- ação esperada
- evidência mínima de sucesso
- gatilhos para parar e pedir confirmação

## Regra
Se uma mudança estrutural piorar a capacidade de satisfazer esses cenários, ela não está pronta.
