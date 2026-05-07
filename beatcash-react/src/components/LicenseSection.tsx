import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { KeyRound, Check, X, RefreshCw } from "lucide-react";
import { bridge } from "../lib/bridge";
import { refreshProState } from "./ProGate";

export function LicenseSection() {
  const [status, setStatus] = useState<{
    plan: "FREE" | "PRO";
    key: string | null;
    valid_until: number | null;
    online: boolean;
    needs_recheck?: boolean;
  } | null>(null);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState("");

  const reload = async () => {
    try { setStatus(await bridge.licenseStatus()); } catch {}
  };

  useEffect(() => { reload(); }, []);

  const activate = async () => {
    if (!input.trim()) return;
    setBusy(true); setMsg("");
    try {
      const r = await bridge.licenseActivate(input.trim());
      if (r.ok) {
        setMsg("✓ License activée. Plan : PRO.");
        setInput("");
        await reload();
        refreshProState();
      } else {
        setMsg("✗ " + (r.error || "Échec"));
      }
    } catch (e: any) {
      setMsg("✗ " + e.message);
    } finally {
      setBusy(false);
    }
  };

  const recheck = async () => {
    setBusy(true); setMsg("");
    try {
      await bridge.licenseRecheck();
      await reload();
      refreshProState();
      setMsg("✓ Vérifié.");
    } catch (e: any) {
      setMsg("✗ " + e.message);
    } finally {
      setBusy(false);
    }
  };

  const deactivate = async () => {
    if (!confirm("Désactiver la license sur cet appareil ?")) return;
    await bridge.licenseDeactivate();
    await reload();
    refreshProState();
  };

  const isPro = status?.plan === "PRO";

  return (
    <motion.section
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.1, ease: [0.22, 1.2, 0.36, 1] }}
      className="gradient-border glass relative rounded-2xl p-6"
    >
      <div className="mb-5 flex items-center gap-3">
        <KeyRound className="size-4" />
        <h2 className="font-display text-[12px] font-bold uppercase tracking-ultra">License</h2>
        <span className={
          "ml-auto rounded-full border px-3 py-1 font-mono text-[10px] font-bold uppercase tracking-ultra " +
          (isPro
            ? "border-white/30 bg-white text-black shadow-glow-sm"
            : "border-white/15 bg-white/[0.04] text-white/70")
        }>
          {status?.plan || "—"}
        </span>
      </div>

      {status?.key ? (
        <div className="space-y-4">
          <div className="rounded-xl border-hairline bg-black/40 p-4">
            <div className="font-mono text-[10px] uppercase tracking-ultra text-white/50">Key</div>
            <div className="mt-1 select-all font-mono text-[15px] tracking-widest text-white">
              {status.key}
            </div>
            <div className="mt-3 grid grid-cols-2 gap-3 font-mono text-[11px]">
              <div>
                <div className="text-white/50">État</div>
                <div className={"mt-1 flex items-center gap-1.5 " + (status.online ? "text-white" : "text-white/60")}>
                  {status.online
                    ? <><Check className="size-3" /> Validé en ligne</>
                    : <><X     className="size-3" /> Hors-ligne / expiré</>}
                </div>
              </div>
              <div>
                <div className="text-white/50">Cache jusqu'à</div>
                <div className="mt-1">
                  {status.valid_until ? new Date(status.valid_until).toLocaleDateString("fr-FR") : "—"}
                </div>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            <button
              data-hover onClick={recheck} disabled={busy}
              className="inline-flex items-center gap-2 rounded-xl border-hairline bg-white/[0.04] px-4 py-2 text-[12px] font-semibold hover:bg-white/[0.08] disabled:opacity-60"
            >
              <RefreshCw className={"size-3.5 " + (busy ? "animate-spin" : "")} />
              Re-vérifier
            </button>
            <button
              data-hover onClick={deactivate}
              className="rounded-xl px-4 py-2 text-[12px] font-semibold text-white/70 hover:bg-white/[0.04] hover:text-white"
            >
              Désactiver
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-3">
          <p className="text-[12px] text-ink-80">
            Tu as une clé Pro <span className="font-mono">BC-XXXX-XXXX-XXXX-XXXX</span> ?
            Colle-la ici. Sinon récupère-la sur ton compte beatcash.app.
          </p>
          <div className="flex gap-2">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value.toUpperCase())}
              placeholder="BC-XXXX-XXXX-XXXX-XXXX"
              data-hover
              maxLength={23}
              className="flex-1 rounded-xl border-hairline bg-black/40 px-4 py-2.5 font-mono text-[13px] tracking-widest text-white placeholder:text-white/30 focus:border-white/40 focus:shadow-glow-sm focus:outline-none"
            />
            <button
              data-hover onClick={activate} disabled={busy || !input.trim()}
              className="rounded-xl bg-white px-5 py-2.5 font-display text-[11px] font-bold tracking-widest2 text-black transition-transform hover:scale-[1.02] disabled:opacity-50"
            >
              {busy ? "…" : "ACTIVER"}
            </button>
          </div>
        </div>
      )}

      {msg && (
        <div className={"mt-4 font-mono text-[11px] " + (msg.startsWith("✓") ? "text-white" : "text-red-400")}>
          {msg}
        </div>
      )}
    </motion.section>
  );
}
