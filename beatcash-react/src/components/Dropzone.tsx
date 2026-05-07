import { useRef, useState } from "react";
import { motion } from "framer-motion";
import { UploadCloud } from "lucide-react";
import { cn } from "../lib/cn";
import { bridge, isInWebview } from "../lib/bridge";

export function Dropzone({
  onPath,
  kind = "video",
}: {
  onPath?: (path: string, label: string) => void;
  kind?: "video" | "audio" | "image";
}) {
  const [hover, setHover] = useState(false);
  const [name, setName] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const browse = async () => {
    if (isInWebview()) {
      const p = await bridge.selectFile(kind);
      if (p) {
        const lbl = p.split(/[\\/]/).pop() || p;
        setName(lbl);
        onPath?.(p, lbl);
      }
    } else {
      inputRef.current?.click();
    }
  };

  const handleFile = (f: File | null) => {
    if (!f) return;
    setName(f.name);
    // Sans PyWebView (mode dev), on ne peut pas obtenir le chemin disque
    onPath?.(f.name, f.name);
  };

  return (
    <motion.label
      data-hover
      onClick={browse}
      onDragEnter={(e) => { e.preventDefault(); setHover(true); }}
      onDragOver={(e) => { e.preventDefault(); setHover(true); }}
      onDragLeave={() => setHover(false)}
      onDrop={(e) => {
        e.preventDefault(); setHover(false);
        handleFile(e.dataTransfer.files?.[0] ?? null);
      }}
      whileHover={{ y: -2 }}
      transition={{ duration: 0.2 }}
      className={cn(
        "group relative flex cursor-pointer flex-col items-center gap-3 rounded-2xl border border-dashed px-10 py-9 text-center transition-all duration-300",
        hover
          ? "border-white/60 bg-white/[0.06] shadow-glow"
          : "border-white/15 bg-white/[0.02] hover:border-white/35 hover:bg-white/[0.04]"
      )}
    >
      {/* sweep highlight */}
      <span className="pointer-events-none absolute inset-0 overflow-hidden rounded-2xl">
        <span className="absolute -left-1/2 top-0 h-full w-1/2 -skew-x-12 bg-gradient-to-r from-transparent via-white/[0.05] to-transparent opacity-0 transition-opacity duration-500 group-hover:left-full group-hover:opacity-100" style={{ transition: "left 1100ms cubic-bezier(.22,1.2,.36,1), opacity 200ms" }} />
      </span>

      <div className="flex size-12 items-center justify-center rounded-full border-hairline-hi bg-white/5 shadow-glow-sm">
        <UploadCloud className="size-5 stroke-[2.2] text-ink-99" />
      </div>
      <div className="text-[13px] text-ink-90">
        <span className="font-semibold text-ink-100">Glisse un fichier</span> ou clique pour parcourir
      </div>
      <div className="font-mono text-[11px] text-ink-70">MP4 · MOV · AVI · max 1 Go</div>
      {name && (
        <div className="mt-1 max-w-[80%] truncate font-mono text-[11px] text-ink-95">→ {name}</div>
      )}
      <input
        id="dz-input"
        ref={inputRef}
        type="file"
        className="hidden"
        onChange={(e) => handleFile(e.target.files?.[0] ?? null)}
      />
    </motion.label>
  );
}
