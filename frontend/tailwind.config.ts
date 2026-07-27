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
          50: "#eef4fc", 100: "#d9e7f8", 200: "#b3cef1", 300: "#82aee6",
          400: "#4d87d6", 500: "#2a66bd", 600: "#1f4f99", 700: "#1b4079",
          800: "#17325f", 900: "#112442",
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
