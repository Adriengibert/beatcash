"use client";
import { useState } from "react";
import Link from "next/link";
import { browserSupabase } from "@/lib/supabase";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [busy, setBusy] = useState(false);
  const [sent, setSent] = useState(false);
  const [err, setErr] = useState("");

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true); setErr("");
    const supa = browserSupabase();
    const { error } = await supa.auth.signInWithOtp({
      email,
      options: { emailRedirectTo: `${window.location.origin}/account` },
    });
    setBusy(false);
    if (error) setErr(error.message);
    else setSent(true);
  };

  return (
    <main className="grid flex-1 place-items-center px-6">
      <div className="w-full max-w-sm">
        <Link href="/" className="mb-10 flex items-baseline justify-center gap-2">
          <span className="font-display text-[26px] font-bold text-glow leading-none">$</span>
          <span className="font-display text-[15px] font-bold tracking-widest2">BEATCASH</span>
        </Link>

        <div className="rounded-2xl border-hairline glass p-7">
          <h1 className="font-display text-xl font-bold tracking-widest2">CONNEXION</h1>
          <p className="mt-2 text-sm text-white/70">
            On t'envoie un lien magique. Pas de mot de passe.
          </p>

          {sent ? (
            <div className="mt-6 rounded-xl border-hairline-hi bg-white/[0.04] p-4 text-center text-sm">
              <div className="font-mono text-[10px] uppercase tracking-ultra text-white/60">— OK —</div>
              <div className="mt-2">Check ta boîte. Le lien expire dans 1h.</div>
            </div>
          ) : (
            <form onSubmit={submit} className="mt-6 space-y-3">
              <input
                type="email" required value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="ton@email.com"
                className="w-full rounded-xl border-hairline bg-black/40 px-4 py-3 font-mono text-sm placeholder:text-white/30 focus:border-white/40 focus:outline-none"
              />
              <button
                type="submit" disabled={busy}
                className="w-full rounded-xl bg-white px-5 py-3 font-display text-[12px] font-bold tracking-widest2 text-black hover:scale-[1.02] active:scale-95 transition-transform disabled:opacity-60"
              >
                {busy ? "ENVOI…" : "RECEVOIR LE LIEN"}
              </button>
              {err && <div className="text-xs text-red-400">{err}</div>}
            </form>
          )}
        </div>
      </div>
    </main>
  );
}
