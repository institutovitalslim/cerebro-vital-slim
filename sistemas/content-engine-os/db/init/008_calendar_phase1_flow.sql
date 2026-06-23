-- Content Engine OS — Fase 1 operacional: aprovação -> calendário -> publicação -> métrica.
-- Idempotente. Mantém governança: não publica em rede externa, só registra status interno.

alter table calendar_entries
  add column if not exists creative_id uuid references creatives(id) on delete set null,
  add column if not exists origin_tag text,
  add column if not exists sprint_thesis text,
  add column if not exists sprint_hook text,
  add column if not exists published_at timestamptz,
  add column if not exists metrics jsonb not null default '{}'::jsonb,
  add column if not exists metrics_recorded_at timestamptz;

create unique index if not exists idx_calendar_entries_creative_id
  on calendar_entries(creative_id)
  where creative_id is not null;

create index if not exists idx_calendar_entries_status
  on calendar_entries(tenant_id, status);

create unique index if not exists idx_publications_creative_id_once
  on publications(creative_id)
  where creative_id is not null;
