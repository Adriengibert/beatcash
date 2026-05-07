import { motion } from "framer-motion";
import { cn } from "../lib/cn";

export function Segmented<T extends string>({
  value,
  onChange,
  options,
}: {
  value: T;
  onChange: (v: T) => void;
  options: { value: T; label: string }[];
}) {
  return (
    <div
      data-hover
      className="relative inline-flex rounded-xl border-hairline bg-black/40 p-1 backdrop-blur-sm"
    >
      {options.map((o) => {
        const active = o.value === value;
        return (
          <button
            key={o.value}
            data-hover
            onClick={() => onChange(o.value)}
            className={cn(
              "relative z-10 px-5 py-2 text-[12.5px] font-bold tracking-wide transition-colors",
              active ? "text-ink-0" : "text-ink-80 hover:text-ink-100"
            )}
          >
            {active && (
              <motion.span
                layoutId="seg-pill"
                className="absolute inset-0 rounded-lg bg-white shadow-glow-sm"
                transition={{ type: "spring", stiffness: 420, damping: 32 }}
              />
            )}
            <span className="relative z-10">{o.label}</span>
          </button>
        );
      })}
    </div>
  );
}
