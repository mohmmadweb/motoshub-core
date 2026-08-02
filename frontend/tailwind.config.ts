import type { Config } from "tailwindcss";

// Design tokens ported verbatim from the prototype (src/index.css @theme) so the
// client matches demo.shub.ir. Dark mode is class-based; the ink scale inverts
// via CSS variables in globals.css.
const config: Config = {
  darkMode: "class",
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: { sans: ["Vazirmatn", "system-ui", "Tahoma", "sans-serif"] },
      colors: {
        brand: {
          50: "var(--brand-50)", 100: "var(--brand-100)", 200: "var(--brand-200)",
          300: "var(--brand-300)", 400: "var(--brand-400)", 500: "var(--brand-500)",
          600: "var(--brand-600)", 700: "var(--brand-700)", 800: "var(--brand-800)", 900: "var(--brand-900)",
        },
        navy: {
          50: "#f4f6f9", 100: "#e3e8ef", 200: "#c3ccd9", 300: "#93a2b8",
          400: "#5e7191", 500: "#3f526f", 600: "#2c3c56", 700: "#213044",
          800: "#182536", 900: "#0f1828",
        },
        // ink is driven by CSS vars so it inverts in dark mode.
        ink: {
          50: "var(--ink-50)", 100: "var(--ink-100)", 200: "var(--ink-200)",
          300: "var(--ink-300)", 400: "var(--ink-400)", 500: "var(--ink-500)",
          600: "var(--ink-600)", 700: "var(--ink-700)", 800: "var(--ink-800)",
          900: "var(--ink-900)",
        },
        surface: "var(--surface)",
      },
    },
  },
  plugins: [],
};
export default config;
