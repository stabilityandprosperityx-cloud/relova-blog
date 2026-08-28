import type { Metadata } from "next";
import Link from "next/link";
import { DEFAULT_AUTHOR } from "@/lib/authors";
import { absoluteUrl } from "@/lib/site";

export const metadata: Metadata = {
  title: "About",
  description:
    "Who writes the Relova Blog, how relocation guides are researched, and how to get in touch.",
  alternates: {
    canonical: "/about",
  },
  openGraph: {
    title: "About Relova Blog",
    description:
      "Who writes the Relova Blog, how relocation guides are researched, and how to get in touch.",
    url: absoluteUrl("/about"),
    type: "website",
  },
};

export default function AboutPage() {
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "AboutPage",
    name: "About Relova Blog",
    url: absoluteUrl("/about"),
    mainEntity: {
      "@type": "Person",
      name: DEFAULT_AUTHOR.name,
      url: absoluteUrl(DEFAULT_AUTHOR.path),
      jobTitle: DEFAULT_AUTHOR.jobTitle,
      worksFor: {
        "@type": "Organization",
        name: "Relova",
        url: "https://relova.ai",
      },
    },
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <article className="mx-auto max-w-3xl px-4 py-14 sm:px-6 sm:py-20">
        <div className="rounded-xl border border-border bg-card px-5 py-8 sm:px-8 sm:py-10">
          <p className="text-[13px] font-medium">
            <Link href="/blog" className="text-primary transition-colors hover:text-primary/85">
              Blog
            </Link>
            <span className="mx-2 text-muted-foreground/40">/</span>
            <span className="text-muted-foreground">About</span>
          </p>
          <h1 className="mt-4 text-3xl font-semibold tracking-tight text-foreground sm:text-[2.25rem] sm:leading-[1.15]">
            About Relova Blog
          </h1>
        </div>

        <div className="prose prose-lg mt-12 max-w-none prose-headings:font-serif prose-headings:font-semibold prose-headings:tracking-tight prose-headings:text-foreground prose-p:leading-[1.75] prose-p:text-muted-foreground prose-a:font-medium prose-a:text-primary prose-a:no-underline hover:prose-a:underline">
          <p>
            Relova is a relocation planning product, and this blog is where we publish the
            research behind it. It is written by{" "}
            <Link href={DEFAULT_AUTHOR.path}>{DEFAULT_AUTHOR.name}</Link>, Relova’s founder — not
            by a large newsroom, and not by licensed immigration lawyers.
          </p>
          <p>
            The problem we started with is familiar if you have ever tried to move countries: visa
            rules, tax thresholds, and cost-of-living numbers live in scattered forums, outdated
            blogs, and government PDFs that do not talk to each other. Relova exists to turn that
            mess into a clearer plan. The blog exists to show the same work in the open — country
            and city guides, visa explainers, and practical setup notes that you can check against
            official sources.
          </p>
          <p>
            How we prepare these articles: we collect and verify current figures on visa programs,
            income floors, tax regimes, and typical living costs, then update pieces when
            legislation or publicly cited thresholds change. Where a number is a planning range
            rather than a statute, we say so. Relova is not legal, tax, or immigration advice. We
            do not represent you before a consulate, and we do not guarantee visa outcomes. For a
            decision that affects your status, money, or family, confirm the current rule with the
            relevant government authority and a qualified professional in that jurisdiction.
          </p>
          <p>
            If something in an article looks wrong or out of date, or you have a question about
            the product, write to{" "}
            <a href="mailto:support@relova.ai">support@relova.ai</a> or use the contact form at{" "}
            <a href="https://relova.ai/contact">relova.ai/contact</a>.
          </p>
          <p>
            To read who writes this blog: <Link href={DEFAULT_AUTHOR.path}>{DEFAULT_AUTHOR.name}</Link>.
            <br />
            To use the planning product: <a href="https://relova.ai">relova.ai</a>.
          </p>
        </div>
      </article>
    </>
  );
}
