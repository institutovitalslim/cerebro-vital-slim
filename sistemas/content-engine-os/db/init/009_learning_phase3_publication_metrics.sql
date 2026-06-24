-- Fase 3: publicação vinculada ao criativo + importação governada de métricas
alter table publications add column if not exists platform text;
alter table publications add column if not exists platform_post_id text;
alter table publications add column if not exists published_url text;
alter table publications add column if not exists campaign_name text;
alter table publications add column if not exists notes text;

create unique index if not exists idx_publications_creative_id_once
  on publications(creative_id)
  where creative_id is not null;

create index if not exists idx_publications_platform_post
  on publications(tenant_id, platform, platform_post_id)
  where platform_post_id is not null;
