import { NextResponse } from "next/server";
import type Stripe from "stripe";
import { stripe } from "@/lib/stripe";
import { adminSupabase } from "@/lib/supabase";
import { generateLicenseKey } from "@/lib/license";

export const runtime = "nodejs";   // requis pour la lecture du raw body

export async function POST(req: Request) {
  const sig = req.headers.get("stripe-signature");
  const buf = Buffer.from(await req.arrayBuffer());

  let event: Stripe.Event;
  try {
    event = stripe.webhooks.constructEvent(buf, sig!, process.env.STRIPE_WEBHOOK_SECRET!);
  } catch (e: any) {
    return NextResponse.json({ error: `bad signature: ${e.message}` }, { status: 400 });
  }

  const supa = adminSupabase();

  switch (event.type) {
    case "checkout.session.completed": {
      const s = event.data.object as Stripe.Checkout.Session;
      const userId = s.metadata?.user_id;
      if (!userId || !s.subscription) break;
      const sub = await stripe.subscriptions.retrieve(s.subscription as string);
      await upsertSubscription(supa, userId, sub);
      await ensureLicense(supa, userId, "PRO");
      await supa.from("profiles").update({ plan: "PRO" }).eq("id", userId);
      break;
    }

    case "customer.subscription.created":
    case "customer.subscription.updated": {
      const sub = event.data.object as Stripe.Subscription;
      const userId = (sub.metadata?.user_id) ||
                     (await userIdFromCustomer(supa, sub.customer as string));
      if (!userId) break;
      await upsertSubscription(supa, userId, sub);
      const isActive = ["active", "trialing"].includes(sub.status);
      await supa.from("profiles").update({ plan: isActive ? "PRO" : "FREE" }).eq("id", userId);
      if (isActive) await ensureLicense(supa, userId, "PRO");
      break;
    }

    case "customer.subscription.deleted": {
      const sub = event.data.object as Stripe.Subscription;
      const userId = (sub.metadata?.user_id) ||
                     (await userIdFromCustomer(supa, sub.customer as string));
      if (!userId) break;
      await supa.from("profiles").update({ plan: "FREE" }).eq("id", userId);
      await supa.from("subscriptions").update({ status: "canceled" }).eq("id", sub.id);
      await supa.from("licenses").update({ plan: "FREE" }).eq("user_id", userId);
      break;
    }
  }

  return NextResponse.json({ received: true });
}

async function userIdFromCustomer(supa: ReturnType<typeof adminSupabase>, customerId: string) {
  const { data } = await supa.from("profiles").select("id").eq("stripe_customer_id", customerId).maybeSingle();
  return data?.id ?? null;
}

async function upsertSubscription(
  supa: ReturnType<typeof adminSupabase>,
  userId: string,
  sub: Stripe.Subscription,
) {
  // current_period_end vit sur les items dans les SDK récents
  const periodEnd =
    (sub as any).current_period_end ??
    sub.items.data[0]?.current_period_end ??
    Math.floor(Date.now() / 1000) + 30 * 86400;
  await supa.from("subscriptions").upsert({
    id: sub.id,
    user_id: userId,
    status: sub.status,
    price_id: sub.items.data[0]?.price.id ?? "",
    current_period_end: new Date(periodEnd * 1000).toISOString(),
    cancel_at_period_end: sub.cancel_at_period_end,
    updated_at: new Date().toISOString(),
  });
}

async function ensureLicense(
  supa: ReturnType<typeof adminSupabase>,
  userId: string,
  plan: "PRO" | "FREE",
) {
  const { data: existing } = await supa.from("licenses").select("key").eq("user_id", userId).maybeSingle();
  if (existing) {
    await supa.from("licenses").update({ plan }).eq("user_id", userId);
    return existing.key;
  }
  const key = generateLicenseKey();
  await supa.from("licenses").insert({ key, user_id: userId, plan });
  return key;
}
