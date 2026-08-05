import type { Metadata } from "next";
import { notFound } from "next/navigation";
import remarkGfm from "remark-gfm";
import rehypeSlug from "rehype-slug";
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
      <article className="mx-auto max-w-3xl px-4 py-14 sm:px-6 sm:py-20">
        <div className="rounded-xl border border-border bg-card px-5 py-8 sm:px-8 sm:py-10">
          <p className="text-[13px] font-medium">
            <Link href="/blog" className="text-primary transition-colors hover:text-primary/85">
              Blog
            </Link>
            <span className="mx-2 text-muted-foreground/40">/</span>
            <span className="tabular-nums text-muted-foreground">{formatDate(post.date)}</span>
          </p>
          <h1 className="mt-4 text-3xl font-semibold tracking-tight text-foreground sm:text-[2.25rem] sm:leading-[1.15]">
            {post.title}
          </h1>
          <p className="mt-3 text-sm text-muted-foreground">By {post.author}</p>
          <p className="mt-6 text-lg leading-relaxed text-muted-foreground">{post.description}</p>
        </div>

        <div className="prose prose-lg mt-12 max-w-none prose-headings:scroll-mt-24 prose-headings:font-serif prose-headings:font-semibold prose-headings:tracking-tight prose-headings:text-foreground prose-h2:mt-12 prose-h3:mt-8 prose-p:leading-[1.75] prose-p:text-muted-foreground prose-a:font-medium prose-a:text-primary prose-a:no-underline hover:prose-a:underline prose-strong:font-semibold prose-strong:text-foreground prose-li:text-muted-foreground prose-li:marker:text-primary/80 prose-blockquote:border-primary prose-blockquote:text-muted-foreground prose-code:rounded prose-code:bg-muted prose-code:px-1 prose-code:text-primary prose-pre:border prose-pre:border-border prose-pre:bg-card">
          <MDXRemote
            source={post.content}
            components={mdxComponents}
            options={{
              mdxOptions: {
                remarkPlugins: [remarkGfm],
                rehypePlugins: [rehypeSlug],
              },
            }}
          />
        </div>
      </article>
    </>
  );
}
