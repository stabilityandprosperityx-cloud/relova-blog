import type { Metadata } from "next";
import { getAllPosts } from "@/lib/posts";
import { absoluteUrl } from "@/lib/site";
import BlogIndexClient from "./BlogIndexClient";

// This is the single most important page on the property (the index of
// every post), and it had zero page-specific metadata — no canonical at
// all, and an inherited generic title/description shared with every other
// unconfigured route. Gives it its own, with a real post count.
//
// Next.js metadata merging is shallow: a child route's `openGraph` object
// entirely REPLACES the parent layout's `openGraph`, it does not deep-merge
// individual keys. So this has to restate siteName/type/locale/images
// explicitly, or /blog silently loses the root layout's default og:image.
export function generateMetadata(): Metadata {
  const count = getAllPosts().length;
  const title = `${count} Relocation Guides — Visas, Remote Work & Moving Abroad`;
  const description = `Browse ${count} practical guides on visas, remote work abroad, and moving overseas — searchable and filterable by country, from the Relova team.`;
  return {
    title,
    description,
    alternates: { canonical: absoluteUrl("/blog") },
    openGraph: {
      title,
      description,
      url: absoluteUrl("/blog"),
      type: "website",
      locale: "en_US",
      siteName: "Relova Blog",
      images: [{ url: absoluteUrl("/images/blog-default.jpg"), width: 1200, height: 630 }],
    },
    twitter: {
      card: "summary_large_image",
      images: [absoluteUrl("/images/blog-default.jpg")],
    },
  };
}

export default function BlogIndexPage() {
  const posts = getAllPosts();
  return <BlogIndexClient posts={posts} />;
}
