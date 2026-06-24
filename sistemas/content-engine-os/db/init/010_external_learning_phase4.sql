-- Fase 4: ingestão externa governada + engenharia reversa de conteúdos campeões
alter table sources add column if not exists finalidade text;
alter table sources add column if not exists objetivo text;

create table if not exists external_content_items (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id) on delete cascade,
  source_network text not null default 'instagram',
  source_profile text not null,
  external_id text not null,
  url text,
  format text,
  caption text,
  published_at timestamptz,
  metric_date date not null default current_date,
  metrics jsonb not null default '{}'::jsonb,
  raw_payload jsonb not null default '{}'::jsonb,
  reverse_engineering jsonb not null default '{}'::jsonb,
  opportunity_score numeric(8,2) not null default 0,
  source text not null default 'rapidapi',
  status text not null default 'new',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (tenant_id, source_network, external_id)
);

create table if not exists content_pattern_library (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id) on delete cascade,
  pattern_key text not null,
  pattern_type text not null,
  label text not null,
  score numeric(8,2) not null default 0,
  examples jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (tenant_id, pattern_key)
);

create index if not exists idx_external_content_score on external_content_items(tenant_id, opportunity_score desc, updated_at desc);
create index if not exists idx_external_content_profile on external_content_items(tenant_id, source_profile, metric_date desc);
create index if not exists idx_pattern_library_score on content_pattern_library(tenant_id, score desc);
