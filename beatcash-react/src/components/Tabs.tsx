import { motion } from "framer-motion";
import { Rocket, Link2, Sparkles, LineChart } from "lucide-react";
import { cn } from "../lib/cn";

export type TabKey = "publier" | "suivi" | "connexions" | "seo";

const tabs: { key: TabKey; label: string; Icon: typeof Rocket }[] = [
  { key: "publier",    label: "Publier",       Icon: Rocket },
  { key: "suivi",      label: "Suivi",         Icon: LineChart },
  { key: "connexions", label: "Connexions",    Icon: Link2 },
  { key: "seo",        label: "SEO & Profils", Icon: Sparkles },
];

export function Tabs({ active, onChange }: { active: TabKey; onChange: (k: TabKey) => void }) {
  return (
    <div
      data-hover
      className="relative flex items-center gap-1 rounded-full border-hairline bg-white/[0.02] p-1 backdrop-blur-sm"
    >
      {tabs.map(({ key, label, Icon }) => {
        const isActive = active === key;
        return (
          <button
            key={key}
            data-hover
            onClick={() => onChange(key)}
            className={cn(
              "relative z-10 flex items-center gap-2 rounded-full px-4 py-2 text-[13px] font-semibold transition-colors",
              isActive ? "text-ink-100" : "text-ink-80 hover:text-ink-99"
            )}
          >
            {isActive && (
              <motion.span
                layoutId="tab-pill"
                className="absolute inset-0 rounded-full border-hairline-hi bg-ink-100/[0.06] shadow-glow-sm"
                transition={{ type: "spring", stiffness: 380, damping: 32 }}
              />
            )}
            <Icon className="relative z-10 size-3.5 stroke-[2.2]" />
            <span className="relative z-10 tracking-[0.04em]">{label}</span>
          </button>
        );
      })}
    </div>
  );
}
