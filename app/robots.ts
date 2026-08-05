import type { MetadataRoute } from "next";

// Vercel Git auto-deploy check — 2026-08-05
const SITE = "https://blog.relova.ai";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
    },
    sitemap: `${SITE}/sitemap.xml`,
  };
}
