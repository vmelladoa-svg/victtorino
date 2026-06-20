import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        navy: { DEFAULT: "#0F2942", 700: "#16365A", 900: "#0A1D30" },
        naranjo: { DEFAULT: "#FF6B35", 600: "#F2570F" },
        warm: "#F5F3EF",
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
      },
      boxShadow: {
        card: "0 1px 2px rgba(15,41,66,.05), 0 10px 30px rgba(15,41,66,.08)",
        cta: "0 8px 22px rgba(255,107,53,.35)",
      },
    },
  },
  plugins: [],
};
export default config;
