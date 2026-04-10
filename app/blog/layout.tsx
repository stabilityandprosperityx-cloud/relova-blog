import type { Metadata } from "next";
import { getSiteUrl } from "@/lib/site";

export const metadata: Metadata = {
  title: "Blog",
  description:
    "Relocation guides, visa explainers, and remote-work destination ideas from Relova.",
  alternates: {
    canonical: "/blog",
  },
  openGraph: {
    title: "Relova Blog",
    description:
      "Relocation guides, visa explainers, and remote-work destination ideas from Relova.",
    url: `${getSiteUrl()}/blog`,
    type: "website",
  },
};

export default function BlogLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
