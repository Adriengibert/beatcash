/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx,js,jsx}"],
  theme: {
    extend: {
      colors: {
        // Off-black + off-white pour confort visuel (vs pur #000/#fff trop dur)
        ink: {
          0:   "#0a0a0c",   // bg principal
          5:   "#0e0e11",
          10:  "#121216",
          15:  "#16161a",
          20:  "#1a1a1f",
          25:  "#1f1f24",
          30:  "#26262d",
          40:  "#2e2e36",
          50:  "#3a3a44",
          60:  "#4b4b58",
          70:  "#65656f",   // un cran plus contrasté qu'avant (#525252)
          80:  "#8a8a94",   // labels mono
          90:  "#b8b8c0",   // body text — meilleur contraste que #a3a3a3
          95:  "#d6d6dc",
          98:  "#ececef",
          99:  "#f1f1f4",   // text primaire (off-white)
          100: "#ffffff",   // pure white pour glow accents
        },
        brand: {
          DEFAULT: "#ff3a30",
          hot:     "#ff5a52",
          dim:     "#cc1100",
        },
      },
      fontFamily: {
        display: ["Syncopate", "Bahnschrift", "Inter", "sans-serif"],
        sans: ["Inter", "Segoe UI", "system-ui", "sans-serif"],
        mono: ["Space Mono", "Cascadia Mono", "Consolas", "monospace"],
      },
      letterSpacing: {
        widest2: "0.18em",
        ultra: "0.32em",
      },
      boxShadow: {
        glow:    "0 0 24px rgba(255,255,255,0.18), 0 0 4px rgba(255,255,255,0.5)",
        "glow-sm": "0 0 12px rgba(255,255,255,0.18)",
        "glow-lg": "0 0 60px rgba(255,255,255,0.20), 0 0 12px rgba(255,255,255,0.55)",
        ring:    "inset 0 0 0 1px rgba(255,255,255,0.08)",
        "ring-2": "inset 0 0 0 1px rgba(255,255,255,0.16)",
        elev:    "0 24px 60px -20px rgba(0,0,0,0.85), 0 8px 20px -10px rgba(0,0,0,0.75)",
      },
      keyframes: {
        "fade-up": {
          from: { opacity: "0", transform: "translateY(12px)" },
          to:   { opacity: "1", transform: "translateY(0)" },
        },
        shimmer: {
          "0%":   { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
        "pulse-soft": {
          "0%, 100%": { boxShadow: "0 0 0 0 rgba(255,255,255,0.4), 0 0 12px rgba(255,255,255,0.5)" },
          "50%":      { boxShadow: "0 0 0 7px rgba(255,255,255,0), 0 0 22px rgba(255,255,255,0.95)" },
        },
        spin360: { to: { transform: "rotate(360deg)" } },
        marquee: { from: { transform: "translateX(0)" }, to: { transform: "translateX(-50%)" } },
        wave: {
          "0%, 100%": { transform: "scaleY(0.4)" },
          "50%":      { transform: "scaleY(1)" },
        },
      },
      animation: {
        "fade-up":    "fade-up 600ms cubic-bezier(.22,1.2,.36,1) both",
        shimmer:      "shimmer 2.4s linear infinite",
        "pulse-soft": "pulse-soft 2.4s ease-in-out infinite",
        spin360:      "spin360 4s linear infinite",
        marquee:      "marquee 18s linear infinite",
        wave:         "wave 1.1s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
