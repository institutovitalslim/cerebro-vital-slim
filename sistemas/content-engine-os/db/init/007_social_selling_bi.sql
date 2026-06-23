-- 007_social_selling_bi.sql
-- BI social e Social Selling governado para Content Engine OS.
-- Read-only/dry-run por padrão: não envia DM, não publica, não automatiza contato.

create table if not exists instagram_profile_daily_metrics (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id) on delete cascade,
  profile_handle text not null,
  metric_date date not null default current_date,
  followers_count int,
  following_count int,
  posts_count int,
  reach int,
  impressions int,
  profile_views int,
  website_clicks int,
  whatsapp_clicks int,
  source text not null default 'rapidapi',
  raw_payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  unique (tenant_id, profile_handle, metric_date, source)
);

create table if not exists instagram_publication_daily_metrics (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id) on delete cascade,
  profile_handle text not null,
  publication_external_id text not null,
  publication_url text,
  format text,
  caption_excerpt text,
  published_at timestamptz,
  metric_date date not null default current_date,
  views int,
  reach int,
  likes int,
  comments int,
  saves int,
  shares int,
  profile_visits int,
  follows int,
  whatsapp_clicks int,
  engagement_rate numeric(8,4),
  source text not null default 'rapidapi',
  raw_payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  unique (tenant_id, publication_external_id, metric_date, source)
);

create table if not exists social_selling_interactors (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id) on delete cascade,
  profile_handle text not null default '@dradaniely.freitas',
  public_handle text not null,
  public_name text,
  interaction_type text not null check (interaction_type in ('comment','like','share','save','follow','profile_click','dm_reply','mention')),
  publication_external_id text,
  publication_url text,
  last_interaction_at timestamptz,
  interaction_count int not null default 1,
  observed_signals jsonb not null default '{}'::jsonb,
  consciousness_stage text not null default 'frio' check (consciousness_stage in ('frio','consciente_da_dor','consciente_da_solucao','quase_pronto')),
  fit_score int not null default 0 check (fit_score between 0 and 100),
  status text not null default 'candidate' check (status in ('candidate','reviewed','approved_for_manual_outreach','discarded','converted')),
  suggested_opening text,
  guardrails jsonb not null default '["sem automação de DM", "sem diagnóstico", "sem promessa", "sem preço sem contexto", "abordagem manual e humanizada"]'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (tenant_id, profile_handle, public_handle)
);

create index if not exists idx_profile_metrics_tenant_date on instagram_profile_daily_metrics (tenant_id, metric_date desc);
create index if not exists idx_publication_metrics_tenant_date on instagram_publication_daily_metrics (tenant_id, metric_date desc);
create index if not exists idx_social_interactors_tenant_status_score on social_selling_interactors (tenant_id, status, fit_score desc, updated_at desc);
