export type Category = {
  id: string;
  label: string;
  emoji: string;
};

export const CATEGORIES: Category[] = [
  { id: "all",       label: "All",               emoji: "🌐" },
  { id: "country",   label: "Country Guides",    emoji: "🌍" },
  { id: "city",      label: "City Guides",        emoji: "🏙️" },
  { id: "visa",      label: "Visas & Residency",  emoji: "📋" },
  { id: "tax",       label: "Taxes & Finance",    emoji: "💰" },
  { id: "work",      label: "Work & Freelance",   emoji: "💼" },
  { id: "living",    label: "Housing & Living",   emoji: "🏠" },
  { id: "lifestyle", label: "Lifestyle",           emoji: "✈️" },
  { id: "retire",    label: "Retirement",          emoji: "🌴" },
];

// City-level slugs: specific cities/neighborhoods/comparisons within a country
const CITY_SLUGS = [
  // Neighborhood guides
  "neighborhood", "quartier",
  // City vs city comparisons
  "lisbon-vs-porto", "lisbon-vs-madrid", "bangkok-vs-chiang",
  "madrid-vs-barcelona", "dubai-vs-abu-dhabi", "singapore-vs-hong-kong",
  "bali-vs-thailand", "lisbon-vs-porto-vs-algarve",
  "medellin-vs-bogota", "kuala-lumpur-vs-penang",
  "tbilisi-vs-batumi", "canggu-vs-ubud",
  // Specific city guides (not country-level)
  "move-to-tokyo", "move-to-bangkok", "move-to-milan", "move-to-rome",
  "move-to-florence", "move-to-kuala-lumpur", "move-to-buenos-aires",
  "move-to-penang", "move-to-fukuoka", "move-to-chiang-mai",
  "move-to-phuket", "move-to-valencia-spain", "move-to-malaga",
  "move-to-tenerife", "move-to-bogota", "move-to-algarve",
  "move-to-madeira", "move-to-azores", "move-to-lisbon",
  "move-to-porto", "move-to-athens", "move-to-budapest",
  "move-to-belgrade", "move-to-tallinn", "move-to-prague",
  "move-to-warsaw", "move-to-berlin", "move-to-vienna",
  "move-to-stockholm", "move-to-amsterdam", "move-to-tbilisi",
  "move-to-batumi", "move-to-kotor", "move-to-medellin",
  "move-to-panama-city", "move-to-oaxaca", "move-to-playa-del-carmen",
  "move-to-mexico-city", "move-to-ho-chi-minh", "move-to-hanoi",
  "move-to-da-nang", "move-to-nairobi", "move-to-kyoto-osaka",
  "move-to-abu-dhabi", "move-to-dubai-freelancer",
  "move-to-south-france", "move-to-cape-town",
  "move-to-slovenia", "move-to-north-macedonia",
  "move-to-albania-riviera", "move-to-kotor",
  "move-to-greek-islands",
  // City-specific setup/budget/checklist
  "tbilisi-neighborhood", "tbilisi-digital-nomad-setup",
  "tbilisi-first-week", "tbilisi-budget",
  "lisbon-budget", "lisbon-freelancer-setup", "lisbon-ultimate-setup",
  "lisbon-american-taxes", "lisbon-american-guide",
  "lisbon-family", "retire-to-lisbon",
  "move-to-barcelona-nomad",
  "dubai-remote-worker",
  "best-cities", "best-coworking",
  // Batch 7 cities
  "move-to-osaka", "move-to-busan", "move-to-vancouver",
  "move-to-sydney-melbourne", "move-to-sao-paulo", "move-to-santiago",
  "move-to-lima", "move-to-zurich-geneva", "move-to-scotland",
  "move-to-tel-aviv", "move-to-amman", "move-to-oman",
  "move-to-maldives", "lisbon-vs-barcelona", "dubai-vs-singapore",
  "cape-town-vs-nairobi", "portugal-vs-italy-vs-greece",
  "tbilisi-complete", "move-to-cape-verde",
  "move-to-sri-lanka", "move-to-cambodia", "move-to-peru",
  "move-to-chile", "move-to-iceland", "move-to-slovakia",
];

// Retirement slugs
const RETIRE_SLUGS = [
  "retire-to-", "retire-abroad", "retire-europe",
  "pension-abroad", "social-security",
  "retire-to-lisbon", "retire-to-spain", "retire-to-greece",
  "retire-to-portugal",
];

export function detectCategory(slug: string, frontmatterCategory?: string): string {
  if (frontmatterCategory) return frontmatterCategory;

  const s = slug.toLowerCase();

  // 1. Retirement (check before lifestyle — retire- overlaps)
  if (RETIRE_SLUGS.some((k) => s.includes(k))) return "retire";

  // 2. City guides (check before country — more specific)
  if (CITY_SLUGS.some((k) => s.includes(k))) return "city";

  // 3. Visas & Residency
  if (
    s.includes("visa") ||
    s.includes("residency") ||
    s.includes("citizenship") ||
    s.includes("passport") ||
    s.includes("permit") ||
    s.includes("schengen") ||
    s.includes("etias") ||
    s.includes("second-passport") ||
    s.includes("apostille") ||
    s.includes("nie-number") ||
    s.includes("nif-number") ||
    s.includes("permanent-residency")
  ) return "visa";

  // 4. Taxes & Finance
  if (
    s.includes("tax") ||
    s.includes("invest") ||
    s.includes("banking") ||
    s.includes("send-money") ||
    s.includes("cost-of-living") ||
    s.includes("cost-of-relocating") ||
    s.includes("salary") ||
    s.includes("crypto") ||
    s.includes("renounce") ||
    s.includes("expat-banking") ||
    s.includes("visa-fees")
  ) return "tax";

  // 5. Work & Freelance
  if (
    s.includes("freelanc") ||
    s.includes("remote-work") ||
    s.includes("work-abroad") ||
    s.includes("working-abroad") ||
    s.includes("job") ||
    s.includes("teaching") ||
    s.includes("developer") ||
    s.includes("designer") ||
    s.includes("lawyer") ||
    s.includes("negotiate") ||
    s.includes("open-company") ||
    s.includes("digital-nomad-tax") ||
    s.includes("nomad-burnout") ||
    s.includes("remote-job") ||
    s.includes("visa-sponsorship") ||
    s.includes("healthcare-professional") ||
    s.includes("entrepreneur") ||
    s.includes("entrepass") ||
    s.includes("time-zones") ||
    s.includes("remote-work-tools") ||
    s.includes("starlink")
  ) return "work";

  // 6. Housing & Living
  if (
    s.includes("apartment") ||
    s.includes("rent") ||
    s.includes("housing") ||
    s.includes("property") ||
    s.includes("buy-property") ||
    s.includes("shipping") ||
    s.includes("bank-account") ||
    s.includes("open-bank") ||
    s.includes("insurance") ||
    s.includes("health-insurance") ||
    s.includes("healthcare") ||
    s.includes("long-term-accommodation") ||
    s.includes("driving-license") ||
    s.includes("car-motorbike") ||
    s.includes("power-of-attorney") ||
    s.includes("inheritance") ||
    s.includes("medical-tourism") ||
    s.includes("dental-tourism") ||
    s.includes("vpn")
  ) return "living";

  // 7. Lifestyle
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
    s.includes("ai-tools") ||
    s.includes("cheapest") ||
    s.includes("countries-pay") ||
    s.includes("homesickness") ||
    s.includes("lgbt") ||
    s.includes("solo-female") ||
    s.includes("vegan") ||
    s.includes("expat-communities") ||
    s.includes("mental-health-support") ||
    s.includes("culture-shock") ||
    s.includes("best-expat-communities")
  ) return "lifestyle";

  // 8. Country guides (default for move-to- and general country articles)
  if (
    s.startsWith("move-to-") ||
    s.startsWith("moving-to-") ||
    s.includes("expat-guide") ||
    s.includes("expat-life")
  ) return "country";

  return "country";
}
