-- 020_motion_videos_higgsfield_studio.sql
-- Motion Videos · Higgsfield Studio + short-form content formats

create table if not exists content_formats (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid references tenants(id) on delete cascade,
  key text not null,
  name text not null,
  description text,
  best_for jsonb not null default '[]'::jsonb,
  objection_targets jsonb not null default '[]'::jsonb,
  default_structure jsonb not null default '[]'::jsonb,
  motion_notes text,
  prompt_bias text,
  compliance_notes text,
  enabled boolean not null default true,
  created_at timestamptz not null default now(),
  unique (tenant_id, key)
);

create table if not exists content_format_examples (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid references tenants(id) on delete cascade,
  content_format_key text not null,
  source_type text,
  source_handle_or_url text,
  external_id text,
  content_url text,
  thumbnail_url text,
  transcript_summary text,
  hook_summary text,
  retention_mechanism text,
  why_this_example_works text,
  compliance_risk text,
  ivs_applicability_score int,
  created_at timestamptz not null default now()
);
create index if not exists idx_content_format_examples_key on content_format_examples(content_format_key);

create table if not exists motion_video_projects (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid references tenants(id) on delete cascade,
  title text not null,
  source_type text not null default 'manual',
  source_id uuid,
  topic text not null,
  thesis text,
  objective text,
  audience text,
  objection text,
  content_format text not null,
  content_strategy text,
  source_example_ids jsonb not null default '[]'::jsonb,
  source_batch_id uuid,
  screen_format text not null default 'reels',
  aspect_ratio text not null default '9:16',
  duration_seconds int not null default 60,
  blocks_count int not null default 6,
  visual_preset text not null default 'ivs_mixed_media_medico_premium',
  narrative_pattern text,
  voiceover text not null default 'documental_feminina_pt_br',
  status text not null default 'planned',
  approval_status text not null default 'plan_only',
  format_fit_score int,
  example_abstraction_score int,
  objection_break_score int,
  retention_score int,
  compliance_score int,
  ivs_avatar_score int,
  estimated_credits jsonb not null default '{}'::jsonb,
  actual_credits numeric,
  plan_payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists idx_motion_video_projects_tenant_created on motion_video_projects(tenant_id, created_at desc);
create index if not exists idx_motion_video_projects_content_format on motion_video_projects(content_format);

create table if not exists motion_video_blocks (
  id uuid primary key default gen_random_uuid(),
  project_id uuid references motion_video_projects(id) on delete cascade,
  block_index int not null,
  narration_text text not null,
  visual_prompt text not null,
  style_reference text,
  scene text,
  motion text,
  audio_prompt text,
  negative_prompt text,
  clip_job_id text,
  audio_job_id text,
  clip_url text,
  audio_url text,
  duration_sec numeric,
  status text not null default 'planned',
  created_at timestamptz not null default now(),
  unique(project_id, block_index)
);

create table if not exists motion_video_runs (
  id uuid primary key default gen_random_uuid(),
  project_id uuid references motion_video_projects(id) on delete cascade,
  run_type text not null,
  provider text not null default 'higgsfield',
  model text,
  request_payload jsonb not null default '{}'::jsonb,
  response_payload jsonb not null default '{}'::jsonb,
  status text not null default 'pending',
  error_message text,
  credits_estimated numeric,
  credits_used numeric,
  created_at timestamptz not null default now(),
  completed_at timestamptz
);

create table if not exists motion_video_outputs (
  id uuid primary key default gen_random_uuid(),
  project_id uuid references motion_video_projects(id) on delete cascade,
  output_type text not null,
  asset_url text,
  local_path text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);
