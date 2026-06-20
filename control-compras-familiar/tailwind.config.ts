import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0f172a",
        brand: { DEFAULT: "#4f46e5", 600: "#4338ca" }, // indigo
        money: "#059669", // emerald (totales)
        // colores por categoría
        cat: {
          productos: "#2563eb",
          insumos: "#d97706",
          servicios: "#7c3aed",
          gastos: "#e11d48",
          retiros: "#475569",
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
        display: ["var(--font-display)", "system-ui", "sans-serif"],
      },
      boxShadow: {
        card: "0 1px 2px rgba(15,23,42,.04), 0 8px 24px rgba(15,23,42,.06)",
      },
    },
  },
  plugins: [],
};
export default config;
