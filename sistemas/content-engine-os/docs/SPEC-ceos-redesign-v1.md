# SPEC-CEOS-REDESIGN-001: Content Engine OS como cockpit operacional de autoridade

## Goal
Transformar o Content Engine OS de um conjunto de páginas soltas em um cockpit operacional extremamente funcional para geração de conteúdo, posicionamento de marca, autoridade clínica e aprendizado contínuo.

## Agentes ativados da `ivs-data-dev-os`
- **Product Analyst IVS:** problema = baixa navegabilidade e fluxo fraco; usuário = Tiaro/João/Maria; métrica = próxima ação óbvia em até 10 segundos.
- **Solution Architect IVS:** organizar sistema em motores claros: Comando, Inteligência, Produção, Publicação e Aprendizado.
- **Data Architect IVS:** expor métricas agregadas sem PII: criativos, calendário, stories, BI e fontes.
- **Security/LGPD Guard IVS:** sem coleta de PII; BI Instagram via RapidAPI é leitura agregada e governada.
- **Builder IVS:** refazer dashboard, navegação, página de BI e endpoints de overview.
- **QA/Bench Engineer IVS:** smoke, build Next, compile Python e validação pública.
- **Release Engineer IVS:** deploy com restart do container web e commit/push.
- **Executive Narrator IVS:** reportar entrega com decisões e próximos passos.

## Acceptance Criteria
- [x] Navegação principal reorganizada por função, não por acúmulo histórico de páginas.
- [x] Home vira cockpit de comando com fluxo claro e próxima ação.
- [x] Existe seção `BI - Business Intelligence` no menu e página funcional.
- [x] BI mostra performance agregada, readiness de RapidAPI e conexão futura com @dradaniely.freitas.
- [x] Sistema explica o que fazer em cada fase: radar → criação → aprovação → publicação → aprendizado.
- [x] Build, compile, smoke e validação pública passam.

## Scope
- **In scope:** layout, sidebar, home, BI page, endpoint `/bi/overview`, documentação e smoke.
- **Out of scope:** chamar RapidAPI real nesta etapa sem revisar credenciais/contrato; publicar no Instagram; enviar WhatsApp; alterar Clara/Z-API.

## Technical Approach
Incremental rebuild: preservar funcionalidades existentes e colocar uma camada de cockpit operacional acima delas. Criar endpoint agregado `bi/overview` para alimentar dashboard BI sem depender de integração externa. O próximo passo real será criar ingestão RapidAPI idempotente.

## Quality Target
O usuário deve abrir o sistema e entender:
1. onde captar sinais;
2. onde transformar sinal em roteiro/peça/story;
3. onde aprovar;
4. onde publicar/planejar;
5. onde medir e realimentar.

## TRUST 5
- [x] **Tested:** comandos reais de build/compile/smoke.
- [x] **Readable:** copy operacional e arquitetura de navegação explícita.
- [x] **Unified:** reaproveita estilo e API do CEOS.
- [x] **Secured:** BI sem PII, read-only/dry-run.
- [x] **Trackable:** spec + commit no cérebro.
