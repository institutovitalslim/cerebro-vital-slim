-- Stories Engine 10x IVS — Fase 1 complementar
-- Idempotente: pode rodar em bancos já existentes.

create table if not exists story_themes (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id) on delete cascade,
  title text not null,
  category text not null default 'tema_livre',
  pain text,
  desire text,
  objection text,
  awareness_level text,
  source text not null default 'ivs_seed',
  confidence numeric(4,2) not null default 0.80,
  created_at timestamptz not null default now(),
  unique (tenant_id, title)
);

create table if not exists story_products (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id) on delete cascade,
  name text not null,
  product_type text not null default 'servico',
  offer text,
  cta_link text,
  tracking_url text,
  lead_destination text not null default 'clara_whatsapp',
  owner text not null default 'joao_marketing',
  created_at timestamptz not null default now(),
  unique (tenant_id, name)
);

create table if not exists story_items (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id) on delete cascade,
  sequence_id uuid not null references story_sequences(id) on delete cascade,
  story_order int not null,
  story_type text not null,
  hook text,
  copy text not null,
  visual_direction text,
  sticker_type text,
  cta_type text,
  link_id uuid,
  expected_metric text,
  compliance_status text not null default 'pending_review',
  quality_score numeric(5,2),
  created_at timestamptz not null default now(),
  unique (sequence_id, story_order)
);

create table if not exists story_debriefs (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id) on delete cascade,
  sequence_id uuid not null references story_sequences(id) on delete cascade,
  first_views int,
  last_views int,
  replies_total int,
  taps_forward int,
  exits int,
  link_clicks int,
  leads int,
  sales int,
  appointments int,
  cost numeric(10,2),
  retention_rate numeric(8,2),
  ctr numeric(8,2),
  drop_story int,
  winning_cta text,
  learning text,
  next_action text,
  created_at timestamptz not null default now()
);

create index if not exists idx_story_themes_tenant_category on story_themes (tenant_id, category, created_at desc);
create index if not exists idx_story_products_tenant on story_products (tenant_id, created_at desc);
create index if not exists idx_story_items_sequence_order on story_items (sequence_id, story_order);
create index if not exists idx_story_debriefs_sequence_created on story_debriefs (sequence_id, created_at desc);

create table if not exists story_click_events (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenants(id) on delete cascade,
  sequence_id uuid not null references story_sequences(id) on delete cascade,
  origin_tag text,
  utm_campaign text,
  utm_content text,
  user_agent text,
  created_at timestamptz not null default now()
);

create index if not exists idx_story_click_events_sequence_created on story_click_events (sequence_id, created_at desc);

alter table story_sequence_performance add column if not exists shares int;
alter table story_sequence_performance add column if not exists saves int;
alter table story_sequence_performance add column if not exists retention_initial_pct numeric(8,2);
alter table story_sequence_performance add column if not exists avg_watch_time_sec numeric(8,2);
alter table story_sequence_performance add column if not exists intent_signal text;
alter table story_sequence_performance add column if not exists quality_metric text;
alter table story_sequence_performance add column if not exists send_save_reason text;

with t as (select id from tenants where slug='demo' limit 1)
insert into story_products (tenant_id, name, product_type, offer, cta_link, tracking_url, lead_destination, owner)
select t.id, v.name, 'servico', v.offer, v.cta_link, v.tracking_url, 'clara_whatsapp', 'joao_marketing'
from t
cross join (values
  ('Consulta Médica', 'Avaliação médica IVS para entender contexto, exames, rotina e caminho possível.', 'https://api.whatsapp.com/send/?phone=557138388708&text=Gostaria+de+saber+mais+informações+sobre+o+Instituto+Vital+Slim', null),
  ('Programa de Acompanhamento', 'Programa IVS com acompanhamento integrado para evolução clínica e comportamental.', 'https://api.whatsapp.com/send/?phone=557138388708&text=Quero+entender+o+programa+de+acompanhamento+do+IVS', null),
  ('Tricologia', 'Avaliação voltada a queixas capilares e contexto clínico.', 'https://api.whatsapp.com/send/?phone=557138388708&text=Quero+saber+mais+sobre+tricologia+no+IVS', null)
) as v(name, offer, cta_link, tracking_url)
on conflict (tenant_id, name) do update set offer=excluded.offer, cta_link=excluded.cta_link;

with t as (select id from tenants where slug='demo' limit 1)
insert into story_themes (tenant_id, title, category, pain, desire, objection, awareness_level, source, confidence)
select t.id, v.title, v.category, v.pain, v.desire, v.objection, v.awareness_level, 'stories10x_mapping_seed', 0.90
from t
cross join (values
  ('Emag - O que é resistência à insulina', 'categorias', 'dificuldade de emagrecer mesmo tentando', 'entender a causa e o caminho seguro', 'já tentei de tudo', 'problem_aware'),
  ('Emag - Diferença entre emagrecer e perder gordura', 'categorias', 'confusão entre balança e composição corporal', 'clareza sobre evolução real', 'não sei se estou evoluindo', 'solution_aware'),
  ('Emag - Quero um tratamento médico que funcione de verdade', 'urgencias_ocultas', 'frustração com tentativas anteriores', 'segurança e método', 'medo de cair em mais uma promessa', 'solution_aware'),
  ('Emag - Quero começar agora, mas não sei em quem confiar', 'situacoes_identificacao', 'urgência misturada com insegurança', 'confiança no processo', 'medo de julgamento ou promessa vazia', 'most_aware'),
  ('Rep Horm - Sintomas que parecem ansiedade, mas são hormonais', 'situacoes_identificacao', 'sintomas difusos e autoculpa', 'investigação com contexto', 'achar que é coisa da cabeça', 'problem_aware'),
  ('Rep Horm - Estou me sentindo esgotada, sem libido, e ganhando peso', 'urgencias_ocultas', 'queda de energia, libido e autoestima', 'se reconhecer e buscar avaliação', 'vergonha de falar', 'problem_aware'),
  ('Emag - Já tentei dieta, remédio e academia — e nada funcionou', 'situacoes_identificacao', 'cansaço de repetir estratégias', 'um plano que considere rotina e exames', 'já tentei de tudo', 'problem_aware'),
  ('Rep Horm - Reposição hormonal é só na menopausa?', 'categorias', 'dúvida sobre indicação e segurança', 'orientação médica contextualizada', 'medo de efeitos colaterais', 'solution_aware')
) as v(title, category, pain, desire, objection, awareness_level)
on conflict (tenant_id, title) do update set
  category=excluded.category,
  pain=excluded.pain,
  desire=excluded.desire,
  objection=excluded.objection,
  awareness_level=excluded.awareness_level,
  source=excluded.source,
  confidence=excluded.confidence;
