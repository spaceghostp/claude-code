#!/usr/bin/env python3
"""Execute a vault migration from a prepared catalog.

Reads a migration catalog JSON, transforms source notes into vault format with
link rewriting and frontmatter synthesis, writes them to the appropriate type
directories. Processes in batches to respect the hard ceiling (10 proposed
notes pauses captures).

Supports per-domain catalogs (--catalog flag) and auto-promotion for
high-scoring notes (score >= threshold in catalog entry).

Usage:
    python3 scripts/migrate-execute.py [--dry-run] [--batch-size N] [--catalog PATH]

No external dependencies — uses only Python stdlib.
"""

import json
import os
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".claude" / "vault" / "_scripts"))
from vault_parsing import find_vault_root, count_wikilinks, TYPE_DIRS


DEFAULT_AUTO_PROMOTE_THRESHOLD = 90


def load_catalog(catalog_path):
    """Load and validate the migration catalog."""
    try:
        with open(catalog_path, "r", encoding="utf-8") as f:
            catalog = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"Error: could not load catalog: {e}", file=sys.stderr)
        sys.exit(1)

    required = ["version", "source_path", "link_map", "notes", "progress"]
    for field in required:
        if field not in catalog:
            print(f"Error: catalog missing required field '{field}'", file=sys.stderr)
            sys.exit(1)

    return catalog


def save_catalog(catalog, catalog_path):
    """Save the catalog with updated progress."""
    try:
        with open(catalog_path, "w", encoding="utf-8") as f:
            json.dump(catalog, f, indent=2, ensure_ascii=False)
            f.write("\n")
    except OSError as e:
        print(f"Error: could not save catalog: {e}", file=sys.stderr)
        sys.exit(1)


def strip_frontmatter(content):
    """Remove existing YAML frontmatter from source content."""
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        return content

    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            # Return everything after the closing ---
            remaining = "\n".join(lines[i + 1:])
            return remaining.lstrip("\n")

    # No closing --- found, return original
    return content


def apply_link_map(content, link_map):
    """Rewrite wikilinks according to the link map.

    Handles four cases:
    - Mapped to vault path: [[External]] -> [[positions/target]]
    - Mapped to null: [[External]] -> External (plain text)
    - Not in map: left unchanged (broken links are acceptable per conventions)
    """
    for old_link, new_link in link_map.items():
        if old_link not in content:
            continue
        if new_link is None:
            # Convert to plain text: strip [[ and ]]
            plain = old_link.lstrip("[").rstrip("]")
            content = content.replace(old_link, plain)
        else:
            content = content.replace(old_link, new_link)

    return content


def load_calibrated_filters(vault_root):
    """Load calibrated filters if present. Returns dict or None."""
    filters_path = Path("migration") / "_calibrated-filters.json"
    # Try relative to vault root's parent (repo root)
    repo_root = vault_root.parent
    candidate = repo_root / filters_path
    if candidate.exists():
        try:
            with open(candidate, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            pass
    return None


def generate_frontmatter(note_type, today, score=None, auto_promote_threshold=None):
    """Generate vault-standard frontmatter for an imported note.

    If score is provided and >= auto_promote_threshold, the note is auto-promoted
    to lifecycle: active / status: working. Otherwise defaults to proposed/unverified.
    """
    threshold = auto_promote_threshold or DEFAULT_AUTO_PROMOTE_THRESHOLD
    if score is not None and score >= threshold:
        lifecycle, status = "active", "working"
    else:
        lifecycle, status = "proposed", "unverified"

    return (
        "---\n"
        f"type: {note_type}\n"
        f"status: {status}\n"
        f"lifecycle: {lifecycle}\n"
        f"created: {today}\n"
        f"last_touched: {today}\n"
        "links_out: {links_out}\n"
        "origin: migration\n"
        "---\n"
    )


def process_note(note_entry, catalog, vault_root, today, dry_run=False,
                 auto_promote_threshold=None):
    """Process a single import note entry. Returns (success, message)."""
    source_rel = note_entry["source"]
    note_type = note_entry.get("type", "")
    filename = note_entry.get("filename", "")

    if not note_type or not filename:
        return False, f"  SKIP {source_rel}: missing type or filename"

    # Determine target directory
    type_dir = TYPE_DIRS.get(note_type)
    if type_dir is None:
        return False, f"  SKIP {source_rel}: unknown type '{note_type}'"

    target_dir = vault_root / type_dir
    target_path = target_dir / filename

    # Idempotency: don't overwrite existing files
    if target_path.exists():
        return False, f"  SKIP {source_rel}: target already exists at {type_dir}/{filename}"

    # Resolve source path (relative to source_path in catalog, or absolute)
    source_path_str = catalog.get("source_path", "")
    source_path = Path(source_rel)
    if not source_path.is_absolute() and source_path_str:
        source_path = Path(source_path_str) / source_rel

    if not source_path.exists():
        return False, f"  SKIP {source_rel}: source file not found at {source_path}"

    # Read source content
    try:
        with open(source_path, "r", encoding="utf-8") as f:
            content = f.read()
    except (OSError, UnicodeDecodeError) as e:
        return False, f"  SKIP {source_rel}: could not read source: {e}"

    # Transform
    content = strip_frontmatter(content)
    content = apply_link_map(content, catalog.get("link_map", {}))
    links_out = count_wikilinks(content)

    # Generate frontmatter with actual link count and auto-promotion
    score = note_entry.get("score")
    fm = generate_frontmatter(note_type, today, score=score,
                              auto_promote_threshold=auto_promote_threshold)
    fm = fm.replace("links_out: {links_out}", f"links_out: {links_out}")

    final_content = fm + "\n" + content
    # Ensure file ends with newline
    if not final_content.endswith("\n"):
        final_content += "\n"

    # Status indicator for auto-promoted notes
    promo_tag = ""
    if score is not None:
        threshold = auto_promote_threshold or DEFAULT_AUTO_PROMOTE_THRESHOLD
        if score >= threshold:
            promo_tag = " [auto-promoted]"

    if dry_run:
        return True, f"  DRY-RUN: would write {type_dir}/{filename} ({links_out} links){promo_tag}"

    # Write the file
    try:
        os.makedirs(target_dir, exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(final_content)
    except OSError as e:
        return False, f"  ERROR {source_rel}: could not write: {e}"

    return True, f"  OK: {type_dir}/{filename} ({links_out} links){promo_tag}"


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Execute vault migration from catalog")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be done without writing files")
    parser.add_argument("--batch-size", type=int, default=0,
                        help="Override batch_size from catalog (0 = use catalog value)")
    parser.add_argument("--catalog", type=str,
                        help="Path to migration catalog (default: vault/_meta/migration-catalog.json)")
    args = parser.parse_args()

    vault_root = find_vault_root()
    if vault_root is None:
        print("Error: vault root not found", file=sys.stderr)
        sys.exit(1)

    # Resolve catalog path
    if args.catalog:
        catalog_path = Path(args.catalog)
    else:
        catalog_path = vault_root / "_meta" / "migration-catalog.json"

    if not catalog_path.exists():
        print(f"Error: no migration catalog found at {catalog_path}", file=sys.stderr)
        print("Create one using Claude triage or partition-domains.py first.", file=sys.stderr)
        sys.exit(1)

    catalog = load_catalog(catalog_path)
    today = date.today().isoformat()

    # Load calibrated filters for auto-promotion threshold override
    calibrated = load_calibrated_filters(vault_root)
    auto_promote_threshold = DEFAULT_AUTO_PROMOTE_THRESHOLD
    if calibrated:
        auto_promote_threshold = calibrated.get("auto_promote_threshold",
                                                DEFAULT_AUTO_PROMOTE_THRESHOLD)
        # Check for domain-specific override
        domain = catalog.get("domain", "")
        domain_overrides = calibrated.get("domain_overrides", {})
        if domain in domain_overrides:
            domain_threshold = domain_overrides[domain].get("auto_promote_threshold")
            if domain_threshold is not None:
                auto_promote_threshold = domain_threshold

    batch_size = args.batch_size if args.batch_size > 0 else catalog.get("batch_size", 8)
    progress = catalog.get("progress", {"processed": 0, "current_batch": 1})
    start_index = progress.get("processed", 0)

    # Filter to import-only notes (skip and merge are handled elsewhere)
    import_notes = [n for n in catalog["notes"] if n.get("action") == "import"]
    total_imports = len(import_notes)

    if start_index >= total_imports:
        print(f"Migration complete: all {total_imports} import notes have been processed.")
        merge_notes = [n for n in catalog["notes"] if n.get("action") == "merge"]
        if merge_notes:
            print(f"\n{len(merge_notes)} merge candidate(s) remain — handle these in a Claude session:")
            for mn in merge_notes:
                print(f"  {mn['source']} -> {mn.get('merge_target', '???')}: {mn.get('reason', '')}")
        sys.exit(0)

    # Determine this batch
    batch_end = min(start_index + batch_size, total_imports)
    batch = import_notes[start_index:batch_end]

    print(f"Migration batch {progress.get('current_batch', 1)}: "
          f"notes {start_index + 1}-{batch_end} of {total_imports} imports")
    if args.dry_run:
        print("(DRY RUN — no files will be written)\n")
    else:
        print()

    # Process each note in the batch
    imported = 0
    skipped = 0
    for entry in batch:
        success, message = process_note(entry, catalog, vault_root, today,
                                        dry_run=args.dry_run,
                                        auto_promote_threshold=auto_promote_threshold)
        print(message)
        if success:
            imported += 1
        else:
            skipped += 1

    # Update progress in catalog (even on dry run, to show what would change)
    if not args.dry_run:
        progress["processed"] = batch_end
        progress["current_batch"] = progress.get("current_batch", 1) + 1
        catalog["progress"] = progress
        save_catalog(catalog, catalog_path)

    # Summary
    print(f"\nBatch complete: {imported} imported, {skipped} skipped")
    remaining = total_imports - batch_end
    if remaining > 0:
        print(f"{remaining} import notes remain in future batches.")
        print("\nNext steps:")
        print("  1. Run: python3 scripts/build-index.py")
        print("  2. Run: /vault-maintain (review proposed notes)")
        print("  3. Re-run: python3 scripts/migrate-execute.py" +
              (f" --catalog {catalog_path}" if args.catalog else ""))
    else:
        print("All import notes processed.")
        print("\nNext steps:")
        print("  1. Run: python3 scripts/build-index.py")
        print("  2. Run: /vault-maintain (review all proposed notes)")

    # Remind about merge candidates
    merge_notes = [n for n in catalog["notes"] if n.get("action") == "merge"]
    if merge_notes:
        print(f"\n{len(merge_notes)} merge candidate(s) remain — handle these in a Claude session:")
        for mn in merge_notes:
            print(f"  {mn['source']} -> {mn.get('merge_target', '???')}: {mn.get('reason', '')}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted. Progress saved — re-run to resume.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
