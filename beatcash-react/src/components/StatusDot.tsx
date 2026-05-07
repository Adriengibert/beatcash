import { cn } from "../lib/cn";

export function StatusDot({ state = "off" }: { state?: "on" | "off" | "wait" }) {
  return (
    <span className="relative inline-flex size-2.5 shrink-0 items-center justify-center">
      <span
        className={cn(
          "absolute inset-0 rounded-full",
          state === "on" && "bg-white animate-pulse-soft",
          state === "off" && "bg-white/25",
          state === "wait" && "bg-white/55 animate-pulse"
        )}
      />
    </span>
  );
}
