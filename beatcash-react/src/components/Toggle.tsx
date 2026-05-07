import { motion } from "framer-motion";
import { cn } from "../lib/cn";

export function Toggle({ on, onChange }: { on: boolean; onChange: (v: boolean) => void }) {
  return (
    <button
      data-hover
      onClick={() => onChange(!on)}
      className={cn(
        "relative h-7 w-12 shrink-0 rounded-full border-hairline transition-colors duration-300",
        on ? "bg-white shadow-glow-sm" : "bg-white/10"
      )}
    >
      <motion.span
        layout
        transition={{ type: "spring", stiffness: 520, damping: 32 }}
        className={cn(
          "absolute top-[2px] size-[22px] rounded-full shadow-md",
          on ? "left-[22px] bg-ink-0" : "left-[2px] bg-white"
        )}
      />
    </button>
  );
}
