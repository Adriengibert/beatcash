import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Logo } from "./components/Logo";
import { Tabs, type TabKey } from "./components/Tabs";
import { Cursor } from "./components/Cursor";
import { Publier } from "./pages/Publier";
import { Suivi } from "./pages/Suivi";
import { Connexions } from "./pages/Connexions";
import { SEO } from "./pages/SEO";

export default function App() {
  const [tab, setTab] = useState<TabKey>("publier");

  // Permet aux pages enfants d'appeler `window.__beatcashGoto("publier")` (CTA empty state, etc.)
  useEffect(() => {
    (window as any).__beatcashGoto = (k: TabKey) => setTab(k);
    return () => { delete (window as any).__beatcashGoto; };
  }, []);

  return (
    <div className="relative min-h-screen overflow-hidden bg-ink-0 text-ink-99">
      {/* radial ambiance */}
      <div className="pointer-events-none fixed inset-0 z-0">
        <div className="absolute inset-0 grid-bg mask-fade opacity-60" />
        <div className="absolute -left-32 top-0 size-[60vmax] rounded-full bg-white/[0.025] blur-3xl" />
        <div className="absolute -right-32 bottom-0 size-[55vmax] rounded-full bg-white/[0.018] blur-3xl" />
      </div>

      <Cursor />
      <div className="spotlight" aria-hidden />

      {/* nav */}
      <header className="relative z-10 flex items-center gap-10 px-9 py-5 bg-ink-5/80 backdrop-blur-sm border-b border-white/[0.05]">
        <Logo />
        <Tabs active={tab} onChange={setTab} />
        <div className="ml-auto flex items-center gap-3">
          <span className="font-mono text-[11px] uppercase tracking-widest2 text-ink-90">
            v 0.3 · beta
          </span>
          <span className="size-1.5 rounded-full bg-white" />
        </div>
      </header>

      {/* page */}
      <main className="relative z-10 mx-auto max-w-[1200px] px-9 pb-24 pt-10">
        <AnimatePresence mode="wait">
          <motion.div
            key={tab}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.28, ease: [0.22, 1.2, 0.36, 1] }}
          >
            {tab === "publier"    && <Publier />}
            {tab === "suivi"      && <Suivi />}
            {tab === "connexions" && <Connexions />}
            {tab === "seo"        && <SEO />}
          </motion.div>
        </AnimatePresence>
      </main>

      {/* bottom edge marquee */}
      <footer className="pointer-events-none fixed inset-x-0 bottom-0 z-10 overflow-hidden border-t border-white/[0.05] bg-black/60 py-2 backdrop-blur-md">
        <div className="flex animate-marquee gap-12 whitespace-nowrap font-mono text-[10px] uppercase tracking-ultra text-ink-70">
          {Array.from({ length: 2 }).map((_, k) => (
            <span key={k} className="flex shrink-0 gap-12">
              <span>$ BEATCASH</span>
              <span>· DESKTOP UPLOAD STUDIO ·</span>
              <span>YOUTUBE</span>
              <span>·</span>
              <span>INSTAGRAM</span>
              <span>·</span>
              <span>AUDIOMACK</span>
              <span>·</span>
              <span>TIKTOK</span>
              <span>·</span>
              <span>BUILT FOR PRODUCERS</span>
              <span>·</span>
              <span>OFFLINE FIRST</span>
              <span>·</span>
            </span>
          ))}
        </div>
      </footer>
    </div>
  );
}
