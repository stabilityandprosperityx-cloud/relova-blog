import { getAuthorByName } from "@/lib/authors";
import { lastmodIsoForPost } from "@/lib/post-lastmod";
import { absoluteUrl } from "@/lib/site";
import type { PostFrontmatter } from "@/lib/posts";

type Props = {
  post: PostFrontmatter;
  url: string;
};

export function BlogPostingJsonLd({ post, url }: Props) {
  const imageUrl = absoluteUrl(post.ogImage);
  const author = getAuthorByName(post.author);
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "Article",
    headline: post.title,
    description: post.description,
    image: [imageUrl],
    datePublished: post.date,
    dateModified: lastmodIsoForPost(post.slug, post.date),
    author: {
      "@type": "Person",
      name: author.name,
      url: absoluteUrl(author.path),
      knowsAbout: author.knowsAbout,
      hasCredential: author.hasCredential,
    },
    publisher: {
      "@type": "Organization",
      name: "Relova",
      url: "https://relova.ai",
    },
    mainEntityOfPage: {
      "@type": "WebPage",
      "@id": url,
    },
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
    />
  );
}
