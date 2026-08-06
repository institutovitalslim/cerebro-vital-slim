# IVS Design QA — Especificação aprovada

## Decisão

Construir um gate local, determinístico e fail-closed para HTML IVS. Ele orquestra componentes existentes em vez de duplicá-los: scanner estático próprio, `ivs-visual-layer` em cópia, `ivs-site validate` para sites quando disponível e Playwright/Chromium para QA real em desktop e mobile.

## Problema

Sites e apresentações têm validações separadas, mas não uma porta única que produza evidência uniforme, preserve o original e bloqueie quebra visual, erro JavaScript, placeholder e falha de governança.

## Usuários

Maria, João e os renderers de apresentações do IVS.

## Escopo v1

- Entrada: um arquivo HTML local.
- Tipos: `site`, `patient-presentation`, `internal-report`.
- Modo de dados: `anonymous` ou `sensitive-local`.
- Saídas em diretório dedicado: auditoria JSON redigida, relatório HTML executivo e screenshots desktop/mobile. A cópia instrumentada do Visual Layer é gerada somente em `anonymous`; em `sensitive-local`, o componente é omitido para não serializar título, headings, IDs ou classes sensíveis.
- Estado: `PASS`, `PASS_WITH_CONCERNS` ou `BLOCKED`.
- Códigos de saída: 0 para aprovação; 2 para bloqueio; 1 para falha interna.
- Original sempre imutável, validado por SHA-256 antes/depois.

## Bloqueios v1

1. Arquivo ausente, vazio ou sem estrutura HTML.
2. Placeholder (`TODO`, `FIXME`, `lorem ipsum`, marcador `[preencher...]`).
3. Falta de `<title>`, `<!doctype html>`, `<meta name="viewport">` ou seção semântica.
4. Erro JavaScript não filtrado.
5. Imagem quebrada.
6. Overflow horizontal em desktop ou mobile.
7. Uso de modo `anonymous` em apresentação com telefone, e-mail ou CPF detectável.
8. Alteração do SHA-256 do original.
9. Falha do `ivs-site validate` quando o tipo for `site` e a ferramenta estiver disponível.

## Preocupações não bloqueantes v1

- Ausência de media query.
- Menos de seis seções.
- Links externos em apresentação de paciente.
- Console warning.
- `ivs-site` ou Visual Layer indisponível fora do repositório canônico.

## Segurança e privacidade

- Nenhum texto da página é copiado para o JSON; apenas contagens, códigos e caminhos.
- O título é omitido do relatório em `sensitive-local`.
- Screenshots de `sensitive-local` são marcados como sensíveis e nunca enviados/publicados automaticamente.
- `patient_send_ready=false` e `external_publish=false` em todas as saídas.
- Nenhuma escrita em QuarkClinic, Omie, WhatsApp, Drive ou publicação externa.

## Arquitetura

1. `static_checks.py`: leitura, hash e regras estáticas.
2. `browser_probe.mjs`: Chromium via `playwright-core`, duas viewports, console, exceções, imagens e overflow.
3. `integrations.py`: adaptadores opcionais para `ivs-site` e Visual Layer.
4. `reporting.py`: relatório JSON/HTML sem conteúdo sensível.
5. `ivs_design_qa.py`: CLI e decisão final.
6. `fixtures/`: landing e apresentação sintética/anônima de homologação.

## Critério de aceite

- Testes unitários e integração passam.
- Teste negativo prova bloqueio de overflow/placeholder.
- Landing piloto retorna `PASS` e gera duas screenshots.
- Casco anônimo de apresentação retorna `PASS` e gera duas screenshots.
- Original de cada piloto mantém o mesmo SHA-256.
- JSONs não contêm telefone, e-mail, CPF, token ou conteúdo clínico identificável.
- `git diff --check`, scanner de segredos disponível e verificação final passam antes do push.
