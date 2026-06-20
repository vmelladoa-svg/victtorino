import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        balon: {
          // naranja básquetbol — color primario de marca
          DEFAULT: "#E8590C",
          50: "#FFF4ED",
          100: "#FFE6D5",
          500: "#E8590C",
          600: "#D24A04",
          700: "#B23C03",
        },
        carbon: {
          DEFAULT: "#1A1A1A",
          800: "#222222",
          900: "#141414",
          950: "#0D0D0D",
        },
        cancha: "#16A34A", // verde cancha
        azulina: "#2563EB", // azul acento
      },
      fontFamily: {
        display: ["var(--font-anton)", "Arial Narrow", "sans-serif"],
        head: ["var(--font-archivo)", "system-ui", "sans-serif"],
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
      },
      boxShadow: {
        card: "0 1px 2px rgba(16,24,40,.05), 0 8px 24px rgba(16,24,40,.07)",
        "card-hover": "0 4px 8px rgba(16,24,40,.06), 0 18px 40px rgba(232,89,12,.18)",
        cta: "0 8px 22px rgba(232,89,12,.32)",
      },
      backgroundImage: {
        "grad-balon": "linear-gradient(135deg, #E8590C 0%, #F97316 60%, #FB923C 100%)",
        "grad-carbon": "linear-gradient(160deg, #1A1A1A 0%, #0D0D0D 100%)",
      },
      keyframes: {
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(16px)" },
          "100%": { opacity: "1", transform: "none" },
        },
        "slide-in": {
          "0%": { transform: "translateX(100%)" },
          "100%": { transform: "translateX(0)" },
        },
      },
      animation: {
        "fade-up": "fade-up .6s cubic-bezier(.16,1,.3,1) both",
        "slide-in": "slide-in .3s cubic-bezier(.16,1,.3,1) both",
      },
    },
  },
  plugins: [],
};

export default config;
