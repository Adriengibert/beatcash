"use client";
import { useState } from "react";

export function EmailCapture({ source = "free_pack" }: { source?: string }) {
  const [email, setEmail] = useState("");
  const [busy, setBusy]   = useState(false);
  const [done, setDone]   = useState(false);
  const [err,  setErr]    = useState("");

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true); setErr("");
    try {
      const r = await fetch("/api/email/subscribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, source }),
      });
      if (!r.ok) throw new Error((await r.json()).error || "fail");
      setDone(true);
    } catch (e: any) {
      setErr(e.message);
    } finally {
      setBusy(false);
    }
  };

  if (done) {
    return (
      <div className="rounded-xl border-hairline-hi bg-white/[0.04] px-5 py-4 text-center">
        <div className="font-mono text-[11px] tracking-ultra uppercase text-white/60">— OK —</div>
        <div className="mt-2 text-sm">Check ta boîte mail. Le lien du pack arrive dans ~30s.</div>
      </div>
    );
  }

  return (
    <form onSubmit={submit} className="flex flex-col gap-2 sm:flex-row">
      <input
        type="email"
        required
        placeholder="ton@email.com"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        className="flex-1 rounded-xl border-hairline bg-black/40 px-4 py-3 font-mono text-sm placeholder:text-white/30 focus:border-white/40 focus:outline-none"
      />
      <button
        type="submit"
        disabled={busy}
        className="rounded-xl bg-white px-6 py-3 font-display text-[13px] font-bold tracking-widest2 text-black transition-transform hover:scale-[1.02] active:scale-95 disabled:opacity-60"
      >
        {busy ? "ENVOI…" : "RÉCUPÉRER LE PACK"}
      </button>
      {err && <div className="text-xs text-red-400 sm:absolute sm:-bottom-6">{err}</div>}
    </form>
  );
}
