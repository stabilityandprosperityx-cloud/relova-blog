import type { Metadata } from "next";
import Link from "next/link";
import { getAllPosts } from "@/lib/posts";
import { getSiteUrl } from "@/lib/site";

export const metadata: Metadata = {
  title: "Blog",
  description:
    "Relocation guides, visa explainers, and remote-work destination ideas from Relova.",
  alternates: {
    canonical: "/blog",
  },
  openGraph: {
    title: "Relova Blog",
    description:
      "Relocation guides, visa explainers, and remote-work destination ideas from Relova.",
    url: `${getSiteUrl()}/blog`,
    type: "website",
  },
};

function formatDate(iso: string) {
  return new Intl.DateTimeFormat("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  }).format(new Date(iso));
}

export default function BlogIndexPage() {
  const posts = getAllPosts();

  return (
    <div className="mx-auto max-w-3xl px-4 py-14 sm:px-6 sm:py-20">
      <header className="mb-14 sm:mb-16">
        <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-terracotta">
          Relova
        </p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight text-white sm:text-4xl sm:leading-tight">
          Relocation insights
        </h1>
        <p className="mt-4 max-w-2xl text-base leading-relaxed text-muted sm:text-lg">
          Visas, destinations, and checklists for people building a life abroad — backed by
          Relova&apos;s relocation tools.
        </p>
      </header>

      <ul className="space-y-5">
        {posts.map((post) => (
          <li key={post.slug}>
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
        ))}
      </ul>
    </div>
  );
}
