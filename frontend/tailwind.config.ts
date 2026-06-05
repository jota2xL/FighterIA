import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: {
          primary: "#0a0a0a",
          secondary: "#111111",
          tertiary: "#1a1a1a",
          hover: "#222222",
        },
        brand: {
          red: "#dc2626",
          "red-dark": "#991b1b",
          "red-light": "#ef4444",
          gold: "#d4af37",
          "gold-light": "#f5d577",
        },
        text: {
          primary: "#f5f5f0",
          secondary: "#a3a3a3",
          muted: "#525252",
        },
        border: {
          DEFAULT: "#2a2a2a",
          strong: "#3a3a3a",
        },
        score: {
          excellent: "#16a34a",
          good: "#ca8a04",
          poor: "#dc2626",
          correct: "#22c55e",
          incorrect: "#ef4444",
        },
        belt: {
          blanco: "#f5f5f0",
          amarillo: "#fbbf24",
          naranja: "#f97316",
          verde: "#16a34a",
          azul: "#2563eb",
          marron: "#92400e",
          negro: "#1a1a1a",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        display: ["Rajdhani", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
} satisfies Config;
