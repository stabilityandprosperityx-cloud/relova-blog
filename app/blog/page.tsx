import type { Metadata } from "next";
import { getAllPosts } from "@/lib/posts";
import { absoluteUrl } from "@/lib/site";
import BlogIndexClient from "./BlogIndexClient";

// This is the single most important page on the property (the index of
// every post), and it had zero page-specific metadata — no canonical at
// all, and an inherited generic title/description shared with every other
// unconfigured route. Gives it its own, with a real post count.
export function generateMetadata(): Metadata {
  const count = getAllPosts().length;
  const title = `${count} Relocation Guides — Visas, Remote Work & Moving Abroad`;
  const description = `Browse ${count} practical guides on visas, remote work abroad, and moving overseas — searchable and filterable by country, from the Relova team.`;
  return {
    title,
    description,
    alternates: { canonical: absoluteUrl("/blog") },
    openGraph: { title, description, url: absoluteUrl("/blog") },
  };
}

export default function BlogIndexPage() {
  const posts = getAllPosts();
  return <BlogIndexClient posts={posts} />;
}
