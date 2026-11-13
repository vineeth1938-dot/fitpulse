-- Run in Supabase -> SQL Editor before every rehearsal and before the real demo.
--
-- Deletes every coach's copy of the demo squad (their logged sessions go with them).
-- Coach ACCOUNTS are kept. The next time a coach opens the dashboard, a fresh copy of the
-- 10 demo athletes is made automatically, so reload the page after running this.
delete from athletes where coach_id is not null;

-- Only if the shared demo athletes themselves were damaged: also run db/seed.sql afterwards.
