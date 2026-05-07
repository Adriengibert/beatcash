import { NextResponse } from "next/server";
import { z } from "zod";
import { stripe, PRICE_IDS } from "@/lib/stripe";
import { serverSupabase } from "@/lib/supabase";

const Body = z.object({
  plan: z.enum(["pro_monthly", "pro_yearly"]),
});

export async function POST(req: Request) {
  const parsed = Body.safeParse(await req.json().catch(() => ({})));
  if (!parsed.success) {
    return NextResponse.json({ error: "bad request" }, { status: 400 });
  }
  const supa = await serverSupabase();
  const { data: { user } } = await supa.auth.getUser();
  if (!user) return NextResponse.json({ error: "auth required" }, { status: 401 });

  // Récupère ou crée le stripe_customer_id
  const { data: profile } = await supa
    .from("profiles").select("stripe_customer_id").eq("id", user.id).single();

  let customerId = profile?.stripe_customer_id;
  if (!customerId) {
    const customer = await stripe.customers.create({
      email: user.email!,
      metadata: { user_id: user.id },
    });
    customerId = customer.id;
    await supa.from("profiles").update({ stripe_customer_id: customerId }).eq("id", user.id);
  }

  const session = await stripe.checkout.sessions.create({
    mode: "subscription",
    customer: customerId,
    line_items: [{ price: PRICE_IDS[parsed.data.plan], quantity: 1 }],
    success_url: `${process.env.NEXT_PUBLIC_APP_URL}/account?ok=1`,
    cancel_url:  `${process.env.NEXT_PUBLIC_APP_URL}/pricing`,
    metadata: { user_id: user.id },
    subscription_data: { metadata: { user_id: user.id } },
    allow_promotion_codes: true,
  });

  return NextResponse.json({ url: session.url });
}
