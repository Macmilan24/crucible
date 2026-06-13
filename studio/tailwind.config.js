/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        crucible: {
          bg: "#0b0b0f",
          panel: "#141419",
          raised: "#1b1b22",
          border: "#26262e",
          accent: "#ff5a1f",
          accent2: "#b14bff",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [],
};
