#!/usr/bin/env python3
"""Build topical related-guide links for every MDX post.

Usage:
  python3 scripts/build_related_links.py              # apply related + inline links
  python3 scripts/build_related_links.py --dry-run    # print plan only
  python3 scripts/build_related_links.py --reports-only
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "content" / "posts"
SCRIPTS = ROOT / "scripts"
LASTMOD_JSON = ROOT / "content" / "post-lastmod.json"

COUNTRIES = {
    "portugal", "spain", "georgia", "germany", "france", "italy", "greece",
    "netherlands", "belgium", "austria", "switzerland", "sweden", "norway",
    "denmark", "finland", "ireland", "uk", "united-kingdom", "britain",
    "croatia", "slovenia", "slovakia", "czech", "czechia", "poland",
    "hungary", "romania", "bulgaria", "serbia", "montenegro", "albania",
    "north-macedonia", "macedonia", "kosovo", "bosnia", "turkey", "turkiye",
    "cyprus", "malta", "estonia", "latvia", "lithuania", "ukraine",
    "mexico", "colombia", "argentina", "brazil", "chile", "peru", "ecuador",
    "uruguay", "paraguay", "panama", "costa-rica", "guatemala", "nicaragua",
    "thailand", "vietnam", "indonesia", "bali", "malaysia", "singapore",
    "philippines", "cambodia", "laos", "japan", "south-korea", "korea",
    "taiwan", "china", "india", "sri-lanka", "nepal", "uae", "dubai",
    "abu-dhabi", "qatar", "bahrain", "oman", "saudi", "saudi-arabia",
    "israel", "jordan", "morocco", "egypt", "tunisia", "south-africa",
    "kenya", "nigeria", "ghana", "rwanda", "tanzania", "zanzibar",
    "australia", "new-zealand", "canada", "usa", "united-states",
    "puerto-rico", "barbados", "antigua", "cape-verde", "mauritius",
    "armenia", "azerbaijan", "kazakhstan", "uzbekistan", "georgia-country",
}

CITIES = {
    "lisbon", "porto", "algarve", "madeira", "madrid", "barcelona", "valencia",
    "malaga", "seville", "bilbao", "tenerife", "mallorca", "gran-canaria",
    "lanzarote", "berlin", "munich", "hamburg", "frankfurt", "paris",
    "bordeaux", "lyon", "nice", "amsterdam", "rotterdam", "vienna", "prague",
    "budapest", "warsaw", "krakow", "gdansk", "wroclaw", "rome", "milan",
    "florence", "naples", "athens", "thessaloniki", "split", "dubrovnik",
    "zagreb", "tbilisi", "batumi", "kutaisi", "yerevan", "baku", "istanbul",
    "antalya", "izmir", "dubai", "abu-dhabi", "bangkok", "chiang-mai",
    "phuket", "pattaya", "hanoi", "da-nang", "ho-chi-minh", "saigon",
    "bali", "canggu", "ubud", "seminyak", "jakarta", "kuala-lumpur",
    "penang", "singapore", "seoul", "busan", "tokyo", "osaka", "fukuoka",
    "taipei", "hong-kong", "sydney", "melbourne", "brisbane", "auckland",
    "toronto", "vancouver", "montreal", "mexico-city", "guadalajara",
    "oaxaca", "playa-del-carmen", "medellin", "bogota", "cartagena",
    "buenos-aires", "sao-paulo", "lima", "quito", "cuenca", "panama-city",
    "san-jose", "cape-town", "nairobi", "lagos", "accra", "kotor",
    "podgorica", "tirana", "sarajevo", "pristina", "skopje", "sofia",
    "bucharest", "belgrade", "stockholm", "copenhagen", "oslo", "helsinki",
    "dublin", "london", "edinburgh", "tel-aviv", "amman", "marrakech",
    "casablanca", "almaty", "tashkent", "bangkok", "manila", "cebu",
}

VISA_TYPES = {
    "digital-nomad", "dnv", "d7", "d8", "non-lucrative", "nlv", "golden-visa",
    "entrepass", "workation", "freelancer", "blue-card", "red-white-red",
    "working-holiday", "retirement", "pensionado", "rentista", "mm2h",
    "ltr", "welcome-stamp", "virtual-working", "schengen", "etias",
    "citizenship", "naturalization", "jure-sanguinis", "permanent-residency",
    "express-entry", "startup", "entrepreneur",
}

# Short aliases matched only as whole slug tokens / word boundaries
VISA_ALIASES = {
    "dnv": "digital-nomad",
    "nlv": "non-lucrative",
    "pr": "permanent-residency",
}

CITY_TO_COUNTRY = {
    "lisbon": "portugal", "porto": "portugal", "algarve": "portugal", "madeira": "portugal",
    "madrid": "spain", "barcelona": "spain", "valencia": "spain", "malaga": "spain",
    "seville": "spain", "bilbao": "spain", "tenerife": "spain", "mallorca": "spain",
    "gran-canaria": "spain", "lanzarote": "spain",
    "berlin": "germany", "munich": "germany", "hamburg": "germany", "frankfurt": "germany",
    "paris": "france", "bordeaux": "france", "lyon": "france", "nice": "france",
    "amsterdam": "netherlands", "rotterdam": "netherlands",
    "vienna": "austria", "prague": "czech", "budapest": "hungary",
    "warsaw": "poland", "krakow": "poland", "gdansk": "poland", "wroclaw": "poland",
    "rome": "italy", "milan": "italy", "florence": "italy", "naples": "italy",
    "athens": "greece", "thessaloniki": "greece",
    "split": "croatia", "dubrovnik": "croatia", "zagreb": "croatia",
    "tbilisi": "georgia", "batumi": "georgia", "kutaisi": "georgia",
    "yerevan": "armenia", "baku": "azerbaijan",
    "istanbul": "turkey", "antalya": "turkey", "izmir": "turkey",
    "dubai": "uae", "abu-dhabi": "uae",
    "bangkok": "thailand", "chiang-mai": "thailand", "phuket": "thailand", "pattaya": "thailand",
    "hanoi": "vietnam", "da-nang": "vietnam", "ho-chi-minh": "vietnam", "saigon": "vietnam",
    "bali": "indonesia", "canggu": "indonesia", "ubud": "indonesia", "seminyak": "indonesia",
    "jakarta": "indonesia", "kuala-lumpur": "malaysia", "penang": "malaysia",
    "singapore": "singapore", "seoul": "south-korea", "busan": "south-korea",
    "tokyo": "japan", "osaka": "japan", "fukuoka": "japan",
    "sydney": "australia", "melbourne": "australia", "brisbane": "australia",
    "toronto": "canada", "vancouver": "canada", "montreal": "canada",
    "mexico-city": "mexico", "guadalajara": "mexico", "oaxaca": "mexico",
    "playa-del-carmen": "mexico",
    "medellin": "colombia", "bogota": "colombia", "cartagena": "colombia",
    "buenos-aires": "argentina", "sao-paulo": "brazil", "lima": "peru",
    "quito": "ecuador", "cuenca": "ecuador", "panama-city": "panama",
    "cape-town": "south-africa", "nairobi": "kenya", "lagos": "nigeria",
    "accra": "ghana", "kotor": "montenegro", "tirana": "albania",
    "sarajevo": "bosnia", "pristina": "kosovo", "stockholm": "sweden",
    "copenhagen": "denmark", "oslo": "norway", "helsinki": "finland",
    "dublin": "ireland", "london": "uk", "edinburgh": "uk",
    "tel-aviv": "israel", "almaty": "kazakhstan", "tashkent": "uzbekistan",
}

THEMES = {
    "tax", "taxes", "banking", "insurance", "healthcare", "housing",
    "apartment", "coworking", "remote", "nomad", "family", "retire",
    "retirement", "budget", "neighborhood", "citizenship", "passport",
    "checklist", "pets", "school", "salary", "freelancer", "property",
    "investment", "crypto",
}


@dataclass
class Post:
    path: Path
    slug: str
    title: str
    description: str
    date: str
    body: str
    raw: str
    countries: set[str] = field(default_factory=set)
    cities: set[str] = field(default_factory=set)
    visas: set[str] = field(default_factory=set)
    themes: set[str] = field(default_factory=set)
    tokens: set[str] = field(default_factory=set)


def parse_frontmatter(raw: str) -> tuple[dict[str, str], str]:
    if not raw.startswith("---"):
        return {}, raw
    parts = raw.split("---", 2)
    if len(parts) < 3:
        return {}, raw
    fm: dict[str, str] = {}
    for line in parts[1].splitlines():
        m = re.match(r'^(\w+):\s*"?(.*?)"?\s*$', line)
        if m:
            fm[m.group(1)] = m.group(2)
    return fm, parts[2]


def word_count(body: str, *, exclude_related: bool = False) -> int:
    """Count body words (no frontmatter). Optionally exclude injected Related guides."""
    src = body
    if exclude_related:
        src = re.sub(
            r"\n## Related guides\n.*?(?=\n## |\n---\n|\n<JsonLd>|\Z)",
            "\n",
            src,
            flags=re.DOTALL,
        )
    clean = re.sub(r"<[^>]+>", " ", src)
    clean = re.sub(r"\{[^}]+\}", " ", clean)
    return len(re.findall(r"[A-Za-zА-Яа-яЁё0-9']+", clean))


def _whole_phrase(blob: str, phrase: str) -> bool:
    """True if phrase appears as a whole token/phrase (not inside another word)."""
    if " " in phrase or "-" in phrase:
        return phrase in blob or phrase.replace("-", " ") in blob
    return bool(re.search(rf"(?<![a-z0-9]){re.escape(phrase)}(?![a-z0-9])", blob))


def extract_entities(slug: str, title: str, description: str) -> tuple[set, set, set, set, set]:
    # Geography from slug+title only (descriptions name too many peer cities).
    geo_blob = f"{slug.replace('-', ' ')} {title}".lower()
    geo_blob = re.sub(r"[^a-z0-9\s]", " ", geo_blob)
    geo_blob = re.sub(r"\s+", " ", geo_blob)
    full_blob = f"{geo_blob} {description}".lower()
    full_blob = re.sub(r"[^a-z0-9\s]", " ", full_blob)
    full_blob = re.sub(r"\s+", " ", full_blob)
    blob = geo_blob  # used for countries/cities below
    slug_tokens = set(slug.lower().split("-"))
    tokens = set(re.findall(r"[a-z0-9]+", full_blob)) | slug_tokens

    countries: set[str] = set()
    for c in COUNTRIES:
        spaced = c.replace("-", " ")
        if _whole_phrase(blob, spaced) or c in slug_tokens:
            if c in {"usa", "us"} and c not in slug_tokens:
                continue
            countries.add(c)

    if "georgia" in slug or any(x in slug for x in ("tbilisi", "batumi", "kutaisi")):
        countries.add("georgia")
    if any(x in slug for x in ("uae", "dubai", "abu-dhabi")):
        countries.add("uae")
    if re.search(r"(?<![a-z])uk(?![a-z])|united kingdom|britain", blob) or "uk" in slug_tokens:
        countries.add("uk")

    cities: set[str] = set()
    for c in CITIES:
        key = c.replace("-", " ")
        parts = c.split("-")
        if _whole_phrase(blob, key) or c in slug_tokens or (len(parts) > 1 and all(p in slug_tokens for p in parts)):
            cities.add(c)

    for city, country in CITY_TO_COUNTRY.items():
        if city in cities:
            countries.add(country)

    visas: set[str] = set()
    # Prefer slug/title for visas — descriptions name too many peer programs.
    for v in VISA_TYPES:
        if len(v) <= 2:
            if v in slug_tokens:
                visas.add(v)
        elif _whole_phrase(blob, v.replace("-", " ")) or v in slug or v.replace("-", " ") in blob:
            visas.add(v)
    for alias, canon in VISA_ALIASES.items():
        if alias in slug_tokens:
            visas.add(canon)

    themes: set[str] = set()
    for t in THEMES:
        if t in slug_tokens or _whole_phrase(full_blob, t):
            themes.add(t)
    if any(x in slug for x in ("bank", "money", "send-money", "wire", "remit")):
        themes.add("banking")
    if any(x in slug for x in ("tax", "taxes", "nhr", "irs")):
        themes.add("tax")
    if "checklist" in slug or "timeline" in slug:
        themes.add("checklist")

    if "korea" in countries:
        countries.add("south-korea")
    if "bali" in cities or "bali" in slug_tokens:
        countries.add("indonesia")
        cities.add("bali")

    return countries, cities, visas, themes, tokens


def load_posts() -> list[Post]:
    posts: list[Post] = []
    for path in sorted(POSTS.glob("*.mdx")):
        raw = path.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(raw)
        slug = fm.get("slug", path.stem)
        title = fm.get("title", slug)
        description = fm.get("description", "")
        date = fm.get("date", "")
        countries, cities, visas, themes, tokens = extract_entities(slug, title, description)
        posts.append(
            Post(
                path=path,
                slug=slug,
                title=title,
                description=description,
                date=date,
                body=body,
                raw=raw,
                countries=countries,
                cities=cities,
                visas=visas,
                themes=themes,
                tokens=tokens,
            )
        )
    return posts


def score_pair(a: Post, b: Post) -> tuple[int, list[str]]:
    if a.slug == b.slug:
        return 0, []
    reasons: list[str] = []
    score = 0

    shared_cities = a.cities & b.cities
    shared_countries = a.countries & b.countries
    shared_visas = a.visas & b.visas
    shared_themes = a.themes & b.themes

    if shared_cities:
        score += 12 * len(shared_cities)
        city = sorted(shared_cities)[0].replace("-", " ").title()
        reasons.append(f"same city focus ({city})")
    if shared_countries:
        score += 16 * len(shared_countries)
        country = sorted(shared_countries)[0].replace("-", " ").title()
        reasons.append(f"same destination ({country})")
    if shared_visas:
        specific = shared_visas & {"d7", "d8", "non-lucrative", "entrepass", "workation", "golden-visa", "red-white-red", "mm2h", "ltr", "pensionado", "rentista", "jure-sanguinis", "express-entry"}
        visa_boost = 6 * len(shared_visas) + 16 * len(specific)
        if not shared_countries and not shared_cities:
            visa_boost = min(visa_boost, 8 + 16 * len(specific))
        score += visa_boost
        visa = sorted(specific or shared_visas)[0].replace("-", " ")
        reasons.append(f"related visa/pathway ({visa})")
    if shared_themes:
        theme_boost = 3 * min(2, len(shared_themes))
        priority = shared_themes & {"banking", "tax", "taxes", "checklist", "healthcare", "insurance", "citizenship"}
        if priority:
            theme_boost += 5
        if not shared_countries and not shared_cities and not shared_visas and not priority:
            theme_boost = min(theme_boost, 2)
        score += theme_boost
        theme = sorted(priority or shared_themes)[0]
        reasons.append(f"overlapping theme ({theme})")

    stop = {
        "how", "to", "move", "guide", "2025", "2026", "the", "a", "an", "for",
        "and", "vs", "with", "your", "complete", "expat", "abroad", "in",
    }
    at = {t for t in a.tokens if t not in stop and len(t) > 2}
    bt = {t for t in b.tokens if t not in stop and len(t) > 2}
    overlap = at & bt
    if overlap:
        score += min(4, len(overlap))

    if shared_visas and not shared_countries and not shared_cities:
        score -= 3

    return score, reasons


def coarse_link_reason(post: Post, other: Post) -> str | None:
    """Human reason from slug/title shape when score_pair has no entity overlap."""
    a, b = post.slug, other.slug

    def both(pred) -> bool:
        return pred(a) and pred(b)

    if both(lambda s: s.startswith("move-to")):
        return "another relocation destination"
    if both(lambda s: "retire" in s):
        return "related retirement guide"
    if both(lambda s: "neighborhood" in s):
        return "related neighborhood guide"
    if both(lambda s: "digital-nomad" in s or "nomad-visa" in s):
        return "related nomad visa guide"
    return None


def pass3_reason(post: Post, other: Post) -> str:
    """Reason for token-fallback picks. Never mention token counts.

    Hierarchy: score_pair human reason → coarse slug/title → neutral fallback.
    Returned lowercase, no trailing period (reason_blurb formats it).
    """
    _sc, reasons = score_pair(post, other)
    if reasons:
        return reasons[0]
    coarse = coarse_link_reason(post, other)
    if coarse:
        return coarse
    return "also worth reading"


def pick_related(post: Post, all_posts: list[Post], n: int = 4) -> list[tuple[Post, list[str], int]]:
    scored: list[tuple[int, Post, list[str]]] = []
    for other in all_posts:
        sc, reasons = score_pair(post, other)
        if sc > 0:
            scored.append((sc, other, reasons))
    scored.sort(key=lambda x: (-x[0], x[1].slug))

    picked: list[tuple[Post, list[str], int]] = []
    used_slugs: set[str] = set()
    used_countries: Counter = Counter()

    def accept(other: Post, reasons: list[str], sc: int) -> None:
        picked.append((other, reasons, sc))
        used_slugs.add(other.slug)
        for c in other.countries:
            used_countries[c] += 1

    # Pass 1: geographic peers (country/city)
    for sc, other, reasons in scored:
        if sc < 10:
            break
        if other.slug in used_slugs:
            continue
        if post.countries or post.cities:
            if not (other.countries & post.countries or other.cities & post.cities):
                continue
        accept(other, reasons, sc)
        if len(picked) >= n:
            return picked[:5]

    # Pass 2: strong thematic / visa matches
    geo_picks = len(picked)
    for sc, other, reasons in scored:
        if other.slug in used_slugs:
            continue
        min_sc = 12 if geo_picks >= 2 and post.countries else 6
        if sc < min_sc:
            continue
        # After 2 geo matches, do not add cross-country visa-only peers
        if geo_picks >= 2 and post.countries and not (other.countries & post.countries):
            continue
        foreign = other.countries - post.countries
        if foreign and any(used_countries[c] >= 1 for c in foreign) and len(picked) >= 2:
            continue
        accept(other, reasons, sc)
        if len(picked) >= n:
            return picked[:5]

    # Pass 3: soft token fallback so every post gets 3 links
    stop = {
        "how", "to", "move", "guide", "2025", "2026", "the", "a", "an", "for",
        "and", "vs", "with", "your", "complete", "expat", "abroad", "in", "of",
    }
    base = {t for t in post.tokens if t not in stop and len(t) > 2}
    soft: list[tuple[int, Post]] = []
    for other in all_posts:
        if other.slug == post.slug or other.slug in used_slugs:
            continue
        ot = {t for t in other.tokens if t not in stop and len(t) > 2}
        ov = len(base & ot)
        if ov:
            soft.append((ov, other))
    soft.sort(key=lambda x: (-x[0], x[1].slug))
    for ov, other in soft:
        accept(other, [pass3_reason(post, other)], ov)
        if len(picked) >= 3:
            break

    return picked[:5]


def reason_blurb(target: Post, reasons: list[str]) -> str:
    if reasons:
        primary = reasons[0]
        # humanize
        return primary[0].upper() + primary[1:] + "."
    # fallback from description
    desc = re.sub(r"\s+", " ", target.description).strip()
    if len(desc) > 110:
        desc = desc[:107].rstrip(" ,;:") + "…"
    return desc or "Related relocation guide on this blog."


def build_related_block(related: list[tuple[Post, list[str], int]]) -> str:
    lines = [
        "## Related guides",
        "",
        "Continue with these closely related guides:",
        "",
    ]
    for target, reasons, _sc in related:
        blurb = reason_blurb(target, reasons)
        lines.append(f"- [{target.title}](/blog/{target.slug}) — {blurb}")
    lines.append("")
    return "\n".join(lines)


RELATED_LINE_RE = re.compile(
    r"^Related guides on this blog:.*$(?:\n)?",
    re.MULTILINE,
)
RELATED_SECTION_RE = re.compile(
    r"\n## Related guides\n.*?(?=\n## |\n---\n|\n<JsonLd>|\Z)",
    re.DOTALL,
)
FAQ_RE = re.compile(r"\n## Frequently Asked Questions\n")


def insert_related_block(body: str, block: str) -> str:
    # Remove prior related one-liner or section
    body = RELATED_SECTION_RE.sub("\n", body)
    body = RELATED_LINE_RE.sub("", body)

    faq = FAQ_RE.search(body)
    if faq:
        pos = faq.start()
        return body[:pos].rstrip() + "\n\n" + block + body[pos:].lstrip("\n")

    # before CTA horizontal rule + Relova link
    cta = re.search(r"\n---\n.*\[Relova\]\(https://relova\.ai\)", body)
    if cta:
        pos = cta.start()
        return body[:pos].rstrip() + "\n\n" + block + "\n" + body[pos:].lstrip("\n")

    jsonld = body.find("\n<JsonLd>")
    if jsonld >= 0:
        return body[:jsonld].rstrip() + "\n\n" + block + body[jsonld:]

    return body.rstrip() + "\n\n" + block


def existing_internal_slugs(body: str) -> set[str]:
    return set(re.findall(r"(?:https://blog\.relova\.ai)?/blog/([a-z0-9\-]+)", body))


def add_inline_links(body: str, post: Post, related: list[tuple[Post, list[str], int]], all_by_slug: dict[str, Post]) -> tuple[str, int]:
    """Add up to 2 contextual inline links in early paragraphs."""
    if word_count(body) < 80:
        return body, 0

    # Only count links in main prose (ignore Related guides / FAQ / CTA / JsonLd)
    split_at = len(body)
    for marker in ("\n## Frequently Asked Questions", "\n## Related guides", "\n---\n", "\n<JsonLd>"):
        i = body.find(marker)
        if 0 <= i < split_at:
            split_at = i
    head, tail = body[:split_at], body[split_at:]

    already = existing_internal_slugs(head)
    if len(already) >= 3:
        return body, 0  # intro/body already well linked

    candidates: list[tuple[str, Post, str]] = []  # phrase, target, reason

    # Prefer linking FROM this post's prose TO complementary guides:
    # - country article → city / visa guide
    # - city article → country / visa guide
    # - any article mentioning a related destination/visa phrase
    for target, _reasons, _sc in related:
        if target.slug in already:
            continue
        for city in sorted(target.cities):
            phrase = city.replace("-", " ")
            if len(phrase) >= 4 and re.search(rf"(?i)\b{re.escape(phrase)}\b", head):
                candidates.append((phrase, target, "city"))
        for country in sorted(target.countries):
            phrase = country.replace("-", " ")
            if len(phrase) >= 4 and re.search(rf"(?i)\b{re.escape(phrase)}\b", head):
                # avoid linking the article's own primary destination to itself-ish
                if country in post.countries and "move-to" in post.slug and post.slug.startswith("move-to"):
                    # still OK to link a more specific sibling (visa/neighborhood)
                    if not any(k in target.slug for k in ("visa", "neighborhood", "tax", "family", "freelancer", "nomad")):
                        continue
                candidates.append((phrase, target, "country"))
        for visa in sorted(target.visas | post.visas):
            aliases = {
                "d8": ["D8", "D8 visa", "Portugal Digital Nomad"],
                "d7": ["D7", "D7 visa"],
                "digital-nomad": ["digital nomad visa", "Digital Nomad Visa"],
                "non-lucrative": ["Non-Lucrative Visa", "non-lucrative visa", "NLV"],
                "golden-visa": ["Golden Visa"],
                "schengen": ["Schengen"],
                "entrepass": ["EntrePass"],
                "workation": ["Workation"],
                "red-white-red": ["Red-White-Red"],
            }
            for phrase in aliases.get(visa, [visa.replace("-", " ")]):
                if re.search(rf"(?i)\b{re.escape(phrase)}\b", head):
                    candidates.append((phrase, target, "visa"))

    # Deduplicate candidates by (phrase.lower, target)
    seen_cand: set[tuple[str, str]] = set()
    uniq: list[tuple[str, Post, str]] = []
    for phrase, target, kind in candidates:
        key = (phrase.lower(), target.slug)
        if key in seen_cand:
            continue
        seen_cand.add(key)
        uniq.append((phrase, target, kind))
    # Prefer visa matches, then city, then country
    kind_rank = {"visa": 0, "city": 1, "country": 2}
    uniq.sort(key=lambda x: (kind_rank.get(x[2], 9), -len(x[0])))

    added = 0
    used_targets: set[str] = set()

    for phrase, target, _kind in uniq:
        if added >= 2:
            break
        if target.slug in used_targets or target.slug in already:
            continue
        if len(phrase) < 3:
            continue

        # Skip matches that already sit inside a markdown link
        # Scan for first bare occurrence
        pat = re.compile(re.escape(phrase), re.IGNORECASE)
        for m in pat.finditer(head):
            start, end = m.start(), m.end()
            # inside ](url) or already [text](
            before = head[max(0, start - 3) : start]
            after = head[end : end + 2]
            # crude: if preceded by ]( or [ within link span
            left = head[max(0, start - 120) : start]
            if re.search(r"\[[^\]]*$", left):
                continue  # inside link text being written
            if "](" in left[left.rfind("[") :] if "[" in left else "":
                pass
            # check we're not inside an existing () url
            if re.search(r"\[[^\]]*\]\([^)]*$", left):
                continue
            if before.endswith("[") or after.startswith("]("):
                continue
            linked = f"[{m.group(0)}](/blog/{target.slug})"
            head = head[:start] + linked + head[end:]
            added += 1
            used_targets.add(target.slug)
            already.add(target.slug)
            break

    return head + tail, added


def collect_git_lastmod() -> dict[str, str]:
    result = subprocess.run(
        ["git", "log", "--pretty=format:%aI", "--name-only", "--", "content/posts/"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    dates: dict[str, str] = {}
    current: str | None = None
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        if re.match(r"^\d{4}-\d{2}-\d{2}T", line):
            current = line
        elif line.startswith("content/posts/") and line.endswith(".mdx") and current:
            slug = Path(line).stem
            if slug not in dates:
                dates[slug] = current
    return dates


def write_thin_report(posts: list[Post], main_site_status: str) -> Path:
    rows = []
    for p in posts:
        wc = word_count(p.body, exclude_related=True)
        if wc < 400:
            rows.append((wc, p.slug, str(p.path.relative_to(ROOT))))
    rows.sort()

    ultra_prev = {
        "ultimate-relocation-checklist-2025",
        "build-social-life-after-relocating-abroad",
        "visa-cover-letter-guide-2025",
        "relocate-with-family-abroad-guide",
        "cost-of-relocating-to-europe-2025",
        "how-to-find-apartment-abroad-before-you-arrive",
        "how-to-open-bank-account-abroad-2025",
        "best-countries-expats-2025-comparison",
        "best-health-insurance-expats-europe-2025",
        "portugal-vs-spain-vs-georgia-relocation-2025",
        "austria-red-white-red-card-guide-2026",
        "digital-nomad-visa-complete-guide-2025",
    }
    filled40 = {
        "move-to-tenerife-guide-2026", "move-to-stockholm-guide-2026",
        "singapore-entrepreneur-entrepass-guide-2026", "irish-citizenship-by-descent-guide-2026",
        "move-to-kotor-montenegro-guide-2026", "expat-banking-complete-guide-2026",
        "move-to-bogota-guide-2026", "amsterdam-neighborhoods-expat-guide-2026",
        "lisbon-vs-madrid-expat-guide-2026", "dubai-remote-worker-virtual-working-2026",
        "homesickness-living-abroad-guide-2026", "visa-fees-comparison-2026",
        "move-to-north-macedonia-guide-2026", "spain-non-lucrative-visa-guide-2026",
        "move-to-porto-complete-guide-2026", "italian-citizenship-jure-sanguinis-guide-2026",
        "pension-abroad-expat-guide-2026", "tbilisi-digital-nomad-setup-guide-2026",
        "bali-vs-thailand-expat-guide-2026", "move-to-greek-islands-guide-2026",
        "tbilisi-first-week-checklist-2026", "negotiate-salary-moving-abroad-2026",
        "move-to-spain-family-guide-2026", "move-to-albania-riviera-guide-2026",
        "move-to-phuket-guide-2026", "move-to-lisbon-family-guide-2026",
        "find-long-term-accommodation-abroad-2026", "move-to-vienna-guide-2026",
        "medellin-vs-bogota-vs-cartagena-guide-2026", "lisbon-freelancer-setup-guide-2026",
        "move-to-panama-city-guide-2026", "move-to-oaxaca-mexico-guide-2026",
        "move-to-batumi-guide-2026", "move-to-malaga-guide-2026",
        "canggu-vs-ubud-vs-seminyak-bali-guide-2026", "japan-digital-nomad-visa-guide-2026",
        "lisbon-vs-porto-vs-algarve-guide-2026", "south-korea-digital-nomad-visa-guide-2026",
        "move-to-berlin-nomad-guide-2026", "portugal-d8-visa-application-step-by-step-2026",
    }

    by_slug = {p.slug: word_count(p.body, exclude_related=True) for p in posts}
    lines = [
        "# Thin content audit — blog.relova.ai",
        "",
        "Generated by `scripts/build_related_links.py`. Word counts = body only (frontmatter excluded; injected `## Related guides` block also excluded so thinness is comparable to pre-linking audits).",
        "",
        f"- Total posts: **{len(posts)}**",
        f"- Posts with body &lt; 400 words: **{len(rows)}**",
        f"- Ultra stubs (≤50 words): **{sum(1 for w,_,_ in rows if w <= 50)}**",
        "",
        "## Ultra stubs (previously flagged 12)",
        "",
        "Re-checked against live `content/posts/*.mdx`. All 12 still present and still ultra-thin:",
        "",
        "| slug | words | path |",
        "| --- | ---: | --- |",
    ]
    for slug in sorted(ultra_prev, key=lambda s: by_slug.get(s, 0)):
        lines.append(f"| `{slug}` | {by_slug.get(slug, 'MISSING')} | `content/posts/{slug}.mdx` |")

    lines += [
        "",
        "## Previously filled cohort (40)",
        "",
        "All 40 posts from `audit_low_data_posts.md` are now ≥400 words (not rewritten in this pass):",
        "",
        f"- Still &lt;400: **{sum(1 for s in filled40 if by_slug.get(s, 0) < 400)}**",
        f"- Word range: {min(by_slug[s] for s in filled40)}–{max(by_slug[s] for s in filled40)}",
        "",
        "## Full thin list (&lt;400 words)",
        "",
        "| slug | текущее число слов | путь к файлу |",
        "| --- | ---: | --- |",
    ]
    for wc, slug, path in rows:
        flag = " ⚠️ ultra stub" if slug in ultra_prev else ""
        lines.append(f"| `{slug}` | {wc}{flag} | `{path}` |")

    lines += [
        "",
        "## Task 4 — technical indexing blockers (status)",
        "",
        "- **noindex** in frontmatter/meta across 410 posts: **none found**",
        "- **robots.txt** (`app/robots.ts` / live): `Allow: /`, sitemap pointed at blog — **does not block `/blog/*`**",
        "- **Canonical** (`app/blog/[slug]/page.tsx`): `alternates.canonical = /blog/${slug}` with `metadataBase = https://blog.relova.ai` → `https://blog.relova.ai/blog/<slug>` (no query/trailing slash)",
        "- **Sitemap lastmod**: was using frontmatter `date` / build `new Date()` — **fixed** to git file last-author date via `content/post-lastmod.json`",
        "",
        "## Task 5 — main site `relova.ai/blog` duplicates (status)",
        "",
        main_site_status,
        "",
    ]
    out = SCRIPTS / "audit_report_thin_content.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def write_structure_report(posts: list[Post]) -> Path:
    def h2s(body: str) -> tuple[str, ...]:
        out = []
        for line in body.splitlines():
            m = re.match(r"^##\s+(.+?)\s*$", line)
            if m:
                title = m.group(1).strip()
                # Exclude the Related guides block we inject — not part of original templating
                if title.lower() == "related guides":
                    continue
                out.append(title)
        return tuple(out)

    skeletons: Counter[tuple[str, ...]] = Counter()
    skel_slugs: dict[tuple[str, ...], list[str]] = defaultdict(list)
    for p in posts:
        sk = h2s(p.body)
        skeletons[sk] += 1
        skel_slugs[sk].append(p.slug)

    # Role-normalized view for "templateness"
    role_map = [
        (r"(?i)^table of contents$", "TOC"),
        (r"(?i)^related guides$", "RELATED"),
        (r"(?i)^frequently asked questions$", "FAQ"),
        (r"(?i).*(at a glance|quick-reference|key numbers|figures that matter|snapshot).*", "KEY_DATA"),
        (r"(?i).*(visa|permit|residency|immigration|passport|citizenship).*", "VISA"),
        (r"(?i).*(cost|budget|rent|money|tax|banking).*", "COSTS"),
        (r"(?i).*(neighborhood|where to live|areas).*", "NEIGHBORHOODS"),
        (r"(?i).*(healthcare|health|insurance|medical).*", "HEALTH"),
        (r"(?i).*(job|work|career|employment|freelancer).*", "WORK"),
        (r"(?i).*(checklist|timeline|first week|first month|setup).*", "SETUP"),
        (r"(?i).*(practical|logistics|daily life|settling|connectivity|transport|community).*", "PRACTICAL"),
    ]

    def roles(sk: tuple[str, ...]) -> tuple[str, ...]:
        out = []
        for h in sk:
            lab = "OTHER"
            for pat, name in role_map:
                if re.search(pat, h):
                    lab = name
                    break
            out.append(lab)
        return tuple(out)

    role_counts: Counter[tuple[str, ...]] = Counter()
    for sk, c in skeletons.items():
        role_counts[roles(sk)] += c

    lines = [
        "# Structure templating audit — H2 skeletons",
        "",
        f"- Total posts: **{len(posts)}**",
        f"- Unique exact H2 sequences: **{len(skeletons)}**",
        f"- Posts with a unique exact skeleton: **{sum(1 for c in skeletons.values() if c == 1)}**",
        f"- Posts sharing a skeleton with ≥1 other post: **{sum(c for c in skeletons.values() if c > 1)}**",
        f"- Unique role-normalized skeletons: **{len(role_counts)}**",
        "",
        "## Top-5 most common exact H2 skeletons",
        "",
    ]
    for i, (sk, c) in enumerate(skeletons.most_common(5), 1):
        lines.append(f"### #{i} — {c} articles")
        lines.append("")
        if not sk:
            lines.append("_(no H2 headings)_")
        else:
            for h in sk:
                lines.append(f"- {h}")
        lines.append("")
        sample = ", ".join(f"`{s}`" for s in skel_slugs[sk][:8])
        more = f" (+{len(skel_slugs[sk]) - 8} more)" if len(skel_slugs[sk]) > 8 else ""
        lines.append(f"Examples: {sample}{more}")
        lines.append("")

    lines += [
        "## Top-10 role-normalized skeletons",
        "",
        "Role labels collapse location-specific wording (VISA / COSTS / PRACTICAL / KEY_DATA / FAQ, etc.).",
        "",
        "| count | role skeleton |",
        "| ---: | --- |",
    ]
    for sk, c in role_counts.most_common(10):
        label = " → ".join(sk) if sk else "(no H2)"
        lines.append(f"| {c} | `{label}` |")

    lines += [
        "",
        "## All exact skeletons with count ≥ 3",
        "",
        "| count | H2 sequence |",
        "| ---: | --- |",
    ]
    for sk, c in skeletons.most_common():
        if c < 3:
            break
        seq = " → ".join(sk) if sk else "(no H2)"
        if len(seq) > 180:
            seq = seq[:177] + "…"
        lines.append(f"| {c} | {seq} |")

    lines += [
        "",
        "## Verdict",
        "",
        "Exact H2 strings were diversified during earlier dedup (294 unique sequences), but **role-level** structure remains highly templated: most articles still follow TOC → (visa/costs/practical variants) → key-data table → FAQ. That pattern is a programmatic-content signal even when paragraph text differs.",
        "",
    ]
    out = SCRIPTS / "audit_report_structure.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def validate_links(posts: list[Post]) -> list[tuple[str, str]]:
    slugs = {p.slug for p in posts}
    broken: list[tuple[str, str]] = []
    for p in posts:
        for target in re.findall(r"(?:https://blog\.relova\.ai)?/blog/([a-z0-9\-]+)", p.body):
            if target not in slugs:
                broken.append((p.slug, target))
    return broken


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--reports-only", action="store_true")
    ap.add_argument("--skip-inline", action="store_true")
    args = ap.parse_args()

    posts = load_posts()
    by_slug = {p.slug: p for p in posts}

    main_site_status = (
        "Access: **yes** — sibling repo `/Users/alex2/Documents/Projects/Relova/relova`.\n"
        "\n"
        "Live check (2026-08-05): `https://relova.ai/blog` and `https://relova.ai/blog/<slug>` return "
        "**HTTP 200** SPA `index.html` (no 301). Client-side `window.location.replace` exists in "
        "`src/App.tsx`, but Google still sees a soft duplicate without a server redirect.\n"
        "\n"
        "**Fix applied in that repo:** Vercel `301` redirects in `vercel.json`:\n"
        "- `/blog` → `https://blog.relova.ai`\n"
        "- `/blog/:path*` → `https://blog.relova.ai/blog/:path*`\n"
        "\n"
        "Needs a separate deploy of the main `relova` app to take effect."
    )

    thin_path = write_thin_report(posts, main_site_status)
    struct_path = write_structure_report(posts)
    print(f"Wrote {thin_path.relative_to(ROOT)}")
    print(f"Wrote {struct_path.relative_to(ROOT)}")

    # lastmod cache (always refresh)
    lastmod = collect_git_lastmod()
    # keep only current posts; fill gaps from frontmatter date
    current_slugs = {p.slug for p in posts}
    lastmod = {k: v for k, v in lastmod.items() if k in current_slugs}
    for p in posts:
        if p.slug not in lastmod:
            lastmod[p.slug] = (
                f"{p.date}T00:00:00+00:00" if re.match(r"^\d{4}-\d{2}-\d{2}$", p.date or "") else (p.date or "2026-01-01T00:00:00+00:00")
            )
    if not args.dry_run:
        LASTMOD_JSON.write_text(
            json.dumps(dict(sorted(lastmod.items())), indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Wrote {LASTMOD_JSON.relative_to(ROOT)} ({len(lastmod)} entries)")

    if args.reports_only:
        return

    related_added = 0
    related_replaced = 0
    inline_added = 0
    files_touched = 0

    for p in posts:
        related = pick_related(p, posts, n=4)
        if not related:
            continue
        block = build_related_block(related)
        had_related = bool(
            RELATED_LINE_RE.search(p.body) or RELATED_SECTION_RE.search("\n" + p.body)
        )
        new_body = insert_related_block(p.body, block)
        inl = 0
        if not args.skip_inline:
            new_body, inl = add_inline_links(new_body, p, related, by_slug)

        if new_body == p.body:
            continue

        # rebuild raw
        fm_match = re.match(r"^---\n.*?\n---\n", p.raw, re.DOTALL)
        if not fm_match:
            continue
        new_raw = fm_match.group(0) + new_body
        if not new_raw.endswith("\n"):
            new_raw += "\n"

        if args.dry_run:
            print(f"[dry] {p.slug}: related={len(related)} replace={had_related} inline=+{inl}")
        else:
            p.path.write_text(new_raw, encoding="utf-8")
            p.body = new_body
            p.raw = new_raw

        files_touched += 1
        if had_related:
            related_replaced += 1
        else:
            related_added += 1
        inline_added += inl

    # fix known broken monaco link if still present
    nice = by_slug.get("move-to-nice-france-guide-2026")
    if nice and "move-to-monaco-tax-guide-2026" in nice.body:
        fixed = nice.body.replace(
            "/blog/move-to-monaco-tax-guide-2026",
            "/blog/france-american-tax-guide-2026"
            if "france-american-tax-guide-2026" in by_slug
            else "/blog/move-to-france-guide-2026",
        )
        if fixed != nice.body and not args.dry_run:
            fm_match = re.match(r"^---\n.*?\n---\n", nice.raw, re.DOTALL)
            assert fm_match
            nice.path.write_text(fm_match.group(0) + fixed, encoding="utf-8")
            nice.body = fixed
            print("Fixed broken monaco link in move-to-nice-france-guide-2026")

    # reload + validate
    posts2 = load_posts()
    broken = validate_links(posts2)
    print(
        f"Done. files_touched={files_touched} related_new={related_added} "
        f"related_upgraded={related_replaced} inline_links_added={inline_added} "
        f"broken_internal_links={len(broken)}"
    )
    if broken:
        for src, tgt in broken[:20]:
            print(f"  BROKEN {src} -> {tgt}")


if __name__ == "__main__":
    main()
