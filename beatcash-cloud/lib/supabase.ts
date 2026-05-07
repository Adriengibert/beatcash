import { createBrowserClient, createServerClient } from "@supabase/ssr";
import { createClient } from "@supabase/supabase-js";
import { cookies } from "next/headers";

const URL  = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const ANON = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

/** Client browser (RSC client components, hooks). */
export function browserSupabase() {
  return createBrowserClient(URL, ANON);
}

/** Client server avec cookies user (RSC, route handlers, server actions). */
export async function serverSupabase() {
  const c = await cookies();
  return createServerClient(URL, ANON, {
    cookies: {
      getAll: () => c.getAll(),
      setAll: (toSet) => toSet.forEach(({ name, value, options }) => c.set(name, value, options)),
    },
  });
}

/** Service role — bypass RLS. À UTILISER uniquement côté serveur (webhook, etc.). */
export function adminSupabase() {
  return createClient(URL, process.env.SUPABASE_SERVICE_ROLE_KEY!, {
    auth: { autoRefreshToken: false, persistSession: false },
  });
}
