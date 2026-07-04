#!/usr/bin/env python3
"""Audit intra-page and cross-page content duplication across content/posts/*.mdx.

Also exposes reusable helpers (``split_body_paragraphs``, ``normalize_paragraph``,
``paragraph_signature``, ``intra_page_duplicates``) that the batch generators
import so a new post is never saved with duplicated body paragraphs.

Usage:
    python scripts/audit_duplication.py            # full audit -> audit_report.csv
    python scripts/audit_duplication.py --top 20   # show top 20 cloned paragraphs
"""
from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "content/posts"
REPORT = ROOT / "audit_report.csv"

# Paragraphs shorter than this (in words) are ignored for duplication scoring:
# short CTAs / one-liners repeating is acceptable per the acceptance criteria.
MIN_WORDS = 12
# Similarity threshold for "near-duplicate" paragraphs.
SIMILARITY = 0.90
# First N words used as a cross-page signature after topic phrase removal.
SIGNATURE_WORDS = 10


def strip_frontmatter(text: str) -> tuple[dict, str]:
    """Return (frontmatter dict, body) for an .mdx file."""
    fm: dict[str, str] = {}
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            raw_fm = text[3:end].strip("\n")
            for line in raw_fm.splitlines():
                m = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", line)
                if m:
                    fm[m.group(1)] = m.group(2).strip().strip('"')
            body = text[end + 4 :]
            return fm, body
    return fm, text


_JSONLD_RE = re.compile(r"<JsonLd>.*?</JsonLd>", re.DOTALL)
_HEADING_RE = re.compile(r"^#{1,6}\s")
_TABLE_RE = re.compile(r"^\s*\|")
_TOC_RE = re.compile(r"^\s*-\s*\[")


def split_body_paragraphs(body: str) -> list[str]:
    """Split MDX body into content paragraphs, dropping structural noise.

    Excludes: JsonLd blocks, headings, table rows, TOC bullets, HR rules,
    and the trailing CTA/related-guides lines. Returns readable prose blocks.
    """
    body = _JSONLD_RE.sub("", body)
    blocks = re.split(r"\n\s*\n", body)
    out: list[str] = []
    for block in blocks:
        b = block.strip()
        if not b:
            continue
        if _HEADING_RE.match(b):
            continue
        if _TABLE_RE.match(b):
            continue
        if _TOC_RE.match(b):
            continue
        if b.startswith("---"):
            continue
        if b.lower().startswith("related guides"):
            continue
        if b.lower().startswith("table of contents"):
            continue
        out.append(b)
    return out


def normalize_paragraph(p: str, topic: str | None = None) -> str:
    """Lowercase, strip markdown/punctuation, drop the injected topic phrase."""
    s = p.lower()
    # Drop leading bold keyword marker like **kw**
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", s)  # markdown links -> text
    if topic:
        s = s.replace(topic.lower(), " ")
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def paragraph_signature(p: str, topic: str | None = None) -> str:
    """First SIGNATURE_WORDS words of the normalized paragraph."""
    norm = normalize_paragraph(p, topic)
    return " ".join(norm.split()[:SIGNATURE_WORDS])


def extract_topic(fm: dict, body: str) -> str | None:
    """Best-effort topic/keyword phrase: leading **bold** of the intro."""
    m = re.search(r"\*\*(.+?)\*\*", body)
    if m:
        return m.group(1).strip()
    return fm.get("title")


def intra_page_duplicates(
    paragraphs: list[str], topic: str | None = None
) -> tuple[int, list[str]]:
    """Count paragraphs that repeat (exact or >=SIMILARITY) within one page.

    Returns (extra_duplicate_count, list_of_duplicated_normalized_texts).
    The count is "extra" occurrences: 5 identical paragraphs => 4.
    """
    norms = [
        normalize_paragraph(p, topic)
        for p in paragraphs
        if len(p.split()) >= MIN_WORDS
    ]
    seen: list[str] = []
    dup_count = 0
    dup_texts: list[str] = []
    for n in norms:
        matched = False
        for s in seen:
            if n == s or SequenceMatcher(None, n, s).ratio() >= SIMILARITY:
                matched = True
                break
        if matched:
            dup_count += 1
            dup_texts.append(n)
        else:
            seen.append(n)
    return dup_count, dup_texts


# ---- FAQ extraction -------------------------------------------------------

_FAQ_HEADER_RE = re.compile(r"^##+\s*Frequently Asked Questions\s*$", re.MULTILINE)


def extract_faq_answers(body: str, topic: str | None = None) -> list[str]:
    """Return normalized FAQ answer texts (the paragraph after each **Q?**)."""
    m = _FAQ_HEADER_RE.search(body)
    if not m:
        return []
    tail = body[m.end() :]
    tail = _JSONLD_RE.sub("", tail)
    tail = tail.split("\n---", 1)[0]
    blocks = re.split(r"\n\s*\n", tail)
    answers: list[str] = []
    expect_answer = False
    for block in blocks:
        b = block.strip()
        if not b:
            continue
        is_question = b.startswith("**") and b.rstrip().endswith("?**")
        if is_question:
            expect_answer = True
            continue
        if expect_answer:
            answers.append(normalize_paragraph(b, topic))
            expect_answer = False
    return answers


def load_posts() -> list[tuple[str, dict, str]]:
    """Return list of (slug, frontmatter, body) for every post."""
    posts = []
    for path in sorted(POSTS.glob("*.mdx")):
        text = path.read_text(encoding="utf-8")
        fm, body = strip_frontmatter(text)
        slug = fm.get("slug") or path.stem
        posts.append((slug, fm, body))
    return posts


def run_audit(top: int = 10) -> None:
    posts = load_posts()
    n = len(posts)

    # Global indexes
    signature_to_slugs: dict[str, set[str]] = defaultdict(set)
    signature_to_example: dict[str, str] = {}
    faq_answer_to_slugs: dict[str, set[str]] = defaultdict(set)

    per_post_paragraphs: dict[str, list[str]] = {}
    per_post_topic: dict[str, str | None] = {}
    per_post_faq: dict[str, list[str]] = {}

    for slug, fm, body in posts:
        topic = extract_topic(fm, body)
        per_post_topic[slug] = topic
        paras = split_body_paragraphs(body)
        per_post_paragraphs[slug] = paras
        for p in paras:
            if len(p.split()) < MIN_WORDS:
                continue
            sig = paragraph_signature(p, topic)
            if not sig:
                continue
            signature_to_slugs[sig].add(slug)
            signature_to_example.setdefault(sig, p.strip())
        faq = extract_faq_answers(body, topic)
        per_post_faq[slug] = faq
        for a in faq:
            if len(a.split()) < 6:
                continue
            faq_answer_to_slugs[a].add(slug)

    # Cross-page signatures that appear in more than one post
    cross_signatures = {
        sig for sig, slugs in signature_to_slugs.items() if len(slugs) > 1
    }
    cross_faq = {a for a, slugs in faq_answer_to_slugs.items() if len(slugs) > 1}

    rows = []
    intra_affected = 0
    cross_affected = 0
    faq_templated_count = 0

    for slug, fm, body in posts:
        topic = per_post_topic[slug]
        paras = per_post_paragraphs[slug]
        intra_count, _ = intra_page_duplicates(paras, topic)

        cross_count = 0
        for p in paras:
            if len(p.split()) < MIN_WORDS:
                continue
            sig = paragraph_signature(p, topic)
            if sig in cross_signatures:
                cross_count += 1

        faq = per_post_faq[slug]
        templated_answers = sum(1 for a in faq if a in cross_faq)
        faq_is_templated = len(faq) > 0 and templated_answers >= 3

        if intra_count > 0:
            intra_affected += 1
        if cross_count > 0:
            cross_affected += 1
        if faq_is_templated:
            faq_templated_count += 1

        rows.append(
            {
                "slug": slug,
                "intra_page_duplicate_paragraphs_count": intra_count,
                "cross_page_duplicate_paragraphs_count": cross_count,
                "faq_is_templated": "true" if faq_is_templated else "false",
            }
        )

    with REPORT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "slug",
                "intra_page_duplicate_paragraphs_count",
                "cross_page_duplicate_paragraphs_count",
                "faq_is_templated",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    # Top cloned paragraph templates
    clone_ranking = sorted(
        ((len(slugs), sig) for sig, slugs in signature_to_slugs.items() if len(slugs) > 1),
        reverse=True,
    )

    print("=" * 78)
    print(f"DUPLICATION AUDIT  —  {n} posts scanned")
    print("=" * 78)
    print(f"Posts with intra-page duplicate paragraphs : {intra_affected} / {n} "
          f"({100 * intra_affected / n:.0f}%)")
    print(f"Posts with cross-page duplicate paragraphs : {cross_affected} / {n} "
          f"({100 * cross_affected / n:.0f}%)")
    print(f"Posts with templated FAQ (>=3 shared answers): {faq_templated_count} / {n} "
          f"({100 * faq_templated_count / n:.0f}%)")
    print(f"Distinct cross-page cloned paragraph templates: {len(cross_signatures)}")
    print(f"Distinct cross-page cloned FAQ answers        : {len(cross_faq)}")
    print(f"\nReport written to {REPORT}")

    print(f"\nTOP {top} MOST-CLONED PARAGRAPH TEMPLATES (appears in N posts):")
    print("-" * 78)
    for count, sig in clone_ranking[:top]:
        example = signature_to_example.get(sig, sig)
        preview = example[:120] + ("…" if len(example) > 120 else "")
        print(f"[{count:>3} posts] {preview}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=10)
    args = ap.parse_args()
    run_audit(top=args.top)
