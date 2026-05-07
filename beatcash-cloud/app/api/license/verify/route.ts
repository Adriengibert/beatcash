import { NextResponse } from "next/server";
import { z } from "zod";
import { adminSupabase } from "@/lib/supabase";
import { signPayload } from "@/lib/license";

const Body = z.object({
  key: z.string().regex(/^BC-[A-Z2-9]{4}-[A-Z2-9]{4}-[A-Z2-9]{4}-[A-Z2-9]{4}$/),
  device_id: z.string().min(1).max(128).optional(),
});

export async function POST(req: Request) {
  const parsed = Body.safeParse(await req.json().catch(() => ({})));
  if (!parsed.success) {
    return NextResponse.json({ valid: false, error: "bad request" }, { status: 400 });
  }
  const { key, device_id } = parsed.data;
  const supa = adminSupabase();

  const { data: lic } = await supa
    .from("licenses").select("*, profiles(email,plan)")
    .eq("key", key).maybeSingle();

  if (!lic) {
    return NextResponse.json({ valid: false, error: "unknown key" }, { status: 404 });
  }

  // Optional device binding (1 device par license)
  if (device_id && lic.device_id && lic.device_id !== device_id) {
    return NextResponse.json({ valid: false, error: "license already bound to another device" }, { status: 409 });
  }
  if (device_id && !lic.device_id) {
    await supa.from("licenses").update({ device_id }).eq("key", key);
  }
  await supa.from("licenses").update({ last_check: new Date().toISOString() }).eq("key", key);

  // Token signé que le desktop garde 7 jours en cache (offline grace)
  const token = signPayload({
    plan: lic.plan,
    user_id: lic.user_id,
    email: (lic as any).profiles?.email,
    issued_at: Date.now(),
    expires_at: Date.now() + 7 * 24 * 3600 * 1000,
  });

  return NextResponse.json({
    valid: true,
    plan:  lic.plan,
    token,
    cached_for_seconds: 7 * 24 * 3600,
  });
}
