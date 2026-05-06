# João — Prompts Canônicos para Ferramentas Web do IVS

**Status:** canônico operacional  
**Origem técnica:** adaptação seletiva do repositório público `nidhinjs/prompt-master`, aprovado por Tiaro em 2026-05-04.  
**Regra de uso:** este arquivo NÃO instala nem adota o repositório externo como skill operacional. Ele extrai apenas padrões úteis de briefing, escopo, critérios de sucesso, limites e stop conditions para uso do João em projetos web do IVS.

## 1. Princípios canônicos

Para qualquer ferramenta web generativa ou agentic, João deve transformar pedido vago em briefing executável com estes blocos mínimos:

1. **Objetivo** — o que precisa ser criado, corrigido ou melhorado.
2. **Contexto IVS** — marca, público, uso interno/externo, decisão anterior e restrições do cérebro.
3. **Stack/ambiente** — ferramenta alvo, framework, dependências permitidas e formato de entrega.
4. **Escopo** — arquivos, telas, componentes ou páginas que podem ser tocados.
5. **Não fazer** — o que a ferramenta não pode inventar, adicionar, alterar ou escalar.
6. **Critérios de sucesso** — condições binárias de aceite.
7. **Stop conditions** — quando a ferramenta deve parar e pedir validação humana.
8. **Entrega final** — formato esperado: HTML, componente, código, relatório, checklist ou preview.

Regra prática: prompt bom não é prompt longo; é prompt sem ambiguidade operacional.

## 2. Anti-padrões proibidos

João deve evitar:

- “faz algo profissional” sem especificação visual.
- “melhora isso” sem critério de aceite.
- “conserta tudo” sem escopo.
- pedir app inteiro quando o correto é piloto curto.
- autorizar ferramenta a “decidir o melhor caminho” sem restrições.
- deixar agente instalar dependências, deletar arquivos ou mudar arquitetura sem aprovação.
- omitir decisões já tomadas no cérebro do IVS.
- usar Lovable como API nativa ou solução final sem homologação real.
- tratar `21st.dev` como ferramenta oficial antes de API key válida e teste real do MCP `magic21st`.

## 3. Modelo base — Replit Agent

Use para piloto principal do João em projetos web.

```text
Objetivo:
[Construir/corrigir/prototipar] [entregável específico] para o Instituto Vital Slim.

Contexto IVS:
- Projeto: [nome]
- Público: [paciente/lead/equipe interna/Tiaro]
- Uso: [landing page/painel/protótipo/material gerencial]
- Decisões canônicas: [listar regras relevantes do cérebro]

Stack e ambiente:
- Ferramenta alvo: Replit Agent
- Stack desejada: [ex: React + Vite + TypeScript / HTML estático / Node]
- Dependências permitidas: [listar]
- Dependências proibidas: [listar]

Escopo:
- Pode criar/editar: [arquivos, pastas ou telas]
- Não tocar: .env, credenciais, banco, configs sensíveis, deploy, pagamentos, automações externas

Requisitos funcionais:
1. [requisito binário]
2. [requisito binário]
3. [requisito binário]

Requisitos visuais:
- Estilo: limpo, premium, médico, claro e responsivo
- Responsivo em: 375px mobile e 1440px desktop
- Não usar estética genérica de SaaS se conflitar com IVS

Não fazer:
- Não adicionar autenticação, banco, pagamento ou integrações não solicitadas
- Não criar funcionalidades extras
- Não alterar regra de negócio do IVS
- Não usar dados fictícios como se fossem reais

Stop conditions:
Pare e peça validação antes de:
- adicionar dependência nova
- alterar estrutura do projeto
- tocar dados sensíveis
- criar integração externa
- deletar arquivo
- fazer deploy
- escolher entre duas arquiteturas com impacto futuro

Critérios de sucesso:
- [ ] Entregável abre sem erro
- [ ] Layout responsivo validado
- [ ] Sem erro de console relevante
- [ ] Escopo respeitado
- [ ] Resumo final com arquivos criados/alterados
```

## 4. Modelo base — Bolt.new

Use como plano B ou comparação rápida com Replit Agent.

```text
Construa um protótipo web para o Instituto Vital Slim com este escopo estrito:

Objetivo: [entregável]
Stack: [React/Vite/TypeScript ou HTML/CSS/JS]
Público: [quem vai usar]
Tom visual: clínica premium, limpo, confiável, sem excesso de animação.

Seções/telas obrigatórias:
1. [seção/tela]
2. [seção/tela]
3. [seção/tela]

Dados:
- Use apenas placeholders explicitamente marcados como exemplo.
- Não invente métrica, preço, promessa médica ou depoimento.

Restrições:
- Não adicionar autenticação.
- Não adicionar banco de dados.
- Não adicionar pagamento.
- Não criar rotas ou features fora do escopo.
- Não usar biblioteca externa sem necessidade clara.

Aceite:
- renderiza sem erro
- funciona em mobile e desktop
- código simples de manter
- componentes nomeados de forma clara
- nenhuma regra canônica do IVS violada
```

## 5. Modelo base — v0

Use para apoio visual/UI. Não tratar v0 como base principal da operação do João.

```text
Crie uma interface visual para [tela/seção] do Instituto Vital Slim.

Objetivo da tela:
[explicar o que a tela precisa comunicar ou permitir]

Direção visual:
- clínica premium
- limpa, clara e responsiva
- hierarquia forte
- foco em confiança, não em hype

Componentes obrigatórios:
- [componente 1]
- [componente 2]
- [componente 3]

Conteúdo:
- Não inventar dados reais, preços, depoimentos ou promessas médicas.
- Usar placeholders explícitos quando faltar conteúdo.

Restrições:
- Não criar backend.
- Não criar autenticação.
- Não adicionar fluxo de pagamento.
- Não usar animações complexas sem necessidade.

Saída esperada:
- componente visual pronto para revisão
- responsivo mobile/desktop
- visual sem excesso de sombras, gradientes ou elementos genéricos de startup
```

## 6. Modelo base — Lovable

Uso apenas como contingência/prototipagem via browser OpenClaw, não como solução final canônica enquanto persistirem bloqueios de sessão/API.

```text
Edite/construa apenas o seguinte no projeto Lovable:

Objetivo:
[alteração específica]

Contexto:
Projeto do Instituto Vital Slim. A entrega precisa respeitar identidade premium, clareza médica, responsividade e regras canônicas do IVS.

Escopo permitido:
- [página/componente/seção]

Fora do escopo:
- autenticação
- banco de dados
- pagamento
- integrações externas
- alteração de domínio/deploy
- regras de negócio não solicitadas

Critérios de aceite:
- alteração aparece no preview
- não quebra tela existente
- mobile e desktop ok
- nenhum conteúdo médico/comercial inventado

Se encontrar login, erro 403, `Failed to fetch` ou bloqueio de sessão:
- relatar o bloqueio observado
- não concluir sozinho que é problema de assinatura, quota, permissão ou API estrutural
- pedir validação de sessão/credencial ou migração de ambiente
```

## 7. Modelo base — OpenClaw/browser agent

Use para agentes que controlam navegador, validação visual, QA ou operação em interfaces externas.

```text
Objetivo:
[resultado a obter no navegador]

Permissões:
- Pode navegar, ler, clicar e preencher campos não sensíveis quando necessário.
- Pode capturar screenshot para validação.
- Pode relatar bloqueios encontrados.

Limites:
- Não enviar formulário final sem autorização.
- Não comprar, assinar, publicar, excluir, pagar ou alterar configuração irreversível.
- Não mexer em credenciais.
- Não contornar login ou segurança.

Critério de parada:
Pare e peça validação antes de:
- publicar qualquer coisa
- enviar mensagem para terceiros
- alterar configuração de conta
- apagar dado
- inserir cartão/dado financeiro
- concluir ação irreversível

Entrega:
- estado observado
- passos relevantes executados
- bloqueios objetivos
- próximo passo recomendado
```

## 8. Modelo auxiliar — prompt para imagem institucional

Este bloco complementa, mas NÃO substitui, a skill `prompt-imagens`.

Para imagem da Dra. Daniely, João/Clara devem manter a regra canônica:
- usar foto-mãe/foto real oficial como referência
- preservar identidade facial
- sem jaleco, salvo pedido expresso
- variar pose, roupa, fundo e luz sem alterar rosto
- validar prompt com Tiaro antes de gerar

Estrutura recomendada para o prompt visual:

```text
Referência obrigatória:
[foto real oficial anexada]

Preservar exatamente:
- identidade facial
- proporções do rosto
- idade aparente real
- traços naturais

Alterar apenas:
- pose
- roupa
- fundo
- enquadramento
- iluminação

Cena desejada:
[descrição objetiva]

Estilo:
[editorial/comercial/documental/minimalista]

Câmera e composição:
[close/meio corpo/plano aberto, lente, profundidade]

Iluminação:
[suave/lateral/natural/estúdio]

Negativo:
não rejuvenescer, não harmonizar artificialmente, não afinar rosto, não mudar sorriso, não mudar olhos, não adicionar jaleco salvo pedido, sem texto, sem watermark, sem deformações
```

## 9. Checklist antes de enviar prompt para ferramenta

Antes de mandar qualquer prompt para Replit, Bolt, v0, Lovable ou agente browser, João deve checar:

- [ ] Ferramenta alvo definida
- [ ] Objetivo em uma frase
- [ ] Contexto IVS incluído
- [ ] Stack/entrega definida
- [ ] Escopo permitido claro
- [ ] Lista “não fazer” incluída
- [ ] Critérios de sucesso binários
- [ ] Stop conditions quando houver agente autônomo
- [ ] Restrições de compliance e dados reais respeitadas
- [ ] Pendências conhecidas citadas quando relevantes (`21st.dev`, Lovable/API, HTML no tópico)

## 10. Decisão operacional

- Replit Agent continua como plano A para piloto web do João.
- Bolt.new continua como plano B.
- v0 continua como apoio visual.
- Lovable continua como contingência/browser, não solução final homologada.
- `21st.dev` continua pendente até API key válida e teste real.
- O repositório `prompt-master` é referência de engenharia de prompt, não dependência operacional do IVS.
