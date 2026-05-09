# Repo Reverse IVS — RightNow-AI/openfang

Data: 2026-05-09T18:53:42.036842
URL analisada: https://github.com/RightNow-AI/openfang
Área IVS: tecnologia
Objetivo IVS: Analisar como o OpenFang pode ser aplicado na operação do Instituto Vital Slim, especialmente sistema de marketing, agentes internos, automações e cockpit operacional, sem copiar código em produção sem validação de licença.

## 1. Identificação
- Repositório: `RightNow-AI/openfang`
- Descrição GitHub: Open-source Agent Operating System
- Stars: 17319
- Forks: 2219
- Branch padrão: main
- Licença detectada: `Apache-2.0`

## 2. Cautela de licença e uso
- Não copiar código sem validar licença.
- Preferir usar este relatório como spec funcional e inspiração de arquitetura.
- Se licença não estiver clara, criar do zero com base nos requisitos, não no código.
- Para IVS, qualquer uso com pacientes/leads precisa respeitar privacidade, compliance médico e logs seguros.

## 3. Stack provável
- Node/JavaScript/TypeScript
- Rust
- Docker/containers

## 4. Estrutura observada
### Diretórios mais relevantes
- `crates/` — 425 arquivos
- `agents/` — 36 arquivos
- `docs/` — 13 arquivos
- `.github/` — 7 arquivos
- `.cargo/` — 1 arquivos
- `deploy/` — 1 arquivos

### Extensões mais comuns
- `.rs` — 258
- `.md` — 87
- `.toml` — 81
- `.js` — 26
- `.json` — 12
- `.yml` — 7
- `.png` — 5
- `.css` — 4
- `.svg` — 4
- `.gitignore` — 2
- `.py` — 2
- `.ico` — 2
- `.html` — 2
- `.dockerignore` — 1
- `.example` — 1

## 5. Arquivos-chave analisados
- `README.md`
- `Cargo.toml`
- `Dockerfile`
- `docker-compose.yml`
- `.env.example`
- `CLAUDE.md`
- `AGENTS.md`
- `CONTRIBUTING.md`
- `SECURITY.md`

## 6. Funcionalidades prováveis
- API/servidor
- Interface web
- CLI/setup guiado
- Banco de dados/persistência
- Autenticação/permissões
- Agentes/IA/LLM
- Mensageria/chat
- Áudio/voz
- Automação/jobs
- Observabilidade/logs

## 7. Oportunidades para o IVS
Área selecionada: `tecnologia` — OpenClaw, skills, agentes, integrações, memória, graphify, bridges e automações.

Possíveis usos:
- Extrair padrões úteis para criar uma skill interna mais simples.
- Adaptar a arquitetura para o cérebro IVS, graphify e rotinas OpenClaw.
- Transformar funcionalidades recorrentes em automação operacional.
- Criar versão IVS-first com compliance, logs e dono operacional.

## 8. O que descartar por padrão
- Telas, fluxos ou dependências que não atendam dor operacional real.
- Qualquer parte que exija instalar stack pesada sem necessidade.
- Código com licença incerta/restritiva.
- Integrações que exponham dados sensíveis sem controle.
- Funcionalidades genéricas que não melhorem Clara, João, operação, financeiro ou tecnologia.

## 9. Prompt para criar nossa versão melhor
```text
Crie uma versão IVS-first inspirada funcionalmente no repositório `RightNow-AI/openfang`, sem copiar código.

Objetivo do IVS:
Analisar como o OpenFang pode ser aplicado na operação do Instituto Vital Slim, especialmente sistema de marketing, agentes internos, automações e cockpit operacional, sem copiar código em produção sem validação de licença.

Área impactada:
tecnologia — OpenClaw, skills, agentes, integrações, memória, graphify, bridges e automações.

Funcionalidades úteis observadas:
- API/servidor
- Interface web
- CLI/setup guiado
- Banco de dados/persistência
- Autenticação/permissões
- Agentes/IA/LLM
- Mensageria/chat
- Áudio/voz
- Automação/jobs
- Observabilidade/logs

Requisitos IVS:
- funcionar como skill OpenClaw quando possível;
- registrar mudanças estruturais no cérebro via graphify/RC-25;
- ter logs claros e seguros;
- não expor secrets;
- respeitar compliance médico;
- evitar dependências pesadas;
- ter dono operacional;
- entregar README, comandos de uso, testes mínimos e checklist de implantação.

Entregue:
1. Spec funcional
2. Arquitetura proposta
3. Arquivos a criar
4. Scripts necessários
5. Variáveis de ambiente, sem valores secretos
6. Critérios de aceite
7. Plano de implementação por etapas
8. Riscos e mitigação
```

## 10. Checklist de implementação
- [ ] Validar licença.
- [ ] Confirmar dono operacional.
- [ ] Confirmar dor real e métrica de sucesso.
- [ ] Criar spec IVS-first.
- [ ] Criar skill em `/root/.openclaw/workspace/skills/`.
- [ ] Criar versão canônica no cérebro quando aplicável.
- [ ] Testar com caso pequeno.
- [ ] Registrar via graphify/RC-25.
- [ ] Atualizar memória operacional.

## 11. Decisão recomendada
**Criar versão própria/adaptada**, não instalar o repo inteiro, salvo se houver motivo técnico claro.

## 12. Erros/limitações da coleta
- Nenhum erro relevante.
