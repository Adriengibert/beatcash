import { useState, useEffect, type ReactNode } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Lock } from "lucide-react";
import { bridge } from "../lib/bridge";

let _cachedPro: boolean | null = null;
const subs = new Set<(p: boolean) => void>();

async function refreshPro() {
  const v = await bridge.isPro();
  _cachedPro = v;
  subs.forEach((cb) => cb(v));
}

export function usePro(): boolean {
  const [pro, setPro] = useState(_cachedPro ?? false);
  useEffect(() => {
    if (_cachedPro === null) refreshPro();
    const cb = (v: boolean) => setPro(v);
    subs.add(cb);
    return () => { subs.delete(cb); };
  }, []);
  return pro;
}

export function refreshProState() {
  void refreshPro();
}

export function ProBadge({ className = "" }: { className?: string }) {
  return (
    <span className={
      "inline-flex items-center gap-1 rounded-full border border-white/20 bg-white/10 px-2 py-0.5 font-mono text-[9px] font-bold uppercase tracking-ultra " + className
    }>
      <Lock className="size-2.5" /> PRO
    </span>
  );
}

/** Wrap les enfants : flou + overlay si plan FREE. */
export function ProGate({
  children,
  feature,
  onUpgrade,
}: {
  children: ReactNode;
  feature?: string;
  onUpgrade?: () => void;
}) {
  const pro = usePro();
  if (pro) return <>{children}</>;
  return (
    <div className="relative">
      <div className="pointer-events-none select-none opacity-40 blur-[2px]">{children}</div>
      <AnimatePresence>
        <motion.div
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3, ease: [0.22, 1.2, 0.36, 1] }}
          className="absolute inset-0 grid place-items-center"
        >
          <div className="rounded-2xl border-hairline-hi glass px-6 py-5 text-center shadow-glow-sm">
            <div className="flex items-center justify-center gap-2">
              <Lock className="size-3.5" />
              <span className="font-mono text-[10px] font-bold uppercase tracking-ultra text-white/90">
                {feature ? `${feature} · PRO` : "Feature PRO"}
              </span>
            </div>
            <button
              data-hover
              onClick={onUpgrade}
              className="mt-3 rounded-xl bg-white px-5 py-2 font-display text-[11px] font-bold tracking-widest2 text-black transition-transform hover:scale-[1.03]"
            >
              UPGRADE
            </button>
          </div>
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
