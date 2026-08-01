-- Content Radar v1 — hardening P0/P1/P2 pós-022
-- A migration 022 não é alterada: seu checksum pode já estar no ledger de schema.
-- Esta migration é aditiva/idempotente, exceto pela substituição deliberada de
-- FKs simples por FKs compostas tenant-aware e da chave única de baseline.

-- ---------------------------------------------------------------- ingest ledger
-- O batch guarda o timestamp efetivo. Se observed_at não veio do coletor, todo
-- replay do mesmo run reutiliza este valor em vez de consultar novamente now().
create table if not exists external_ingest_batches (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id),
  provider text not null,
  collector_run_id text not null,
  request_fingerprint text not null check (char_length(request_fingerprint) = 64),
  identity_count integer not null check (identity_count between 1 and 100),
  effective_observed_at timestamptz not null,
  created_at timestamptz not null default now(),
  unique (tenant_id, provider, collector_run_id)
);

-- Ledger imutável por identidade. Não depende de external_metric_snapshots:
-- itens sem métricas também ocupam definitivamente sua chave idempotente.
create table if not exists external_ingest_ledger (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id),
  provider text not null,
  collector_run_id text not null,
  source_network text not null,
  external_identity text not null,
  payload_fingerprint text not null check (char_length(payload_fingerprint) = 64),
  effective_observed_at timestamptz not null,
  created_at timestamptz not null default now(),
  unique (tenant_id, provider, collector_run_id, source_network, external_identity),
  constraint external_ingest_ledger_batch_tenant_fkey
    foreign key (tenant_id, provider, collector_run_id)
    references external_ingest_batches(tenant_id, provider, collector_run_id)
);

create or replace function reject_external_ingest_ledger_mutation()
returns trigger
language plpgsql
as $$
begin
  raise exception '% is an immutable ingestion ledger', tg_table_name
    using errcode = '55000';
end
$$;

do $$
begin
  if not exists (
    select 1 from pg_trigger
    where tgrelid = 'public.external_ingest_batches'::regclass
      and tgname = 'external_ingest_batches_immutable'
      and not tgisinternal
  ) then
    create trigger external_ingest_batches_immutable
      before update or delete on external_ingest_batches
      for each row execute function reject_external_ingest_ledger_mutation();
  end if;
  if not exists (
    select 1 from pg_trigger
    where tgrelid = 'public.external_ingest_ledger'::regclass
      and tgname = 'external_ingest_ledger_immutable'
      and not tgisinternal
  ) then
    create trigger external_ingest_ledger_immutable
      before update or delete on external_ingest_ledger
      for each row execute function reject_external_ingest_ledger_mutation();
  end if;
end $$;

create index if not exists idx_external_ingest_ledger_identity
  on external_ingest_ledger(tenant_id, source_network, external_identity, created_at desc);

-- ----------------------------------------------------------- legacy audit / rollback
-- A 022 normalizou campos legados in-place. Como seu checksum deve permanecer
-- intacto, preservamos aqui o estado encontrado antes de qualquer hardening 023.
-- O documento de rollback registra também o limite: casing/@ anteriores à 022
-- só podem ser recuperados de backup quando actual_source_profile não os reteve.
create table if not exists external_content_items_022_state_audit (
  content_item_id uuid primary key,
  tenant_id uuid not null,
  row_snapshot jsonb not null,
  captured_at timestamptz not null default now()
);

insert into external_content_items_022_state_audit (content_item_id, tenant_id, row_snapshot)
select e.id, e.tenant_id, to_jsonb(e)
from external_content_items e
on conflict (content_item_id) do nothing;

-- --------------------------------------------------------------- ideias_estado
-- CREATE TABLE IF NOT EXISTS da 022 não endurece uma tabela legada já existente;
-- por isso todos os lookups abaixo são escopados por conrelid, nunca só conname.
alter table ideias_estado alter column tenant_id set not null;
alter table ideias_estado alter column ideia_id set not null;
alter table ideias_estado alter column estado set not null;
alter table ideias_estado alter column criado_em set default now();
alter table ideias_estado alter column criado_em set not null;

do $$
begin
  if not exists (
    select 1 from pg_constraint
    where conrelid = 'public.ideias_estado'::regclass
      and contype = 'p'
  ) then
    alter table ideias_estado
      add constraint ideias_estado_pkey primary key (tenant_id, ideia_id);
  end if;
  if not exists (
    select 1 from pg_constraint
    where conrelid = 'public.ideias_estado'::regclass
      and conname = 'ideias_estado_tenant_id_fkey'
  ) then
    alter table ideias_estado
      add constraint ideias_estado_tenant_id_fkey
      foreign key (tenant_id) references tenants(id) on delete cascade;
  end if;
  if not exists (
    select 1 from pg_constraint
    where conrelid = 'public.ideias_estado'::regclass
      and conname = 'ideias_estado_ideia_id_check'
  ) then
    alter table ideias_estado
      add constraint ideias_estado_ideia_id_check
      check (char_length(btrim(ideia_id)) between 1 and 500);
  end if;
  if not exists (
    select 1 from pg_constraint
    where conrelid = 'public.ideias_estado'::regclass
      and conname = 'ideias_estado_estado_check'
  ) then
    alter table ideias_estado
      add constraint ideias_estado_estado_check
      check (estado in ('guardada', 'produzida', 'descartada'));
  end if;
end $$;

-- ----------------------------------------------------- tenant-aware unique keys
-- As PKs UUID isoladas continuam existindo; as uniques compostas são os alvos
-- necessários para impedir referências cruzadas entre tenants via FK composta.
do $$
begin
  if not exists (select 1 from pg_constraint where conrelid='public.external_radar_sources'::regclass and conname='external_radar_sources_tenant_id_id_key') then
    alter table external_radar_sources add constraint external_radar_sources_tenant_id_id_key unique (tenant_id, id);
  end if;
  if not exists (select 1 from pg_constraint where conrelid='public.external_content_items'::regclass and conname='external_content_items_tenant_id_id_key') then
    alter table external_content_items add constraint external_content_items_tenant_id_id_key unique (tenant_id, id);
  end if;
  if not exists (select 1 from pg_constraint where conrelid='public.external_metric_snapshots'::regclass and conname='external_metric_snapshots_tenant_id_id_key') then
    alter table external_metric_snapshots add constraint external_metric_snapshots_tenant_id_id_key unique (tenant_id, id);
  end if;
  if not exists (select 1 from pg_constraint where conrelid='public.external_content_baselines'::regclass and conname='external_content_baselines_tenant_id_id_key') then
    alter table external_content_baselines add constraint external_content_baselines_tenant_id_id_key unique (tenant_id, id);
  end if;
end $$;

alter table external_baseline_members add column if not exists tenant_id uuid;
update external_baseline_members m
set tenant_id = b.tenant_id
from external_content_baselines b
where b.id = m.baseline_id and m.tenant_id is null;
alter table external_baseline_members alter column tenant_id set not null;

-- Falhar fechado se houver corrupção anterior; nunca “corrigir” associação de
-- tenant silenciosamente.
do $$
begin
  if exists (
    select 1 from external_radar_source_decisions d join external_radar_sources s on s.id=d.radar_source_id
    where d.tenant_id <> s.tenant_id
  ) or exists (
    select 1 from external_content_items e join external_radar_sources s on s.id=e.radar_source_id
    where e.radar_source_id is not null and e.tenant_id <> s.tenant_id
  ) or exists (
    select 1 from external_metric_snapshots s join external_content_items e on e.id=s.content_item_id
    where s.tenant_id <> e.tenant_id
  ) or exists (
    select 1 from external_content_baselines b join external_content_items e on e.id=b.candidate_content_item_id
    where b.tenant_id <> e.tenant_id
  ) or exists (
    select 1 from external_content_baselines b join external_metric_snapshots s on s.id=b.candidate_metric_snapshot_id
    where b.tenant_id <> s.tenant_id
  ) or exists (
    select 1 from external_baseline_members m join external_content_baselines b on b.id=m.baseline_id
    where m.tenant_id <> b.tenant_id
  ) or exists (
    select 1 from external_baseline_members m join external_metric_snapshots s on s.id=m.metric_snapshot_id
    where m.tenant_id <> s.tenant_id
  ) or exists (
    select 1 from external_baseline_members m join external_content_items e on e.id=m.content_item_id
    where m.tenant_id <> e.tenant_id
  ) then
    raise exception 'Content Radar contém referência cross-tenant; hardening 023 abortado';
  end if;
end $$;

-- Retira FKs simples criadas pela 022 e instala versões tenant-aware.
alter table external_radar_source_decisions drop constraint if exists external_radar_source_decisions_radar_source_id_fkey;
alter table external_content_items drop constraint if exists external_content_items_radar_source_id_fkey;
alter table external_metric_snapshots drop constraint if exists external_metric_snapshots_content_item_id_fkey;
alter table external_content_baselines drop constraint if exists external_content_baselines_candidate_content_item_id_fkey;
alter table external_content_baselines drop constraint if exists external_content_baselines_candidate_metric_snapshot_id_fkey;
alter table external_baseline_members drop constraint if exists external_baseline_members_baseline_id_fkey;
alter table external_baseline_members drop constraint if exists external_baseline_members_metric_snapshot_id_fkey;
alter table external_baseline_members drop constraint if exists external_baseline_members_content_item_id_fkey;

do $$
begin
  if not exists (select 1 from pg_constraint where conrelid='public.external_radar_source_decisions'::regclass and conname='radar_decision_source_tenant_fkey') then
    alter table external_radar_source_decisions add constraint radar_decision_source_tenant_fkey
      foreign key (tenant_id, radar_source_id) references external_radar_sources(tenant_id, id) on delete cascade;
  end if;
  if not exists (select 1 from pg_constraint where conrelid='public.external_content_items'::regclass and conname='external_content_source_tenant_fkey') then
    alter table external_content_items add constraint external_content_source_tenant_fkey
      foreign key (tenant_id, radar_source_id) references external_radar_sources(tenant_id, id);
  end if;
  if not exists (select 1 from pg_constraint where conrelid='public.external_metric_snapshots'::regclass and conname='external_snapshot_content_tenant_fkey') then
    alter table external_metric_snapshots add constraint external_snapshot_content_tenant_fkey
      foreign key (tenant_id, content_item_id) references external_content_items(tenant_id, id) on delete cascade;
  end if;
  if not exists (select 1 from pg_constraint where conrelid='public.external_content_baselines'::regclass and conname='external_baseline_candidate_tenant_fkey') then
    alter table external_content_baselines add constraint external_baseline_candidate_tenant_fkey
      foreign key (tenant_id, candidate_content_item_id) references external_content_items(tenant_id, id) on delete cascade;
  end if;
  if not exists (select 1 from pg_constraint where conrelid='public.external_content_baselines'::regclass and conname='external_baseline_snapshot_tenant_fkey') then
    alter table external_content_baselines add constraint external_baseline_snapshot_tenant_fkey
      foreign key (tenant_id, candidate_metric_snapshot_id) references external_metric_snapshots(tenant_id, id) on delete restrict;
  end if;
  if not exists (select 1 from pg_constraint where conrelid='public.external_baseline_members'::regclass and conname='external_member_baseline_tenant_fkey') then
    alter table external_baseline_members add constraint external_member_baseline_tenant_fkey
      foreign key (tenant_id, baseline_id) references external_content_baselines(tenant_id, id) on delete cascade;
  end if;
  if not exists (select 1 from pg_constraint where conrelid='public.external_baseline_members'::regclass and conname='external_member_snapshot_tenant_fkey') then
    alter table external_baseline_members add constraint external_member_snapshot_tenant_fkey
      foreign key (tenant_id, metric_snapshot_id) references external_metric_snapshots(tenant_id, id) on delete restrict;
  end if;
  if not exists (select 1 from pg_constraint where conrelid='public.external_baseline_members'::regclass and conname='external_member_content_tenant_fkey') then
    alter table external_baseline_members add constraint external_member_content_tenant_fkey
      foreign key (tenant_id, content_item_id) references external_content_items(tenant_id, id) on delete restrict;
  end if;
end $$;

-- --------------------------------------------------------- baseline uniqueness
-- A mesma data/run pode produzir snapshots candidatos distintos. A snapshot faz
-- parte da identidade do cálculo; o lookup da API usa exatamente esta chave.
do $$
declare
  old_constraint record;
begin
  for old_constraint in
    select conname
    from pg_constraint
    where conrelid = 'public.external_content_baselines'::regclass
      and contype = 'u'
      and pg_get_constraintdef(oid) like '%candidate_content_item_id%metric_basis%algorithm_version%cutoff_at%'
      and pg_get_constraintdef(oid) not like '%candidate_metric_snapshot_id%'
  loop
    execute format('alter table external_content_baselines drop constraint %I', old_constraint.conname);
  end loop;

  if not exists (
    select 1 from pg_constraint
    where conrelid = 'public.external_content_baselines'::regclass
      and conname = 'external_baseline_candidate_snapshot_key'
  ) then
    alter table external_content_baselines
      add constraint external_baseline_candidate_snapshot_key
      unique (tenant_id, candidate_content_item_id, candidate_metric_snapshot_id, metric_basis, algorithm_version, cutoff_at);
  end if;
end $$;
