import fs from "fs";
import path from "path";

export type LastmodMap = Record<string, string>;

export function loadPostLastmod(): LastmodMap {
  const file = path.join(process.cwd(), "content/post-lastmod.json");
  if (!fs.existsSync(file)) return {};
  try {
    return JSON.parse(fs.readFileSync(file, "utf8")) as LastmodMap;
  } catch {
    return {};
  }
}

export function lastmodForPost(slug: string, fallbackDate: string, lastmod?: LastmodMap): Date {
  const map = lastmod ?? loadPostLastmod();
  const fromGit = map[slug];
  if (fromGit) {
    const d = new Date(fromGit);
    if (!Number.isNaN(d.getTime())) return d;
  }
  const mdxPath = path.join(process.cwd(), "content/posts", `${slug}.mdx`);
  try {
    return fs.statSync(mdxPath).mtime;
  } catch {
    return new Date(fallbackDate);
  }
}

export function lastmodIsoForPost(slug: string, fallbackDate: string): string {
  const map = loadPostLastmod();
  const fromGit = map[slug];
  if (fromGit) return fromGit;
  return lastmodForPost(slug, fallbackDate, map).toISOString();
}
