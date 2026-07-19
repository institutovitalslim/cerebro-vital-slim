-- 021_motion_video_examples_matrix.sql
-- Fase 2: content_format_examples + matriz 8x8 + winners

alter table content_format_examples
  add column if not exists content_format_id uuid references content_formats(id) on delete cascade;

alter table content_format_examples
  add column if not exists metadata jsonb not null default '{}'::jsonb;

drop index if exists ux_content_format_examples_tenant_external;
create unique index if not exists ux_content_format_examples_tenant_external
  on content_format_examples(tenant_id, external_id);

create table if not exists competitor_research_batches (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid references tenants(id) on delete cascade,
  batch_date date not null default current_date,
  theme text not null,
  objective text,
  owner text default 'joao',
  status text not null default 'draft',
  matrix_rows jsonb not null default '[]'::jsonb,
  matrix_columns jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists competitor_research_items (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid references tenants(id) on delete cascade,
  batch_id uuid references competitor_research_batches(id) on delete cascade,
  example_id uuid references content_format_examples(id) on delete set null,
  source_type text,
  source_handle_or_url text,
  external_id text,
  content_url text,
  content_format_key text,
  hook_summary text,
  objection text,
  retention_mechanism text,
  proof_type text,
  cta_type text,
  compliance_risk text,
  ivs_applicability_score numeric,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists batch_winners (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid references tenants(id) on delete cascade,
  batch_id uuid references competitor_research_batches(id) on delete cascade,
  winner_type text not null check (winner_type in ('attention','conversion','ivs_fit')),
  research_item_id uuid references competitor_research_items(id) on delete set null,
  rationale text,
  selected_for_generation boolean not null default false,
  outputs_required jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now(),
  unique(batch_id, winner_type)
);

create index if not exists idx_competitor_research_batches_tenant on competitor_research_batches(tenant_id, created_at desc);
create index if not exists idx_competitor_research_items_batch on competitor_research_items(batch_id);
create index if not exists idx_batch_winners_batch on batch_winners(batch_id);
