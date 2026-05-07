import Link from "next/link";
import { redirect } from "next/navigation";
import { serverSupabase } from "@/lib/supabase";

export const dynamic = "force-dynamic";

export default async function AccountPage() {
  const supa = await serverSupabase();
  const { data: { user } } = await supa.auth.getUser();
  if (!user) redirect("/login");

  const { data: profile } = await supa.from("profiles").select("*").eq("id", user.id).single();
  const { data: license } = await supa.from("licenses").select("*").eq("user_id", user.id).maybeSingle();
  const { data: sub }     = await supa.from("subscriptions").select("*").eq("user_id", user.id).order("created_at", { ascending: false }).limit(1).maybeSingle();

  return (
    <main className="mx-auto w-full max-w-2xl flex-1 px-6 py-16">
      <Link href="/" className="mb-12 flex items-baseline gap-2">
        <span className="font-display text-[22px] font-bold text-glow leading-none">$</span>
        <span className="font-display text-[13px] font-bold tracking-widest2">BEATCASH</span>
      </Link>

      <div className="font-mono text-[11px] uppercase tracking-ultra text-white/50">— Compte —</div>
      <h1 className="mt-2 font-display text-3xl font-bold uppercase tracking-widest2">{user.email}</h1>

      <section className="mt-10 rounded-2xl border-hairline glass p-7">
        <div className="flex items-baseline justify-between">
          <div>
            <div className="font-mono text-[10px] uppercase tracking-ultra text-white/50">Plan actuel</div>
            <div className="mt-2 font-display text-2xl font-bold tracking-widest2">{profile?.plan || "FREE"}</div>
          </div>
          {profile?.plan !== "PRO" && (
            <Link href="/pricing" className="rounded-xl bg-white px-5 py-2.5 font-display text-[11px] font-bold tracking-widest2 text-black">
              UPGRADE
            </Link>
          )}
        </div>
        {sub && (
          <div className="mt-5 grid grid-cols-2 gap-4 font-mono text-[12px]">
            <div>
              <div className="text-white/50">Statut Stripe</div>
              <div className="mt-1">{sub.status}</div>
            </div>
            <div>
              <div className="text-white/50">Renouvellement</div>
              <div className="mt-1">{new Date(sub.current_period_end).toLocaleDateString("fr-FR")}</div>
            </div>
          </div>
        )}
      </section>

      <section className="mt-5 rounded-2xl border-hairline glass p-7">
        <div className="font-mono text-[10px] uppercase tracking-ultra text-white/50">License key</div>
        {license ? (
          <>
            <div className="mt-3 select-all rounded-xl border-hairline-hi bg-black/60 p-4 font-mono text-lg tracking-widest text-white">
              {license.key}
            </div>
            <p className="mt-3 text-[12px] text-white/60">
              Colle cette clé dans Beat Cash → menu Compte → Activer la license.
              {license.device_id && (
                <> Liée à l'appareil <span className="font-mono">{license.device_id.slice(0, 8)}…</span>.</>
              )}
            </p>
          </>
        ) : (
          <p className="mt-3 text-[13px] text-white/60">
            Pas encore de license. Souscris à Pro pour en générer une.
          </p>
        )}
      </section>

      <Link href="/download" className="mt-5 block rounded-2xl border-hairline bg-white/[0.02] p-7 hover:bg-white/[0.05]">
        <div className="font-mono text-[10px] uppercase tracking-ultra text-white/50">Téléchargement</div>
        <div className="mt-2 font-display text-[14px] font-bold tracking-widest2">→ Télécharger Beat Cash desktop</div>
      </Link>
    </main>
  );
}
