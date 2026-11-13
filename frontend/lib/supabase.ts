import { createClient } from "@supabase/supabase-js";

// Both values are public by design (the anon key only works within Row Level Security).
const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

export const supabase = url && anonKey ? createClient(url, anonKey) : null;
