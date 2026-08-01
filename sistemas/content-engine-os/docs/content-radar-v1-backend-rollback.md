# Rollback backend — Content Radar v1 (migrations 022/023)

Este procedimento é operacional e **não executa rollback automaticamente**. Não deve ser usado em produção sem janela, backup e validação do responsável pelo banco.

## Rollback seguro da aplicação

1. Desligar `CONTENT_RADAR_V1_ENABLED` para interromper ingestão e leituras das tabelas 022/023.
2. Reverter somente o código da API para a versão anterior ao Content Radar.
3. Manter as tabelas aditivas. Não apagar `external_ingest_batches` nem `external_ingest_ledger`: elas são o histórico imutável das chaves já aceitas.
4. Validar `/ideias/fila` com a flag desligada. Nesse modo a API não consulta `external_content_items`, `external_content_baselines` nem `ideias_estado`, portanto funciona também em bancos pré-022.

## Mutações legadas feitas pela 022

A migration 022 normalizou `external_content_items.source_profile` e preencheu `radar_source_id`, `canonical_format`, `actual_source_profile`, `first_seen_at` e `last_seen_at`. A 023 preserva, antes do hardening, uma cópia JSON integral de cada linha em `external_content_items_022_state_audit`.

Para inspecionar a imagem preservada:

```sql
select content_item_id, tenant_id, row_snapshot, captured_at
from external_content_items_022_state_audit
where tenant_id = $1
order by captured_at, content_item_id;
```

Rollback lógico dos campos **adicionados** pela 022, quando explicitamente aprovado, pode ser preparado a partir do audit e executado com parâmetros/escopo de tenant. Não se recomenda remover colunas ou tabelas, pois versões novas podem continuar referenciando-as.

Atenção: a 022 já havia removido casing e `@` de `source_profile` antes de a 023 capturar o estado. Para perfis não temáticos, `actual_source_profile` permite recuperar a identidade canônica, mas não necessariamente a grafia original. Para restauração byte a byte do valor anterior à 022, a fonte de verdade é o backup/PITR feito antes da 022. Não inventar a grafia ausente.

## Hardening 023

A 023 troca FKs simples por FKs compostas com `tenant_id`, inclui `candidate_metric_snapshot_id` na unicidade de baseline e adiciona `tenant_id` aos membros do baseline. Para recuar o binário da API não é necessário desfazer essas constraints: elas são compatíveis com os dados da 022 e mais restritivas contra referências cross-tenant.

Se for indispensável desfazer apenas a unicidade nova, primeiro interromper gravações e comprovar que não existem duas linhas que colidiriam na chave antiga. A operação deve ser feita em migration posterior; **não alterar o checksum da 022 ou da 023 já aplicada**.

## Verificações pós-rollback

- Feature flag desligada.
- `/ideias/fila` responde sem acesso às tabelas 022.
- Nenhuma nova linha surge em `external_ingest_batches`/`external_ingest_ledger`.
- Contagem e checksums de `schema_migrations` permanecem intactos.
- Audit `external_content_items_022_state_audit` e backups continuam disponíveis.
