import { useEffect } from "react";

/**
 * Mouse-position tracker pour le spotlight (var CSS --mx/--my).
 * RAF-throttled : 1 update / frame max au lieu de chaque mousemove.
 */
export function Cursor() {
  useEffect(() => {
    let raf = 0;
    let nx = 0, ny = 0;
    const onMove = (e: MouseEvent) => {
      nx = e.clientX; ny = e.clientY;
      if (raf) return;
      raf = requestAnimationFrame(() => {
        document.documentElement.style.setProperty("--mx", `${nx}px`);
        document.documentElement.style.setProperty("--my", `${ny}px`);
        raf = 0;
      });
    };
    window.addEventListener("mousemove", onMove, { passive: true });
    return () => {
      window.removeEventListener("mousemove", onMove);
      if (raf) cancelAnimationFrame(raf);
    };
  }, []);
  return null;
}
