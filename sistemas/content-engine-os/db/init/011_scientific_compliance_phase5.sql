-- Fase 5: científico/compliance premium antes de publicação
alter table scientific_sources add column if not exists topic text;
alter table scientific_sources add column if not exists doi text;
alter table scientific_sources add column if not exists pmid text;

create table if not exists compliance_assessments (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id) on delete cascade,
  creative_id uuid references creatives(id) on delete cascade,
  content_hash text not null,
  status text not null,
  risk_level text not null,
  score numeric(5,2) not null default 0,
  claims jsonb not null default '[]'::jsonb,
  red_flags jsonb not null default '[]'::jsonb,
  evidence jsonb not null default '[]'::jsonb,
  missing_sources jsonb not null default '[]'::jsonb,
  fixes jsonb not null default '[]'::jsonb,
  required_footer text,
  created_at timestamptz not null default now()
);

create index if not exists idx_compliance_assessments_creative on compliance_assessments(creative_id, created_at desc);
create index if not exists idx_compliance_assessments_status on compliance_assessments(tenant_id, status, risk_level);
