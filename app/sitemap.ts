import fs from "fs";
import path from "path";
import type { MetadataRoute } from "next";
import { getAllPosts } from "@/lib/posts";

const SITE = "https://blog.relova.ai";

type LastmodMap = Record<string, string>;

function loadPostLastmod(): LastmodMap {
  const file = path.join(process.cwd(), "content/post-lastmod.json");
  if (!fs.existsSync(file)) return {};
  try {
    return JSON.parse(fs.readFileSync(file, "utf8")) as LastmodMap;
  } catch {
    return {};
  }
}

function lastmodForPost(slug: string, fallbackDate: string, lastmod: LastmodMap): Date {
  const fromGit = lastmod[slug];
  if (fromGit) {
    const d = new Date(fromGit);
    if (!Number.isNaN(d.getTime())) return d;
  }
  // Prefer on-disk mtime over frontmatter publish date when git cache is missing
  const mdxPath = path.join(process.cwd(), "content/posts", `${slug}.mdx`);
  try {
    const st = fs.statSync(mdxPath);
    return st.mtime;
  } catch {
    return new Date(fallbackDate);
  }
}

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
    ...postEntries,
  ];
}
