#!/usr/bin/env python3
"""Rewrite templated/duplicated posts into unique, fact-driven articles.

Decisions are driven by audit_report.csv: a post is rewritten when it has
intra-page duplicate paragraphs OR a templated FAQ OR a high cross-page count.
Genuinely unique (hand-written) posts are left untouched.

Usage:
    python scripts/rewrite_posts.py --dry-run          # report what would change
    python scripts/rewrite_posts.py --only SLUG        # rewrite one post, print it
    python scripts/rewrite_posts.py                    # rewrite all flagged posts
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

from content_lib import (
    build_boilerplate_index,
    has_intra_duplication,
    parse_mdx,
    rebuild_post,
)

ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "content/posts"
REPORT = ROOT / "audit_report.csv"

CROSS_THRESHOLD = 4  # cross-page dup paragraphs that alone justify a rewrite


def load_flags() -> dict[str, dict]:
    flags: dict[str, dict] = {}
    if not REPORT.exists():
        return flags
    with REPORT.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            flags[row["slug"]] = row
    return flags


def should_rewrite(row: dict) -> bool:
    intra = int(row.get("intra_page_duplicate_paragraphs_count", 0) or 0)
    cross = int(row.get("cross_page_duplicate_paragraphs_count", 0) or 0)
    faq = (row.get("faq_is_templated") or "false").lower() == "true"
    return intra > 0 or faq or cross >= CROSS_THRESHOLD


def split_raw_frontmatter(text: str) -> tuple[str, str]:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[: end + 4], text[end + 4 :]
    return "", text


def rewrite_file(path: Path, boiler_p: set[str], boiler_t: set[str]) -> tuple[bool, str]:
    text = path.read_text(encoding="utf-8")
    raw_fm, _ = split_raw_frontmatter(text)
    if not raw_fm:
        return False, "no frontmatter"
    post = parse_mdx(text)
    new_body, mode = rebuild_post(text, boiler_p, boiler_t)
    if mode == "A" and not post.facts:
        return False, "no extractable facts (skipped)"
    if has_intra_duplication(new_body, post.topic):
        return False, "WARNING: rebuilt body still has intra dup (skipped)"
    new_text = raw_fm.rstrip() + "\n\n" + new_body
    path.write_text(new_text, encoding="utf-8")
    return True, f"rewritten ({mode})"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", type=str, default=None)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    flags = load_flags()

    # Build the corpus-wide boilerplate index from ALL posts (shared paragraphs
    # and tables that appear in >= BOILERPLATE_MIN_SLUGS distinct articles).
    all_texts = [
        (p.stem, p.read_text(encoding="utf-8")) for p in sorted(POSTS.glob("*.mdx"))
    ]
    boiler_p, boiler_t = build_boilerplate_index(all_texts)
    print(f"Boilerplate index: {len(boiler_p)} paragraphs, {len(boiler_t)} tables.")

    if args.only:
        path = POSTS / f"{args.only}.mdx"
        body, mode = rebuild_post(path.read_text(encoding="utf-8"), boiler_p, boiler_t)
        print(f"[mode {mode}]\n")
        print(body)
        return

    targets = []
    for path in sorted(POSTS.glob("*.mdx")):
        slug = path.stem
        row = flags.get(slug)
        if row is None:
            continue
        if should_rewrite(row):
            targets.append(path)

    if args.limit:
        targets = targets[: args.limit]

    print(f"{len(targets)} posts flagged for rewrite (of {len(flags)} audited).")
    if args.dry_run:
        for p in targets[:30]:
            print(f"  would rewrite: {p.stem}")
        if len(targets) > 30:
            print(f"  ... and {len(targets) - 30} more")
        return

    changed = 0
    modes = {"A": 0, "B": 0}
    skipped = []
    for p in targets:
        ok, msg = rewrite_file(p, boiler_p, boiler_t)
        if ok:
            changed += 1
            if "(A)" in msg:
                modes["A"] += 1
            elif "(B)" in msg:
                modes["B"] += 1
        else:
            skipped.append((p.stem, msg))
    print(f"Rewrote {changed} posts (fact-rebuild A={modes['A']}, keep-clean B={modes['B']}).")
    if skipped:
        print(f"Skipped {len(skipped)}:")
        for slug, msg in skipped[:40]:
            print(f"  {slug}: {msg}")


if __name__ == "__main__":
    main()
