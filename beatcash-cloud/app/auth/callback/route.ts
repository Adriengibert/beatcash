import { NextResponse } from "next/server";
import { serverSupabase } from "@/lib/supabase";

/**
 * Handler appelé par Supabase après le clic sur le magic link.
 * Échange le `code` contre une session, puis redirige vers /account.
 */
export async function GET(req: Request) {
  const url    = new URL(req.url);
  const code   = url.searchParams.get("code");
  const next   = url.searchParams.get("next") || "/account";
  const origin = url.origin;

  if (!code) {
    return NextResponse.redirect(`${origin}/login?error=missing_code`);
  }

  const supa = await serverSupabase();
  const { error } = await supa.auth.exchangeCodeForSession(code);
  if (error) {
    return NextResponse.redirect(`${origin}/login?error=${encodeURIComponent(error.message)}`);
  }

  return NextResponse.redirect(`${origin}${next}`);
}
