import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        surface: "#0A0A0F",
        card: "#12121A",
        accent: "#38BDF8",
        muted: "#94A3B8",
        terracotta: "#E07A5F",
        navy: "#2D3561",
        cream: "#F4F1DE",
      },
      fontFamily: {
        sans: [
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "sans-serif",
        ],
      },
      typography: () => ({
        invert: {
          css: {
            "--tw-prose-body": "#94A3B8",
            "--tw-prose-headings": "#ffffff",
            "--tw-prose-lead": "#94A3B8",
            "--tw-prose-links": "#38BDF8",
            "--tw-prose-bold": "#ffffff",
            "--tw-prose-counters": "#38BDF8",
            "--tw-prose-bullets": "#38BDF8",
            "--tw-prose-hr": "rgb(56 189 248 / 0.2)",
            "--tw-prose-quotes": "#94A3B8",
            "--tw-prose-quote-borders": "rgb(56 189 248 / 0.25)",
            "--tw-prose-captions": "#94A3B8",
            "--tw-prose-code": "#ffffff",
            "--tw-prose-pre-code": "rgb(255 255 255 / 0.9)",
            "--tw-prose-pre-bg": "#12121A",
            "--tw-prose-th-borders": "rgb(56 189 248 / 0.15)",
            "--tw-prose-td-borders": "rgb(255 255 255 / 0.06)",
          },
        },
      }),
    },
  },
  plugins: [require("@tailwindcss/typography")],
};

export default config;
