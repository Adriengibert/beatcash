import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { Eye, DollarSign, TrendingUp, Music, ArrowUpRight, LineChart } from "lucide-react";
import { YT, IG, TikTok as TT, Audiomack as AM } from "../components/BrandIcons";
import { Card } from "../components/Card";
import { Waveform } from "../components/Waveform";

type Plat = "youtube" | "instagram" | "tiktok" | "audiomack";

interface BeatRow {
  id: string;
  title: string;
  date: string;
  platforms: Plat[];
  views: number;
  revenue: number;
  trend: number;
}

const PLAT_ICON: Record<Plat, any> = { youtube: YT, instagram: IG, tiktok: TT, audiomack: AM };

export function Suivi() {
  const [range, setRange] = useState<"7j" | "30j" | "tout">("30j");
  const [beats, setBeats] = useState<BeatRow[]>([]);

  // Plus tard : remplacer par bridge.fetchStats(range) côté Python
  useEffect(() => {
    setBeats([]);
  }, [range]);

  const totals = useMemo(() => {
    const v = beats.reduce((s, b) => s + b.views, 0);
    const r = beats.reduce((s, b) => s + b.revenue, 0);
    const avg = beats.length ? beats.reduce((s, b) => s + b.trend, 0) / beats.length : 0;
    return { views: v, revenue: r, trend: avg, count: beats.length };
  }, [beats]);

  const max = beats.length ? Math.max(...beats.map((b) => b.views)) : 1;
  const empty = beats.length === 0;

  return (
    <div className="space-y-5">
      <Header range={range} setRange={setRange} />

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <Metric Icon={Eye}        label="Vues totales"  value={empty ? "—" : fmtN(totals.views)}                           trend={empty ? undefined : totals.trend} delay={0.05} />
        <Metric Icon={DollarSign} label="Revenu estimé" value={empty ? "—" : `${totals.revenue.toFixed(2)} €`}             trend={empty ? undefined : totals.trend} delay={0.10} />
        <Metric Icon={Music}      label="Beats publiés" value={String(totals.count)}                                       delay={0.15} />
      </div>

      {empty ? (
        <EmptyState />
      ) : (
        <Card title={`Tes ${beats.length} derniers beats`} delay={0.20}>
          <div className="space-y-3">
            {beats.map((b, i) => <BeatRowItem key={b.id} b={b} max={max} delay={i * 0.04} />)}
          </div>
        </Card>
      )}

      <p className="px-1 font-mono text-[11px] text-ink-80">
        Stats agrégées : YouTube Analytics + Instagram Insights + TikTok Reports.
        Mises à jour toutes les 6 h. Revenu estimé selon les CPM publics.
      </p>
    </div>
  );
}

/* ─── helpers ─────────────────────────────────────────── */

function Header({ range, setRange }: { range: "7j" | "30j" | "tout"; setRange: (r: any) => void }) {
  return (
    <motion.div
      initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.5 }}
      className="relative mb-6 flex items-center gap-3 pl-5"
    >
      <div className="absolute left-0 top-1 bottom-2 w-[3px] rounded-full bg-gradient-to-b from-white via-white/60 to-transparent" />
      <h1 className="font-display text-[26px] font-bold tracking-widest2 text-glow leading-none">SUIVI</h1>
      <p className="ml-4 hidden text-[14px] text-ink-90 sm:block">Vues, revenu et performance par beat.</p>
      <div className="ml-auto inline-flex rounded-full border-hairline bg-white/[0.03] p-1">
        {(["7j","30j","tout"] as const).map((r) => {
          const active = r === range;
          return (
            <button
              key={r}
              onClick={() => setRange(r)}
              className={
                "rounded-full px-3.5 py-1.5 font-mono text-[11px] font-bold uppercase tracking-widest2 transition-colors " +
                (active ? "bg-white text-black" : "text-ink-90 hover:text-white")
              }
            >{r}</button>
          );
        })}
      </div>
    </motion.div>
  );
}

function Metric({
  Icon, label, value, trend, delay,
}: { Icon: any; label: string; value: string; trend?: number; delay?: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay, ease: [0.22,1.2,0.36,1] }}
      className="gradient-border glass relative overflow-hidden rounded-2xl p-5"
    >
      <div className="flex items-center gap-3">
        <div className="grid size-10 place-items-center rounded-xl border-hairline-hi bg-white/[0.04]">
          <Icon className="size-4 stroke-[1.8]" />
        </div>
        <div className="font-mono text-[11px] font-bold uppercase tracking-widest2 text-ink-90">{label}</div>
      </div>
      <div className="mt-4 flex items-end justify-between">
        <div className="font-display text-[28px] font-bold tracking-tight text-glow leading-none">{value}</div>
        {typeof trend === "number" && (
          <div className={
            "flex items-center gap-1 font-mono text-[12px] font-bold " +
            (trend >= 0 ? "text-white" : "text-ink-90")
          }>
            <TrendingUp className={"size-3 " + (trend >= 0 ? "" : "rotate-180")} />
            {trend >= 0 ? "+" : ""}{trend.toFixed(0)}%
          </div>
        )}
      </div>
    </motion.div>
  );
}

function EmptyState() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: [0.22,1.2,0.36,1] }}
      className="gradient-border glass relative overflow-hidden rounded-2xl p-14 text-center"
    >
      <div className="mx-auto grid size-14 place-items-center rounded-2xl border-hairline-hi bg-white/[0.04]">
        <LineChart className="size-6 stroke-[1.6] text-ink-90" />
      </div>
      <h3 className="mt-5 font-display text-[16px] font-bold uppercase tracking-widest2">Pas encore de beats</h3>
      <p className="mx-auto mt-3 max-w-md text-[14px] text-ink-90 leading-relaxed">
        Les vues, le revenu et les tendances de tes beats apparaîtront ici dès que tu auras publié.
      </p>
      <a
        href="#"
        onClick={(e) => { e.preventDefault(); (window as any).__beatcashGoto?.("publier"); }}
        className="mt-7 inline-flex items-center gap-2 rounded-xl bg-white px-6 py-3 font-display text-[12px] font-bold tracking-widest2 text-black transition-transform hover:scale-[1.03]"
      >
        ▶ PUBLIER MON PREMIER BEAT
      </a>
    </motion.div>
  );
}

function BeatRowItem({ b, max, delay }: { b: BeatRow; max: number; delay: number }) {
  const pct = Math.round((b.views / max) * 100);
  return (
    <motion.div
      initial={{ opacity: 0, x: -8 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.35, delay, ease: [0.22,1.2,0.36,1] }}
      className="group relative flex items-center gap-5 rounded-xl border-hairline bg-white/[0.02] p-4 transition-colors hover:border-white/15 hover:bg-white/[0.05]"
    >
      <div className="hidden w-20 shrink-0 sm:block">
        <Waveform bars={20} animate={false} />
      </div>

      <div className="min-w-0 flex-1">
        <div className="text-[14px] font-semibold text-ink-99">{b.title}</div>
        <div className="mt-1 flex items-center gap-3 font-mono text-[11px] text-ink-90">
          <span>{b.date}</span>
          <span className="opacity-40">·</span>
          <span className="flex items-center gap-1.5">
            {b.platforms.map((p) => {
              const I = PLAT_ICON[p];
              return <I key={p} className="size-3 opacity-90" />;
            })}
          </span>
        </div>

        <div className="mt-3 h-[3px] w-full overflow-hidden rounded-full bg-white/5">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${pct}%` }}
            transition={{ duration: 0.6, delay: delay + 0.1, ease: [0.22,1.2,0.36,1] }}
            className="h-full rounded-full bg-gradient-to-r from-white/50 via-white to-white/80"
          />
        </div>
      </div>

      <div className="flex shrink-0 items-end gap-6 text-right">
        <Stat label="vues" value={fmtN(b.views)} />
        <Stat label="€"    value={b.revenue.toFixed(2)} />
        <div className="hidden sm:block">
          <div className="font-mono text-[11px] uppercase tracking-widest2 text-ink-90">7j</div>
          <div className={
            "flex items-center gap-1 font-mono text-[13px] font-bold leading-none " +
            (b.trend >= 0 ? "text-white" : "text-ink-90")
          }>
            <TrendingUp className={"size-3 " + (b.trend >= 0 ? "" : "rotate-180")} />
            {b.trend >= 0 ? "+" : ""}{b.trend}%
          </div>
        </div>
      </div>

      <ArrowUpRight className="size-4 shrink-0 text-ink-90 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5 group-hover:text-white" />
    </motion.div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="font-mono text-[11px] uppercase tracking-widest2 text-ink-90">{label}</div>
      <div className="font-display text-[18px] font-bold tracking-tight text-glow leading-none">{value}</div>
    </div>
  );
}

function fmtN(n: number): string {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + "M";
  if (n >= 1_000)     return (n / 1_000).toFixed(n >= 10_000 ? 0 : 1) + "k";
  return String(n);
}
