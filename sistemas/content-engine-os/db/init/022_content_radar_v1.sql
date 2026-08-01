-- Content Radar v1 — P0/P1 aditivo e auditável
-- Regra: ausência de métrica permanece ausência; nunca criar métricas estimadas.

create table if not exists external_radar_sources (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id) on delete cascade,
  network text not null,
  canonical_key text not null,
  display_name text,
  handle_or_url text,
  source_kind text not null check (
    source_kind in ('approved', 'candidate', 'excluded', 'own_account', 'thematic_search')
  ),
  active boolean not null default true,
  decision_reason text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (tenant_id, network, canonical_key)
);

create table if not exists external_radar_source_decisions (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id) on delete cascade,
  radar_source_id uuid not null references external_radar_sources(id) on delete cascade,
  from_kind text,
  to_kind text not null check (
    to_kind in ('approved', 'candidate', 'excluded', 'own_account', 'thematic_search')
  ),
  reason text not null,
  decided_by text not null,
  decided_at timestamptz not null default now()
);

alter table external_content_items add column if not exists radar_source_id uuid references external_radar_sources(id);
alter table external_content_items add column if not exists canonical_format text;
alter table external_content_items add column if not exists actual_source_profile text;
alter table external_content_items add column if not exists first_seen_at timestamptz;
alter table external_content_items add column if not exists last_seen_at timestamptz;

do $$
begin
  if not exists (
    select 1 from pg_constraint where conname = 'external_content_items_canonical_format_check'
  ) then
    alter table external_content_items
      add constraint external_content_items_canonical_format_check
      check (canonical_format is null or canonical_format in ('reel', 'carousel', 'post', 'story', 'other'));
  end if;
end $$;

create table if not exists external_metric_snapshots (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id) on delete cascade,
  content_item_id uuid not null references external_content_items(id) on delete cascade,
  observed_at timestamptz not null,
  metric_basis text not null check (
    metric_basis in ('views', 'plays', 'reach', 'public_interactions')
  ),
  metric_value numeric not null check (metric_value >= 0 and metric_value <= 1000000000000000),
  provider text not null,
  collector_run_id text not null,
  raw_metrics jsonb not null default '{}'::jsonb,
  payload_fingerprint text not null,
  legacy_import boolean not null default false,
  created_at timestamptz not null default now(),
  unique (tenant_id, content_item_id, metric_basis, provider, collector_run_id)
);

create table if not exists external_content_baselines (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id) on delete cascade,
  candidate_content_item_id uuid not null references external_content_items(id) on delete cascade,
  candidate_metric_snapshot_id uuid not null references external_metric_snapshots(id) on delete restrict,
  source_network text not null,
  source_profile text not null,
  canonical_format text not null check (canonical_format in ('reel', 'carousel', 'post', 'story', 'other')),
  metric_basis text not null check (
    metric_basis in ('views', 'plays', 'reach', 'public_interactions')
  ),
  observation_window text not null check (
    observation_window in ('0_24h', '24_72h', '72h_7d', '7d_plus')
  ),
  cutoff_at timestamptz not null,
  algorithm_version text not null,
  sample_count integer not null check (sample_count >= 0 and sample_count <= 30),
  median_value numeric,
  maturity text not null check (maturity in ('insufficient', 'provisional', 'target')),
  performance_ratio numeric,
  signal_state text not null check (signal_state in ('insufficient', 'signal', 'outlier', 'breakout')),
  reason text,
  computed_at timestamptz not null default now(),
  unique (tenant_id, candidate_content_item_id, metric_basis, algorithm_version, cutoff_at)
);

create table if not exists external_baseline_members (
  baseline_id uuid not null references external_content_baselines(id) on delete cascade,
  metric_snapshot_id uuid not null references external_metric_snapshots(id) on delete restrict,
  content_item_id uuid not null references external_content_items(id) on delete restrict,
  metric_value numeric not null check (metric_value >= 0),
  primary key (baseline_id, metric_snapshot_id)
);

create table if not exists ideias_estado (
  tenant_id uuid not null references tenants(id) on delete cascade,
  ideia_id text not null,
  estado text not null check (estado in ('guardada', 'produzida', 'descartada')),
  criado_em timestamptz not null default now(),
  primary key (tenant_id, ideia_id)
);

create index if not exists idx_external_radar_sources_kind
  on external_radar_sources(tenant_id, source_kind, active, network);
create index if not exists idx_external_metric_snapshots_lookup
  on external_metric_snapshots(tenant_id, content_item_id, metric_basis, observed_at desc);
create index if not exists idx_external_content_baselines_group
  on external_content_baselines(tenant_id, source_profile, canonical_format, metric_basis, cutoff_at desc);
create index if not exists idx_external_baseline_members_content
  on external_baseline_members(content_item_id, baseline_id);

-- Governança inicial por decisão explícita do IVS.
insert into external_radar_sources (
  tenant_id, network, canonical_key, display_name, handle_or_url, source_kind, decision_reason
)
select t.id, 'instagram', seed.canonical_key, seed.display_name, seed.handle_or_url,
       seed.source_kind, 'Backfill governado Content Radar v1'
from tenants t
cross join (values
  ('dr.marlonbatista', 'Dr. Marlon Batista', '@dr.marlonbatista', 'approved'),
  ('dra.camilapaes', 'Dra. Camila Paes', '@dra.camilapaes', 'approved'),
  ('dradaniely.freitas', 'Dra. Daniely Freitas', '@dradaniely.freitas', 'own_account'),
  ('yuribarbosaoficial', 'Yuri Barbosa', '@yuribarbosaoficial', 'excluded'),
  ('oestevaosouza', 'Estevão Souza', '@oestevaosouza', 'excluded')
) as seed(canonical_key, display_name, handle_or_url, source_kind)
where t.slug = 'demo'
on conflict (tenant_id, network, canonical_key) do nothing;

insert into external_radar_sources (
  tenant_id, network, canonical_key, display_name, source_kind, decision_reason
)
select distinct e.tenant_id, e.source_network,
       lower(ltrim(btrim(e.source_profile), '@')), e.source_profile,
       case
         when e.source = 'phase4_sample' then 'excluded'
         when lower(e.source_profile) like 'theme_search:%' then 'thematic_search'
         else 'candidate'
       end,
       case
         when e.source = 'phase4_sample' then 'Amostra técnica; não participa do radar'
         when e.source_profile like 'theme_search:%' then 'Descoberta temática sem autor canônico'
         else 'Fonte existente aguardando curadoria'
       end
from external_content_items e
on conflict (tenant_id, network, canonical_key) do nothing;

update external_content_items e
set radar_source_id = s.id,
    source_profile = s.canonical_key,
    canonical_format = case
      when lower(coalesce(e.format, '')) in ('clips', 'reels', 'reel', 'short', 'shorts') then 'reel'
      when lower(coalesce(e.format, '')) in ('carousel_container', 'carousel', 'carrossel') then 'carousel'
      when lower(coalesce(e.format, '')) in ('feed', 'post', 'static', 'estatico', 'estático') then 'post'
      when lower(coalesce(e.format, '')) in ('story', 'stories') then 'story'
      else 'other'
    end,
    actual_source_profile = case
      when lower(e.source_profile) like 'theme_search:%' then null
      else lower(ltrim(btrim(e.source_profile), '@'))
    end,
    first_seen_at = coalesce(e.first_seen_at, e.created_at),
    last_seen_at = coalesce(e.last_seen_at, e.updated_at)
from external_radar_sources s
where s.tenant_id = e.tenant_id
  and s.network = e.source_network
  and s.canonical_key = lower(ltrim(btrim(e.source_profile), '@'));

-- Backfill legado conservador: somente valores positivos realmente armazenados.
-- Zero legado é ambíguo porque coletores antigos usavam 0 para "indisponível".
insert into external_metric_snapshots (
  tenant_id, content_item_id, observed_at, metric_basis, metric_value,
  provider, collector_run_id, raw_metrics, payload_fingerprint, legacy_import
)
select e.tenant_id, e.id, coalesce(e.updated_at, e.created_at), basis.metric_basis,
       basis.metric_value, e.source, 'legacy:' || e.id::text || ':' || basis.metric_basis,
       e.metrics, 'legacy:' || e.id::text || ':' || basis.metric_basis, true
from external_content_items e
cross join lateral (
  values
    ('views', case when jsonb_typeof(e.metrics->'views') = 'number' and (e.metrics->>'views')::numeric > 0 then (e.metrics->>'views')::numeric end),
    ('plays', case when jsonb_typeof(e.metrics->'plays') = 'number' and (e.metrics->>'plays')::numeric > 0 then (e.metrics->>'plays')::numeric end),
    ('reach', case when jsonb_typeof(e.metrics->'reach') = 'number' and (e.metrics->>'reach')::numeric > 0 then (e.metrics->>'reach')::numeric end),
    ('public_interactions', case
      when coalesce(case when jsonb_typeof(e.metrics->'likes') = 'number' then (e.metrics->>'likes')::numeric end, 0)
         + coalesce(case when jsonb_typeof(e.metrics->'comments') = 'number' then (e.metrics->>'comments')::numeric end, 0) > 0
      then coalesce(case when jsonb_typeof(e.metrics->'likes') = 'number' then (e.metrics->>'likes')::numeric end, 0)
         + coalesce(case when jsonb_typeof(e.metrics->'comments') = 'number' then (e.metrics->>'comments')::numeric end, 0)
      end)
) as basis(metric_basis, metric_value)
where basis.metric_value is not null
on conflict (tenant_id, content_item_id, metric_basis, provider, collector_run_id) do nothing;
