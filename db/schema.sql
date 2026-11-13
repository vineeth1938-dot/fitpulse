-- FitPulse schema. Paste into Supabase -> SQL Editor -> Run.
-- WARNING: this DELETES the old athletes and workout_logs tables (they held only a test row) and recreates them.
create extension if not exists pgcrypto;

drop table if exists workout_logs cascade;
drop table if exists athletes cascade;

create table athletes (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  sport text,
  position text,
  resting_hr int
);

create table workout_logs (
  id uuid primary key default gen_random_uuid(),
  athlete_id uuid not null references athletes(id) on delete cascade,
  session_date date not null,
  duration_mins int not null check (duration_mins > 0),
  rpe int not null check (rpe between 1 and 10),
  sleep_hours float,
  notes text
);

create index workout_logs_athlete_date_idx on workout_logs (athlete_id, session_date desc);
