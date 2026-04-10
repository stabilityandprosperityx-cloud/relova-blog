"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import type { PostListItem } from "@/lib/posts";
import { CATEGORIES, detectCategory } from "@/lib/category";

function formatDate(iso: string) {
  return new Intl.DateTimeFormat("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  }).format(new Date(iso));
}

export default function BlogIndexClient({ posts }: { posts: PostListItem[] }) {
  const [active, setActive] = useState("all");

  const postsWithCategory = useMemo(
    () =>
      posts.map((p) => ({
        ...p,
        resolvedCategory: detectCategory(p.slug, p.category),
      })),
    [posts]
  );

  const counts = useMemo(() => {
    const map: Record<string, number> = { all: posts.length };
    for (const p of postsWithCategory) {
      map[p.resolvedCategory] = (map[p.resolvedCategory] ?? 0) + 1;
    }
    return map;
  }, [posts.length, postsWithCategory]);

  return (
    <div className="mx-auto max-w-3xl px-4 py-14 sm:px-6 sm:py-20">
      <header className="mb-10 sm:mb-12">
        <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-terracotta">
          Relova
        </p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight text-white sm:text-4xl sm:leading-tight">
          Relocation insights
        </h1>
        <p className="mt-4 max-w-2xl text-base leading-relaxed text-muted sm:text-lg">
          Visas, destinations, and checklists for people building a life abroad - backed by
          Relova&apos;s relocation tools.
        </p>
      </header>

      <div className="mb-10 flex flex-wrap gap-2">
        {CATEGORIES.map((cat) => {
          const count = counts[cat.id] ?? 0;
          if (cat.id !== "all" && count === 0) return null;
          const isActive = active === cat.id;
          return (
            <button
              key={cat.id}
              onClick={() => setActive(cat.id)}
              className={`inline-flex items-center gap-1.5 rounded-full border px-3.5 py-1.5 text-[13px] font-medium transition-colors ${
                isActive
                  ? "border-accent bg-accent/10 text-accent"
                  : "border-accent/10 bg-card text-muted hover:border-accent/30 hover:text-white"
              }`}
            >
              <span>{cat.emoji}</span>
              <span>{cat.label}</span>
              <span
                className={`rounded-full px-1.5 py-0.5 text-[11px] font-semibold tabular-nums ${
                  isActive ? "bg-accent/20 text-accent" : "bg-white/5 text-muted"
                }`}
              >
                {count}
              </span>
            </button>
          );
        })}
      </div>

      <ul className="space-y-5">
        {postsWithCategory.map((post) => {
          const hidden = active !== "all" && post.resolvedCategory !== active;
          return (
            <li key={post.slug} className={hidden ? "hidden" : undefined}>
              <article className="group rounded-xl border border-accent/10 bg-card p-6 shadow-[0_0_0_1px_rgba(255,255,255,0.02)_inset] transition-colors hover:border-accent/20 sm:p-7">
                <p className="text-[13px] font-medium tabular-nums text-terracotta/90">
                  {formatDate(post.date)}
                </p>
                <h2 className="mt-2 text-lg font-semibold leading-snug tracking-tight text-white sm:text-xl">
                  <Link
                    href={`/blog/${post.slug}`}
                    className="transition-colors hover:text-accent"
                  >
                    {post.title}
                  </Link>
                </h2>
                <p className="mt-3 text-[15px] leading-relaxed text-muted">{post.description}</p>
                <Link
                  href={`/blog/${post.slug}`}
                  className="mt-4 inline-flex items-center text-sm font-medium text-accent transition-colors hover:text-accent/90"
                >
                  Read article
                  <span className="ml-1 transition-transform group-hover:translate-x-0.5" aria-hidden>
                    →
                  </span>
                </Link>
              </article>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
