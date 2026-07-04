#!/usr/bin/env python3
"""Shared content engine used by the rewrite tool and the batch generators.

Core idea: build every body paragraph and FAQ answer from the article's OWN
structured facts (intro prose, the comparison table figures, and the
description clauses). Because those facts differ per article, the resulting
prose is unique across pages instead of drawing from one shared sentence pool.

Public helpers:
    parse_mdx(text)            -> ParsedPost
    build_body(post)           -> str   (unique H2 sections + table + FAQ)
    build_faq(post)            -> list[(question, answer)]
    render_post(...)           -> str   (full .mdx, used by generators)
    has_intra_duplication(md)  -> bool  (pre-save guard for generators)
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field

# audit_duplication lives in the same folder; reuse its detection so the
# generator guard matches exactly what the audit reports.
try:
    from audit_duplication import (
        split_body_paragraphs,
        intra_page_duplicates,
        extract_topic,
        strip_frontmatter,
        normalize_paragraph,
    )
except ImportError:  # when imported as scripts.content_lib
    from scripts.audit_duplication import (  # type: ignore
        split_body_paragraphs,
        intra_page_duplicates,
        extract_topic,
        strip_frontmatter,
        normalize_paragraph,
    )


# --------------------------------------------------------------------------
# Parsing
# --------------------------------------------------------------------------

@dataclass
class Fact:
    """A single structured fact extracted from a table row or description."""

    label: str          # e.g. "Senggigi 1BR"  (may be "" for desc clauses)
    value: str          # e.g. "$300–550/mo"
    note: str = ""      # e.g. "west-coast demand"
    raw: str = ""       # original text (for desc clauses used verbatim)
    theme: str = "general"


@dataclass
class ParsedPost:
    frontmatter: dict
    body: str
    slug: str
    topic: str | None
    intro: str                       # everything before the first "## "
    table_md: str                    # the markdown comparison table (kept as-is)
    related_line: str                # "Related guides on this blog: ..."
    related_links: list[tuple[str, str]]  # (title, url)
    cta: str
    article_jsonld: str
    facts: list[Fact] = field(default_factory=list)


_TABLE_BLOCK_RE = re.compile(
    r"((?:^\s*\|.*\|\s*$\n?){2,})", re.MULTILINE
)
_RELATED_RE = re.compile(r"^Related guides on this blog:.*$", re.MULTILINE)
_JSONLD_RE = re.compile(r"<JsonLd>\s*(.*?)\s*</JsonLd>", re.DOTALL)
_ARTICLE_JSONLD_RE = re.compile(
    r"<JsonLd>\s*\{`(.*?\"@type\": ?\"Article\".*?)`\}\s*</JsonLd>", re.DOTALL
)
_CTA_RE = re.compile(r"^-{3,}\n(.*\[Relova\]\(https://relova\.ai\).*)$", re.MULTILINE)


# Ordered classification rules: the first matching bucket wins. Housing costs
# are checked before visa so a "1BR rent" row never lands in the visa section,
# and clear visa signals are checked before generic money words like "budget".
_COST_HOUSING = [
    "rent", "1br", "2br", "3br", "studio", "condo", "apartment", "villa",
    "tuition", "school fee", "deposit", "utilities", "groceries",
]
_VISA_KW = [
    "visa", "permit", "residency", "residence", "resident", "citizen",
    "naturaliz", "passport", "golden", "d7", "d8", "dnv", "mm2h", "e33g",
    "ltr", "pensionado", "rentista", "express entry", "blue card",
    "opportunity card", "chancenkarte", "hsm", "act 60", "welcome stamp",
    "points test", "sponsor", "e-visa", "evisa", "green card", "pnp",
    "365", "orientation year", "daft", "premium residency", "ilr",
]
_HEALTH_KW = [
    "health", "insurance", "hospital", "clinic", "medical", "iess", "imss",
    "caja", "sns", "ehic", "ghic", "evac", "pediatric", "dental", "medevac",
    "jci", "krankenkasse", "eps", "cover",
]
_COST_OTHER = [
    "budget", "cost", "tax", "iva", "irpf", "reta", "gestor", "salary",
    "price", "fee", "band", "discount", "savings", "flight", "/mo",
    "per month", "monthly", "income", "pension", "spend", "usd", "eur",
]


def _classify(text: str) -> str:
    t = text.lower()
    if any(k in t for k in _COST_HOUSING):
        return "cost"
    if any(k in t for k in _VISA_KW):
        return "visa"
    if any(k in t for k in _HEALTH_KW):
        return "health"
    if any(k in t for k in _COST_OTHER):
        return "cost"
    return "general"


# Header words that mark column 2 as a "value" column and column 3 as a "note"
# column (i.e. the normal label/value/note layout, not an A-vs-B comparison).
_GENERIC_HEADERS = {
    "figure", "band", "value", "rule", "rule of thumb", "cost", "rate", "amount",
    "price", "threshold", "term", "requirement", "status", "detail", "note",
    "notes", "impact", "fix", "caveat", "why", "why it matters", "reason",
    "proof", "typical proof", "step", "key step", "lever", "core lever",
    "point boost", "route", "visa", "tool", "filing impact", "current rule",
    "income cited", "baseline", "source-style note", "typical 2026 band",
    "typical duration", "2026 band", "point", "data", "answer", "figures",
    "monthly", "1br range", "1br", "1br rent", "rent range", "salary band",
}


def _is_generic_header(h: str) -> bool:
    hl = h.lower().strip()
    if hl in _GENERIC_HEADERS:
        return True
    # anything containing these tokens is a value/note column, not an option.
    return any(tok in hl for tok in (
        "figure", "band", "note", "rule", "cost", "rent", "range", "salary",
        "detail", "impact", "why", "proof", "duration", "requirement",
    ))


def _parse_table_facts(table_md: str) -> list[Fact]:
    lines = [l.strip() for l in table_md.splitlines() if l.strip().startswith("|")]
    # Locate the header separator row (| --- | --- |) and treat everything up
    # to and including it as the header, so header labels never become facts.
    sep_idx = None
    for i, line in enumerate(lines):
        cells = [c.strip() for c in line.strip("|").split("|")]
        if cells and all(set(c) <= set("-: ") and c for c in cells):
            sep_idx = i
            break
    header_cells: list[str] = []
    if sep_idx is not None and sep_idx >= 1:
        header_cells = [c.strip() for c in lines[sep_idx - 1].strip("|").split("|")]
    elif lines:
        header_cells = [c.strip() for c in lines[0].strip("|").split("|")]
    data_lines = lines[sep_idx + 1 :] if sep_idx is not None else lines[1:]

    # Comparison table: 3 columns where columns 2 & 3 are options (e.g. two
    # cities) rather than value + note.
    comparison = (
        len(header_cells) >= 3
        and not _is_generic_header(header_cells[1])
        and not _is_generic_header(header_cells[2])
    )

    facts: list[Fact] = []
    for line in data_lines:
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not cells:
            continue
        label = cells[0]
        value = cells[1] if len(cells) > 1 else ""
        note = cells[2] if len(cells) > 2 else ""
        if not label or not value:
            continue
        theme = _classify(f"{label} {note}")
        if comparison and note:
            raw = f"{label}: {header_cells[1]} {value}, {header_cells[2]} {note}"
            facts.append(Fact(label="", value="", raw=raw, theme=theme))
        else:
            facts.append(Fact(label=label, value=value, note=note, theme=theme))
    return facts


_DESC_FILLER = re.compile(r"verify official sources\.?", re.IGNORECASE)


def _parse_desc_facts(description: str, topic: str | None) -> list[Fact]:
    desc = description
    truncated = desc.rstrip().endswith("…")
    if topic and desc.lower().startswith(topic.lower()):
        desc = desc[len(topic):]
    desc = desc.lstrip(": ")
    desc = _DESC_FILLER.sub("", desc)
    desc = desc.rstrip(" ….")
    clauses = [c.strip().rstrip("…").strip() for c in re.split(r"[;]", desc)]
    # A truncated description ends mid-word; drop that final fragment.
    if truncated and clauses:
        clauses = clauses[:-1]
    facts: list[Fact] = []
    for c in clauses:
        if len(c.split()) < 4:
            continue
        if c.lower().startswith("verify"):
            continue
        facts.append(Fact(label="", value="", raw=c, theme=_classify(c)))
    return facts


def parse_mdx(text: str) -> ParsedPost:
    fm, body = strip_frontmatter(text)
    slug = fm.get("slug", "")
    topic = extract_topic(fm, body)

    # Article JsonLd (keep verbatim if present)
    article_jsonld = ""
    m = _ARTICLE_JSONLD_RE.search(body)
    if m:
        article_jsonld = m.group(0)

    # Table
    table_md = ""
    tm = _TABLE_BLOCK_RE.search(body)
    if tm:
        table_md = tm.group(1).strip()

    # Related guides
    related_line = ""
    related_links: list[tuple[str, str]] = []
    rm = _RELATED_RE.search(body)
    if rm:
        related_line = rm.group(0).strip()
        for title, url in re.findall(r"\[([^\]]+)\]\(([^)]+)\)", related_line):
            related_links.append((title, url))

    # CTA
    cta = ""
    cm = _CTA_RE.search(body)
    if cm:
        cta = cm.group(1).strip()

    # Intro = text between frontmatter and first "## " heading
    first_h2 = body.find("\n## ")
    intro = body[:first_h2].strip() if first_h2 != -1 else ""
    # Drop a leading TOC that sometimes precedes the first H2 (rare)

    facts = _parse_table_facts(table_md)
    # Description clauses supplement thin tables but are redundant (and often
    # truncated) when a rich table already exists, so only use them if needed.
    if len(facts) < 5:
        facts += _parse_desc_facts(fm.get("description", ""), topic)

    return ParsedPost(
        frontmatter=fm,
        body=body,
        slug=slug,
        topic=topic,
        intro=intro,
        table_md=table_md,
        related_line=related_line,
        related_links=related_links,
        cta=cta,
        article_jsonld=article_jsonld,
        facts=facts,
    )


# --------------------------------------------------------------------------
# Deterministic per-article variation
# --------------------------------------------------------------------------

def _seed(slug: str, salt: str = "") -> int:
    return int(hashlib.md5(f"{slug}::{salt}".encode()).hexdigest(), 16)


def _pick(options: list[str], slug: str, salt: str) -> str:
    return options[_seed(slug, salt) % len(options)]


# --------------------------------------------------------------------------
# Fact -> sentence
# --------------------------------------------------------------------------

_TABLE_FRAMES = [
    "{label}: {value}{note_paren}.",
    "{label} runs {value}{note_paren}.",
    "{label} is typically {value}{note_paren}.",
    "{label} sits near {value}{note_paren}.",
    "{label} lands around {value}{note_paren}.",
    "Expect {label} at {value}{note_paren}.",
    "Plan for {label} at roughly {value}{note_paren}.",
    "Budget {value} for {label}{note_paren}.",
    "{label} comes in at {value}{note_paren}.",
    "Figure on {value} for {label}{note_paren}.",
]


_HEDGE_PREFIX_RE = re.compile(r"^(~|about |around |roughly |approx\.? )+", re.IGNORECASE)


def _is_sentence_value(value: str) -> bool:
    """A table value that is already a full, article-specific sentence — in which
    case the column label (often generic like 'Housing anchor') is noise."""
    return len(value.split()) >= 7 or value.rstrip().endswith((".", "!", "?"))


def _fact_sentence(fact: Fact, slug: str, idx: int) -> str:
    if fact.raw:
        s = fact.raw.strip()
        s = s[0].upper() + s[1:] if s else s
        if not s.endswith((".", "!", "?")):
            s += "."
        return s
    # Normalise the value so a hedging frame ("roughly", "near") doesn't stack
    # on top of a value that already starts with "~" / "about".
    value = _HEDGE_PREFIX_RE.sub("", fact.value).strip()
    if _is_sentence_value(value):
        s = value[0].upper() + value[1:]
        if not s.endswith((".", "!", "?")):
            s += "."
        return s
    note_paren = ""
    if fact.note and fact.note.lower() != value.lower():
        note_paren = f" ({fact.note})"
    label = fact.label
    if label.lower().startswith("vs "):
        rest = label[3:].strip()
        return f"Compared with {rest}, plan on {value}{note_paren}."
    frame = _TABLE_FRAMES[_seed(slug, f"frame{idx}") % len(_TABLE_FRAMES)]
    s = frame.format(label=label, value=value, note_paren=note_paren)
    return s


# --------------------------------------------------------------------------
# Section building
# --------------------------------------------------------------------------

SECTION_DEFS = [
    (
        "visa",
        [
            "Visas, residency, and the legal basis to stay",
            "Getting your visa and residency right",
            "Visa routes, permits, and lawful status",
            "Immigration: which route actually fits",
        ],
        [
            "Lock the legal basis before anything else.",
            "Sort the paperwork that gates everything else first.",
            "Your route to lawful stay drives the whole timeline.",
        ],
    ),
    (
        "cost",
        [
            "Rent, budget, and the real monthly numbers",
            "What it actually costs each month",
            "Costs, rent, and a realistic budget",
            "Money: rent, taxes, and monthly burn",
        ],
        [
            "Here are the numbers that shape a monthly budget.",
            "Model the recurring costs before you commit.",
            "These figures decide whether the move pencils out.",
        ],
    ),
    (
        "health",
        [
            "Healthcare, insurance, and staying covered",
            "Health cover and medical logistics",
            "Insurance, hospitals, and health planning",
        ],
        [
            "Plan health cover from day one, not after arrival.",
            "Medical logistics deserve early attention.",
            "Sort insurance before the first appointment.",
        ],
    ),
    (
        "general",
        [
            "Neighborhoods, logistics, and settling in",
            "Practical logistics and daily life",
            "Getting set up: connectivity, transport, and community",
            "The practical details that shape daily life",
        ],
        [
            "A few practical details make the first months smoother.",
            "The logistics below tend to trip up first-time movers.",
            "These are the operational details worth planning early.",
        ],
    ),
]


def _slugify_heading(text: str) -> str:
    s = text.lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"\s+", "-", s).strip("-")
    return s


def build_sections(post: ParsedPost) -> list[tuple[str, list[str]]]:
    """Return list of (heading, [paragraph, ...]) built from the post's facts."""
    slug = post.slug
    by_theme: dict[str, list[Fact]] = {"visa": [], "cost": [], "health": [], "general": []}
    for f in post.facts:
        by_theme.setdefault(f.theme, by_theme["general"])
        by_theme[f.theme].append(f)

    # Merge health into general if health is thin, to avoid stub sections.
    if len(by_theme["health"]) < 2:
        by_theme["general"] = by_theme["health"] + by_theme["general"]
        by_theme["health"] = []

    sections: list[tuple[str, list[str]]] = []
    global_idx = 0
    for theme, headings, _leads in SECTION_DEFS:
        facts = by_theme.get(theme, [])
        if not facts:
            continue
        heading = _pick(headings, slug, f"h-{theme}")
        sentences: list[str] = []
        for f in facts:
            sentences.append(_fact_sentence(f, slug, global_idx))
            global_idx += 1
        # Assemble into readable paragraphs (max ~4 sentences per paragraph).
        # No generic lead sentence: paragraphs start with an article-specific
        # fact so their text never collides with other pages.
        paras: list[str] = []
        chunk: list[str] = []
        for s in sentences:
            chunk.append(s)
            if len(chunk) >= 4:
                paras.append(" ".join(chunk))
                chunk = []
        if chunk:
            paras.append(" ".join(chunk))
        sections.append((heading, paras))

    return sections


# --------------------------------------------------------------------------
# FAQ building (topic + fact specific)
# --------------------------------------------------------------------------

def _first_fact(post: ParsedPost, theme: str) -> Fact | None:
    for f in post.facts:
        if f.theme == theme:
            return f
    return None


def _fact_phrase(fact: Fact) -> str:
    if fact.raw:
        return fact.raw
    value = _HEDGE_PREFIX_RE.sub("", fact.value).strip()
    # Drop generic column labels ("Housing anchor") when the value stands alone.
    if _is_sentence_value(value):
        return value.rstrip(".")
    if fact.note and fact.note.lower() != value.lower():
        return f"{fact.label} at {value} ({fact.note})"
    return f"{fact.label} at {value}"


# Suffix banks add practical guidance after the article-specific fact. They are
# varied per-article by hash so FAQ answers do not read identically across pages.
_Q1_SUFFIX = [
    "Add insurance, local transport, and a setup buffer on top of housing before you treat that as your true monthly figure.",
    "Layer in health cover, mobility, and a contingency for deposits before calling it your real monthly spend.",
    "Rent is only the anchor — utilities, transport, and a first-month setup fund push the real number higher.",
    "Stack food, transport, insurance, and a currency buffer onto rent to get an honest monthly total.",
    "Treat that as the floor: add insurance, transport, and one overlap month of housing while you settle in.",
    "Budget separately for deposits and agency fees, which routinely add a month or two of rent up front.",
    "Remember that groceries, mobile data, and coworking can quietly rival rent in the first few months.",
    "Pad the figure for exchange-rate swings if your income arrives in a different currency.",
]
_Q2_SUFFIX = [
    "Confirm the exact figure and document list on the official immigration source the week you file, because thresholds shift.",
    "Verify the current requirement and paperwork directly with the consulate before paying anyone, since rules change quietly.",
    "Check the live threshold and evidence checklist on the government portal before you commit, as numbers are revised often.",
    "Match your income proof to the current published requirement before booking an appointment; adjudicators benchmark strictly.",
    "Confirm eligibility and renewal duties with licensed counsel before moving money or booking flights.",
    "Read the small print on renewal and time-in-country rules, since they often matter more than the entry threshold.",
    "Line up apostilles and certified translations early, because they are the step that quietly delays most applications.",
]
_Q3_SUFFIX = [
    "Details like this are easy to miss from abroad but shape daily life fast once you land.",
    "It is the kind of detail spreadsheets skip and arrival week exposes.",
    "Small facts like this decide whether the first month feels smooth or stressful.",
    "This is exactly the sort of thing worth verifying before you sign anything.",
    "Plan around it early rather than discovering it after you have committed.",
    "It rarely shows up in glossy relocation guides but hits your routine immediately.",
    "Sorting it before departure saves a stressful scramble in your first weeks.",
]
_Q4_SUFFIX = [
    "Buy private cover that names your destination explicitly until any public enrollment is active.",
    "Keep a policy that lists the country by name and includes evacuation until local coverage kicks in.",
    "Bridge with private insurance whose wording matches visa requirements before you rely on the public system.",
    "Carry comprehensive cover with clear inpatient limits until residency-based healthcare is confirmed.",
    "Check whether your permit requires proof of insurance on day one, then buy accordingly.",
    "Keep receipts and policy documents handy, since some registrations ask for them at the counter.",
]
_Q5_SUFFIX = [
    "against your own income and timeline, then build a dated evidence folder before you pay any non-refundable deposit.",
    "against your real numbers, then sequence appointments before signing a lease or wiring a deposit.",
    "before anything else, then assemble document proof so paperwork never becomes the bottleneck.",
    "against your situation, then lock the legal steps before optimizing lifestyle or taxes.",
    "against a conservative budget, then book the first official appointment before committing to housing.",
    "before you fall for a neighborhood, then confirm the paperwork sequence so nothing stalls on arrival.",
]


def build_faq(post: ParsedPost) -> list[tuple[str, str]]:
    """Topic-specific Q&A, each answer led by an article-specific fact."""
    topic = (post.topic or post.frontmatter.get("title", "this move")).strip()
    slug = post.slug
    qa: list[tuple[str, str]] = []

    cost = _first_fact(post, "cost")
    visa = _first_fact(post, "visa")
    health = _first_fact(post, "health")
    others = [f for f in post.facts if f.theme == "general"]

    if cost:
        q = _pick(
            [
                f"How much does {topic} cost per month?",
                f"What monthly budget should I plan for {topic}?",
                f"Is {topic} affordable, and what are the real costs?",
                f"What does {topic} realistically cost each month?",
                f"How far does a mid-range budget go for {topic}?",
                f"What are the true monthly numbers behind {topic}?",
            ],
            slug, "q1",
        )
        a = f"{_fact_sentence(cost, slug, 101)} {_pick(_Q1_SUFFIX, slug, 'q1s')}"
        qa.append((q, a))

    if visa:
        q = _pick(
            [
                f"What visa or residency route fits {topic}?",
                f"Which permit should I prioritize for {topic}?",
                f"How do I stay legally for {topic}?",
                f"What is the cleanest legal path for {topic}?",
                f"Which residency option makes {topic} workable?",
                f"How do the visa rules actually apply to {topic}?",
            ],
            slug, "q2",
        )
        a = f"{_fact_sentence(visa, slug, 102)} {_pick(_Q2_SUFFIX, slug, 'q2s')}"
        qa.append((q, a))

    if others:
        pick = others[_seed(slug, "q3") % len(others)]
        q = _pick(
            [
                f"What surprises people most about {topic}?",
                f"What practical detail matters for {topic}?",
                f"What should I check before committing to {topic}?",
                f"What do people underestimate about {topic}?",
                f"Which detail catches newcomers out with {topic}?",
                f"What is easy to overlook when planning {topic}?",
            ],
            slug, "q3q",
        )
        a = f"{_fact_sentence(pick, slug, 103)} {_pick(_Q3_SUFFIX, slug, 'q3s')}"
        qa.append((q, a))

    if health:
        q = _pick(
            [
                f"How does healthcare work for {topic}?",
                f"What should I know about health cover for {topic}?",
                f"Is private or public health cover better for {topic}?",
                f"How do I handle medical insurance for {topic}?",
            ],
            slug, "q4",
        )
        a = f"{_fact_sentence(health, slug, 104)} {_pick(_Q4_SUFFIX, slug, 'q4s')}"
        qa.append((q, a))

    anchor = cost or visa or (others[0] if others else health)
    if anchor:
        q = _pick(
            [
                f"What is the smartest first step for {topic}?",
                f"Where should I start with {topic}?",
                f"What should I do first when planning {topic}?",
                f"What is the right opening move for {topic}?",
                f"How should I begin planning {topic}?",
                f"What comes first when preparing {topic}?",
            ],
            slug, "q5",
        )
        a = (
            f"Start by pressure-testing the headline number — {_fact_phrase(anchor)} — "
            f"{_pick(_Q5_SUFFIX, slug, 'q5s')}"
        )
        qa.append((q, a))

    return qa


# Intro openers used only when an article's original intro is shared boilerplate.
# Kept varied so rebuilt intros do not collapse into a single template, and each
# intro leads with the article's own fact where one exists.
_INTRO_OPENERS = [
    "rewards people who anchor every decision to real numbers instead of vibes.",
    "gets far easier when you treat it as a logistics project, not a daydream.",
    "comes down to a handful of unglamorous choices you make before you book flights.",
    "is mostly about sequencing money, documents, and timing in the right order.",
    "trips up newcomers on the details that are hard to see from your home country.",
    "works best when the plan survives first contact with a spreadsheet.",
    "is less about luck and more about ticking the right boxes early.",
    "starts with the paperwork and budget math most people postpone for too long.",
    "hinges on a few numbers that decide whether the whole plan holds together.",
    "goes smoothly for people who front-load the boring administrative work.",
    "turns on timing: the order you tackle visas, housing, and banking matters.",
    "is easier to get right when you separate the dream from the due diligence.",
    "asks for a realistic budget and a document trail before anything romantic.",
    "rewards early research into costs, permits, and the quirks of local bureaucracy.",
    "comes together once you pin down the visa route and the true cost of living.",
    "favors movers who plan around worst-case timelines, not brochure promises.",
]


_CTXLINK_TEMPLATES = [
    "[{title}]({url}) covers a closely related route in more depth.",
    "For a deeper dive, [{title}]({url}) is the companion guide.",
    "See [{title}]({url}) if you are weighing nearby options.",
    "If you are comparing paths, [{title}]({url}) is worth reading next.",
    "[{title}]({url}) unpacks an adjacent option in more detail.",
    "For the neighbouring scenario, start with [{title}]({url}).",
    "Pair this with [{title}]({url}) for the fuller picture.",
]


def _ctxlink(title: str, url: str, slug: str) -> str:
    tpl = _pick(_CTXLINK_TEMPLATES, slug, "ctxlink")
    return tpl.format(title=title, url=url)


def _unique_intro(post: ParsedPost) -> str:
    """Build a fresh intro when the original is shared boilerplate.

    Leads with the bold topic keyword, then the article's own headline fact so
    the paragraph's opening words differ across pages that carry real data.
    """
    topic = (post.topic or post.frontmatter.get("title", "this move")).strip()
    slug = post.slug
    # Lead with structured (table) facts — desc-derived facts are often the shared
    # marketing description, which would just re-introduce boilerplate. The bold
    # topic acts as a lead-in label, then article-specific fact sentences follow,
    # so the opening words differ across pages that carry real data.
    table_facts = [f for f in post.facts if not f.raw]
    if table_facts:
        sentences = [_fact_sentence(table_facts[0], slug, 200)]
        if len(table_facts) > 1:
            sentences.append(_fact_sentence(table_facts[1], slug, 201))
        intro = f"**{topic}** " + " ".join(sentences)
        return re.sub(r"\s+", " ", intro).strip()
    opener = _pick(_INTRO_OPENERS, slug, "intro-open")
    return f"**{topic}** {opener}"


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------

def _esc_json(obj) -> str:
    return (
        json.dumps(obj, ensure_ascii=False)
        .replace("\\", "\\\\")
        .replace("`", "\\`")
        .replace("${", "\\${")
    )


def _faq_jsonld(qa: list[tuple[str, str]]) -> str:
    mainEntity = [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
        for q, a in qa
    ]
    schema = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": mainEntity}
    return "<JsonLd>\n{`" + _esc_json(schema) + "`}\n</JsonLd>"


TABLE_HEADINGS = [
    "Key numbers at a glance",
    "The figures that matter",
    "Quick-reference data",
    "At a glance",
]


def build_body(post: ParsedPost) -> str:
    """Rebuild the full MDX body with unique, fact-driven sections + FAQ."""
    slug = post.slug
    parts: list[str] = []

    # Intro (kept verbatim — already unique per article)
    if post.intro:
        parts.append(post.intro.strip())

    sections = build_sections(post)

    # Table of contents
    toc_lines = ["## Table of Contents"]
    for heading, _ in sections:
        toc_lines.append(f"- [{heading}](#{_slugify_heading(heading)})")
    if post.table_md:
        table_heading = _pick(TABLE_HEADINGS, slug, "tbl")
        toc_lines.append(f"- [{table_heading}](#{_slugify_heading(table_heading)})")
    parts.append("\n".join(toc_lines))

    # Sections
    for heading, paras in sections:
        block = [f"## {heading}"]
        block += paras
        parts.append("\n\n".join(block))

    # Table under its own heading
    if post.table_md:
        parts.append(f"## {table_heading}\n\n{post.table_md}")

    # In-body contextual internal link (Priority 6) — leads with linked title
    if post.related_links:
        title, url = post.related_links[0]
        parts.append(_ctxlink(title, url, slug))

    # Related guides block (kept)
    if post.related_line:
        parts.append(post.related_line)

    # FAQ
    qa = build_faq(post)
    if qa:
        faq_block = ["## Frequently Asked Questions"]
        for q, a in qa:
            faq_block.append(f"**{q}**\n\n{a}")
        parts.append("\n\n".join(faq_block))

    # CTA
    cta = post.cta or "Start your personalized relocation plan today at [Relova](https://relova.ai)."
    parts.append(f"---\n{cta}")

    # JsonLd: keep Article, rebuild FAQ
    if post.article_jsonld:
        parts.append(post.article_jsonld)
    if qa:
        parts.append(_faq_jsonld(qa))

    return "\n\n".join(parts).strip() + "\n"


# --------------------------------------------------------------------------
# Two-mode rebuild: strip shared boilerplate (Class B) or rebuild from facts
# (Class A). Driven by a corpus-wide boilerplate index.
# --------------------------------------------------------------------------

BOILERPLATE_MIN_SLUGS = 3  # a paragraph/table in >= this many posts is shared filler
CLASS_B_MIN_PARAS = 3      # keep the existing structure if this much unique prose survives
CLASS_B_MIN_WORDS = 150


def _split_regions(body: str) -> tuple[str, str, str]:
    """Return (intro, sections_text, faq_text)."""
    first_h2 = body.find("\n## ")
    if first_h2 == -1:
        return body.strip(), "", ""
    intro = body[:first_h2].strip()
    rest = body[first_h2:]
    fi = rest.find("## Frequently Asked Questions")
    if fi != -1:
        return intro, rest[:fi], rest[fi:]
    return intro, rest, ""


def _norm_table(table_md: str) -> str:
    return re.sub(r"\s+", " ", table_md.replace("|", " ").replace("-", " ")).strip().lower()


def _classify_block(b: str) -> str:
    if b.startswith("## Table of Contents") or b.startswith("- ["):
        return "toc"
    if b.startswith("## "):
        return "heading"
    if b.startswith("|"):
        return "table"
    if b.lower().startswith("related guides on this blog:"):
        return "related"
    if b.startswith("---"):
        return "hr"
    if "<JsonLd>" in b:
        return "jsonld"
    if "[Relova](https://relova.ai)" in b and len(b.split()) < 45:
        return "cta"
    return "para"


def _parse_section_blocks(sections_text: str) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    for raw in re.split(r"\n\s*\n", sections_text):
        b = raw.strip()
        if b:
            blocks.append((_classify_block(b), b))
    return blocks


def _parse_faq_pairs(faq_text: str) -> list[tuple[str, str]]:
    if not faq_text:
        return []
    tail = _JSONLD_RE.sub("", faq_text)
    tail = tail.split("\n---", 1)[0]
    tail = re.sub(r"^##+\s*Frequently Asked Questions\s*", "", tail).strip()
    pairs: list[tuple[str, str]] = []
    q: str | None = None
    for raw in re.split(r"\n\s*\n", tail):
        b = raw.strip()
        if not b:
            continue
        if b.startswith("**") and b.rstrip().endswith("?**"):
            q = b.strip("*").strip()
        elif q is not None:
            pairs.append((q, b))
            q = None
    return pairs


def iter_index_paragraphs(text: str):
    """Yield (normalized_paragraph, normalized_table) items for corpus scan."""
    fm, body = strip_frontmatter(text)
    topic = extract_topic(fm, body)
    for p in split_body_paragraphs(body):
        if len(p.split()) >= 8:
            yield ("para", normalize_paragraph(p, topic))
    for tm in _TABLE_BLOCK_RE.findall(body):
        yield ("table", _norm_table(tm))


# Populated by build_boilerplate_index: fact texts shared across many posts.
# _BOILER_DESCFACTS holds description-derived blurbs reused verbatim; _BOILER_FACTS
# holds table rows (label/value) that repeat across posts. Both are filtered out of
# fact generation so we never emit shared data as body or FAQ content.
_BOILER_DESCFACTS: set[str] = set()
_BOILER_FACTS: set[str] = set()


def _descfact_key(text: str) -> str:
    # Signature = first 8 normalized words, so near-identical marketing blurbs
    # (which diverge only in their tail) still collapse to one shared key.
    words = re.sub(r"[^a-z0-9\s]", " ", text.lower()).split()
    return " ".join(words[:8])


def _factkey(f: "Fact") -> str:
    return re.sub(r"[^a-z0-9\s]", " ", f"{f.label} {f.value}".lower()).strip()


def build_boilerplate_index(texts: list[tuple[str, str]]) -> tuple[set[str], set[str]]:
    """Return (boilerplate_paragraphs, boilerplate_tables) from (slug, text) list.

    Also refreshes the module-level ``_BOILER_DESCFACTS`` and ``_BOILER_FACTS``
    sets of shared description- and table-derived facts.
    """
    from collections import defaultdict

    para_slugs: dict[str, set[str]] = defaultdict(set)
    table_slugs: dict[str, set[str]] = defaultdict(set)
    descfact_slugs: dict[str, set[str]] = defaultdict(set)
    fact_slugs: dict[str, set[str]] = defaultdict(set)
    for slug, text in texts:
        seen_p, seen_t = set(), set()
        for kind, norm in iter_index_paragraphs(text):
            if kind == "para" and norm not in seen_p:
                seen_p.add(norm)
                para_slugs[norm].add(slug)
            elif kind == "table" and norm not in seen_t:
                seen_t.add(norm)
                table_slugs[norm].add(slug)
        fm, body = strip_frontmatter(text)
        topic = extract_topic(fm, body)
        for f in _parse_desc_facts(fm.get("description", ""), topic):
            descfact_slugs[_descfact_key(f.raw)].add(slug)
        for tm in _TABLE_BLOCK_RE.findall(body):
            for f in _parse_table_facts(tm.strip()):
                fact_slugs[_factkey(f)].add(slug)
    boiler_p = {n for n, s in para_slugs.items() if len(s) >= BOILERPLATE_MIN_SLUGS}
    boiler_t = {n for n, s in table_slugs.items() if len(s) >= BOILERPLATE_MIN_SLUGS}
    _BOILER_DESCFACTS.clear()
    _BOILER_DESCFACTS.update(
        k for k, s in descfact_slugs.items() if len(s) >= BOILERPLATE_MIN_SLUGS
    )
    _BOILER_FACTS.clear()
    _BOILER_FACTS.update(k for k, s in fact_slugs.items() if len(s) >= BOILERPLATE_MIN_SLUGS)
    return boiler_p, boiler_t
    


def _faq_templated(pairs: list[tuple[str, str]], topic: str | None,
                   boiler_p: set[str]) -> bool:
    if not pairs:
        return True
    shared = sum(1 for _q, a in pairs if normalize_paragraph(a, topic) in boiler_p)
    return shared >= 2


def _assemble_class_b(
    post: ParsedPost,
    intro: str,
    kept: list[tuple[str, str]],
    faq_pairs: list[tuple[str, str]],
    faq_is_templated: bool,
    boiler_p: set[str] | None = None,
) -> str:
    slug = post.slug
    # Group kept blocks into (heading, [content]) sections; capture related line.
    groups: list[tuple[str | None, list[str]]] = []
    cur_h: str | None = None
    cur_c: list[str] = []
    related_line = ""
    for kind, b in kept:
        if kind == "heading":
            if cur_h is not None or cur_c:
                groups.append((cur_h, cur_c))
            cur_h, cur_c = b, []
        elif kind == "related":
            related_line = b
        else:
            cur_c.append(b)
    if cur_h is not None or cur_c:
        groups.append((cur_h, cur_c))
    groups = [(h, c) for h, c in groups if c]

    parts: list[str] = [intro]

    toc = ["## Table of Contents"]
    for h, _c in groups:
        if h:
            ht = h[3:].strip()
            toc.append(f"- [{ht}](#{_slugify_heading(ht)})")
    if len(toc) > 1:
        parts.append("\n".join(toc))

    for h, c in groups:
        block = [h] if h else []
        block += c
        parts.append("\n\n".join(block))

    if post.related_links:
        title, url = post.related_links[0]
        parts.append(_ctxlink(title, url, slug))
    if related_line:
        parts.append(related_line)
    elif post.related_line:
        parts.append(post.related_line)

    # Drop any FAQ answers that are shared boilerplate, then rebuild from facts
    # if the FAQ was templated (falling back to whatever unique pairs remain).
    bp = boiler_p or set()
    clean_pairs = [
        (q, a) for q, a in faq_pairs if normalize_paragraph(a, post.topic) not in bp
    ]
    if faq_is_templated:
        qa = build_faq(post) or clean_pairs
    else:
        qa = clean_pairs
    if qa:
        faq_block = ["## Frequently Asked Questions"]
        for q, a in qa:
            faq_block.append(f"**{q}**\n\n{a}")
        parts.append("\n\n".join(faq_block))

    cta = post.cta or "Start your personalized relocation plan today at [Relova](https://relova.ai)."
    parts.append(f"---\n{cta}")
    if post.article_jsonld:
        parts.append(post.article_jsonld)
    if qa:
        parts.append(_faq_jsonld(qa))
    return "\n\n".join(parts).strip() + "\n"


def _refresh_facts(post: ParsedPost, boiler_t: set[str]) -> None:
    """Recompute facts from NON-boilerplate tables + description.

    Prevents Class A from synthesising sentences out of a generic table that is
    shared verbatim across dozens of posts.
    """
    all_tables = _TABLE_BLOCK_RE.findall(post.body)
    good_tables = [t.strip() for t in all_tables if _norm_table(t) not in boiler_t]
    facts: list[Fact] = []
    for t in good_tables:
        # Drop individual rows that repeat across many posts (shared data).
        facts += [f for f in _parse_table_facts(t) if _factkey(f) not in _BOILER_FACTS]
    if len(facts) < 5:
        for f in _parse_desc_facts(post.frontmatter.get("description", ""), post.topic):
            # Skip description blurbs reused verbatim across many posts.
            if _descfact_key(f.raw) in _BOILER_DESCFACTS:
                continue
            facts.append(f)
    post.facts = facts
    post.table_md = good_tables[0] if good_tables else ""


# A post needs at least this many real, non-boilerplate facts to justify a
# fact-driven rebuild; below it we fall back to a minimal clean (boilerplate
# still stripped). Kept low so a post with even a small real table gets its
# shared filler replaced by fact-driven prose rather than merely de-duplicated.
CLASS_A_MIN_FACTS = 2


def rebuild_post(text: str, boiler_p: set[str], boiler_t: set[str]) -> tuple[str | None, str]:
    """Rebuild one post. Returns (new_body, mode).

    mode is one of:
    * 'SKIP' the post is already clean (no shared filler / intra-dup / templated
             FAQ); new_body is None and the caller must leave the file untouched.
    * 'B'    keep the article's unique prose/tables, strip shared filler.
    * 'A'    rebuild the body from the post's own (non-boilerplate) facts.
    * 'C'    minimal clean: no usable facts, so keep only non-boilerplate prose.
    """
    post = parse_mdx(text)
    intro, sections_text, faq_text = _split_regions(post.body)
    blocks = _parse_section_blocks(sections_text)
    topic = post.topic

    kept_strict: list[tuple[str, str]] = []   # boilerplate + intra-dup removed
    seen_norms: set[str] = set()
    seen_tables: set[str] = set()
    para_norms: list[str] = []
    has_boiler = False
    for kind, b in blocks:
        if kind in ("toc", "hr", "jsonld", "cta"):
            continue
        if kind == "para":
            norm = normalize_paragraph(b, topic)
            long_enough = len(norm.split()) >= 8
            if long_enough:
                para_norms.append(norm)
                if norm in boiler_p:
                    has_boiler = True
            if norm in seen_norms:
                continue
            seen_norms.add(norm)
            if not (long_enough and norm in boiler_p):
                kept_strict.append((kind, b))
        elif kind == "table":
            tn = _norm_table(b)
            if tn in seen_tables:
                continue
            seen_tables.add(tn)
            if tn in boiler_t:
                has_boiler = True
            else:
                kept_strict.append((kind, b))
        else:
            kept_strict.append((kind, b))

    faq_pairs = _parse_faq_pairs(faq_text)
    templated = bool(faq_pairs) and _faq_templated(faq_pairs, topic, boiler_p)
    faq_boiler = any(
        len((nn := normalize_paragraph(a, topic)).split()) >= 8 and nn in boiler_p
        for _q, a in faq_pairs
    )
    intra_dup = len(para_norms) != len(set(para_norms))

    # The intro region may hold several paragraphs (lead + shared CTA blurbs).
    # Keep the article-specific lead, but drop any shared/boilerplate paragraphs.
    intro_paras = [p.strip() for p in re.split(r"\n\s*\n", intro) if p.strip()] if intro else []
    lead = intro_paras[0] if intro_paras else ""
    lead_norm = normalize_paragraph(lead, topic) if lead else ""
    lead_is_boiler = bool(lead_norm) and len(lead_norm.split()) >= 8 and lead_norm in boiler_p
    kept_intro_extra: list[str] = []
    for p in intro_paras[1:]:
        n = normalize_paragraph(p, topic)
        if len(n.split()) >= 8 and n in boiler_p:
            has_boiler = True  # shared blurb/CTA hiding above the first heading
            continue
        kept_intro_extra.append(p)

    # Comprehensive boilerplate check across every region (intro, sections, FAQ,
    # trailing promos) so a shared paragraph anywhere prevents a wrongful SKIP.
    if not has_boiler:
        for p in split_body_paragraphs(post.body):
            n = normalize_paragraph(p, topic)
            if len(n.split()) >= 8 and n in boiler_p:
                has_boiler = True
                break

    # Already-clean article (e.g. hand-written editorial): leave it untouched.
    if not has_boiler and not intra_dup and not templated and not lead_is_boiler \
            and not faq_boiler:
        return None, "SKIP"

    # Recompute facts from NON-boilerplate tables + description up front so both
    # the intro rebuild and the Class A decision can use them.
    _refresh_facts(post, boiler_t)

    # Replace a shared/boilerplate lead with a fact-led, per-article one.
    if lead_is_boiler or not lead:
        lead = _unique_intro(post)
    intro = "\n\n".join([lead, *kept_intro_extra])
    post.intro = intro

    unique_paras = [b for k, b in kept_strict if k == "para"]
    words = sum(len(b.split()) for b in unique_paras)

    if len(unique_paras) >= CLASS_B_MIN_PARAS and words >= CLASS_B_MIN_WORDS:
        return _assemble_class_b(post, intro, kept_strict, faq_pairs, templated, boiler_p), "B"

    if len(post.facts) >= CLASS_A_MIN_FACTS:
        return build_body(post), "A"

    # Class C — no usable facts; keep only the non-boilerplate prose that exists.
    return _assemble_class_b(post, intro, kept_strict, faq_pairs, templated, boiler_p), "C"


def has_intra_duplication(body: str, topic: str | None = None, threshold: int = 0) -> bool:
    """True if the body has more intra-page duplicate paragraphs than threshold.

    Used by generators as a pre-save guard.
    """
    paras = split_body_paragraphs(body)
    count, _ = intra_page_duplicates(paras, topic)
    return count > threshold


# --------------------------------------------------------------------------
# Generator entry point (used by gen_batchN.py for batch 11+)
# --------------------------------------------------------------------------

def _article_jsonld(title: str, description: str, date: str, slug: str,
                    author: str = "Relova Team") -> str:
    art = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": description,
        "datePublished": date,
        "dateModified": date,
        "author": {"@type": "Organization", "name": author},
        "publisher": {"@type": "Organization", "name": "Relova", "url": "https://relova.ai"},
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": f"https://blog.relova.ai/blog/{slug}",
        },
    }
    return "<JsonLd>\n{`" + _esc_json(art) + "`}\n</JsonLd>"


class DuplicationError(ValueError):
    """Raised when a freshly generated post fails the pre-save dedup guard."""


def render_post_from_spec(
    *,
    title: str,
    slug: str,
    date: str,
    kw: str,
    description: str,
    links: list[str],
    intro: str,
    table_md: str,
    author: str = "Relova Team",
    og_image: str = "/images/blog-default.jpg",
    cta: str | None = None,
) -> str:
    """Build a complete, de-duplicated .mdx for a new post.

    Body sections and FAQ are synthesised from the spec's own facts (table +
    description), guaranteeing per-article uniqueness. Raises DuplicationError
    if the result somehow still contains intra-page duplicate paragraphs, so a
    generator never silently writes a templated file.
    """
    fm_lines = [
        "---",
        f'title: "{title}"',
        f'description: "{description}"',
        f'date: "{date}"',
        f"slug: {slug}",
        f'author: "{author}"',
        f'ogImage: "{og_image}"',
        "---",
    ]
    intro_block = intro.strip()
    if not intro_block.startswith("**"):
        intro_block = f"**{kw}** {intro_block}"

    related_links = [
        (s.replace("-", " ").title(), f"https://blog.relova.ai/blog/{s}") for s in links
    ]
    related_line = ""
    if related_links:
        related_line = "Related guides on this blog: " + ", ".join(
            f"[{t}]({u})" for t, u in related_links
        ) + "."

    facts = _parse_table_facts(table_md)
    if len(facts) < 5:
        facts += _parse_desc_facts(description, kw)

    post = ParsedPost(
        frontmatter={
            "title": title,
            "description": description,
            "date": date,
            "slug": slug,
        },
        body="",
        slug=slug,
        topic=kw,
        intro=intro_block,
        table_md=table_md.strip(),
        related_line=related_line,
        related_links=related_links,
        cta=cta or "Start your personalized relocation plan today at [Relova](https://relova.ai).",
        article_jsonld=_article_jsonld(title, description, date, slug, author),
        facts=facts,
    )
    body = build_body(post)
    if has_intra_duplication(body, kw):
        raise DuplicationError(
            f"{slug}: generated body still has duplicate paragraphs; "
            "add more distinct facts to the spec's table/description."
        )
    return "\n".join(fm_lines) + "\n\n" + body

