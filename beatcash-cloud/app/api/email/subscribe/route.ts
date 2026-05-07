import { NextResponse } from "next/server";
import { z } from "zod";
import { Resend } from "resend";
import { adminSupabase } from "@/lib/supabase";

const Body = z.object({
  email: z.string().email(),
  source: z.string().optional(),
});

export async function POST(req: Request) {
  const parsed = Body.safeParse(await req.json().catch(() => ({})));
  if (!parsed.success) return NextResponse.json({ error: "bad email" }, { status: 400 });

  const { email, source = "free_pack" } = parsed.data;
  const supa = adminSupabase();

  // Upsert email subscriber
  await supa.from("email_subscribers").upsert(
    { email, source, free_pack_sent_at: new Date().toISOString() },
    { onConflict: "email" },
  );

  // Send free pack email via Resend
  const resend = new Resend(process.env.RESEND_API_KEY!);
  const FROM   = process.env.RESEND_FROM_EMAIL || "hello@beatcash.app";
  const PACK   = process.env.FREE_PACK_URL || "#";

  try {
    await resend.emails.send({
      from: FROM,
      to: email,
      subject: "Ton free pack Beat Cash 🎁",
      html: `
        <div style="font-family: -apple-system, system-ui, sans-serif; max-width: 480px; margin: 0 auto; padding: 24px; color: #111;">
          <div style="font-family: monospace; font-size: 12px; letter-spacing: .2em; color: #666; margin-bottom: 16px;">$ BEATCASH</div>
          <h1 style="font-size: 22px; margin: 0 0 12px;">Voilà ton free pack 50 type beats.</h1>
          <p style="line-height: 1.6;">Merci d'être passé ! Le pack contient 50 type beats libres pour t'inspirer ou tester ton workflow.</p>
          <p style="margin: 28px 0;">
            <a href="${PACK}" style="display:inline-block;background:#000;color:#fff;padding:14px 22px;border-radius:10px;text-decoration:none;font-weight:600;">→ Télécharger le pack</a>
          </p>
          <p style="font-size: 13px; color: #666; line-height: 1.6;">
            Beat Cash publie tes beats sur YouTube + Instagram + TikTok + Audiomack en 1 clic, avec SEO IA.
            <br/><br/>
            <a href="${process.env.NEXT_PUBLIC_APP_URL}/pricing" style="color:#000;">→ Découvrir Beat Cash Pro</a>
          </p>
        </div>
      `,
    });
  } catch (e) {
    console.error("[resend] send failed", e);
    // Pas bloquant : on a quand même capturé l'email
  }

  return NextResponse.json({ ok: true });
}
