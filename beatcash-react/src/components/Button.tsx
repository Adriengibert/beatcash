import { type ButtonHTMLAttributes, type ReactNode, useRef } from "react";
import { motion } from "framer-motion";
import { cn } from "../lib/cn";

type Variant = "primary" | "secondary" | "ghost";

export function Button({
  children,
  variant = "secondary",
  className,
  ...rest
}: { children: ReactNode; variant?: Variant } & ButtonHTMLAttributes<HTMLButtonElement>) {
  const ref = useRef<HTMLButtonElement>(null);

  const onMove = (e: React.MouseEvent) => {
    const el = ref.current;
    if (!el) return;
    const r = el.getBoundingClientRect();
    const x = e.clientX - r.left - r.width / 2;
    const y = e.clientY - r.top - r.height / 2;
    el.style.transform = `translate(${x * 0.18}px, ${y * 0.22}px)`;
  };
  const onLeave = () => {
    if (ref.current) ref.current.style.transform = "translate(0,0)";
  };

  const base =
    "relative inline-flex items-center justify-center gap-2 rounded-xl px-5 py-2.5 text-[13px] font-semibold transition-[background,color,box-shadow] duration-200 will-change-transform";

  const styles: Record<Variant, string> = {
    primary:
      "bg-white text-ink-0 shadow-glow hover:bg-white hover:shadow-glow-lg",
    secondary:
      "border-hairline bg-white/[0.04] text-ink-99 hover:bg-white/[0.08] hover:border-white/20 shadow-ring",
    ghost:
      "bg-transparent text-ink-90 hover:text-ink-100 hover:bg-white/[0.04]",
  };

  return (
    <motion.button
      ref={ref}
      data-hover
      onMouseMove={onMove}
      onMouseLeave={onLeave}
      whileTap={{ scale: 0.97 }}
      className={cn(base, styles[variant], className)}
      {...(rest as any)}
    >
      {children}
    </motion.button>
  );
}
