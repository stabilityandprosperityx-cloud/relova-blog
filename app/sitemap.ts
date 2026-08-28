import type { MetadataRoute } from "next";
import { getAllAuthors } from "@/lib/authors";
import { getAllPosts } from "@/lib/posts";
import { lastmodForPost, loadPostLastmod } from "@/lib/post-lastmod";

const SITE = "https://blog.relova.ai";

export default function sitemap(): MetadataRoute.Sitemap {
  const posts = getAllPosts();
  const lastmod = loadPostLastmod();

  let newestPost = new Date(0);
  const postEntries: MetadataRoute.Sitemap = posts.map((post) => {
    const modified = lastmodForPost(post.slug, post.date, lastmod);
    if (modified > newestPost) newestPost = modified;
    return {
      url: `${SITE}/blog/${post.slug}`,
      lastModified: modified,
      changeFrequency: "monthly",
      priority: 0.8,
    };
  });

  const indexLastmod = newestPost.getTime() > 0 ? newestPost : new Date();

  return [
    {
      url: SITE,
      lastModified: indexLastmod,
      changeFrequency: "weekly",
      priority: 1,
    },
    {
      url: `${SITE}/blog`,
      lastModified: indexLastmod,
      changeFrequency: "weekly",
      priority: 0.9,
    },
    {
      url: `${SITE}/about`,
      lastModified: indexLastmod,
      changeFrequency: "monthly",
      priority: 0.6,
    },
    ...getAllAuthors().map((author) => ({
      url: `${SITE}${author.path}`,
      lastModified: indexLastmod,
      changeFrequency: "monthly" as const,
      priority: 0.6,
    })),
    ...postEntries,
  ];
}
