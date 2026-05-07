"use client";
import { useState } from "react";

export function PricingCard({
  name, price, period, features, plan, highlight,
}: {
  name: string;
  price: string;
  period: string;
  features: string[];
  plan?: "pro_monthly" | "pro_yearly";
  highlight?: boolean;
}) {
  const [busy, setBusy] = useState(false);
  const [err,  setErr]  = useState("");

  const subscribe = async () => {
    if (!plan) return;
    setBusy(true); setErr("");
    try {
      const r = await fetch("/api/checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ plan }),
      });
      const data = await r.json();
      if (!r.ok) throw new Error(data.error || "fail");
      window.location.href = data.url;
    } catch (e: any) {
      setErr(e.message);
      setBusy(false);
    }
  };

  return (
    <div className={
      "relative rounded-2xl p-7 " +
      (highlight
        ? "border-hairline-hi bg-white text-black shadow-[0_0_60px_rgba(255,255,255,0.18)]"
        : "border-hairline glass")
    }>
      {highlight && (
        <div className="absolute -top-3 left-7 rounded-full border-hairline-hi bg-black px-3 py-1 font-mono text-[10px] tracking-ultra uppercase text-white">
          Recommandé
        </div>
      )}
      <div className="font-display text-[12px] font-bold tracking-ultra uppercase">{name}</div>
      <div className="mt-3 flex items-baseline gap-2">
        <span className="font-display text-4xl font-bold tracking-tight">{price}</span>
        <span className="text-sm opacity-60">/ {period}</span>
      </div>
      <ul className="mt-6 space-y-2.5">
        {features.map((f) => (
          <li key={f} className="flex items-start gap-3 text-[13px]">
            <span className={"mt-1 size-1.5 rounded-full shrink-0 " + (highlight ? "bg-black" : "bg-white")} />
            <span className={highlight ? "text-black/80" : "text-white/80"}>{f}</span>
          </li>
        ))}
      </ul>
      {plan ? (
        <button
          onClick={subscribe}
          disabled={busy}
          className={
            "mt-7 block w-full rounded-xl px-5 py-3 font-display text-[12px] font-bold tracking-widest2 transition-transform hover:scale-[1.02] active:scale-95 " +
            (highlight
              ? "bg-black text-white"
              : "border-hairline-hi bg-white/[0.04] text-white hover:bg-white/[0.08]")
          }
        >
          {busy ? "REDIRECTION…" : "SOUSCRIRE"}
        </button>
      ) : (
        <a
          href="/download"
          className="mt-7 block w-full rounded-xl border-hairline bg-white/[0.02] px-5 py-3 text-center font-display text-[12px] font-bold tracking-widest2 hover:bg-white/[0.05]"
        >
          TÉLÉCHARGER GRATUIT
        </a>
      )}
      {err && <div className="mt-3 text-xs text-red-400">{err}</div>}
    </div>
  );
}
