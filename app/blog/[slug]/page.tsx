import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { MDXRemote } from "next-mdx-remote/rsc";
import { BlogPostingJsonLd } from "@/components/BlogPostingJsonLd";
import { mdxComponents } from "@/components/mdx-components";
import { getPostBySlug, getPostSlugs } from "@/lib/posts";
import { absoluteUrl } from "@/lib/site";
import Link from "next/link";

type Props = { params: { slug: string } };

export async function generateStaticParams() {
  return getPostSlugs().map((slug) => ({ slug }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = params;
  const post = getPostBySlug(slug);
  if (!post) return {};

  const canonicalPath = `/blog/${post.slug}`;
  const pageUrl = absoluteUrl(canonicalPath);
  const ogImage = absoluteUrl(post.ogImage);

  return {
    title: post.title,
    description: post.description,
    alternates: {
      canonical: canonicalPath,
    },
    openGraph: {
      title: post.title,
      description: post.description,
      url: pageUrl,
      type: "article",
      publishedTime: post.date,
      authors: [post.author],
      images: [{ url: ogImage, alt: post.title }],
    },
    twitter: {
      card: "summary_large_image",
      title: post.title,
      description: post.description,
      images: [ogImage],
    },
  };
}

function formatDate(iso: string) {
  return new Intl.DateTimeFormat("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  }).format(new Date(iso));
}

export default async function BlogPostPage({ params }: Props) {
  const { slug } = params;
  const post = getPostBySlug(slug);
  if (!post) notFound();

  const pageUrl = absoluteUrl(`/blog/${post.slug}`);

  return (
    <>
      <BlogPostingJsonLd post={post} url={pageUrl} />
      <article className="mx-auto max-w-3xl px-4 py-12 sm:px-6 sm:py-16">
        <p className="text-sm font-medium text-terracotta">
          <Link href="/blog" className="hover:underline">
            Blog
          </Link>
          <span className="mx-2 text-navy/40">/</span>
          {formatDate(post.date)}
        </p>
        <h1 className="mt-3 text-3xl font-bold tracking-tight text-navy sm:text-4xl">
          {post.title}
        </h1>
        <p className="mt-2 text-navy/70">By {post.author}</p>
        <p className="mt-6 text-lg leading-relaxed text-navy/85">{post.description}</p>

        <div className="prose prose-lg mt-10 max-w-none text-navy/90 prose-headings:scroll-mt-24 prose-headings:font-semibold prose-headings:text-navy prose-p:leading-relaxed prose-a:text-terracotta prose-a:no-underline hover:prose-a:underline prose-strong:text-navy">
          <MDXRemote source={post.content} components={mdxComponents} />
        </div>
      </article>
    </>
  );
}
