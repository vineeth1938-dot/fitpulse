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
  resting_hr int check (resting_hr is null or resting_hr between 25 and 120),
  -- null = shared demo template; otherwise the coach (Supabase Auth user) who owns this athlete
  coach_id uuid references auth.users(id) on delete cascade,
  template_id uuid  -- set on copies made from a demo template
);

create index athletes_coach_idx on athletes (coach_id);
create unique index athletes_coach_template_uq on athletes (coach_id, template_id) where template_id is not null;

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

-- Copies the demo squad (athletes with coach_id null) to one coach in a SINGLE transaction, so a coach can never
-- end up with athletes that have no sessions. The advisory lock makes a double click or two tabs wait for each other.
-- Session dates are shifted so the latest template session lands on p_today. Returns the number of athletes the coach owns.
create or replace function clone_demo_roster(p_coach uuid, p_today date)
returns int
language plpgsql
set search_path = public
as $$
declare
  shift int;
  n int;
begin
  perform pg_advisory_xact_lock(hashtext(p_coach::text));
  if exists (select 1 from athletes where coach_id = p_coach) then
    return 0;
  end if;

  select p_today - max(l.session_date) into shift
    from workout_logs l join athletes a on a.id = l.athlete_id
   where a.coach_id is null;
  shift := coalesce(shift, 0);

  with new_athletes as (
    insert into athletes (name, sport, position, resting_hr, coach_id, template_id)
    select name, sport, position, resting_hr, p_coach, id from athletes where coach_id is null
    returning id, template_id
  )
  insert into workout_logs (athlete_id, session_date, duration_mins, rpe, sleep_hours, notes)
  select n.id, l.session_date + shift, l.duration_mins, l.rpe, l.sleep_hours, l.notes
    from new_athletes n join workout_logs l on l.athlete_id = n.template_id;

  select count(*) into n from athletes where coach_id = p_coach;
  return n;
end;
$$;

-- Only the backend (service role) may call it; the browser's anon key must not.
revoke all on function clone_demo_roster(uuid, date) from public, anon, authenticated;
grant execute on function clone_demo_roster(uuid, date) to service_role;
