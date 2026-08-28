import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getAllAuthors, getAuthorBySlug } from "@/lib/authors";
import { absoluteUrl } from "@/lib/site";

type Props = { params: { slug: string } };

export function generateStaticParams() {
  return getAllAuthors().map((author) => ({ slug: author.slug }));
}

export function generateMetadata({ params }: Props): Metadata {
  const author = getAuthorBySlug(params.slug);
  if (!author) return {};

  const description = author.paragraphs[0];
  return {
    title: author.name,
    description,
    alternates: {
      canonical: author.path,
    },
    openGraph: {
      title: author.name,
      description,
      url: absoluteUrl(author.path),
      type: "profile",
    },
  };
}

export default function AuthorPage({ params }: Props) {
  const author = getAuthorBySlug(params.slug);
  if (!author) notFound();

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "Person",
    name: author.name,
    url: absoluteUrl(author.path),
    jobTitle: author.jobTitle,
    description: author.paragraphs.join(" "),
    worksFor: {
      "@type": "Organization",
      name: "Relova",
      url: "https://relova.ai",
    },
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <article className="mx-auto max-w-3xl px-4 py-14 sm:px-6 sm:py-20">
        <div className="rounded-xl border border-border bg-card px-5 py-8 sm:px-8 sm:py-10">
          <p className="text-[13px] font-medium">
            <Link href="/blog" className="text-primary transition-colors hover:text-primary/85">
              Blog
            </Link>
            <span className="mx-2 text-muted-foreground/40">/</span>
            <span className="text-muted-foreground">Author</span>
          </p>
          <h1 className="mt-4 text-3xl font-semibold tracking-tight text-foreground sm:text-[2.25rem] sm:leading-[1.15]">
            {author.name}
          </h1>
          <p className="mt-3 text-sm text-muted-foreground">{author.jobTitle}, Relova</p>
        </div>

        <div className="prose prose-lg mt-12 max-w-none prose-p:leading-[1.75] prose-p:text-muted-foreground prose-a:font-medium prose-a:text-primary prose-a:no-underline hover:prose-a:underline">
          {author.paragraphs.map((paragraph) => (
            <p key={paragraph.slice(0, 48)}>{paragraph}</p>
          ))}
          <p>
            <Link href="/about">About Relova</Link>
            {" · "}
            <a href="https://relova.ai">relova.ai</a>
          </p>
        </div>
      </article>
    </>
  );
}
