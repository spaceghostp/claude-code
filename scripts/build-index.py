#!/usr/bin/env python3
"""Build a JSON index of all cognitive vault notes.

Scans vault markdown files (excluding _meta/), parses frontmatter and body,
extracts wikilinks and keywords, computes bidirectional links, and writes
a structured index to vault/_meta/index.json.

No external dependencies — uses only Python stdlib.
"""

import json
import os
import re
import sys
from datetime import date
from pathlib import Path


# Words too common to be useful as keywords
STOP_WORDS = frozenset({
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "it", "its", "this", "that", "are",
    "was", "be", "as", "has", "had", "not", "no", "if", "do", "did", "does",
    "will", "would", "could", "should", "can", "may", "might", "about",
    "what", "when", "where", "which", "who", "how", "why", "all", "each",
    "every", "both", "few", "more", "most", "other", "some", "such", "than",
    "too", "very", "just", "also", "into", "over", "after", "before", "between",
    "through", "during", "without", "again", "further", "then", "once", "here",
    "there", "these", "those", "my", "your", "his", "her", "our", "their",
    "i", "me", "we", "you", "he", "she", "they", "them", "been", "being",
    "have", "having", "any", "up", "out", "so", "only", "own", "same",
    "don", "doesn", "didn", "won", "isn", "aren", "wasn", "weren", "hasn",
    "haven", "hadn", "couldn", "shouldn", "wouldn", "mustn", "needn",
    "ve", "re", "ll", "t", "s", "d", "m",
})

# Minimum keyword length
MIN_KEYWORD_LEN = 3


def find_vault_root():
    """Find the vault directory relative to the script or working directory."""
    # Try sibling to script's parent (scripts/ and vault/ are siblings at repo root)
    script_dir = Path(__file__).resolve().parent
    vault_from_script = script_dir.parent / "vault"
    if (vault_from_script / "_meta" / "conventions.md").exists():
        return vault_from_script

    # Try working directory
    cwd = Path.cwd()
    vault_from_cwd = cwd / "vault"
    if (vault_from_cwd / "_meta" / "conventions.md").exists():
        return vault_from_cwd

    return None


def parse_frontmatter(filepath):
    """Parse YAML frontmatter from a markdown file.

    Simple key:value parser matching resurface.py approach.
    Returns (dict, remaining_lines) or (None, []) on failure.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except (OSError, UnicodeDecodeError):
        return None, []

    if not lines or lines[0].strip() != "---":
        return None, []

    frontmatter = {}
    found_end = False

    end_index = 0
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            found_end = True
            end_index = i
            break
        if ":" in line:
            key, _, value = line.partition(":")
            frontmatter[key.strip()] = value.strip()

    if not found_end:
        return None, []

    body_lines = lines[end_index + 1:]
    return frontmatter, body_lines


def strip_code(text):
    """Remove fenced code blocks and inline code from text.

    This prevents extracting wikilinks or keywords from code examples.
    """
    # Remove fenced code blocks (```...```) first
    text = re.sub(r"```[\s\S]*?```", "", text)
    # Remove inline code (`...`)
    text = re.sub(r"`[^`]+`", "", text)
    return text


def extract_title(body_lines):
    """Extract the first H1 heading from body lines."""
    for line in body_lines:
        stripped = line.strip()
        if stripped.startswith("# ") and not stripped.startswith("## "):
            return stripped[2:].strip()
    return ""


def extract_wikilinks(body_text):
    """Extract all [[wikilink]] targets from body content (code already stripped)."""
    # Match [[path/name]] or [[path/name|display]]
    matches = re.findall(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]", body_text)
    links = []
    for match in matches:
        # Normalize: strip whitespace, remove .md if present
        link = match.strip()
        if link.endswith(".md"):
            link = link[:-3]
        links.append(link)
    return links


def extract_heading_words(body_lines):
    """Extract words from ## and ### headings."""
    words = []
    for line in body_lines:
        stripped = line.strip()
        if stripped.startswith("## ") or stripped.startswith("### "):
            # Remove the heading markers
            heading_text = re.sub(r"^#{2,3}\s+", "", stripped)
            # Split into words, strip punctuation
            for word in re.findall(r"[a-zA-Z]+", heading_text):
                words.append(word.lower())
    return words


def extract_keywords(body_lines, wikilinks):
    """Extract keywords from headings, wikilinks, and body terms.

    Sources:
    - Words from ## and ### headings
    - Basenames of wikilink targets (split on hyphens)
    - Deduplicated, lowercased, stop words filtered
    """
    keywords = set()

    # 1. Words from ## and ### headings
    heading_words = extract_heading_words(body_lines)
    for word in heading_words:
        w = word.lower()
        if w not in STOP_WORDS and len(w) >= MIN_KEYWORD_LEN:
            keywords.add(w)

    # 2. Basenames of wikilink targets (last path component, split on hyphens)
    for link in wikilinks:
        basename = link.split("/")[-1]
        for part in basename.split("-"):
            w = part.lower()
            if w not in STOP_WORDS and len(w) >= MIN_KEYWORD_LEN:
                keywords.add(w)

    return sorted(keywords)


def deduplicate_links(links):
    """Deduplicate while preserving order."""
    seen = set()
    result = []
    for link in links:
        if link not in seen:
            seen.add(link)
            result.append(link)
    return result


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
