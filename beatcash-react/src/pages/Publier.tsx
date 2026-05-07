import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { ChevronDown, Play, FolderClock, BarChart3, CalendarClock } from "lucide-react";
import { YT, IG, TikTok as TT, Audiomack as AM } from "../components/BrandIcons";
import { Card } from "../components/Card";
import { Button } from "../components/Button";
import { Toggle } from "../components/Toggle";
import { Segmented } from "../components/Segmented";
import { Dropzone } from "../components/Dropzone";
import { StatusDot } from "../components/StatusDot";
import { Waveform } from "../components/Waveform";
import { ProGate, ProBadge, usePro } from "../components/ProGate";
import { bridge } from "../lib/bridge";

export function Publier() {
  const pro = usePro();
  const [src, setSrc] = useState<"video" | "mp3img">("video");
  const [filePath, setFilePath] = useState<string>("");
  const [fileLabel, setFileLabel] = useState<string>("");
  const [title, setTitle] = useState<string>("");
  const [yt, setYt] = useState(true);
  const [ig, setIg] = useState(true);
  const [tt, setTt] = useState(false);
  const [am, setAm] = useState(false);
  const [statut, setStatut] = useState("Public");
  const [cat, setCat] = useState("Music");
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState<"idle" | "running" | "done" | "error">("idle");
  const [resultMsg, setResultMsg] = useState<string>("");
  const [conns, setConns] = useState<{ youtube: boolean; instagram: boolean; tiktok: boolean }>({
    youtube: false, instagram: false, tiktok: false,
  });

  useEffect(() => {
    Promise.all([bridge.youtubeStatus(), bridge.instagramStatus(), bridge.tiktokStatus()])
      .then(([yt, ig, tt]) => setConns({
        youtube:   !!yt.connected,
        instagram: !!ig.connected,
        tiktok:    !!tt.connected,
      }))
      .catch(() => {});
  }, []);

  const targets = [
    yt && "youtube",
    ig && "instagram",
    tt && "tiktok",
    am && "audiomack",
  ].filter(Boolean) as string[];

  const launch = async () => {
    if (status === "running") return;
    if (!filePath) { setResultMsg("Choisis un fichier d'abord."); setStatus("error"); return; }
    if (targets.length === 0) { setResultMsg("Active au moins une plateforme."); setStatus("error"); return; }

    setStatus("running"); setProgress(5); setResultMsg("");
    const tick = setInterval(() => setProgress((p) => Math.min(95, p + 3)), 600);

    try {
      const res = await bridge.publish({
        file: filePath,
        title: title || fileLabel.replace(/\.[^.]+$/, "") || "Untitled beat",
        targets,
        yt_privacy: statut === "Public" ? "public" : statut === "Privé" ? "private" : "unlisted",
      });
      clearInterval(tick); setProgress(100);
      const lines = Object.entries(res.results || {}).map(
        ([k, v]) => `${k} : ${v.ok ? "✓" : "✗ " + (v.error || "échec")}`,
      );
      setResultMsg(lines.join(" · "));
      setStatus(Object.values(res.results || {}).every((v) => v.ok) ? "done" : "error");
    } catch (e: any) {
      clearInterval(tick);
      setStatus("error");
      setResultMsg(e.message || "Erreur inconnue");
    }
  };

  return (
    <div className="space-y-5">
      <PageHeader />

      <Card title="Connexions" delay={0.05}>
        <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
          <ConnRow Icon={YT} name="YouTube"   state={conns.youtube   ? "on" : "off"} hint={conns.youtube   ? "OAuth ✓" : "non connecté"} />
          <ConnRow Icon={IG} name="Instagram" state={conns.instagram ? "on" : "off"} hint={conns.instagram ? "session ✓" : "non connecté"} />
          <ConnRow Icon={TT} name="TikTok"    state={conns.tiktok    ? "on" : "off"} hint={conns.tiktok    ? "OAuth ✓" : "non connecté"} pro />
          <ConnRow Icon={AM} name="Audiomack" state="off" hint="à venir" pro />
        </div>
      </Card>

      <Card title="Source &amp; publication" delay={0.10}>
        <Segmented<typeof src>
          value={src}
          onChange={setSrc}
          options={[{ value: "video", label: "Vidéo MP4" }, { value: "mp3img", label: "MP3 + Image" }]}
        />

        <div className="mt-5">
          {src === "video" ? (
            <Dropzone
              kind="video"
              onPath={(p, lbl) => { setFilePath(p); setFileLabel(lbl); }}
            />
          ) : (
            <div className="grid grid-cols-2 gap-3">
              <Dropzone kind="audio" onPath={(p, lbl) => { setFilePath(p); setFileLabel(lbl); }} />
              <Dropzone kind="image" />
            </div>
          )}
        </div>

        <div className="mt-5">
          <label className="flex flex-col gap-1.5">
            <span className="font-mono text-[10px] font-bold uppercase tracking-ultra text-ink-70">Titre</span>
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder={fileLabel ? fileLabel.replace(/\.[^.]+$/, "") : "Mon nouveau beat"}
              className="rounded-xl border-hairline bg-black/40 px-4 py-3 text-[13px] text-ink-99 placeholder:text-ink-70 focus:border-white/40 focus:shadow-glow-sm focus:outline-none"
            />
          </label>
        </div>

        <div className="mt-5 grid grid-cols-2 gap-3">
          <TargetRow Icon={YT} label="YouTube"   on={yt} setOn={setYt} hint={yt ? "Vidéo publique"     : "Désactivé"} />
          <TargetRow Icon={IG} label="Instagram" on={ig} setOn={setIg} hint={ig ? "Reel · auto-format" : "Désactivé"} />
          <TargetRow Icon={TT} label="TikTok"    on={tt} setOn={setTt} hint={tt ? "Vertical · auto-format" : "Désactivé"} pro={!pro} />
          <TargetRow Icon={AM} label="Audiomack" on={am} setOn={setAm} hint={am ? "Auto-tags + cover" : "Désactivé"} pro={!pro} />
        </div>

        <div className="mt-5 grid grid-cols-2 gap-3">
          <Field label="Statut YouTube"   value={statut} setValue={setStatut} options={["Public", "Non répertorié", "Privé"]} />
          <Field label="Catégorie"        value={cat}    setValue={setCat}    options={["Music", "People & Blogs", "Entertainment"]} />
        </div>
      </Card>

      {filePath && (
        <Card title="Aperçu" delay={0.15}>
          <div className="flex items-center gap-5">
            <button
              data-hover
              className="grid size-14 place-items-center rounded-full bg-white text-ink-0 transition-transform hover:scale-105 active:scale-95"
            >
              <Play className="size-6 translate-x-[1px] fill-ink-0 stroke-ink-0" />
            </button>
            <div className="flex-1 min-w-0">
              <div className="truncate font-mono text-[12px] text-ink-90">{fileLabel || filePath}</div>
              <div className="mt-2"><Waveform bars={32} /></div>
            </div>
          </div>
        </Card>
      )}

      {/* Pro features grid — gated */}
      <div className="grid grid-cols-1 gap-5 md:grid-cols-3">
        <Card title="Watch folder" delay={0.20}>
          <ProGate feature="Watch folder">
            <div className="space-y-3">
              <div className="rounded-xl border-hairline bg-black/40 p-3 font-mono text-[11px]">
                <FolderClock className="mb-1 size-4 text-ink-90" />
                C:\Users\…\Beats\_publish_queue\
              </div>
              <Button variant="ghost" className="text-[11px]">Choisir le dossier</Button>
            </div>
          </ProGate>
        </Card>
        <Card title="Programmer" delay={0.22}>
          <ProGate feature="Scheduled posts">
            <div className="flex items-center gap-3">
              <CalendarClock className="size-4 text-ink-90" />
              <input
                type="datetime-local"
                className="flex-1 rounded-xl border-hairline bg-black/40 px-3 py-2 font-mono text-[12px] text-white focus:border-white/40 focus:outline-none"
              />
            </div>
          </ProGate>
        </Card>
        <Card title="Stats des derniers posts" delay={0.24}>
          <ProGate feature="Analytics">
            <div className="flex items-end gap-2 text-[11px] font-mono text-ink-80">
              <BarChart3 className="size-4" /> 12 publications · 4.2k vues · 38 likes
            </div>
          </ProGate>
        </Card>
      </div>

      <div className="space-y-3 pt-2">
        <PublishCTA progress={progress} status={status} onClick={launch} />
        <ProgressBar value={progress} status={status} />
        {resultMsg && (
          <motion.div
            initial={{ opacity: 0, y: 4 }} animate={{ opacity: 1, y: 0 }}
            className={
              "rounded-xl border px-4 py-3 font-mono text-[12px] " +
              (status === "error"
                ? "border-red-500/40 bg-red-500/5 text-red-300"
                : "border-white/15 bg-white/[0.04] text-ink-99")
            }>
            {resultMsg}
          </motion.div>
        )}
      </div>
    </div>
  );
}

/* ─── helpers ─────────────────────────────────────────── */

function PageHeader() {
  const pro = usePro();
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6 }}
      className="relative mb-6 pl-5"
    >
      <div className="absolute left-0 top-1 bottom-2 w-[3px] rounded-full bg-gradient-to-b from-white via-white/60 to-transparent shadow-glow-sm" />
      <div className="flex items-center gap-3">
        <h1 className="font-display text-[26px] font-bold tracking-widest2 text-glow leading-none">PUBLIER</h1>
        {pro
          ? <span className="rounded-full border border-white/30 bg-white px-2.5 py-0.5 font-mono text-[10px] font-bold uppercase tracking-ultra text-black shadow-glow-sm">PRO</span>
          : <ProBadge />}
      </div>
      <p className="mt-2 text-[13px] text-ink-80">
        Publie en une fois sur YouTube, Instagram, TikTok, Audiomack — formats adaptés automatiquement.
      </p>
    </motion.div>
  );
}

function ConnRow({ Icon, name, state, hint, pro }: { Icon: any; name: string; state: "on" | "off" | "wait"; hint: string; pro?: boolean }) {
  return (
    <div data-hover className="group flex items-center gap-3 rounded-xl border-hairline bg-white/[0.02] p-3 transition-colors hover:border-white/15 hover:bg-white/[0.05]">
      <div className="grid size-10 place-items-center rounded-lg border-hairline bg-white/[0.03]">
        <Icon className="size-4 stroke-[2]" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 text-[13px] font-semibold">
          {name}
          <StatusDot state={state} />
          {pro && <ProBadge />}
        </div>
        <div className="font-mono text-[10.5px] text-ink-70">{hint}</div>
      </div>
    </div>
  );
}

function TargetRow({ Icon, label, on, setOn, hint, pro }: { Icon: any; label: string; on: boolean; setOn: (v: boolean) => void; hint: string; pro?: boolean }) {
  return (
    <div data-hover className={
      "flex items-center justify-between rounded-xl border-hairline bg-white/[0.02] px-4 py-3 transition-colors hover:bg-white/[0.05] hover:border-white/15 " +
      (pro ? "opacity-70" : "")
    }>
      <div className="flex items-center gap-3">
        <Icon className="size-4 opacity-90" />
        <div>
          <div className="flex items-center gap-2 text-[13px] font-semibold">
            {label}
            {pro && <ProBadge />}
          </div>
          <div className="font-mono text-[10.5px] text-ink-70">{hint}</div>
        </div>
      </div>
      <Toggle on={on && !pro} onChange={(v) => !pro && setOn(v)} />
    </div>
  );
}

function Field({ label, value, setValue, options }: { label: string; value: string; setValue: (v: string) => void; options: string[] }) {
  return (
    <label className="flex flex-col gap-1.5">
      <span className="font-mono text-[10px] font-bold uppercase tracking-ultra text-ink-70">{label}</span>
      <div data-hover className="relative">
        <select
          value={value}
          onChange={(e) => setValue(e.target.value)}
          className="w-full appearance-none rounded-xl border-hairline bg-black/40 px-4 py-3 pr-10 font-mono text-[12.5px] text-ink-99 transition-all focus:border-white/40 focus:shadow-glow-sm focus:outline-none"
        >
          {options.map((o) => <option key={o}>{o}</option>)}
        </select>
        <ChevronDown className="pointer-events-none absolute right-3 top-1/2 size-4 -translate-y-1/2 stroke-[2] text-ink-80" />
      </div>
    </label>
  );
}

function PublishCTA({ status, onClick }: { progress: number; status: "idle" | "running" | "done" | "error"; onClick: () => void }) {
  return (
    <motion.button
      data-hover
      onClick={onClick}
      whileHover={{ y: -2 }}
      whileTap={{ scale: 0.99 }}
      className="group relative w-full overflow-hidden rounded-2xl bg-white px-8 py-5 text-ink-0 shadow-glow-lg"
    >
      <span className="pointer-events-none absolute inset-0">
        <span className="absolute inset-0 bg-gradient-to-r from-white via-ink-95 to-white opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
        <span className="absolute -inset-px rounded-2xl bg-[conic-gradient(from_var(--a,0deg),rgba(255,255,255,0.5),transparent_30%,rgba(255,255,255,0.6),transparent_70%,rgba(255,255,255,0.5))] opacity-0 blur-[6px] transition-opacity duration-300 group-hover:opacity-100 group-hover:animate-spin360" />
      </span>
      <span className="relative z-10 flex items-center justify-center gap-3 font-display text-[14px] font-bold tracking-ultra">
        {status === "running" ? "PUBLICATION EN COURS…"
          : status === "done"  ? "PUBLIÉ ✓"
          : status === "error" ? "RÉESSAYER"
          : "▶ PUBLIER MAINTENANT"}
      </span>
    </motion.button>
  );
}

function ProgressBar({ value, status }: { value: number; status: "idle" | "running" | "done" | "error" }) {
  return (
    <div className="flex items-center gap-3 px-1 font-mono text-[11px] text-ink-80">
      <span className="w-28">
        {status === "idle"    && "● Prêt"}
        {status === "running" && "● Upload"}
        {status === "done"    && "● Terminé"}
        {status === "error"   && "● Erreur"}
      </span>
      <div className="relative h-[3px] flex-1 overflow-hidden rounded-full bg-white/[0.06]">
        <motion.div
          animate={{ width: `${value}%` }}
          transition={{ duration: 0.4, ease: [0.22, 1.2, 0.36, 1] }}
          className="absolute inset-y-0 left-0 rounded-full bg-gradient-to-r from-white/60 via-white to-white/80 shadow-glow-sm"
        />
        {status === "running" && (
          <span className="absolute inset-0 animate-shimmer bg-[linear-gradient(110deg,transparent_30%,rgba(255,255,255,0.15)_50%,transparent_70%)] bg-[length:200%_100%]" />
        )}
      </div>
      <span className="w-12 text-right tabular-nums">{value}%</span>
    </div>
  );
}
