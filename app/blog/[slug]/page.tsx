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
        <div className="rounded-xl border border-accent/10 bg-card px-5 py-8 sm:px-8 sm:py-10">
          <p className="text-[13px] font-medium">
            <Link href="/blog" className="text-accent transition-colors hover:text-accent/85">
              Blog
            </Link>
            <span className="mx-2 text-white/20">/</span>
            <span className="tabular-nums text-muted">{formatDate(post.date)}</span>
          </p>
          <h1 className="mt-4 text-3xl font-semibold tracking-tight text-white sm:text-[2.25rem] sm:leading-[1.15]">
            {post.title}
          </h1>
          <p className="mt-3 text-sm text-muted">By {post.author}</p>
          <p className="mt-6 text-lg leading-relaxed text-muted">{post.description}</p>
        </div>

        <div className="prose prose-lg prose-invert mt-12 max-w-none prose-headings:scroll-mt-24 prose-headings:font-semibold prose-headings:tracking-tight prose-h2:mt-12 prose-h2:text-white prose-h3:mt-8 prose-h3:text-white prose-p:leading-[1.75] prose-a:font-medium prose-a:text-accent prose-a:no-underline hover:prose-a:text-accent/90 hover:prose-a:underline prose-strong:font-semibold prose-strong:text-white prose-li:marker:text-accent/80">
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
