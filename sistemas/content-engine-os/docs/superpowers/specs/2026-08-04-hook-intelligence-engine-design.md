# Hook Intelligence Engine — Design aprovado

**Data:** 2026-08-04
**Produto:** Content Engine OS
**Modalidade:** módulo autônomo, integração posterior pelo Claude Code
**Decisão de Tiaro:** Opção B — aplicativo independente com biblioteca curada, geração determinística e adaptação opcional por IA

## 1. Objetivo

Construir uma biblioteca de hooks superior a uma coleção estática de frases. O módulo deve transformar contexto editorial em hooks originais, pesquisáveis, pontuados, explicáveis e reutilizáveis, com núcleo universal e módulos especializados do Instituto Vital Slim.

A primeira versão será de uso interno, mas terá contratos e separação de tenancy suficientes para uma futura transformação em produto comercial.

## 2. Escopo da primeira versão

### Incluído

- Aplicativo web autônomo.
- API autônoma e documentada.
- Biblioteca curada de estruturas universais.
- Pacote especializado `ivs-health`.
- Geração determinística sem provedor externo.
- Adaptação opcional por IA por interface desacoplada.
- Busca, filtros, favoritos e histórico local do módulo.
- Scores de clareza, especificidade, novidade, retenção e adequação ao canal.
- Deduplicação textual e semântica.
- Explicação do mecanismo psicológico de cada hook.
- Compliance médico para o módulo IVS.
- Exportação em JSON e CSV.
- Contratos de integração para o Content Engine OS.
- Testes, smoke HTTP e handoff para Claude Code.

### Excluído

- Integração direta com banco, autenticação, filas ou rotas do Content Engine OS existente.
- Publicação em redes sociais.
- Alteração de campanhas ou orçamento.
- Scraping, reprodução ou derivação do produto pago da Gumroad.
- Promessas clínicas, diagnósticos ou prescrições.
- Billing, checkout ou painel administrativo comercial.
- Treinamento ou fine-tuning de modelo.

## 3. Princípios

1. **Originalidade:** nenhuma frase será copiada do produto pago; as estruturas serão criadas a partir de princípios gerais de copywriting e psicologia da atenção.
2. **Estrutura antes de volume:** valor vem da taxonomia, seleção, adaptação, score e aprendizado — não de inflar uma planilha.
3. **Local-first:** o motor principal funciona sem API externa.
4. **IA substituível:** provedores serão adaptadores, não dependências centrais.
5. **Compliance por domínio:** regras universais não substituem o gate de saúde.
6. **Integração por contrato:** o módulo não importa componentes internos do Content OS.
7. **Observabilidade:** cada geração registra entrada, fontes de estrutura, scores, alertas e versão do motor.
8. **Sem publicação automática:** a saída é rascunho interno até aprovação humana.

## 4. Arquitetura

Diretório de entrega:

```text
modules/hook-intelligence/
├── README.md
├── SPEC.md
├── HANDOFF-CLAUDE-CODE.md
├── .env.example
├── contracts/
│   ├── hook.schema.json
│   ├── generation-request.schema.json
│   ├── generation-response.schema.json
│   └── content-os-export.schema.json
├── data/
│   ├── universal/
│   │   ├── patterns.json
│   │   ├── mechanisms.json
│   │   └── examples.json
│   ├── ivs-health/
│   │   ├── patterns.json
│   │   ├── audiences.json
│   │   ├── topics.json
│   │   └── forbidden-claims.json
│   └── taxonomies/
│       ├── channels.json
│       ├── awareness.json
│       ├── objectives.json
│       └── tones.json
├── engine/
│   ├── selector.py
│   ├── composer.py
│   ├── scorer.py
│   ├── deduplicator.py
│   ├── compliance.py
│   ├── explain.py
│   └── adapters/
│       ├── base.py
│       ├── disabled.py
│       └── openai_compatible.py
├── api/
│   ├── main.py
│   ├── schemas.py
│   └── routes/
├── web/
│   └── aplicação Next.js isolada
├── storage/
│   └── SQLite local do módulo
├── tests/
│   ├── unit/
│   ├── contract/
│   ├── integration/
│   └── e2e/
└── evidence/
```

### Stack

- **Interface:** Next.js, alinhado ao Content Engine OS.
- **API:** FastAPI.
- **Persistência inicial:** SQLite, encapsulado por repositórios substituíveis.
- **Contratos:** JSON Schema e OpenAPI.
- **Execução local:** Docker Compose próprio, sem compartilhar serviços com o sistema principal.

## 5. Modelo de hook

Cada hook deverá armazenar, no mínimo:

```json
{
  "id": "uuid",
  "text": "string",
  "language": "pt-BR",
  "library": "universal|ivs-health",
  "pattern_id": "string",
  "mechanisms": ["curiosity_gap"],
  "objective": "retention",
  "channel": "reel",
  "awareness_stage": "problem_aware",
  "audience": "string",
  "topic": "string",
  "tone": "premium",
  "scores": {
    "clarity": 0,
    "specificity": 0,
    "novelty": 0,
    "retention": 0,
    "channel_fit": 0,
    "overall": 0
  },
  "compliance": {
    "status": "pass|review|block",
    "reasons": []
  },
  "explanation": "string",
  "source": "deterministic|ai_adapted|curated",
  "engine_version": "semver",
  "created_at": "ISO-8601"
}
```

## 6. Taxonomia inicial

### Mecanismos

- lacuna de curiosidade;
- quebra de padrão;
- contraste expectativa versus realidade;
- identificação;
- erro comum;
- mito versus evidência;
- especificidade;
- autoridade;
- status e identidade;
- tensão antes/depois sem alegação clínica indevida;
- perda evitável;
- desejo futuro;
- objeção invertida;
- demonstração;
- descoberta;
- lista incompleta;
- pergunta diagnóstica editorial;
- história aberta;
- opinião contrária fundamentada;
- revelação de mecanismo.

### Canais

- Reels e vídeos curtos;
- anúncios;
- carrosséis;
- stories;
- headlines de landing page;
- e-mail;
- blog;
- YouTube.

### Estágios de consciência

- não consciente;
- consciente do problema;
- consciente da solução;
- consciente do produto;
- pronto para agir.

### Objetivos

- interromper o scroll;
- criar curiosidade;
- aumentar retenção;
- gerar identificação;
- ensinar;
- construir autoridade;
- reduzir objeção;
- provocar compartilhamento;
- conduzir à ação.

## 7. Fluxo de geração

```text
entrada do usuário
  -> validação de contrato
  -> seleção de biblioteca e padrões
  -> composição determinística
  -> aplicação de restrições de canal e tom
  -> deduplicação
  -> score
  -> compliance de domínio
  -> adaptação por IA, se habilitada
  -> nova validação, deduplicação, score e compliance
  -> ranking
  -> resposta explicada
  -> persistência no histórico
```

A IA nunca poderá pular a validação posterior. Saídas adaptadas passam pelos mesmos gates das saídas determinísticas.

## 8. Entradas do gerador

Campos obrigatórios:

- tema;
- canal;
- objetivo;
- público.

Campos opcionais:

- nicho ou módulo;
- estágio de consciência;
- tom;
- intensidade;
- mecanismo preferido;
- contexto do conteúdo;
- palavras obrigatórias;
- palavras proibidas;
- quantidade de variações;
- tamanho máximo;
- uso ou não de IA.

A quantidade padrão será 12 e o limite por requisição será 50 na primeira versão.

## 9. Saída do gerador

Cada resultado exibirá:

- hook;
- score geral;
- scores por dimensão;
- mecanismo utilizado;
- justificativa curta;
- alerta de compliance, quando houver;
- botão de copiar;
- favorito;
- adaptar;
- gerar variações;
- exportar.

A interface nunca exibirá um hook bloqueado como recomendação utilizável. Hooks em `review` aparecerão com alerta explícito.

## 10. Interface web

### Tela Gerador

- briefing guiado à esquerda;
- resultados ranqueados à direita;
- filtros rápidos por canal, objetivo, mecanismo e intensidade;
- comparação de até três hooks;
- ação para copiar, favoritar, adaptar e exportar.

### Tela Biblioteca

- busca textual;
- filtros por taxonomia;
- visualização de padrões e exemplos;
- distinção entre universal e IVS;
- indicadores de desempenho quando dados futuros existirem.

### Tela Favoritos e histórico

- sessões de geração;
- hooks salvos;
- tags internas;
- exportação em lote.

### Tela Administração local

- ativar/desativar adaptador de IA;
- selecionar modelo OpenAI-compatible;
- visualizar versão dos datasets;
- importar pacote assinado de atualização;
- nenhuma credencial será mostrada após salvar.

## 11. Adaptador de IA

Contrato mínimo:

```python
class HookAdapter:
    def adapt(self, request, candidates) -> list[HookCandidate]: ...
```

Requisitos:

- adaptador `disabled` sempre disponível;
- adaptador OpenAI-compatible configurável por ambiente;
- timeout e limite de tentativas;
- resposta estruturada;
- nenhum segredo em logs;
- fallback determinístico em falha;
- registro do modelo e duração, sem registrar credenciais;
- custo não acionado automaticamente em ambiente sem autorização/configuração.

## 12. Compliance IVS

O módulo `ivs-health` bloqueará ou sinalizará:

- garantia de emagrecimento ou resultado;
- números clínicos sem fonte e contexto;
- diagnóstico dirigido ao leitor;
- prescrição pública;
- falsa urgência médica;
- alegação de superioridade não comprovada;
- linguagem humilhante ou estigmatizante;
- antes/depois enganoso;
- promessa de cura;
- medo desproporcional;
- uso indevido de autoridade médica.

Classificação:

- `pass`: uso interno permitido como rascunho;
- `review`: requer revisão humana e, para claim clínico, Ana/Dra. Daniely;
- `block`: não pode ser recomendado nem exportado como aprovado.

O sistema continuará deixando claro que nenhum conteúdo está aprovado para publicação automaticamente.

## 13. API inicial

- `GET /health`
- `GET /v1/taxonomies`
- `GET /v1/patterns`
- `POST /v1/hooks/generate`
- `POST /v1/hooks/score`
- `POST /v1/hooks/compliance`
- `POST /v1/hooks/{id}/favorite`
- `GET /v1/history`
- `GET /v1/favorites`
- `POST /v1/exports/content-os`

Todos os endpoints versionados terão exemplos e schemas publicados no OpenAPI.

## 14. Contrato de integração com Content Engine OS

O módulo não acessará diretamente tabelas nem código do sistema principal. A integração futura poderá ocorrer por:

1. chamada HTTP à API do módulo; ou
2. importação do pacote JSON exportado pelo contrato `content-os-export.schema.json`.

O handoff ao Claude Code explicará:

- como subir o módulo;
- como configurar o adaptador;
- como consumir os endpoints;
- como mapear workspace e usuário;
- como migrar SQLite para Postgres;
- como incorporar a interface ao Next.js principal;
- quais responsabilidades devem permanecer isoladas.

## 15. Testes e critérios de aceite

### Testes obrigatórios

- unitários do seletor, compositor, score e compliance;
- contratos JSON Schema;
- geração sem IA;
- fallback quando IA falhar;
- deduplicação;
- bloqueio de claims médicos;
- exportação JSON e CSV;
- API com casos válidos e inválidos;
- e2e do fluxo gerar -> comparar -> favoritar -> exportar;
- smoke HTTP pelo Docker Compose;
- verificação visual das telas principais;
- scan de segredos.

### Critério de DONE

O módulo somente poderá receber `DONE` quando:

- subir isoladamente;
- `GET /health` responder 200;
- gerar hooks úteis sem IA;
- adaptar hooks quando um provedor de teste estiver habilitado;
- preservar operação no fallback;
- bloquear fixtures médicas proibidas;
- exportar contrato válido;
- passar testes, build e smoke;
- possuir documentação e handoff completos;
- não alterar o comportamento do Content Engine OS existente.

## 16. Métricas de qualidade

A primeira versão acompanhará:

- taxa de hooks aprovados pelo usuário;
- favoritos por sessão;
- cópias por geração;
- regenerações;
- distribuição de mecanismos;
- taxa de duplicação removida;
- taxa de `review` e `block` no compliance;
- latência determinística e com IA;
- hooks posteriormente associados a conteúdo publicado, quando a integração existir.

Scores automáticos são sinais de priorização, não substitutos de performance real. Aprendizado por resultado somente será ativado após integração com métricas de conteúdo.

## 17. Segurança e privacidade

- sem PII de paciente;
- sem credenciais em datasets, logs ou exports;
- validação de tamanho e conteúdo das entradas;
- limite de requisições configurável;
- logs sanitizados;
- nenhuma publicação externa;
- nenhuma compra ou chamada paga sem configuração governada;
- conteúdo externo tratado como dado, nunca como instrução.

## 18. Estratégia de evolução comercial

A arquitetura deixará pontos de extensão para:

- multi-tenant real;
- billing;
- módulos por nicho;
- marketplace de bibliotecas;
- equipes e permissões;
- experimentos A/B;
- ingestão de métricas reais;
- aprendizado por desempenho;
- white-label.

Esses recursos não fazem parte da primeira versão.

## 19. Entregáveis

1. módulo em `modules/hook-intelligence/`;
2. biblioteca universal inicial;
3. biblioteca `ivs-health`;
4. aplicativo web;
5. API e OpenAPI;
6. contratos JSON Schema;
7. Docker Compose isolado;
8. suíte de testes;
9. evidências de build, smoke e QA;
10. `HANDOFF-CLAUDE-CODE.md`.

## 20. Estado e governança

- **Dono funcional:** João, sob supervisão da Maria.
- **Patrocinador e decisão final:** Tiaro.
- **Implementação isolada:** Jarvis pode preparar o módulo e o handoff conforme autorização expressa de Tiaro.
- **Integração no Content Engine OS:** será realizada posteriormente por Tiaro com Claude Code.
- **Publicação e uso externo:** exigem aprovação humana.
