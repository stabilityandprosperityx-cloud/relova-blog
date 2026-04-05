import { absoluteUrl } from "@/lib/site";
import type { PostFrontmatter } from "@/lib/posts";

type Props = {
  post: PostFrontmatter;
  url: string;
};

export function BlogPostingJsonLd({ post, url }: Props) {
  const imageUrl = absoluteUrl(post.ogImage);
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    headline: post.title,
    description: post.description,
    image: [imageUrl],
    datePublished: post.date,
    dateModified: post.date,
    author: {
      "@type": "Person",
      name: post.author,
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
