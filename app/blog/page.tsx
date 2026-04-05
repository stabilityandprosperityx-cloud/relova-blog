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
    <div className="mx-auto max-w-3xl px-4 py-12 sm:px-6 sm:py-16">
      <header className="mb-12">
        <h1 className="text-3xl font-bold tracking-tight text-navy sm:text-4xl">
          Relocation insights
        </h1>
        <p className="mt-3 max-w-2xl text-lg text-navy/75">
          Visas, destinations, and checklists for people building a life abroad — backed by Relova&apos;s
          relocation tools.
        </p>
      </header>

      <ul className="space-y-10">
        {posts.map((post) => (
          <li key={post.slug}>
            <article>
              <p className="text-sm font-medium text-terracotta">{formatDate(post.date)}</p>
              <h2 className="mt-1 text-xl font-semibold text-navy">
                <Link
                  href={`/blog/${post.slug}`}
                  className="transition-colors hover:text-terracotta"
                >
                  {post.title}
                </Link>
              </h2>
              <p className="mt-2 text-navy/80">{post.description}</p>
              <Link
                href={`/blog/${post.slug}`}
                className="mt-3 inline-block text-sm font-medium text-terracotta underline-offset-2 hover:underline"
              >
                Read article
              </Link>
            </article>
          </li>
        ))}
      </ul>
    </div>
  );
}
