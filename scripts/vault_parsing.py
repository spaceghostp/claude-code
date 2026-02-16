#!/usr/bin/env python3
"""Shared parsing utilities for cognitive vault scripts.

Extracted from build-index.py and migrate-execute.py to eliminate duplication.
Used by: build-index.py, migrate-execute.py, pre-filter-vault.py,
         partition-domains.py, merge-linkmaps.py

No external dependencies — uses only Python stdlib.
"""

import re
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


def find_vault_root(from_path=None):
    """Find the vault directory relative to a given path or script/working directory.

    Search order:
    1. If from_path provided: from_path/vault/
    2. Sibling to script's parent: scripts/../vault/
    3. Current working directory: ./vault/

    Returns Path or None.
    """
    if from_path is not None:
        candidate = Path(from_path) / "vault"
        if (candidate / "_meta" / "conventions.md").exists():
            return candidate

    # Try sibling to caller's script parent (scripts/ and vault/ are siblings)
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

    Simple key:value parser. Returns (dict, remaining_lines) or (None, []).
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

    Prevents extracting wikilinks or keywords from code examples.
    """
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r"`[^`]+`", "", text)
    return text


def extract_wikilinks(body_text):
    """Extract all [[wikilink]] targets from body content (code already stripped).

    Returns list of link targets (deduplicated, .md suffix stripped).
    """
    matches = re.findall(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]", body_text)
    links = []
    for match in matches:
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
            heading_text = re.sub(r"^#{2,3}\s+", "", stripped)
            for word in re.findall(r"[a-zA-Z]+", heading_text):
                words.append(word.lower())
    return words


def count_wikilinks(content):
    """Count unique wikilinks in content (for links_out frontmatter)."""
    matches = re.findall(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]", content)
    return len(set(matches))


def extract_title(body_lines):
    """Extract the first H1 heading from body lines."""
    for line in body_lines:
        stripped = line.strip()
        if stripped.startswith("# ") and not stripped.startswith("## "):
            return stripped[2:].strip()
    return ""


def extract_keywords(body_lines, wikilinks):
    """Extract keywords from headings, wikilinks, and body terms.

    Sources: ## and ### heading words, wikilink target basenames.
    Deduplicated, lowercased, stop words filtered.
    """
    keywords = set()

    heading_words = extract_heading_words(body_lines)
    for word in heading_words:
        w = word.lower()
        if w not in STOP_WORDS and len(w) >= MIN_KEYWORD_LEN:
            keywords.add(w)

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


# Map type names to their directory names
TYPE_DIRS = {
    "atom": "atoms",
    "tension": "tensions",
    "encounter": "encounters",
    "position": "positions",
    "question": "questions",
    "revision": "revisions",
    "anti-library": "anti-library",
    "falsification": "falsifications",
}
