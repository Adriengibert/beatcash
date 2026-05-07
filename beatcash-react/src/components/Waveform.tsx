import { useMemo } from "react";

export function Waveform({ bars = 48, animate = true }: { bars?: number; animate?: boolean }) {
  const heights = useMemo(
    () =>
      Array.from({ length: bars }, (_, i) => {
        const t = i / bars;
        const env = Math.sin(t * Math.PI) * 0.7 + 0.3;
        const noise = (Math.sin(i * 9.31) + 1) / 2;
        return Math.max(0.12, env * (0.55 + noise * 0.45));
      }),
    [bars]
  );

  return (
    <div className="flex h-12 items-end gap-[3px]">
      {heights.map((h, i) => (
        <span
          key={i}
          className="w-[3px] origin-bottom rounded-sm bg-white/70"
          style={{
            height: `${h * 100}%`,
            animation: animate ? `wave 1.${(i % 9) + 1}s ease-in-out infinite` : undefined,
            animationDelay: `${(i * 22) % 800}ms`,
            opacity: 0.55 + h * 0.45,
          }}
        />
      ))}
    </div>
  );
}
