import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Plug, ShieldCheck } from "lucide-react";
import { YT, IG, TikTok, Audiomack } from "../components/BrandIcons";
import { Card } from "../components/Card";
import { Button } from "../components/Button";
import { StatusDot } from "../components/StatusDot";
import { LicenseSection } from "../components/LicenseSection";
import { ProBadge, usePro } from "../components/ProGate";
import { bridge } from "../lib/bridge";

type PlatKey = "youtube" | "instagram" | "tiktok" | "audiomack";
type PlatState = "on" | "off" | "wait";

interface PlatConfig {
  key: PlatKey;
  Icon: any;
  name: string;
  subtitle: string;
  pro?: boolean;
  comingSoon?: boolean;
}

const platforms: PlatConfig[] = [
  { key: "youtube",   Icon: YT,        name: "YouTube",   subtitle: "OAuth Google · Data API v3" },
  { key: "instagram", Icon: IG,        name: "Instagram", subtitle: "Session cookie · auto-format Reels" },
  { key: "tiktok",    Icon: TikTok,    name: "TikTok",    subtitle: "Content Posting API · vertical", pro: true },
  { key: "audiomack", Icon: Audiomack, name: "Audiomack", subtitle: "API · catalog + plays sync", pro: true, comingSoon: true },
];

export function Connexions() {
  const [states, setStates] = useState<Record<PlatKey, { state: PlatState; meta?: string; busy?: boolean; error?: string }>>({
    youtube:   { state: "off", meta: "non connecté" },
    instagram: { state: "off", meta: "non connecté" },
    tiktok:    { state: "off", meta: "non connecté" },
    audiomack: { state: "off", meta: "à venir" },
  });

  const refresh = async () => {
    try {
      const [yt, ig, tt] = await Promise.all([
        bridge.youtubeStatus(),
        bridge.instagramStatus(),
        bridge.tiktokStatus(),
      ]);
      setStates((s) => ({
        ...s,
        youtube:   yt.connected ? { state: "on",  meta: yt.cached ? "token caché" : "connecté" }
                                : { state: "off", meta: yt.error ?? "non connecté" },
        instagram: ig.connected ? { state: "on",  meta: ig.cached ? "session cachée" : "connecté" }
                                : { state: "off", meta: ig.error ?? "non connecté" },
        tiktok:    tt.connected
          ? { state: tt.expired ? "wait" : "on", meta: tt.expired ? "token expiré" : "connecté" }
          : { state: "off", meta: tt.error ?? "non connecté" },
      }));
    } catch {}
  };

  useEffect(() => { refresh(); }, []);

  const connect = async (key: PlatKey) => {
    setStates((s) => ({ ...s, [key]: { ...s[key], busy: true, error: undefined } }));
    try {
      let r: { ok: boolean; error?: string };
      if (key === "tiktok")        r = await bridge.tiktokConnect();
      else if (key === "youtube")  r = await bridge.connectYoutube();
      else if (key === "instagram") {
        const login    = prompt("Login Instagram :") || "";
        if (!login) { setStates((s) => ({ ...s, [key]: { state: "off", meta: "annulé" } })); return; }
        const password = prompt("Mot de passe Instagram :\n(stocké uniquement en local)") || "";
        if (!password) { setStates((s) => ({ ...s, [key]: { state: "off", meta: "annulé" } })); return; }
        const code     = prompt("Code 2FA (vide si pas de 2FA) :") || "";
        r = await bridge.connectInstagram(login, password, code);
      }
      else r = { ok: false, error: "À venir" };
      setStates((s) => ({
        ...s,
        [key]: r.ok
          ? { state: "on", meta: "connecté" }
          : { state: "off", meta: r.error || "échec", error: r.error },
      }));
      refresh();
    } catch (e: any) {
      setStates((s) => ({ ...s, [key]: { ...s[key], state: "off", error: e.message, busy: false } }));
    }
  };

  const disconnect = async (key: PlatKey) => {
    if (key === "tiktok")        await bridge.tiktokDisconnect();
    else if (key === "youtube")  await bridge.disconnectYoutube();
    else if (key === "instagram") await bridge.disconnectInstagram();
    setStates((s) => ({ ...s, [key]: { state: "off", meta: "déconnecté" } }));
  };

  return (
    <div className="space-y-5">
      <Header />

      <Card title="Plateformes" delay={0.05}>
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
          {platforms.map((p, i) => (
            <PlatCard
              key={p.key}
              p={p}
              status={states[p.key]}
              onConnect={() => connect(p.key)}
              onDisconnect={() => disconnect(p.key)}
              delay={i * 0.05}
            />
          ))}
        </div>
      </Card>

      <LicenseSection />

      <Card title="Sécurité &amp; sessions" delay={0.20}>
        <ul className="divide-y divide-white/[0.06] font-mono text-[12px]">
          <Row Icon={ShieldCheck} label="Token YouTube"     value={states.youtube.state === "on"   ? "OAuth · refresh ok" : "—"} />
          <Row Icon={Plug}        label="Session Instagram" value={states.instagram.state === "on" ? "active" : "—"} />
          <Row Icon={ShieldCheck} label="Session TikTok"    value={states.tiktok.state === "on"    ? "OAuth · refresh ok" : "—"} />
          <Row Icon={ShieldCheck} label="Stockage local"    value="C:\\Users\\…\\BeatCash\\" />
        </ul>
      </Card>
    </div>
  );
}

function Header() {
  return (
    <motion.div
      initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.6 }}
      className="relative mb-6 pl-5"
    >
      <div className="absolute left-0 top-1 bottom-2 w-[3px] rounded-full bg-gradient-to-b from-white via-white/60 to-transparent shadow-glow-sm" />
      <h1 className="font-display text-[26px] font-bold tracking-widest2 text-glow leading-none">CONNEXIONS</h1>
      <p className="mt-2 text-[13px] text-ink-80">Tes comptes connectés. Tokens stockés en local, jamais transmis.</p>
    </motion.div>
  );
}

function PlatCard({
  p, status, onConnect, onDisconnect, delay,
}: {
  p: PlatConfig;
  status: { state: PlatState; meta?: string; busy?: boolean; error?: string };
  onConnect: () => void;
  onDisconnect: () => void;
  delay: number;
}) {
  const pro = usePro();
  const proLocked = !!p.pro && !pro;
  const disabled = p.comingSoon || proLocked;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay, ease: [0.22, 1.2, 0.36, 1] }}
      data-hover
      className={
        "group relative overflow-hidden rounded-xl border-hairline bg-white/[0.02] p-5 transition-colors " +
        (disabled ? "" : "hover:border-white/15 hover:bg-white/[0.05]")
      }
    >
      <span className="pointer-events-none absolute -right-16 -top-16 size-48 rounded-full bg-white/[0.025] blur-2xl transition-opacity duration-500 group-hover:bg-white/[0.06]" />
      <div className="flex items-start gap-4">
        <div className="grid size-12 place-items-center rounded-xl border-hairline-hi bg-white/[0.04]">
          <p.Icon className="size-5 stroke-[1.8]" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 text-[14px] font-semibold">
            {p.name}
            <StatusDot state={status.state} />
            {p.pro && <ProBadge />}
          </div>
          <div className="mt-0.5 text-[11.5px] text-ink-80">{p.subtitle}</div>
          <div className="mt-2 font-mono text-[11px] text-ink-70">
            {status.error ? <span className="text-red-400">{status.error}</span> : status.meta}
          </div>
        </div>
      </div>
      <div className="mt-4 flex gap-2">
        {status.state === "on" ? (
          <>
            <Button variant="ghost" className="text-[11px]">Tester</Button>
            <Button variant="ghost" onClick={onDisconnect} className="text-[11px] text-ink-80 hover:text-white">
              Déconnecter
            </Button>
          </>
        ) : p.comingSoon ? (
          <Button variant="ghost" className="text-[11px] opacity-60" disabled>Bientôt</Button>
        ) : proLocked ? (
          <Button variant="ghost" className="text-[11px] opacity-80">Disponible en Pro</Button>
        ) : (
          <Button variant="primary" onClick={onConnect} disabled={status.busy} className="text-[12px]">
            {status.busy ? "…" : "Connecter"}
          </Button>
        )}
      </div>
    </motion.div>
  );
}

function Row({ Icon, label, value }: { Icon: any; label: string; value: string }) {
  return (
    <li className="flex items-center justify-between py-3">
      <span className="flex items-center gap-3 text-ink-90">
        <Icon className="size-4 stroke-[1.8]" />
        {label}
      </span>
      <span className="text-ink-80">{value}</span>
    </li>
  );
}
