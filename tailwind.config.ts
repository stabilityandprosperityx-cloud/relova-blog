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
        terracotta: "#E07A5F",
        navy: "#2D3561",
        cream: "#F4F1DE",
        void: "#0F0F0F",
        graphite: "#111111",
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
      typography: ({ theme }: { theme: (path: string) => string }) => ({
        invert: {
          css: {
            "--tw-prose-body": theme("colors.cream / 0.88"),
            "--tw-prose-headings": theme("colors.cream"),
            "--tw-prose-lead": theme("colors.cream / 0.75"),
            "--tw-prose-links": theme("colors.terracotta"),
            "--tw-prose-bold": theme("colors.cream"),
            "--tw-prose-counters": theme("colors.terracotta"),
            "--tw-prose-bullets": theme("colors.terracotta"),
            "--tw-prose-hr": "rgb(45 53 97 / 0.45)",
            "--tw-prose-quotes": theme("colors.cream / 0.72"),
            "--tw-prose-quote-borders": theme("colors.navy"),
            "--tw-prose-captions": theme("colors.cream / 0.55"),
            "--tw-prose-code": theme("colors.cream"),
            "--tw-prose-pre-code": theme("colors.cream / 0.9"),
            "--tw-prose-pre-bg": theme("colors.graphite"),
            "--tw-prose-th-borders": "rgb(45 53 97 / 0.4)",
            "--tw-prose-td-borders": "rgb(255 255 255 / 0.08)",
          },
        },
      }),
    },
  },
  plugins: [require("@tailwindcss/typography")],
};

export default config;
