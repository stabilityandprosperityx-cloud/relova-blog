export type Category = {
  id: string;
  label: string;
  emoji: string;
};

export const CATEGORIES: Category[] = [
  { id: "all", label: "All", emoji: "🌐" },
  { id: "country", label: "Country Guides", emoji: "🌍" },
  { id: "city", label: "City Guides", emoji: "🏙️" },
  { id: "visa", label: "Visas & Residency", emoji: "📋" },
  { id: "tax", label: "Taxes & Finance", emoji: "💰" },
  { id: "work", label: "Work & Freelance", emoji: "💼" },
  { id: "living", label: "Housing & Living", emoji: "🏠" },
  { id: "lifestyle", label: "Lifestyle", emoji: "✈️" },
];

export function detectCategory(slug: string, frontmatterCategory?: string): string {
  if (frontmatterCategory) return frontmatterCategory;

  const s = slug.toLowerCase();

  // City guides (check before country — more specific)
  if (
    s.includes("neighborhood") ||
    s.includes("lisbon-vs-porto") ||
    s.includes("bangkok-vs-chiang") ||
    s.includes("madrid-vs-barcelona") ||
    s.includes("best-cities") ||
    s.includes("best-coworking")
  )
    return "city";

  // Country guides
  if (
    s.startsWith("move-to-") ||
    s.startsWith("moving-to-") ||
    s.includes("expat-guide") ||
    s.includes("expat-life")
  )
    return "country";

  // Visas & Residency
  if (
    s.includes("visa") ||
    s.includes("residency") ||
    s.includes("citizenship") ||
    s.includes("passport") ||
    s.includes("permit") ||
    s.includes("permanent-residency") ||
    s.includes("schengen") ||
    s.includes("etias") ||
    s.includes("eu-citizenship") ||
    s.includes("second-passport")
  )
    return "visa";

  // Taxes & Finance
  if (
    s.includes("tax") ||
    s.includes("finance") ||
    s.includes("invest") ||
    s.includes("banking") ||
    s.includes("money") ||
    s.includes("cost-of-living") ||
    s.includes("cost-of-relocating") ||
    s.includes("salary") ||
    s.includes("crypto") ||
    s.includes("renounce")
  )
    return "tax";

  // Work & Freelance
  if (
    s.includes("freelanc") ||
    s.includes("remote-work") ||
    s.includes("work-abroad") ||
    s.includes("working-abroad") ||
    s.includes("job") ||
    s.includes("teaching") ||
    s.includes("developer") ||
    s.includes("nurse") ||
    s.includes("doctor") ||
    s.includes("negotiate") ||
    s.includes("open-company") ||
    s.includes("digital-nomad-tax") ||
    s.includes("nomad-burnout")
  )
    return "work";

  // Housing & Living
  if (
    s.includes("apartment") ||
    s.includes("rent") ||
    s.includes("housing") ||
    s.includes("property") ||
    s.includes("buy-property") ||
    s.includes("shipping") ||
    s.includes("bank-account") ||
    s.includes("send-money") ||
    s.includes("insurance") ||
    s.includes("health-insurance") ||
    s.includes("healthcare")
  )
    return "living";

  // Lifestyle
  if (
    s.includes("family") ||
    s.includes("pets") ||
    s.includes("school") ||
    s.includes("homeschool") ||
    s.includes("mental-health") ||
    s.includes("culture-shock") ||
    s.includes("language") ||
    s.includes("social") ||
    s.includes("burnout") ||
    s.includes("scouting") ||
    s.includes("checklist") ||
    s.includes("no-money") ||
    s.includes("home-country") ||
    s.includes("retire") ||
    s.includes("ai-tools") ||
    s.includes("cheapest") ||
    s.includes("countries-pay")
  )
    return "lifestyle";

  return "country";
}
