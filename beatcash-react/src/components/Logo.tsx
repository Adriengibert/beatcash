import { motion } from "framer-motion";

export function Logo() {
  return (
    <motion.div
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: [0.22, 1.2, 0.36, 1] }}
      className="flex flex-col gap-1 select-none"
    >
      <div className="flex items-baseline gap-2">
        <span className="font-display font-bold text-3xl text-glow leading-none">$</span>
        <span className="font-display font-bold text-[18px] tracking-widest2 text-glow-soft">BEATCASH</span>
      </div>
      <div className="flex flex-col gap-[2px] ml-1">
        <div className="h-[2px] w-44 bg-gradient-to-r from-white via-white/70 to-transparent shadow-glow-sm" />
        <div className="h-[1px] w-32 bg-gradient-to-r from-white/60 to-transparent" />
      </div>
    </motion.div>
  );
}
