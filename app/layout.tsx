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
  },
  twitter: {
    card: "summary_large_image",
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
