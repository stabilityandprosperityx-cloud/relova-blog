# Structure templating audit — H2 skeletons

- Total posts: **410**
- Unique exact H2 sequences: **294**
- Posts with a unique exact skeleton: **238**
- Posts sharing a skeleton with ≥1 other post: **172**
- Unique role-normalized skeletons: **86**

## Top-5 most common exact H2 skeletons

### #1 — 12 articles

_(no H2 headings)_

Examples: `austria-red-white-red-card-guide-2026`, `best-countries-expats-2025-comparison`, `best-health-insurance-expats-europe-2025`, `build-social-life-after-relocating-abroad`, `cost-of-relocating-to-europe-2025`, `digital-nomad-visa-complete-guide-2025`, `how-to-find-apartment-abroad-before-you-arrive`, `how-to-open-bank-account-abroad-2025` (+4 more)

### #2 — 9 articles

- Table of Contents
- The practical details that shape daily life
- At a glance
- Frequently Asked Questions

Examples: `etias-explained-expats-2026`, `expat-health-insurance-complete-guide-2026`, `lgbt-expat-guide-2026`, `move-to-finland-guide-2026`, `move-to-thessaloniki-guide-2026`, `renounce-us-citizenship-guide-2026`, `retire-abroad-complete-planning-guide-2026`, `software-developer-working-abroad-2026` (+1 more)

### #3 — 7 articles

- Table of Contents
- Neighborhoods, logistics, and settling in
- Quick-reference data
- Frequently Asked Questions

Examples: `buy-property-abroad-foreigner-2026`, `cheapest-countries-europe-2026`, `move-abroad-no-money-guide-2026`, `move-to-bulgaria-guide-2026`, `move-to-medellin-guide-2026`, `move-to-serbia-guide-2026`, `move-to-sweden-guide-2026`

### #4 — 6 articles

- Table of Contents
- Getting set up: connectivity, transport, and community
- At a glance
- Frequently Asked Questions

Examples: `move-to-abu-dhabi-guide-2026`, `move-to-gdansk-guide-2026`, `move-to-uruguay-guide-2026`, `musician-artist-working-abroad-2026`, `relocation-scouting-trip-guide-2026`, `voting-abroad-expat-guide-2026`

### #5 — 5 articles

- Table of Contents
- Neighborhoods, logistics, and settling in
- The figures that matter
- Frequently Asked Questions

Examples: `australia-permanent-residency-guide-2026`, `best-coworking-spaces-digital-nomads-2026`, `countries-pay-you-to-move-2026`, `house-sitting-abroad-guide-2026`, `move-to-uk-guide-2026`

## Top-10 role-normalized skeletons

Role labels collapse location-specific wording (VISA / COSTS / PRACTICAL / KEY_DATA / FAQ, etc.).

| count | role skeleton |
| ---: | --- |
| 76 | `TOC → VISA → COSTS → PRACTICAL → KEY_DATA → FAQ` |
| 53 | `TOC → PRACTICAL → KEY_DATA → FAQ` |
| 51 | `TOC → COSTS → PRACTICAL → KEY_DATA → FAQ` |
| 28 | `TOC → VISA → COSTS → KEY_DATA → FAQ` |
| 24 | `TOC → VISA → COSTS → NEIGHBORHOODS → KEY_DATA → FAQ` |
| 21 | `TOC → VISA → COSTS → SETUP → COSTS → WORK → FAQ` |
| 18 | `TOC → NEIGHBORHOODS → KEY_DATA → FAQ` |
| 14 | `TOC → COSTS → KEY_DATA → FAQ` |
| 13 | `TOC → COSTS → NEIGHBORHOODS → KEY_DATA → FAQ` |
| 12 | `(no H2)` |

## All exact skeletons with count ≥ 3

| count | H2 sequence |
| ---: | --- |
| 12 | (no H2) |
| 9 | Table of Contents → The practical details that shape daily life → At a glance → Frequently Asked Questions |
| 7 | Table of Contents → Neighborhoods, logistics, and settling in → Quick-reference data → Frequently Asked Questions |
| 6 | Table of Contents → Getting set up: connectivity, transport, and community → At a glance → Frequently Asked Questions |
| 5 | Table of Contents → Neighborhoods, logistics, and settling in → The figures that matter → Frequently Asked Questions |
| 5 | Table of Contents → Practical logistics and daily life → Quick-reference data → Frequently Asked Questions |
| 5 | Table of Contents → Getting set up: connectivity, transport, and community → Quick-reference data → Frequently Asked Questions |
| 5 | Table of Contents → Practical logistics and daily life → The figures that matter → Frequently Asked Questions |
| 5 | Table of Contents → Neighborhoods, logistics, and settling in → Key numbers at a glance → Frequently Asked Questions |
| 5 | Table of Contents → Getting set up: connectivity, transport, and community → Key numbers at a glance → Frequently Asked Questions |
| 4 | Table of Contents → The practical details that shape daily life → Key numbers at a glance → Frequently Asked Questions |
| 4 | Table of Contents → Practical logistics and daily life → At a glance → Frequently Asked Questions |
| 3 | Table of Contents → Getting set up: connectivity, transport, and community → The figures that matter → Frequently Asked Questions |
| 3 | Table of Contents → Money: rent, taxes, and monthly burn → Practical logistics and daily life → At a glance → Frequently Asked Questions |
| 3 | Table of Contents → Money: rent, taxes, and monthly burn → Getting set up: connectivity, transport, and community → Quick-reference data → Frequently Asked Questions |
| 3 | Table of Contents → Costs, rent, and a realistic budget → Getting set up: connectivity, transport, and community → Key numbers at a glance → Frequently Asked Questions |
| 3 | Table of Contents → Immigration: which route actually fits → What it actually costs each month → The practical details that shape daily life → At a glance → Frequently Asked Que… |
| 3 | Table of Contents → Money: rent, taxes, and monthly burn → Getting set up: connectivity, transport, and community → The figures that matter → Frequently Asked Questions |
| 3 | Table of Contents → Rent, budget, and the real monthly numbers → Practical logistics and daily life → Quick-reference data → Frequently Asked Questions |
| 3 | Table of Contents → Immigration: which route actually fits → What it actually costs each month → The practical details that shape daily life → Key numbers at a glance → Frequent… |
| 3 | Table of Contents → The practical details that shape daily life → The figures that matter → Frequently Asked Questions |
| 3 | Table of Contents → What it actually costs each month → Neighborhoods, logistics, and settling in → Quick-reference data → Frequently Asked Questions |
| 3 | Table of Contents → Visa routes, permits, and lawful status → Rent, budget, and the real monthly numbers → Practical logistics and daily life → Quick-reference data → Frequently… |
| 3 | Table of Contents → What it actually costs each month → The practical details that shape daily life → The figures that matter → Frequently Asked Questions |

## Verdict

Exact H2 strings were diversified during earlier dedup (294 unique sequences), but **role-level** structure remains highly templated: most articles still follow TOC → (visa/costs/practical variants) → key-data table → FAQ. That pattern is a programmatic-content signal even when paragraph text differs.

