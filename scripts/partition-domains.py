#!/usr/bin/env python3
"""Partition pre-filtered vault notes into domain-specific migration catalogs.

Reads the JSONL output from pre-filter-vault.py, clusters notes by wikilink
co-occurrence, and produces per-domain catalog JSON files ready for Claude
triage and migrate-execute.py.

Usage:
    python3 scripts/partition-domains.py [--tier medium|large|massive]
                                         [--max-domain-size 5000]
                                         [--source-path /path/to/source]

Output:
    migration/catalog-domain-{name}.json (per-domain catalogs)
    migration/_progress.json (global progress tracker)

No external dependencies — uses only Python stdlib.
"""

import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


# Tier cutoff thresholds (must match pre-filter-vault.py)
TIER_CUTOFFS = {
    "medium": 40,
    "large": 60,
    "massive": 75,
}

# Batch sizes per tier
TIER_BATCH_SIZES = {
    "medium": 20,
    "large": 50,
    "massive": 100,
}


def load_filtered_notes(jsonl_path, cutoff):
    """Load notes from JSONL that meet the tier cutoff. Yields dicts."""
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            if entry.get("score", 0) >= cutoff:
                yield entry


def extract_wikilink_targets(wikilinks):
    """Extract bare targets from [[wikilink]] strings."""
    targets = []
    for link in wikilinks:
        match = re.match(r"\[\[([^\]|]+)", link)
        if match:
            targets.append(match.group(1).strip())
    return targets


def build_domain_signatures(notes):
    """Compute domain signature for each note based on top-5 link targets.

    Returns list of (note_entry, signature_tuple) pairs.
    """
    # Count global link target frequency
    target_counter = Counter()
    note_targets = []

    for note in notes:
        targets = extract_wikilink_targets(note.get("wikilinks", []))
        target_counter.update(targets)
        note_targets.append((note, targets))

    # For each note, signature = sorted top-5 most-referenced targets
    result = []
    for note, targets in note_targets:
        if not targets:
            # No links — assign to "unlinked" domain
            result.append((note, ("__unlinked__",)))
            continue

        # Score targets by global frequency (higher = more common = better domain marker)
        scored = [(target_counter[t], t) for t in set(targets)]
        scored.sort(reverse=True)
        top5 = tuple(t for _, t in scored[:5])
        result.append((note, top5))

    return result


def cluster_by_signature(note_signatures):
    """Group notes with identical domain signatures.

    Returns dict of {signature: [note_entries]}.
    """
    clusters = defaultdict(list)
    for note, sig in note_signatures:
        clusters[sig].append(note)
    return clusters


def merge_small_clusters(clusters, min_size=3):
    """Merge clusters smaller than min_size into the most similar larger cluster.

    Returns merged clusters dict.
    """
    large = {}
    small = {}

    for sig, notes in clusters.items():
        if len(notes) >= min_size:
            large[sig] = notes
        else:
            small[sig] = notes

    if not large:
        # All clusters are small — just return as-is
        return clusters

    # Merge each small cluster into the large cluster with most shared targets
    for sig, notes in small.items():
        sig_set = set(sig)
        best_match = None
        best_overlap = -1
        for large_sig in large:
            overlap = len(sig_set & set(large_sig))
            if overlap > best_overlap:
                best_overlap = overlap
                best_match = large_sig

        if best_match is not None:
            large[best_match].extend(notes)
        else:
            # Shouldn't happen, but safety
            large[sig] = notes

    return large


def name_domain(signature, clusters_notes):
    """Generate a human-readable domain name from a cluster's signature."""
    if signature == ("__unlinked__",):
        return "unlinked"

    # Use the most common wikilink target across all notes in the cluster
    target_counter = Counter()
    for note in clusters_notes:
        targets = extract_wikilink_targets(note.get("wikilinks", []))
        target_counter.update(targets)

    if target_counter:
        most_common = target_counter.most_common(1)[0][0]
        # Clean up: take basename, kebab-case
        name = Path(most_common).stem
        name = re.sub(r"[^a-zA-Z0-9-]", "-", name).lower().strip("-")
        return name or "misc"
    return "misc"


def split_oversized_domain(name, notes, max_size):
    """Split a domain exceeding max_size by filename first character.

    Returns list of (name, notes) tuples.
    """
    if len(notes) <= max_size:
        return [(name, notes)]

    # Group by first character of filename
    char_groups = defaultdict(list)
    for note in notes:
        source = note.get("source", "")
        basename = Path(source).stem
        first_char = basename[0].lower() if basename else "_"
        char_groups[first_char].append(note)

    # If still too large after char split, just chunk
    result = []
    current_batch = []
    current_name_suffix = 0

    for char in sorted(char_groups.keys()):
        group = char_groups[char]
        if len(current_batch) + len(group) > max_size and current_batch:
            current_name_suffix += 1
            result.append((f"{name}-{current_name_suffix}", current_batch))
            current_batch = []
        current_batch.extend(group)

    if current_batch:
        current_name_suffix += 1
        result.append((f"{name}-{current_name_suffix}", current_batch))

    return result


def suggest_type(note):
    """Pre-populate suggested_type based on heuristics."""
    source = note.get("source", "").lower()
    basename = Path(source).stem.lower()
    wikilinks = note.get("wikilinks", [])

    # Date-prefixed filename -> encounter
    if re.match(r"\d{4}-\d{2}-\d{2}", basename):
        return "encounter"

    # Title contains tension markers
    if "vs" in basename or "tension" in basename or "tradeoff" in basename:
        return "tension"

    # Short + high link density -> atom
    word_count = note.get("word_count", 0)
    if word_count < 150 and len(wikilinks) >= 2:
        return "atom"

    # Question markers
    if basename.endswith("?") or "question" in basename:
        return "question"

    # Default: encounter (safest general type)
    return "encounter"


def build_catalog(domain_name, notes, source_path, tier, batch_size, total_source):
    """Build a per-domain catalog JSON structure."""
    catalog_notes = []
    for note in notes:
        catalog_notes.append({
            "source": note["source"],
            "score": note.get("score", 0),
            "suggested_type": suggest_type(note),
            "action": None,
            "type": None,
            "filename": None,
            "reason": None,
        })

    return {
        "version": "1.0",
        "domain": domain_name,
        "source_path": str(source_path),
        "created": datetime.now().strftime("%Y-%m-%d"),
        "batch_size": batch_size,
        "source_count": total_source,
        "filtered_count": len(notes),
        "link_map": {},
        "notes": catalog_notes,
        "progress": {"processed": 0, "current_batch": 1},
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Partition pre-filtered notes into domain-specific catalogs"
    )
    parser.add_argument("--tier", choices=["medium", "large", "massive"],
                        default="medium", help="Migration tier")
    parser.add_argument("--max-domain-size", type=int, default=5000,
                        help="Maximum notes per domain catalog")
    parser.add_argument("--source-path", type=str, default="",
                        help="Source vault path (stored in catalogs for migrate-execute)")
    parser.add_argument("--input", type=str,
                        help="Input JSONL path (default: migration/_pre-filter-scores.jsonl)")
    args = parser.parse_args()

    input_path = Path(args.input) if args.input else Path("migration") / "_pre-filter-scores.jsonl"
    if not input_path.exists():
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        print("Run pre-filter-vault.py first.", file=sys.stderr)
        sys.exit(1)

    tier_cutoff = TIER_CUTOFFS[args.tier]
    batch_size = TIER_BATCH_SIZES[args.tier]

    print(f"Partitioning notes (tier: {args.tier}, cutoff: {tier_cutoff})")

    # Load filtered notes into memory for clustering
    notes = list(load_filtered_notes(str(input_path), tier_cutoff))
    if not notes:
        print("No notes above cutoff threshold. Nothing to partition.", file=sys.stderr)
        sys.exit(0)

    print(f"  {len(notes)} notes above cutoff")

    # Build domain signatures and cluster
    print("  Computing domain signatures...")
    note_sigs = build_domain_signatures(notes)
    raw_clusters = cluster_by_signature(note_sigs)
    print(f"  {len(raw_clusters)} raw clusters")

    # Merge small clusters
    merged = merge_small_clusters(raw_clusters)
    print(f"  {len(merged)} clusters after merging small groups")

    # Name domains and split oversized ones
    named_domains = []
    for sig, cluster_notes in merged.items():
        name = name_domain(sig, cluster_notes)
        splits = split_oversized_domain(name, cluster_notes, args.max_domain_size)
        named_domains.extend(splits)

    # Deduplicate domain names
    seen_names = Counter()
    final_domains = []
    for name, domain_notes in named_domains:
        seen_names[name] += 1
        if seen_names[name] > 1:
            name = f"{name}-{seen_names[name]}"
        final_domains.append((name, domain_notes))

    # Count total source notes (approximate from JSONL line count)
    total_source = 0
    with open(input_path, "r", encoding="utf-8") as f:
        for _ in f:
            total_source += 1

    # Write per-domain catalogs
    output_dir = Path("migration")
    os.makedirs(output_dir, exist_ok=True)

    progress_domains = {}
    for name, domain_notes in final_domains:
        catalog = build_catalog(
            name, domain_notes, args.source_path, args.tier,
            batch_size, total_source
        )
        catalog_path = output_dir / f"catalog-domain-{name}.json"
        with open(catalog_path, "w", encoding="utf-8") as f:
            json.dump(catalog, f, indent=2, ensure_ascii=False)
            f.write("\n")

        progress_domains[name] = {
            "status": "pending",
            "notes_filtered": len(domain_notes),
            "notes_processed": 0,
            "last_batch": 0,
        }

        print(f"  Domain '{name}': {len(domain_notes)} notes -> {catalog_path}")

    # Write global progress file
    progress = {
        "tier": args.tier,
        "source_vault": args.source_path,
        "total_source_notes": total_source,
        "total_filtered_notes": len(notes),
        "domains": progress_domains,
        "last_updated": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    progress_path = output_dir / "_progress.json"
    with open(progress_path, "w", encoding="utf-8") as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"\nPartitioning complete:")
    print(f"  {len(final_domains)} domain catalog(s) created")
    print(f"  Progress file: {progress_path}")
    print(f"\nNext steps:")
    print(f"  1. Review samples per domain (Claude calibration session)")
    print(f"  2. Triage notes: fill action/type/filename in each catalog")
    print(f"  3. Execute: python3 scripts/migrate-execute.py --catalog migration/catalog-domain-<name>.json")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
