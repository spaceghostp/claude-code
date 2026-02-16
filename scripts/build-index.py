#!/usr/bin/env python3
"""Build a JSON index of all cognitive vault notes.

Scans vault markdown files (excluding _meta/), parses frontmatter and body,
extracts wikilinks and keywords, computes bidirectional links, and writes
a structured index to vault/_meta/index.json.

No external dependencies — uses only Python stdlib.
"""

import json
import os
import sys
from datetime import date

from vault_parsing import (
    find_vault_root,
    parse_frontmatter,
    strip_code,
    extract_wikilinks,
    extract_title,
    extract_keywords,
    deduplicate_links,
)


def load_existing_index(index_path):
    """Load existing index.json if it exists. Returns dict or None."""
    try:
        with open(index_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError, ValueError):
        return None


def main():
    warnings = 0
    today = date.today().isoformat()

    vault_root = find_vault_root()
    if vault_root is None:
        print("Index built: 0 notes indexed, 0 warnings", file=sys.stdout)
        print("Warning: vault root not found", file=sys.stderr)
        sys.exit(0)

    index_path = vault_root / "_meta" / "index.json"

    # Load existing index to preserve maintenance fields
    existing = load_existing_index(index_path)
    if existing is not None:
        last_maintained = existing.get("last_maintained", today)
        notes_since_maintenance = existing.get("notes_since_maintenance", 0)
    else:
        last_maintained = today
        notes_since_maintenance = 0

    # Scan all vault markdown files, excluding _meta/
    notes = {}
    all_md_files = sorted(vault_root.rglob("*.md"))

    for md_file in all_md_files:
        rel = md_file.relative_to(vault_root)
        parts = rel.parts

        # Skip _meta/ directory
        if parts[0] == "_meta":
            continue

        # Skip hidden files/directories
        if any(p.startswith(".") for p in parts):
            continue

        # Build the note key: relative path without .md
        note_key = str(rel.with_suffix(""))
        # Normalize to forward slashes (should already be on Linux, but be safe)
        note_key = note_key.replace(os.sep, "/")

        # Parse frontmatter
        fm, body_lines = parse_frontmatter(md_file)
        if fm is None:
            print(
                f"Warning: skipping {note_key} (malformed or missing frontmatter)",
                file=sys.stderr,
            )
            warnings += 1
            continue

        # Extract fields from frontmatter
        note_type = fm.get("type", "")
        status = fm.get("status", "")
        lifecycle = fm.get("lifecycle", "active")
        created = fm.get("created", "")
        last_touched = fm.get("last_touched", "")
        origin = fm.get("origin", "")

        # Extract title from first H1
        title = extract_title(body_lines)

        # Strip code blocks and inline code before extracting wikilinks
        body_text = strip_code("".join(body_lines))

        # Extract wikilinks from cleaned body
        raw_links = extract_wikilinks(body_text)
        links_out = deduplicate_links(raw_links)

        # Extract keywords (headings use raw body_lines, wikilinks from cleaned)
        keywords = extract_keywords(body_lines, links_out)

        notes[note_key] = {
            "type": note_type,
            "status": status,
            "lifecycle": lifecycle,
            "created": created,
            "last_touched": last_touched,
            "origin": origin,
            "keywords": keywords,
            "links_out": links_out,
            "links_in": [],  # Populated in second pass
            "title": title,
        }

    # Second pass: compute links_in (bidirectional)
    for source_key, source_data in notes.items():
        for target in source_data["links_out"]:
            if target in notes:
                if source_key not in notes[target]["links_in"]:
                    notes[target]["links_in"].append(source_key)

    # Sort links_in for deterministic output
    for note_data in notes.values():
        note_data["links_in"].sort()

    # Build the index
    index = {
        "last_updated": today,
        "last_maintained": last_maintained,
        "notes_since_maintenance": notes_since_maintenance,
        "notes": notes,
    }

    # Write index.json
    try:
        os.makedirs(vault_root / "_meta", exist_ok=True)
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
            f.write("\n")
    except OSError as e:
        print(f"Warning: could not write index: {e}", file=sys.stderr)
        warnings += 1

    print(f"Index built: {len(notes)} notes indexed, {warnings} warnings")
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Warning: unexpected error: {e}", file=sys.stderr)
        print("Index built: 0 notes indexed, 1 warnings")
        sys.exit(0)
