import { useState } from "react";
import { motion } from "framer-motion";
import { Sparkles, Hash, Type, FileText, Wand2, Copy } from "lucide-react";
import { Card } from "../components/Card";
import { Button } from "../components/Button";

const profiles = ["Default", "Trap drill", "Lo-fi chill", "Boom bap classic", "Afrobeat soft"];

export function SEO() {
  const [profile, setProfile] = useState(profiles[0]);
  const [prompt, setPrompt] = useState("");
  const [busy, setBusy] = useState(false);
  const [out, setOut] = useState({ title: "", desc: "", tags: "", cap: "", htag: "" });

  const generate = () => {
    setBusy(true);
    setTimeout(() => { setBusy(false); }, 800);
  };

  return (
    <div className="space-y-5">
      <Header />

      <Card title="Profil &amp; prompt" delay={0.05}>
        <div className="space-y-4">
          <div className="flex flex-wrap gap-2">
            {profiles.map((p) => {
              const active = p === profile;
              return (
                <button
                  key={p}
                  data-hover
                  onClick={() => setProfile(p)}
                  className={
                    "rounded-full border px-3.5 py-1.5 text-[11.5px] font-semibold transition-all " +
                    (active
                      ? "border-white/60 bg-white text-ink-0 shadow-glow-sm"
                      : "border-white/10 bg-white/[0.03] text-ink-90 hover:border-white/30 hover:bg-white/[0.06]")
                  }
                >
                  {p}
                </button>
              );
            })}
          </div>

          <div className="space-y-2">
            <label className="font-mono text-[10px] font-bold uppercase tracking-ultra text-ink-70">Prompt</label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              rows={3}
              data-hover
              className="w-full resize-none rounded-xl border-hairline bg-black/40 px-4 py-3 font-mono text-[12.5px] text-ink-99 placeholder:text-ink-70 focus:border-white/40 focus:shadow-glow-sm focus:outline-none"
              placeholder="décris ton beat — style, mood, BPM, références"
            />
          </div>

          <div className="flex items-center gap-3">
            <Button variant="primary" onClick={generate} className="px-6 py-3 text-[12.5px]">
              <Wand2 className="size-4" />
              {busy ? "Génération…" : "Générer le contenu"}
            </Button>
            <span className="font-mono text-[11px] text-ink-70">
              {busy ? "● Claude réfléchit…" : "● Prêt à générer YT title + desc + tags + IG caption"}
            </span>
          </div>
        </div>
      </Card>

      <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
        <Card title="YouTube" delay={0.10}>
          <Field Icon={Type}     label="Title"       value={out.title} onChange={(v) => setOut({ ...out, title: v })} mono />
          <Field Icon={FileText} label="Description" value={out.desc}  onChange={(v) => setOut({ ...out, desc: v })}  textarea />
          <Field Icon={Hash}     label="Tags"        value={out.tags}  onChange={(v) => setOut({ ...out, tags: v })}  mono />
        </Card>

        <Card title="Instagram" delay={0.15}>
          <Field Icon={Type} label="Caption" value={out.cap}  onChange={(v) => setOut({ ...out, cap: v })}  textarea />
          <Field Icon={Hash} label="Hashtags" value={out.htag} onChange={(v) => setOut({ ...out, htag: v })} mono />
          <div className="mt-4 grid grid-cols-3 gap-2 text-center">
            <Stat n="22" label="hashtags" />
            <Stat n="1.4k" label="reach est." />
            <Stat n="A+" label="SEO score" />
          </div>
        </Card>
      </div>
    </div>
  );
}

function Header() {
  return (
    <motion.div
      initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.6 }}
      className="relative mb-6 flex items-center gap-3 pl-5"
    >
      <div className="absolute left-0 top-1 bottom-2 w-[3px] rounded-full bg-gradient-to-b from-white via-white/60 to-transparent shadow-glow-sm" />
      <h1 className="font-display text-[26px] font-bold tracking-widest2 text-glow leading-none">SEO &amp; PROFILS</h1>
      <Sparkles className="size-5 text-white/80 animate-pulse" />
      <p className="ml-auto text-[12px] font-mono text-ink-80">propulsé par Claude</p>
    </motion.div>
  );
}

function Field({
  Icon, label, value, onChange, mono, textarea,
}: { Icon: any; label: string; value: string; onChange: (v: string) => void; mono?: boolean; textarea?: boolean }) {
  const copy = () => navigator.clipboard?.writeText(value);
  return (
    <div className="mb-4 last:mb-0">
      <div className="mb-1.5 flex items-center justify-between">
        <span className="flex items-center gap-1.5 font-mono text-[10px] font-bold uppercase tracking-ultra text-ink-70">
          <Icon className="size-3" />
          {label}
        </span>
        <button data-hover onClick={copy} className="text-ink-70 transition-colors hover:text-ink-100">
          <Copy className="size-3.5" />
        </button>
      </div>
      {textarea ? (
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          rows={3}
          data-hover
          className={
            "w-full resize-none rounded-xl border-hairline bg-black/40 px-4 py-3 text-[12.5px] text-ink-99 focus:border-white/40 focus:shadow-glow-sm focus:outline-none " +
            (mono ? "font-mono" : "")
          }
        />
      ) : (
        <input
          value={value}
          onChange={(e) => onChange(e.target.value)}
          data-hover
          className={
            "w-full rounded-xl border-hairline bg-black/40 px-4 py-3 text-[12.5px] text-ink-99 focus:border-white/40 focus:shadow-glow-sm focus:outline-none " +
            (mono ? "font-mono" : "")
          }
        />
      )}
    </div>
  );
}

function Stat({ n, label }: { n: string; label: string }) {
  return (
    <div className="rounded-xl border-hairline bg-white/[0.02] py-3">
      <div className="font-display text-[20px] font-bold text-glow leading-none">{n}</div>
      <div className="mt-1 font-mono text-[10px] uppercase tracking-ultra text-ink-70">{label}</div>
    </div>
  );
}
