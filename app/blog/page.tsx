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
        <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-terracotta/90">
          Relova
        </p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight text-cream sm:text-4xl sm:leading-tight">
          Relocation insights
        </h1>
        <p className="mt-4 max-w-2xl text-base leading-relaxed text-cream/60 sm:text-lg">
          Visas, destinations, and checklists for people building a life abroad — backed by
          Relova&apos;s relocation tools.
        </p>
      </header>

      <ul className="space-y-5">
        {posts.map((post) => (
          <li key={post.slug}>
            <article className="group rounded-xl border border-white/[0.08] bg-graphite/80 p-6 shadow-[0_0_0_1px_rgba(255,255,255,0.02)_inset] transition-colors hover:border-white/[0.12] hover:bg-graphite sm:p-7">
              <p className="text-[13px] font-medium tabular-nums text-terracotta">
                {formatDate(post.date)}
              </p>
              <h2 className="mt-2 text-lg font-semibold leading-snug tracking-tight text-cream sm:text-xl">
                <Link
                  href={`/blog/${post.slug}`}
                  className="transition-colors group-hover:text-terracotta"
                >
                  {post.title}
                </Link>
              </h2>
              <p className="mt-3 text-[15px] leading-relaxed text-cream/55">{post.description}</p>
              <Link
                href={`/blog/${post.slug}`}
                className="mt-4 inline-flex items-center text-sm font-medium text-terracotta transition-colors hover:text-terracotta/85"
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
