-- Run once in Supabase -> SQL Editor. Non-destructive: keeps all existing data.
-- Adds per-coach ownership (and makes sure Row Level Security is on, so the browser's anon key reaches no rows). The 10 existing demo athletes keep coach_id = null and act as templates
-- that are copied into each new coach's account on first sign-in.

alter table athletes enable row level security;
alter table workout_logs enable row level security;

alter table athletes add column if not exists coach_id uuid references auth.users(id) on delete cascade;
alter table athletes add column if not exists template_id uuid;

create index if not exists athletes_coach_idx on athletes (coach_id);

-- A coach can hold at most one copy of each template, so a double click cannot clone the squad twice.
create unique index if not exists athletes_coach_template_uq on athletes (coach_id, template_id) where template_id is not null;

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
