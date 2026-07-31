-- Proveniência auditável do handoff Content Radar -> pipeline criativo.
-- Aditiva/idempotente: consumidores legados continuam lendo brief/payload sem mudanças.

alter table creatives
  add column if not exists radar_provenance jsonb not null default '{}'::jsonb;

alter table creative_test_cycles
  add column if not exists radar_provenance jsonb not null default '{}'::jsonb;

alter table story_sequences
  add column if not exists radar_provenance jsonb not null default '{}'::jsonb;

do $$
begin
  if not exists (
    select 1 from pg_constraint
    where conrelid = 'public.creatives'::regclass
      and conname = 'creatives_radar_provenance_shape_check'
  ) then
    alter table creatives add constraint creatives_radar_provenance_shape_check check (
      jsonb_typeof(radar_provenance) = 'object'
      and (
        radar_provenance = '{}'::jsonb
        or (
          radar_provenance @> '{"source":"radar"}'::jsonb
          and radar_provenance ?& array[
            'radar_item_id', 'radar_external_id', 'radar_baseline_id',
            'radar_snapshot_id', 'radar_cutoff_at', 'radar_algorithm_version'
          ]
        )
      )
    );
  end if;

  if not exists (
    select 1 from pg_constraint
    where conrelid = 'public.creative_test_cycles'::regclass
      and conname = 'creative_test_cycles_radar_provenance_shape_check'
  ) then
    alter table creative_test_cycles add constraint creative_test_cycles_radar_provenance_shape_check check (
      jsonb_typeof(radar_provenance) = 'object'
      and (
        radar_provenance = '{}'::jsonb
        or (
          radar_provenance @> '{"source":"radar"}'::jsonb
          and radar_provenance ?& array[
            'radar_item_id', 'radar_external_id', 'radar_baseline_id',
            'radar_snapshot_id', 'radar_cutoff_at', 'radar_algorithm_version'
          ]
        )
      )
    );
  end if;

  if not exists (
    select 1 from pg_constraint
    where conrelid = 'public.story_sequences'::regclass
      and conname = 'story_sequences_radar_provenance_shape_check'
  ) then
    alter table story_sequences add constraint story_sequences_radar_provenance_shape_check check (
      jsonb_typeof(radar_provenance) = 'object'
      and (
        radar_provenance = '{}'::jsonb
        or (
          radar_provenance @> '{"source":"radar"}'::jsonb
          and radar_provenance ?& array[
            'radar_item_id', 'radar_external_id', 'radar_baseline_id',
            'radar_snapshot_id', 'radar_cutoff_at', 'radar_algorithm_version'
          ]
        )
      )
    );
  end if;
end $$;

create index if not exists idx_creatives_radar_item
  on creatives ((radar_provenance->>'radar_item_id'))
  where radar_provenance <> '{}'::jsonb;

create index if not exists idx_creative_test_cycles_radar_item
  on creative_test_cycles ((radar_provenance->>'radar_item_id'))
  where radar_provenance <> '{}'::jsonb;

create index if not exists idx_story_sequences_radar_item
  on story_sequences ((radar_provenance->>'radar_item_id'))
  where radar_provenance <> '{}'::jsonb;

comment on column creatives.radar_provenance is
  'Cadeia Radar validada no tenant: item/external/snapshot/baseline/cutoff/algorithm_version.';
comment on column creative_test_cycles.radar_provenance is
  'Cadeia Radar recebida no início do ciclo matriz e copiada para cada variante.';
comment on column story_sequences.radar_provenance is
  'Cadeia Radar validada que originou a sequência de Stories.';
