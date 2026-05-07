import { motion } from "framer-motion";
import type { ReactNode } from "react";
import { cn } from "../lib/cn";

export function Card({
  title,
  children,
  className,
  delay = 0,
}: {
  title?: string;
  children: ReactNode;
  className?: string;
  delay?: number;
}) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.55, ease: [0.22, 1.2, 0.36, 1], delay }}
      className={cn(
        "gradient-border glass relative rounded-2xl p-6 shadow-elev",
        className
      )}
    >
      {title && (
        <div className="mb-5 flex items-center gap-3">
          <span className="size-1.5 rounded-full bg-white shadow-glow-sm" />
          <h2 className="font-display text-[12px] font-bold uppercase tracking-ultra text-ink-99">
            {title}
          </h2>
          <div className="ml-auto h-px flex-1 bg-gradient-to-r from-white/10 via-white/5 to-transparent" />
        </div>
      )}
      {children}
    </motion.section>
  );
}
