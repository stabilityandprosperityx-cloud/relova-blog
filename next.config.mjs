/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  transpilePackages: ["next-mdx-remote"],
  async redirects() {
    return [
      {
        source: "/blog/best-countries-expats-2025-comparison",
        destination: "/blog/best-countries-expats-2026-comparison",
        permanent: true,
      },
      {
        source: "/blog/best-countries-remote-workers-2025",
        destination: "/blog/best-countries-remote-workers-2026",
        permanent: true,
      },
      {
        source: "/blog/best-health-insurance-expats-europe-2025",
        destination: "/blog/best-health-insurance-expats-europe-2026",
        permanent: true,
      },
      {
        source: "/blog/cost-of-relocating-to-europe-2025",
        destination: "/blog/cost-of-relocating-to-europe-2026",
        permanent: true,
      },
      {
        source: "/blog/digital-nomad-visa-complete-guide-2025",
        destination: "/blog/digital-nomad-visa-complete-guide-2026",
        permanent: true,
      },
      {
        source: "/blog/how-to-open-bank-account-abroad-2025",
        destination: "/blog/how-to-open-bank-account-abroad-2026",
        permanent: true,
      },
      {
        source: "/blog/portugal-vs-spain-vs-georgia-relocation-2025",
        destination: "/blog/portugal-vs-spain-vs-georgia-relocation-2026",
        permanent: true,
      },
      {
        source: "/blog/ultimate-relocation-checklist-2025",
        destination: "/blog/ultimate-relocation-checklist-2026",
        permanent: true,
      },
      {
        source: "/blog/visa-cover-letter-guide-2025",
        destination: "/blog/visa-cover-letter-guide-2026",
        permanent: true,
      },
    ];
  },
};

export default nextConfig;
