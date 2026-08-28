export type Author = {
  name: string;
  slug: string;
  path: string;
  jobTitle: string;
  paragraphs: string[];
  knowsAbout: string[];
  hasCredential: {
    "@type": "EducationalOccupationalCredential";
    name: string;
  };
};

export const AUTHORS: Record<string, Author> = {
  "Anna Moore": {
    name: "Anna Moore",
    slug: "anna-moore",
    path: "/author/anna-moore",
    jobTitle: "Founder",
    paragraphs: [
      "Anna Moore is the founder of Relova, a relocation planning product that helps people compare countries, understand visa and document steps, and turn scattered research into a clearer move plan. Anna holds a law degree and spent over 10 years working in the legal field, including at a relocation company in Cyprus. Anna’s interest in the topic is also personal: a relocation path that ran Russia → Cyprus → Georgia → Cyprus.",
      "Anna researches and verifies visa thresholds, tax regimes, and cost-of-living data across countries, and writes the Relova Blog so readers can navigate relocation with accurate, up-to-date information — then confirm the current rule with official sources and a qualified professional.",
      "The Relova Blog is not a substitute for legal or immigration advice.",
    ],
    knowsAbout: ["Relocation planning", "Visa requirements", "Legal research"],
    hasCredential: {
      "@type": "EducationalOccupationalCredential",
      name: "Law degree",
    },
  },
};

export const DEFAULT_AUTHOR = AUTHORS["Anna Moore"];

export function getAuthorByName(name: string): Author {
  return AUTHORS[name] ?? DEFAULT_AUTHOR;
}

export function getAuthorBySlug(slug: string): Author | undefined {
  return Object.values(AUTHORS).find((author) => author.slug === slug);
}

export function getAllAuthors(): Author[] {
  return Object.values(AUTHORS);
}
