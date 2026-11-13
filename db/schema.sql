-- FitPulse schema. Paste into Supabase -> SQL Editor -> Run.
-- WARNING: this DELETES the old athletes and workout_logs tables (they held only a test row) and recreates them.
create extension if not exists pgcrypto;

drop table if exists workout_logs cascade;
drop table if exists athletes cascade;

create table athletes (
  id uuid primary key default gen_random_uuid(),
  name text not null check (length(trim(name)) > 0),
  sport text,
  position text,
  resting_hr int check (resting_hr is null or resting_hr between 25 and 120)
);

create table workout_logs (
  id uuid primary key default gen_random_uuid(),
  athlete_id uuid not null references athletes(id) on delete cascade,
  session_date date not null,
  duration_mins int not null check (duration_mins between 1 and 600),
  rpe int not null check (rpe between 1 and 10),
  sleep_hours numeric(3,1) check (sleep_hours is null or sleep_hours between 0 and 24),
  notes text
);

create index workout_logs_athlete_date_idx on workout_logs (athlete_id, session_date desc);

-- Supabase exposes public tables through the anon key. Lock them down: the FastAPI
-- backend uses the service_role key, which bypasses RLS. No policies = no anon access.
alter table athletes enable row level security;
alter table workout_logs enable row level security;
