create table if not exists pr_snapshot (
  id bigint generated always as identity primary key,
  repo_name text not null,
  pr_number int not null,
  title text not null,
  url text not null,
  state text not null,
  draft boolean not null default false,
  author text,
  created_at timestamptz not null,
  updated_at timestamptz not null,
  last_seen_at timestamptz not null default now(),
  unique (repo_name, pr_number)
);

create table if not exists activity_log (
  id bigint generated always as identity primary key,
  occurred_at timestamptz not null default now(),
  repo_name text not null,
  entity_type text not null,
  entity_number int,
  action text not null,
  actor text,
  title text,
  url text,
  detail jsonb
);

create index if not exists activity_log_occurred_at_idx on activity_log (occurred_at desc);
create index if not exists activity_log_repo_idx on activity_log (repo_name);

alter table pr_snapshot enable row level security;
alter table activity_log enable row level security;

drop policy if exists "public read pr_snapshot" on pr_snapshot;
create policy "public read pr_snapshot" on pr_snapshot for select using (true);

drop policy if exists "public read activity_log" on activity_log;
create policy "public read activity_log" on activity_log for select using (true);
