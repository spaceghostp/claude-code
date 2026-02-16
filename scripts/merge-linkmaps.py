#!/usr/bin/env python3
"""Merge per-domain link maps and resolve cross-domain wikilinks.

After all domains are processed by migrate-execute.py, this script:
1. Reads all per-domain link map files (migration/_linkmap-{domain}.json)
2. Builds a unified {old_title: new_vault_path} mapping
3. Scans all migrated notes (origin: migration) in the vault
4. Rewrites unresolved wikilinks using the cross-domain index

Usage:
    python3 scripts/merge-linkmaps.py [--dry-run]

No external dependencies — uses only Python stdlib.
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".claude" / "vault" / "_scripts"))
from vault_parsing import find_vault_root, parse_frontmatter, strip_code, extract_wikilinks


def load_linkmaps(migration_dir):
    """Load all _linkmap-*.json files from the migration directory.

    Returns unified dict of {old_wikilink_text: new_vault_path}.
    """
    unified = {}
    linkmap_files = sorted(migration_dir.glob("_linkmap-*.json"))

    if not linkmap_files:
        return unified

    for lm_path in linkmap_files:
        try:
            with open(lm_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            print(f"  Warning: could not read {lm_path.name}: {e}", file=sys.stderr)
            continue

        if isinstance(data, dict):
            for old, new in data.items():
                if new is not None:
                    unified[old] = new

        print(f"  Loaded {lm_path.name}: {len(data)} entries")

    return unified


def find_migrated_notes(vault_root):
    """Find all vault notes with origin: migration. Returns list of Paths."""
    migrated = []

    for md_file in vault_root.rglob("*.md"):
        rel = md_file.relative_to(vault_root)
        parts = rel.parts

        # Skip _meta/ and hidden
        if parts[0] == "_meta" or any(p.startswith(".") for p in parts):
            continue

        fm, _ = parse_frontmatter(md_file)
        if fm is not None and fm.get("origin") == "migration":
            migrated.append(md_file)

    return migrated


def find_unresolved_links(content, vault_root):
    """Find wikilinks in content that don't resolve to existing vault notes.

    Returns list of raw wikilink targets that are unresolved.
    """
    cleaned = strip_code(content)
    links = extract_wikilinks(cleaned)
    unresolved = []

    for link in links:
        # Check if the link resolves to a file
        target_path = vault_root / (link + ".md")
        if not target_path.exists():
            # Also try without directory prefix
            unresolved.append(link)

    return unresolved


def rewrite_links(content, cross_index):
    """Rewrite unresolved wikilinks using the cross-domain index.

    Returns (new_content, rewrite_count).
    """
    count = 0
    for old_text, new_path in cross_index.items():
        # Match [[old_text]] or [[old_text|display]]
        pattern = re.compile(
            r"\[\[" + re.escape(old_text) + r"(\|[^\]]*)?\]\]"
        )
        matches = pattern.findall(content)
        if matches or pattern.search(content):
            # Replace with new path, preserving display text if present
            def replace_fn(m):
                display = m.group(1) or ""
                return f"[[{new_path}{display}]]"
            new_content = pattern.sub(replace_fn, content)
            if new_content != content:
                count += 1
                content = new_content

    return content, count


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Merge per-domain link maps and resolve cross-domain wikilinks"
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be rewritten without modifying files")
    args = parser.parse_args()

    vault_root = find_vault_root()
    if vault_root is None:
        print("Error: vault root not found", file=sys.stderr)
        sys.exit(1)

    migration_dir = vault_root.parent / "migration"
    if not migration_dir.is_dir():
        print("Error: migration/ directory not found", file=sys.stderr)
        sys.exit(1)

    # Step 1: Load and merge all domain link maps
    print("Loading per-domain link maps...")
    cross_index = load_linkmaps(migration_dir)
    if not cross_index:
        print("No link maps found. Nothing to merge.")
        print("Link maps are created during Claude triage sessions as migration/_linkmap-{domain}.json")
        sys.exit(0)

    print(f"  Unified cross-domain index: {len(cross_index)} mappings")

    # Write cross-domain index for reference
    index_path = migration_dir / "_cross-domain-index.json"
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(cross_index, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"  Written: {index_path}")

    # Step 2: Find all migrated notes
    print("\nScanning migrated notes...")
    migrated = find_migrated_notes(vault_root)
    print(f"  Found {len(migrated)} notes with origin: migration")

    if not migrated:
        print("No migrated notes found. Run migrate-execute.py first.")
        sys.exit(0)

    # Step 3: Rewrite unresolved links
    print("\nResolving cross-domain links...")
    total_rewrites = 0
    files_modified = 0

    for md_file in migrated:
        try:
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()
        except (OSError, UnicodeDecodeError) as e:
            print(f"  Warning: could not read {md_file}: {e}", file=sys.stderr)
            continue

        new_content, rewrite_count = rewrite_links(content, cross_index)

        if rewrite_count > 0:
            rel = md_file.relative_to(vault_root)
            if args.dry_run:
                print(f"  DRY-RUN: would rewrite {rewrite_count} link(s) in {rel}")
            else:
                with open(md_file, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"  Rewrote {rewrite_count} link(s) in {rel}")

            total_rewrites += rewrite_count
            files_modified += 1

    # Summary
    print(f"\nCross-domain link resolution complete:")
    print(f"  Files {'would be ' if args.dry_run else ''}modified: {files_modified}")
    print(f"  Links {'would be ' if args.dry_run else ''}rewritten: {total_rewrites}")

    if total_rewrites > 0 and not args.dry_run:
        print("\nNext steps:")
        print("  1. Run: python3 scripts/build-index.py")
        print("  2. Run: /vault-maintain (spot-check review)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
