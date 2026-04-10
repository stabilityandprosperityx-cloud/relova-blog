import { getAllPosts } from "@/lib/posts";
import BlogIndexClient from "./BlogIndexClient";

export default function BlogIndexPage() {
  const posts = getAllPosts();
  return <BlogIndexClient posts={posts} />;
}
