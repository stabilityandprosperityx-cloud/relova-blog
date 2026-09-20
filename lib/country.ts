// Country detection for blog posts, mirroring relova/src/data/countries.ts (63 destinations).
// Used to power the /blog country filter and to pick the cross-link target for a post
// (see scripts used for the Sep 2026 blog<->countries cross-linking batch).

export const COUNTRY_NAMES: Record<string, string> = {
  albania: "Albania",
  argentina: "Argentina",
  armenia: "Armenia",
  australia: "Australia",
  austria: "Austria",
  belgium: "Belgium",
  brazil: "Brazil",
  bulgaria: "Bulgaria",
  canada: "Canada",
  chile: "Chile",
  colombia: "Colombia",
  "costa-rica": "Costa Rica",
  croatia: "Croatia",
  cyprus: "Cyprus",
  "czech-republic": "Czech Republic",
  denmark: "Denmark",
  ecuador: "Ecuador",
  estonia: "Estonia",
  finland: "Finland",
  france: "France",
  georgia: "Georgia",
  germany: "Germany",
  greece: "Greece",
  hungary: "Hungary",
  indonesia: "Indonesia",
  ireland: "Ireland",
  italy: "Italy",
  japan: "Japan",
  latvia: "Latvia",
  lithuania: "Lithuania",
  malaysia: "Malaysia",
  malta: "Malta",
  mexico: "Mexico",
  montenegro: "Montenegro",
  morocco: "Morocco",
  netherlands: "Netherlands",
  "new-zealand": "New Zealand",
  norway: "Norway",
  panama: "Panama",
  paraguay: "Paraguay",
  peru: "Peru",
  philippines: "Philippines",
  poland: "Poland",
  portugal: "Portugal",
  "puerto-rico": "Puerto Rico",
  qatar: "Qatar",
  romania: "Romania",
  serbia: "Serbia",
  singapore: "Singapore",
  slovakia: "Slovakia",
  slovenia: "Slovenia",
  "south-africa": "South Africa",
  "south-korea": "South Korea",
  spain: "Spain",
  sweden: "Sweden",
  switzerland: "Switzerland",
  thailand: "Thailand",
  turkey: "Turkey",
  uae: "United Arab Emirates",
  uk: "United Kingdom",
  uruguay: "Uruguay",
  usa: "United States",
  vietnam: "Vietnam",
};

// city/alias keyword -> country slug. Single-word keys are matched as whole hyphen-tokens
// of the post slug (so "uk" never matches "ukraine"); multi-word keys are matched as a
// hyphenated substring of the slug (low false-positive risk, e.g. "costa-rica").
const ALIASES: Record<string, string[]> = {
  portugal: ["portugal", "lisbon", "porto", "algarve", "madeira", "cascais"],
  spain: ["spain", "madrid", "barcelona", "malaga", "valencia", "seville", "canary"],
  uae: ["dubai", "abu-dhabi", "uae", "emirates"],
  usa: ["usa", "united-states", "america"],
  canada: ["canada", "toronto", "vancouver"],
  germany: ["germany", "berlin", "munich"],
  australia: ["australia", "sydney", "melbourne"],
  thailand: ["thailand", "bangkok", "phuket", "chiang-mai", "koh-samui"],
  mexico: ["mexico", "cdmx", "playa-del-carmen", "oaxaca"],
  estonia: ["estonia", "tallinn"],
  indonesia: ["indonesia", "bali", "lombok", "canggu", "ubud", "seminyak"],
  singapore: ["singapore"],
  argentina: ["argentina", "buenos-aires"],
  italy: ["italy", "milan", "rome", "florence"],
  greece: ["greece", "athens", "greek-islands"],
  croatia: ["croatia", "split", "dubrovnik", "zadar"],
  montenegro: ["montenegro", "kotor"],
  cyprus: ["cyprus"],
  malta: ["malta"],
  france: ["france", "paris", "nice-france"],
  netherlands: ["netherlands", "amsterdam", "rotterdam"],
  belgium: ["belgium", "brussels"],
  austria: ["austria", "vienna"],
  panama: ["panama"],
  "costa-rica": ["costa-rica"],
  colombia: ["colombia", "bogota", "medellin", "cartagena"],
  brazil: ["brazil", "sao-paulo", "rio"],
  peru: ["peru", "lima"],
  uruguay: ["uruguay", "montevideo"],
  ecuador: ["ecuador", "quito"],
  chile: ["chile", "santiago"],
  "puerto-rico": ["puerto-rico"],
  paraguay: ["paraguay", "asuncion"],
  switzerland: ["switzerland", "zurich", "geneva"],
  sweden: ["sweden", "stockholm"],
  norway: ["norway", "oslo"],
  denmark: ["denmark", "copenhagen"],
  finland: ["finland", "helsinki"],
  ireland: ["ireland", "dublin"],
  uk: ["united-kingdom", "london"],
  poland: ["poland", "warsaw", "krakow"],
  "czech-republic": ["czech", "prague"],
  hungary: ["hungary", "budapest"],
  romania: ["romania", "bucharest"],
  bulgaria: ["bulgaria", "sofia"],
  serbia: ["serbia", "belgrade"],
  albania: ["albania", "tirana"],
  georgia: ["georgia", "tbilisi", "batumi", "kutaisi"],
  armenia: ["armenia", "yerevan"],
  latvia: ["latvia", "riga"],
  lithuania: ["lithuania", "vilnius"],
  slovenia: ["slovenia", "ljubljana"],
  slovakia: ["slovakia", "bratislava"],
  philippines: ["philippines", "manila", "cebu"],
  malaysia: ["malaysia", "kuala-lumpur", "langkawi", "penang"],
  vietnam: ["vietnam", "hanoi", "ho-chi-minh", "danang"],
  japan: ["japan", "tokyo", "kyoto", "osaka"],
  "south-korea": ["south-korea", "seoul"],
  turkey: ["turkey", "istanbul"],
  qatar: ["qatar", "doha"],
  morocco: ["morocco", "marrakech", "casablanca"],
  "south-africa": ["south-africa", "cape-town"],
  "new-zealand": ["new-zealand", "auckland", "wellington"],
};

/**
 * Detects a single unambiguous country for a post slug. Returns null when the slug
 * matches zero or more-than-one country (comparison posts like "spain-uk-citizen-guide"
 * are intentionally left unclassified rather than guessing the primary one).
 */
export function detectCountry(slug: string): string | null {
  const tokens = new Set(slug.split("-"));
  const found = new Set<string>();

  for (const [countrySlug, keywords] of Object.entries(ALIASES)) {
    for (const kw of keywords) {
      const kwTokens = kw.split("-");
      if (kwTokens.length === 1) {
        if (tokens.has(kw)) {
          found.add(countrySlug);
          break;
        }
      } else if (slug.includes(kw)) {
        found.add(countrySlug);
        break;
      }
    }
  }
  if (tokens.has("uk")) found.add("uk");

  if (found.size !== 1) return null;
  return Array.from(found)[0];
}

export function countryName(slug: string): string {
  return COUNTRY_NAMES[slug] ?? slug;
}
