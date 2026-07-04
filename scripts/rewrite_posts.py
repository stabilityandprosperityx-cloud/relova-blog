#!/usr/bin/env python3
"""Rewrite templated/duplicated posts into unique, fact-driven articles.

The rewrite engine self-flags: every post is examined, and one is only touched
when it actually carries shared filler, intra-page duplication, or a templated
FAQ. Genuinely unique (hand-written) posts are reported as SKIP and left
untouched. No dependency on a stale audit_report.csv.

Usage:
    python scripts/rewrite_posts.py --dry-run          # report what would change
    python scripts/rewrite_posts.py --only SLUG        # rewrite one post, print it
    python scripts/rewrite_posts.py                    # rewrite all flagged posts
"""
from __future__ import annotations

import argparse
from pathlib import Path

from content_lib import (
    build_boilerplate_index,
    has_intra_duplication,
    parse_mdx,
    rebuild_post,
)

ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "content/posts"


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
    if mode == "SKIP" or new_body is None:
        return False, "SKIP (already clean)"
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
        print(body if body is not None else "(unchanged)")
        return

    targets = sorted(POSTS.glob("*.mdx"))
    if args.limit:
        targets = targets[: args.limit]

    if args.dry_run:
        modes = {"A": 0, "B": 0, "C": 0, "SKIP": 0}
        for p in targets:
            body, mode = rebuild_post(p.read_text(encoding="utf-8"), boiler_p, boiler_t)
            modes[mode] = modes.get(mode, 0) + 1
        print(f"{len(targets)} posts examined.")
        for m in ("A", "B", "C", "SKIP"):
            print(f"  mode {m}: {modes.get(m, 0)}")
        return

    changed = 0
    modes = {"A": 0, "B": 0, "C": 0}
    skipped = []
    warnings = []
    for p in targets:
        ok, msg = rewrite_file(p, boiler_p, boiler_t)
        if ok:
            changed += 1
            for m in ("A", "B", "C"):
                if f"({m})" in msg:
                    modes[m] += 1
        elif msg.startswith("WARNING"):
            warnings.append((p.stem, msg))
        else:
            skipped.append((p.stem, msg))
    print(
        f"Rewrote {changed} posts "
        f"(fact-rebuild A={modes['A']}, keep-clean B={modes['B']}, minimal C={modes['C']})."
    )
    print(f"Left untouched (already clean): {len(skipped)}.")
    if warnings:
        print(f"WARNINGS ({len(warnings)}):")
        for slug, msg in warnings:
            print(f"  {slug}: {msg}")


if __name__ == "__main__":
    main()
