#!/usr/bin/env python3
"""Pre-filter a source vault for migration by structural scoring.

Scans all markdown files in a source vault, scores each note on structural
quality signals (wikilink density, word count, heading count, recency), and
outputs scored results as streaming JSONL for downstream partitioning.

Two-pass algorithm:
  Pass 1: Score individual notes (word count, links, headings, recency)
  Pass 2: Add bidirectional link scores from inverted index

Usage:
    python3 scripts/pre-filter-vault.py /path/to/source [--tier medium|large|massive]

Output: migration/_pre-filter-scores.jsonl

No external dependencies — uses only Python stdlib.
"""

import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".claude" / "vault" / "_scripts"))
from vault_parsing import parse_frontmatter, strip_code, extract_wikilinks


# Tier cutoff thresholds
TIER_CUTOFFS = {
    "medium": 40,   # 200-10K notes, ~30-50% reduction
    "large": 60,    # 10K-100K notes, ~70-80% reduction
    "massive": 75,  # 100K-1M notes, ~90-95% reduction
}


def score_wikilink_density(wikilink_count, word_count):
    """Score based on wikilinks per 100 words. Max 30 points."""
    if word_count == 0:
        return 0
    density = wikilink_count / (word_count / 100.0)
    if density >= 0.10:
        return 30
    if density >= 0.05:
        return 15
    return 0


def score_word_count(word_count):
    """Score based on word count (sweet spot 200-800). Max 20 points."""
    if 200 <= word_count <= 800:
        return 20
    if 100 <= word_count <= 1500:
        return 10
    return 0


def score_recency(mtime_str, now):
    """Score based on file modification time. Max 15 points."""
    try:
        mtime = datetime.strptime(mtime_str, "%Y-%m-%d")
        days = (now - mtime).days
        if days <= 90:
            return 15
        if days <= 365:
            return 5
    except (ValueError, TypeError):
        pass
    return 0


def score_headings(heading_count):
    """Score based on heading structure. Max 10 points."""
    if heading_count >= 3:
        return 10
    return 0


def count_words(text):
    """Count words in text (simple whitespace split)."""
    return len(text.split())


def count_headings(body_lines):
    """Count ## and ### headings in body."""
    count = 0
    for line in body_lines:
        stripped = line.strip()
        if stripped.startswith("## ") or stripped.startswith("### "):
            count += 1
    return count


def get_mtime_str(filepath):
    """Get file modification time as YYYY-MM-DD string."""
    try:
        mtime = os.path.getmtime(filepath)
        return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
    except OSError:
        return ""


def scan_source_vault(source_path):
    """Yield all .md files in the source vault."""
    source = Path(source_path)
    for md_file in sorted(source.rglob("*.md")):
        # Skip hidden files/directories
        rel = md_file.relative_to(source)
        if any(p.startswith(".") for p in rel.parts):
            continue
        yield md_file, str(rel)


def pass1_score_notes(source_path, tmp_path, now):
    """Pass 1: Score individual notes and write to temp JSONL.

    Returns the inverted link index {target: [sources]} for Pass 2.
    """
    inverted_index = {}  # {wikilink_target: set(source_paths)}
    note_count = 0

    with open(tmp_path, "w", encoding="utf-8") as out:
        for md_file, rel_path in scan_source_vault(source_path):
            fm, body_lines = parse_frontmatter(md_file)

            # Score even without frontmatter — source vaults may not use it
            if fm is None:
                try:
                    with open(md_file, "r", encoding="utf-8") as f:
                        body_lines = f.readlines()
                except (OSError, UnicodeDecodeError):
                    continue

            body_text = strip_code("".join(body_lines))
            wikilinks = extract_wikilinks(body_text)
            wikilink_strs = [f"[[{link}]]" for link in wikilinks]
            word_count = count_words(body_text)
            heading_count = count_headings(body_lines)
            mtime_str = get_mtime_str(md_file)

            # Compute individual scores (no bidirectional yet)
            s_links = score_wikilink_density(len(wikilinks), word_count)
            s_words = score_word_count(word_count)
            s_recency = score_recency(mtime_str, now)
            s_headings = score_headings(heading_count)
            base_score = s_links + s_words + s_recency + s_headings

            # Build inverted index for Pass 2
            for link in wikilinks:
                if link not in inverted_index:
                    inverted_index[link] = set()
                inverted_index[link].add(rel_path)

            entry = {
                "source": rel_path,
                "base_score": base_score,
                "wikilinks": wikilink_strs,
                "wikilink_targets": wikilinks,
                "word_count": word_count,
                "heading_count": heading_count,
                "mtime": mtime_str,
            }
            out.write(json.dumps(entry, ensure_ascii=False) + "\n")
            note_count += 1

    return inverted_index, note_count


def pass2_add_bidirectional(tmp_path, output_path, inverted_index, tier_cutoff):
    """Pass 2: Re-read temp JSONL, add bidirectional link scores, write final.

    Returns (total_scored, above_cutoff) counts.
    """
    total = 0
    above_cutoff = 0

    with open(tmp_path, "r", encoding="utf-8") as inp, \
         open(output_path, "w", encoding="utf-8") as out:
        for line in inp:
            entry = json.loads(line)
            source = entry["source"]

            # Count bidirectional links: how many other notes link to this one?
            # Check both full relative path (without .md) and basename
            source_key = source
            if source_key.endswith(".md"):
                source_key = source_key[:-3]
            source_basename = Path(source_key).stem

            bidir_count = 0
            # Check if anyone links to this note's path or basename
            for target, sources in inverted_index.items():
                if target == source_key or target == source_basename:
                    bidir_count += len(sources)

            # Score bidirectional links (max 25)
            if bidir_count >= 3:
                s_bidir = 25
            elif bidir_count >= 1:
                s_bidir = 10
            else:
                s_bidir = 0

            final_score = entry["base_score"] + s_bidir

            # Write final entry (drop intermediate fields)
            final_entry = {
                "source": source,
                "score": final_score,
                "wikilinks": entry["wikilinks"],
                "word_count": entry["word_count"],
                "heading_count": entry["heading_count"],
                "bidirectional_links": bidir_count,
                "mtime": entry["mtime"],
            }
            out.write(json.dumps(final_entry, ensure_ascii=False) + "\n")

            total += 1
            if final_score >= tier_cutoff:
                above_cutoff += 1

    return total, above_cutoff


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Pre-filter a source vault for migration by structural scoring"
    )
    parser.add_argument("source", type=str, help="Path to source vault directory")
    parser.add_argument("--tier", choices=["medium", "large", "massive"],
                        default="medium", help="Migration tier (affects cutoff threshold)")
    parser.add_argument("--output", type=str,
                        help="Output path (default: migration/_pre-filter-scores.jsonl)")
    args = parser.parse_args()

    source_path = Path(args.source)
    if not source_path.is_dir():
        print(f"Error: source path is not a directory: {source_path}", file=sys.stderr)
        sys.exit(1)

    tier_cutoff = TIER_CUTOFFS[args.tier]
    now = datetime.now()

    # Ensure output directory exists
    output_path = Path(args.output) if args.output else Path("migration") / "_pre-filter-scores.jsonl"
    os.makedirs(output_path.parent, exist_ok=True)

    print(f"Pre-filtering source vault: {source_path}")
    print(f"Tier: {args.tier} (cutoff score: {tier_cutoff})")

    # Pass 1: Score individual notes
    print("Pass 1: Scoring individual notes...")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False,
                                     encoding="utf-8") as tmp:
        tmp_path = tmp.name

    try:
        inverted_index, note_count = pass1_score_notes(source_path, tmp_path, now)
        print(f"  Scanned {note_count} notes, {len(inverted_index)} unique link targets")

        # Pass 2: Add bidirectional link scores
        print("Pass 2: Computing bidirectional link scores...")
        total, above_cutoff = pass2_add_bidirectional(
            tmp_path, str(output_path), inverted_index, tier_cutoff
        )
    finally:
        # Clean up temp file
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

    # Summary
    reduction = ((total - above_cutoff) / total * 100) if total > 0 else 0
    print(f"\nResults:")
    print(f"  Total notes scanned: {total}")
    print(f"  Above cutoff (score >= {tier_cutoff}): {above_cutoff}")
    print(f"  Filtered out: {total - above_cutoff} ({reduction:.0f}% reduction)")
    print(f"\nOutput: {output_path}")
    print(f"\nNext step: python3 scripts/partition-domains.py --tier {args.tier}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
