import fs from "fs";
import path from "path";
import matter from "gray-matter";

const postsDirectory = path.join(process.cwd(), "content/posts");

export type PostFrontmatter = {
  title: string;
  description: string;
  date: string;
  slug: string;
  author: string;
  ogImage: string;
  category?: string;
};

export type PostListItem = PostFrontmatter;

export type Post = PostFrontmatter & {
  content: string;
};

function parseFrontmatter(data: Record<string, unknown>): PostFrontmatter {
  const required = ["title", "description", "date", "slug", "author", "ogImage"] as const;
  for (const key of required) {
    if (typeof data[key] !== "string" || !(data[key] as string).length) {
      throw new Error(`Missing or invalid frontmatter: ${key}`);
    }
  }
  return {
    ...(data as unknown as PostFrontmatter),
    ...(typeof data.category === "string" ? { category: data.category } : {}),
  };
}

export function getPostSlugs(): string[] {
  if (!fs.existsSync(postsDirectory)) return [];
  return fs
    .readdirSync(postsDirectory)
    .filter((f) => f.endsWith(".mdx"))
    .map((f) => f.replace(/\.mdx$/, ""));
}

export function getPostBySlug(slug: string): Post | null {
  const fullPath = path.join(postsDirectory, `${slug}.mdx`);
  if (!fs.existsSync(fullPath)) return null;
  const raw = fs.readFileSync(fullPath, "utf8");
  const { data, content } = matter(raw);
  const meta = parseFrontmatter(data as Record<string, unknown>);
  if (meta.slug !== slug) {
    throw new Error(`Slug mismatch in ${slug}.mdx: frontmatter slug is "${meta.slug}"`);
  }
  return { ...meta, content };
}

export function getAllPosts(): PostListItem[] {
  return getPostSlugs()
    .map((slug) => {
      const post = getPostBySlug(slug);
      return post
        ? {
            title: post.title,
            description: post.description,
            date: post.date,
            slug: post.slug,
            author: post.author,
            ogImage: post.ogImage,
            ...(post.category ? { category: post.category } : {}),
          }
        : null;
    })
    .filter((p): p is PostListItem => p !== null)
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
}
