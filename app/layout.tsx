import type { Metadata } from "next";
import { GoogleAnalytics } from "@next/third-parties/google";
import "./globals.css";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { getSiteUrl } from "@/lib/site";

const GA_MEASUREMENT_ID = "G-KE26E43W5L";

const siteUrl = getSiteUrl();

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: "Relova Blog",
    template: "%s · Relova Blog",
  },
  description:
    "Practical guides on visas, remote work abroad, and moving overseas — from the team at Relova.",
  openGraph: {
    type: "website",
    locale: "en_US",
    siteName: "Relova Blog",
    url: siteUrl,
    // Site-wide fallback OG image — this file already existed in public/
    // but was referenced nowhere, so any page without its own og image
    // (root layout default, /blog, /about) had none at all in social
    // share previews. Individual blog posts still set their own via
    // post.ogImage in generateMetadata (app/blog/[slug]/page.tsx).
    images: [{ url: `${siteUrl}/images/blog-default.jpg`, width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    images: [`${siteUrl}/images/blog-default.jpg`],
  },
};

const themeInitScript = `(function(){try{if(localStorage.getItem('relova-theme')==='dark'){document.documentElement.classList.add('dark');}}catch(e){}})();`;

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeInitScript }} />
      </head>
      <body className="flex min-h-screen flex-col font-sans selection:bg-primary/20 selection:text-foreground">
        <Header />
        <main className="flex-1">{children}</main>
        <Footer />
        <GoogleAnalytics gaId={GA_MEASUREMENT_ID} />
      </body>
    </html>
  );
}
