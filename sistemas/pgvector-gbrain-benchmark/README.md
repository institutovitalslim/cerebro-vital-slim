# Benchmark pgvector × GBrain — IVS

Piloto governado para decidir se uma camada PostgreSQL/pgvector separada traz valor incremental ao GBrain do Instituto Vital Slim.

## Escopo e segurança

- corpus pgvector integralmente sintético e sem dados pessoais reais;
- termos operacionais como Omie e QuarkClinic aparecem apenas em fixtures fictícios, sem conexão ou escrita nesses sistemas;
- GBrain consultado somente com `search`, sem escrita e sem persistir caminhos retornados;
- PostgreSQL efêmero em Docker, autenticado e limitado a `127.0.0.1:55432`;
- DSN aceito somente para host, porta, banco, usuário e `application_name` exatos do sandbox;
- métricas dos dois backends **não são diretamente comparáveis**, pois os corpora e os pipelines diferem.

## Gates

Os thresholds vivem somente em `manifest.json`; o runner carrega esse arquivo, aplica cada gate e persiste observado, limite, comparador, escopo e resultado no JSON/HTML.

- pgvector sintético: Recall@3 ≥ 0,90; MRR ≥ 0,80; p95 ≤ 250 ms;
- GBrain: acerto de caminho esperado no Top 3 e pass rate operacional ≥ 0,90;
- latência do GBrain é observacional e não autoriza banco paralelo;
- falha do GBrain exige investigação interna; o corpus sintético não prova que pgvector separado resolve a lacuna;
- promoção para produção exige teste no mesmo corpus, gate humano e caso real reproduzível.

## Executar

```bash
uv sync
./scripts/run_benchmark.sh
./scripts/test.sh
```

Os scripts fixam arquivo e nome do projeto Compose, geram senha efêmera, sobem o banco em `tmpfs` e removem os recursos ao final sem apagar volumes externos.

## Interpretação de desempenho

O índice HNSW é criado e sua disponibilidade é verificada com `EXPLAIN`. Com apenas 20 documentos, o plano padrão pode usar varredura sequencial; por isso, a latência do microbenchmark **não é apresentada como benchmark de HNSW**.

## Decisão esperada

Se o GBrain mantiver qualidade operacional, preservar a arquitetura atual. Se houver lacuna estruturada, investigar e otimizar o GBrain; só reabrir uma camada separada após avaliação equivalente no mesmo corpus.
