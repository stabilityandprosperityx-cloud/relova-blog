"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import type { PostListItem } from "@/lib/posts";
import { CATEGORIES, detectCategory } from "@/lib/category";
import { countryName } from "@/lib/country";

function formatDate(iso: string) {
  return new Intl.DateTimeFormat("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  }).format(new Date(iso));
}

export default function BlogIndexClient({ posts }: { posts: PostListItem[] }) {
  const [active, setActive] = useState("all");
  const [country, setCountry] = useState("all");
  const [query, setQuery] = useState("");

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

  const countryOptions = useMemo(() => {
    const countByCountry = new Map<string, number>();
    for (const p of posts) {
      if (!p.country) continue;
      countByCountry.set(p.country, (countByCountry.get(p.country) ?? 0) + 1);
    }
    return Array.from(countByCountry.entries())
      .map(([slug, count]) => ({ slug, name: countryName(slug), count }))
      .sort((a, b) => a.name.localeCompare(b.name));
  }, [posts]);

  const q = query.trim().toLowerCase();

  const visiblePosts = postsWithCategory.filter((post) => {
    if (active !== "all" && post.resolvedCategory !== active) return false;
    if (country !== "all" && post.country !== country) return false;
    if (q && !post.title.toLowerCase().includes(q) && !post.description.toLowerCase().includes(q)) {
      return false;
    }
    return true;
  });

  return (
    <div className="mx-auto max-w-3xl px-4 py-14 sm:px-6 sm:py-20">
      <header className="mb-10 sm:mb-12">
        <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-primary">
          Relova
        </p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight text-foreground sm:text-4xl sm:leading-tight">
          Relocation insights
        </h1>
        <p className="mt-4 max-w-2xl text-base leading-relaxed text-muted-foreground sm:text-lg">
          Visas, destinations, and checklists for people building a life abroad - backed by
          Relova&apos;s relocation tools.
        </p>
      </header>

      <div className="mb-6 flex flex-col gap-3 sm:flex-row">
        <div className="relative flex-1">
          <svg
            className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            aria-hidden
          >
            <circle cx="11" cy="11" r="7" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search articles — e.g. digital nomad visa, Portugal, taxes..."
            className="w-full rounded-lg border border-border bg-card py-2.5 pl-10 pr-9 text-sm text-foreground placeholder:text-muted-foreground focus:border-primary/40 focus:outline-none focus:ring-2 focus:ring-primary/20"
          />
          {query && (
            <button
              type="button"
              onClick={() => setQuery("")}
              aria-label="Clear search"
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
            >
              ✕
            </button>
          )}
        </div>

        <select
          value={country}
          onChange={(e) => setCountry(e.target.value)}
          className="rounded-lg border border-border bg-card px-3.5 py-2.5 text-sm text-foreground focus:border-primary/40 focus:outline-none focus:ring-2 focus:ring-primary/20 sm:w-56"
        >
          <option value="all">All countries</option>
          {countryOptions.map((c) => (
            <option key={c.slug} value={c.slug}>
              {c.name} ({c.count})
            </option>
          ))}
        </select>
      </div>

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
                  ? "border-primary bg-primary/10 text-primary"
                  : "border-border bg-card text-muted-foreground hover:border-primary/30 hover:text-foreground"
              }`}
            >
              <span>{cat.emoji}</span>
              <span>{cat.label}</span>
              <span
                className={`rounded-full px-1.5 py-0.5 text-[11px] font-semibold tabular-nums ${
                  isActive ? "bg-primary/20 text-primary" : "bg-muted text-muted-foreground"
                }`}
              >
                {count}
              </span>
            </button>
          );
        })}
      </div>

      {(query || country !== "all") && (
        <p className="mb-4 text-sm text-muted-foreground">
          {visiblePosts.length === 0
            ? "No articles match your filters."
            : `${visiblePosts.length} article${visiblePosts.length === 1 ? "" : "s"} found`}
        </p>
      )}

      <ul className="space-y-5">
        {visiblePosts.map((post) => (
          <li key={post.slug}>
            <article className="group rounded-xl border border-border bg-card p-6 transition-colors hover:border-primary/30 sm:p-7">
              <p className="text-[13px] font-medium tabular-nums text-muted-foreground">
                {post.updatedAt.slice(0, 10) !== post.date.slice(0, 10)
                  ? `Updated ${formatDate(post.updatedAt)}`
                  : formatDate(post.date)}
              </p>
              <h2 className="mt-2 text-lg font-semibold leading-snug tracking-tight text-foreground sm:text-xl">
                <Link
                  href={`/blog/${post.slug}`}
                  className="transition-colors hover:text-primary"
                >
                  {post.title}
                </Link>
              </h2>
              <p className="mt-3 text-[15px] leading-relaxed text-muted-foreground">{post.description}</p>
              <Link
                href={`/blog/${post.slug}`}
                className="mt-4 inline-flex items-center text-sm font-medium text-primary transition-colors hover:text-primary/90"
              >
                Read article
                <span className="ml-1 transition-transform group-hover:translate-x-0.5" aria-hidden>
                  →
                </span>
              </Link>
            </article>
          </li>
        ))}
      </ul>
    </div>
  );
}
